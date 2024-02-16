# Code gathered at https://docs.python.org/3/library/asyncio-stream.html
import argparse
import asyncio
import json
import logging
import os
import signal
import threading
import time
from typing import Optional
import sys

import random

from typing import Any, Callable, Dict, Set , Union
import enum

# Check https://www.geeksforgeeks.org/python-import-from-parent-directory/
# For better information
# getting the name of the directory
# where this file is present.
current = os.path.dirname(os.path.realpath(__file__))
 
# Getting the parent directory name
# where the current directory is present.
parent = os.path.dirname(current)
 
# adding the parent directory to
# the sys.path.
sys.path.append(parent)

try:
    from .call import Call , CallAction
except Exception:
    from call import Call , CallAction
from common.communication import *
import common.asymmetric as asymmetric
from common.entity import Entity , INVALID_SEQ_NUMBER , find_seq_number_by_stream , find_seq_number_by_stream_writer , Banned_Reason , Bans, print_user_list
from common.state import State
from common.logger import Logger
from cryptography import x509
from common.asymmetric import sign_message
from termcolor import colored

def truncate_dict(d: dict, max_length: int = 50) -> dict:
    """
    Truncate the values in the dictionary to a maximum length.
    """

    if not isinstance(d , dict):
        raise ValueError(f"trucate_dict 'd' argument must be of type 'dict', received {type(d)}")

    if not isinstance(max_length , int):
        raise ValueError(f"trucate_dict 'max_length' argument must be of type 'int', received {type(max_length)}")

    if max_length <= 0:
        raise ValueError(f"truncate_dict 'max_length' argument must be greater than 0")

    truncated_d: dict = {}
    for key, value in d.items():
        if len(str(value)) > max_length:
            truncated_value = str(value)[:max_length - 3] + "..."
        else:
            truncated_value = value
        truncated_d[key] = truncated_value
    return truncated_d
            

async def processPA(call : dict , reader : asyncio.streams.StreamReader , writer : asyncio.streams.StreamWriter) -> None:
    """
        Redirects the call and checks for errors
    """
    if not isinstance(call , dict):
        raise ValueError(f"Call must be of type 'dict'")

    if 'type' in call.keys():
        if API.validCallType(call['type']):
            sender_seq : int = find_seq_number_by_stream(reader, API.players) if (call['type'] not in ['login','get_nonce']) else len(API.players)
            
            if sender_seq != INVALID_SEQ_NUMBER:

                callAction: CallAction = API.handleCall(call , writer , reader)

                if "UUID" in call:
                    if "UUID" in uuid_map:
                        debug_logger.warning(f"Repeated message received from user with sequence number {sender_seq}")
                    
                    uuid_map.add(call["UUID"])
                    callAction.awnser["UUID"] = call["UUID"]

                await send_by_call_action(callAction,reader,writer,priv_key)

        else:
            raise ValueError(f"Invalid call ({call['type']}) value")
    else:
        raise ValueError(f"call argument should have a 'type' field")

async def send_by_call_action(callAction: CallAction , reader: asyncio.streams.StreamReader , writer: asyncio.streams.StreamWriter , private_key: rsa.RSAPrivateKey) -> None:

    sender_seq: int = find_seq_number_by_stream(reader,API.players)
    debug_logger.debug(f'Sending to {callAction.broadcast_rule} : {str(truncate_dict(callAction.awnser))}')
    print(callAction.brief_as_str())

    if 'log' not in callAction.awnser:
        logger.insert(sender_seq , str(callAction.awnser) , bytes_to_base_64(asymmetric.sign_message(str(callAction.awnser).encode('utf-8'),priv_key)))

    sign_dict = lambda message : sign_message(json_to_bytes(message),private_key)

    pcopy = API.players.copy()
    if callAction.broadcast_rule == 'all':
        for player in pcopy.values():
            if player.writer != writer:
                await send_dict(player.writer , callAction.awnser , sign_dict(callAction.awnser))
                
        await send_dict(writer, callAction.awnser , sign_dict(callAction.awnser)) #guarantee that everyone receives the message


    if callAction.broadcast_rule == 'all_except_sender':
    #find a way to get 'nseq' of the sender
        for player in pcopy.values():
            if player.writer != writer: await send_dict(player.writer , callAction.awnser , sign_dict(callAction.awnser))
                
    if callAction.broadcast_rule == 'sender':
        await send_dict(writer , callAction.awnser , sign_dict(callAction.awnser))

    if callAction.reawnser != None:
        debug_logger.debug(f'Sending to "all_except_sender" : {str(truncate_dict(callAction.reawnser))}')
        logger.insert(sender_seq , str(callAction.reawnser) , bytes_to_base_64(asymmetric.sign_message(str(callAction.reawnser).encode('utf-8'),priv_key)))
        for player in pcopy.values():
            if player.writer != writer: await send_dict(player.writer , callAction.reawnser , sign_dict(callAction.reawnser))

    if callAction.change_state != None:
        old_state: str = state.getState()
        state.apply(callAction.change_state)
        debug_logger.info(f"State transition from {old_state} to {state.getState()}")
        if state.getState() == "IDLE":
            seq_numbers: list[int] = [key for key in reversed(players.keys())]
            for _seq in seq_numbers:
                API.removeClient(_seq)

            API.reload()
            logger.reset()
            

async def handle_client(reader : asyncio.streams.StreamReader, writer : asyncio.streams.StreamWriter) -> None:
    try:
        while True:
            seq: int = find_seq_number_by_stream(reader, API.players)
            if seq == INVALID_SEQ_NUMBER:
                if reader in API.nonce_cache:
                    if API.nonce_cache[reader].method == 'certificate':
                        reader_certificate: x509.Certificate = asymmetric.import_certificate(API.nonce_cache[reader].auth_data)
                        data: dict | None = await recv_dict(reader , reader_certificate)
                    else: #pubkey
                        reader_pubkey: rsa.RSAPublicKey = asymmetric.public_key_from_string(API.nonce_cache[reader].auth_data)
                        data = await recv_dict(reader, reader_pubkey)

                else:
                    data = await recv_dict(reader)
            else:
                try:
                    data = await recv_dict(reader , API.players[seq].publicKey)
                except SyntaxError as e: #invalid signature
                    debug_logger.error(colored(f"Message received from sequence number {seq} has a wrong signature",'red'))
                    if state.getState() in ['IDLE','WAITING'] and seq != 0:
                        callAction: CallAction | None = API.removeClient(seq)
                        if callAction != None:
                            await send_by_call_action(callAction, reader , writer , priv_key)
                    else:
                        callAction = API.banPlayer({'type' : 'ban_player' , 'info' : Banned_Reason.BAD_SIGNATURE.value , 'seq' : seq} , writer , reader , True)
                        await send_by_call_action(callAction , reader , writer , priv_key)
                    continue


            if data == None: raise OSError()
            
            logger.insert(seq , str(data) , bytes_to_base_64(asymmetric.sign_message(str(data).encode('utf-8'),priv_key)))
            
            debug_logger.debug(f'Received from user with sequence number {seq}: {truncate_dict(data)!r}')

            if 'type' in data:
                print(colored(f"User with sequence number {seq} requested {data['type']}" , "blue"))
            else:
                print(colored(f"User with sequence number {seq} sent invalid request" , "red"))
            try:
                await processPA(data , reader , writer)
            except ValueError as e:
                message: dict = {'status' : 1 , 'info' : e.__str__()}
                debug_logger.debug("Sending to 'sender': " + str(truncate_dict(message)))
                await send_dict(writer, message , sign_message(json_to_bytes(message),priv_key))


    except OSError:
        debug_logger.debug("Closed connection")
        seq_closed: int = find_seq_number_by_stream_writer(writer , players=API.players)
        try:
            remove_flag: bool = state.getState() != "AUDIT"
            action: CallAction | None = API.removeClient(seq_closed , True)
            if action == None: #caller disconnected
                old_state: str = state.getState()
                API.state.apply("IDLE")
                API.reload()
                logger.reset()

                debug_logger.info(f"State transition from {old_state} to {'IDLE'}")
            else:
                if state.getState() != 'AUDIT':
                    await send_by_call_action(action , reader , writer , priv_key)
                else:
                    debug_logger.debug(f'Player with sequence number {seq_closed} sucessfully disconnected!')
                    if len(API.players) == 0:
                        API.state.apply("IDLE")
                        API.reload()
                        logger.reset()
                        debug_logger.info(f"State transition from AUDIT to 'IDLE")

                        

        except ValueError as e:
            writer.close()  # this happens when a non logged user disconnects


def bytes_to_base_64(data: bytes) -> str:
    return base64.b64encode(data).decode('utf-8')

def input_handler():

    while True:
        input_str: str = input("Options avaliable\n\t[0] : Get user list\n\t[1] : Get logs\n\t[2] : Get current state\n\t[3] : exit\n")
        try:
            opt: int = int(input_str)
            if opt not in [0,1,2,3]:
                raise Exception
        except Exception as e:
            print("Invalid input")
            continue
        
        if opt == 0:
            if len(API.players.values()) == 0:
                print("There aren't any players connected")
            else:
                print("Sure, here's the list of players!")
                for player in API.players.values():
                    print(player.__str__())
        if opt == 1:
            print(logger.getLog())
        if opt == 2:
            print(state.getState())
        if opt == 3:
            if os.name == 'posix': #linux
                os.kill(os.getpid(), signal.SIGTERM)
            elif os.name == 'nt': #windows
                os._exit(0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--bind", help="IP address to bind to", default="127.0.0.1")
    parser.add_argument("--port", help="TCP port", type=int, default=8000)
    parser.add_argument("--log", help="Log threshold (default=INFO)", type=str, default='INFO')
    parser.add_argument("--N", help="Number of cards", type=int, default=16)
    parser.add_argument("--max_players", help="Max players allowed", type=int, default=4)
    args = parser.parse_args()

    if args.max_players < 2:
        sys.exit("invalid max_players, max_players should be greater or equal than 2")

    if args.N < 4 or args.N % 4 != 0:
        sys.exit("invalid N argument, N should be greater or equal than 4 and a multiple of 4")

    input_thread = threading.Thread(target=input_handler)
    
    input_thread.start()


    numericLogLeved = getattr(logging, args.log.upper(), None)
    if not isinstance(numericLogLeved, int):
        raise ValueError('Invalid log level: %s' % numericLogLeved)

    #generate key pair
    priv_key : rsa.RSAPrivateKeyWithSerialization = asymmetric.generate_private_key(2048)
    pub_key  : rsa.RSAPublicKey = asymmetric.generate_public_key(priv_key)

    asymmetric.save_key("private.pem",priv_key)
    asymmetric.save_key("public.pem",pub_key)

    uuid_map: set = set() # check duplicate uuids

    logger: Logger = Logger()
    players: dict[int, Entity] = dict()
    bans: Bans = Bans()
    state: State = State(['IDLE','WAITING','SUBMIT_CARD','SUBMIT_DECK','SUBMIT_KEYS','SHARE_WINNERS','AUDIT'],
        {
            'IDLE' : ['WAITING'],
            'WAITING' : ['IDLE','SUBMIT_CARD'],
            'SUBMIT_CARD' : ['IDLE','SUBMIT_DECK'],
            'SUBMIT_DECK' : ['IDLE','SUBMIT_KEYS'],
            'SUBMIT_KEYS' : ['IDLE' , 'SHARE_WINNERS'],
            'SHARE_WINNERS' : ['IDLE','AUDIT'],
            'AUDIT'         : ['IDLE']
        },
     'IDLE')

    debug_logger = logging.getLogger("Monitor")
    debug_logger.setLevel(logging.DEBUG)


    # create console handler and set level to log argument
    ch = logging.StreamHandler()
    ch.setLevel(numericLogLeved)
    ch.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))

    # create file handlet and set level to debug
    if not os.path.exists('./debug_logs'):
        os.mkdir('./debug_logs')
    logName = r'./debug_logs/playing_area_' + str(time.time()) + '.log'
    fh = logging.FileHandler(logName)
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(logging.Formatter('%(asctime)s - [%(name)s, %(levelname)s]: %(message)s'))

    # add ch to logger
    debug_logger.addHandler(ch)

    # add fh to logger
    debug_logger.addHandler(fh)

    API: Call = Call(state,players,logger,asymmetric.public_key_to_string(pub_key),bans,args.max_players,args.N)

    async def main() -> None:
        server = await asyncio.start_server(
            handle_client, args.bind, args.port)

        addrs = ', '.join(str(sock.getsockname()) for sock in server.sockets)
        debug_logger.info(f'Serving on {addrs}')

        async with server:
            await server.serve_forever()

    try:
        # Run server until ctrl + c is pressed
        asyncio.run(main())
    except KeyboardInterrupt:
        debug_logger.fatal("Server Closed")
    except OSError as e:
        debug_logger.fatal("Error Launching Server: " + str(e))
    except Exception as e:
        debug_logger.fatal("Error occurred: " + str(e))