# Code gathered at https://docs.python.org/3/library/asyncio-stream.html
import asyncio
import argparse
import sys
import os
import logging
import time
from random import randint

import uuid

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

from common.communication import *
import common.asymmetric as asymmetric
import common.symmetric as symmetric
from common.state import State
from common.bingo import Bingo
from common.deck import Deck
from common.entity import PlayerValues,CallerValues,print_players_cards_and_deck


async def send(writer: asyncio.streams.StreamWriter,message: dict,cheat_signature : bool = True, useCard: bool = False):
    global uuid_buffer
    global cheat
    try:
        #insert UUID into the message
        random_uuid: str = str(uuid.uuid4())
        message['UUID'] = random_uuid
        # uuid_buffer.append(random_uuid)
        logger.debug("Sending: " + str(message))

        

        if cheat_signature == True:
            rand = randint(0,100)
            if rand < cheat:
                print("cheated signature")
            else:
                cheat_signature = False

        if useCard:
            await send_dict(
                writer,
                message,
                asymmetric.sign_message_cc(cardPin, json_to_bytes(message)),
                cheat_signature)
        else:
            await send_dict(
                writer,
                message,
                asymmetric.sign_message(json_to_bytes(message),priv_key),
                cheat_signature)


    except Exception as e:
        logger.error("Something went wrong while trying to send message: " + str(e))
        exit(1)

async def receive(reader: asyncio.streams.StreamReader):
    try:
        if PA_pubkey == None:
            data = await recv_dict(reader)
        else:
            data = await recv_dict(reader , PA_pubkey)
        logger.debug("Received: " + str(data))
        return data
    except SyntaxError as e:
        logger.error("Playing signature is invalid, aborting client")
        exit(1)
    except Exception as e:
        logger.error("Something went wrong while trying to receive a message: " + str(e))
        exit(1)

async def get_nonce(writer: asyncio.streams.StreamWriter , pubkey: str):
    """
    Get nonce from playing area
    """
    # Not card auth
    if cardPin == '':
        message = {'type': "get_nonce" , 'pubkey' : pubkey}
    else: # Card auth
        message = {
            'type': "get_nonce" , 
            'certificate' : asymmetric.export_certificate(asymmetric.get_certificate(cardPin))
            }

    logger.debug("Sending: " + str(message))
    await send(writer,message,False)

async def login(writer : asyncio.streams.StreamWriter,nonce: str,nick: str) -> None:
    """
    Send a login request to the playing area
    """
    # Not card auth
    if cardPin == '':
        message = {"type": "login", "role": "player", "nick": nick,"nonce" : nonce}
        await send(writer,message,False)
    else: # Card auth
        message = {
            "type": "login",
            "role": "player", 
            "nick": nick,
            "nonce" : nonce,
            "pubkey": asymmetric.public_key_to_string(pub_key)
            }
        await send(writer,message,False,True)

async def submit_card(writer : asyncio.streams.StreamWriter, card : list[str]) -> None:
    """
    @param writer : StreamWriter -> the writer to send the message to
    @param seq : int -> the sequence number of the user
    @param card : list[str] -> the card (encrypted)
    """
    message = {"type" : "submit_card" , "card" : card}
    await send(writer,message)

async def submit_deck(writer: asyncio.streams.StreamWriter, deck: list[str]) -> None:
    message = {'type' : 'submit_deck' , 'deck' : deck}
    logger.debug("Sending: " + str(message))
    await send(writer,message)

async def submit_keys(writer: asyncio.streams.StreamWriter, key: str) -> None:
    message = {'type' : 'send_keys' , 'key' : key}
    logger.debug("Sending: " + str(message))
    await send(writer,message)

async def share_winner(writer: asyncio.streams.StreamWriter , winner: list[int]) -> None:
    message = {'type' : 'share_winner' , 'winner' : winner}
    logger.debug("Sending: " + str(message))
    await send(writer,message)

def check_player_card(card : list):
    # check for repeated numbers, signature not valid, invalid size
    pass

def encrypt_each(card: list,key : bytes) -> list[str]:
    new_list: list[str] = []

    for element in card:
        new_list.append(symmetric.bytes_to_string(symmetric.encrypt_values(str(element),key)))

    return new_list

async def process_msg(msg: dict, writer,reader):
    global N
    global M
    global myseq
    global PA_pubkey
    global cards
    global banned_players
    global finalDeck
    global winner_sent
    global playerNicks
    global uuid_buffer
    global cheat
    global nick
    global nplayers

    # if request_state.getState() == "IDLE" or "UUID" not in msg:
    if main_state.getState() == "WAITING":
        if 'type' in msg and msg['type'] == 'game_started':
            print("ANNNNNNNNDDDD THE PARTY STARTED!!!\nLET THE GAMES BEGIN!")
            main_state.apply('SUBMIT_CARD')
            bingo: Bingo = Bingo(N , M)
            rand = randint(0,100)
            if rand < cheat:
                print("cheated card")
                newN = randint(0,N*2)
                rand = randint(0,100) #50% chance to keep M or 50% chance to be random (1 .. M-1)
                #smaller M means higher chance of winning
                newM = M
                if rand < 50:
                    newM = randint(1,M-1)

                bingo = Bingo(newN,newM)
            card: list[int] = bingo.getCard()
            encrypted_card: list[str] = encrypt_each(card, SYM_KEY)
            cards[myseq] = encrypted_card # type: ignore
            await submit_card(writer , encrypted_card)
            await send(writer,{"type": "get_users_list"})
            if request_state.getState() != "WAITING_FOR_RESPONSE":
                request_state.apply("WAITING_FOR_RESPONSE")

        if 'type' in msg and msg['type'] == 'new_client':
            print(f"{msg['nick']} has entered the party!")
            playerNicks[msg["seq"]] = msg["nick"]
            logger.log(1,f"New player{msg['seq']} named {msg['nick']} arrived")

    if main_state.getState() == "SUBMIT_CARD":
        if 'type' in msg and msg['type'] == 'submit_card':
            cards[msg['seq']] = msg['card']
            logger.log(1,f"Player with sequence number {msg['seq']} sucessfully sent his card")
            if len(cards.keys()) == nplayers:
                main_state.apply('SUBMIT_DECK')

    if main_state.getState() == "SUBMIT_DECK":
        if 'type' in msg and msg['type'] == 'submit_deck':
            decks.add_deck([symmetric.bytes_from_string(card) for card in msg['deck']], msg['seq'])
            logger.log(1,f'Received deck from user with sequence number {msg["seq"]}')

            if myseq == msg['seq'] + 1:
                rand = randint(0,100)
                if rand < cheat:
                    print("cheated deck")
                    deck_length = len(msg["deck"])
                    msg["deck"] = cards[myseq] #make the deck = to my card
                    for i in range(len(msg["deck"]),deck_length):
                        msg["deck"].append(randint(0,N)) # type: ignore

                shuffled: list[str] = Bingo.shuffle(msg['deck'])
                encrypted_shuffled: list[str] = encrypt_each(shuffled , SYM_KEY)
                await submit_deck(writer, encrypted_shuffled)
                if request_state.getState() != "WAITING_FOR_RESPONSE":
                    request_state.apply("WAITING_FOR_RESPONSE")

    if main_state.getState() == "SUBMIT_DECK" and 'type' in msg and msg['type'] == 'start_send_keys':
        main_state.apply('SUBMIT_KEYS')
        await submit_keys(writer, symmetric.bytes_to_string(keys[myseq]))
        if request_state.getState() != "WAITING_FOR_RESPONSE":
            request_state.apply('WAITING_FOR_RESPONSE')

    if main_state.getState() == "SUBMIT_KEYS" and 'type' in msg and msg['type'] == 'send_keys':
        logger.log(1,f'Received symmetric key from user with sequence number {msg["seq"]}')
        keys[msg["seq"]] = symmetric.bytes_from_string(msg["key"])
        if(len(keys) == 5):
            main_state.apply("END_GAME")

    if 'type' in msg and msg['type'] == 'disconnect':
        logger.log(1,f'The player{msg["seq"]} disconnected')
        playerName = playerNicks.pop(msg["seq"],"Unknown")
        print(f"{playerName} drunk too much and left the party. (Don't worry, he is safe)")
        banned_players.append(msg["seq"])

    if "type" in msg and msg["type"] == "abort_game":
        info = msg["info"]
        logger.log(1,f"game aborted:{info}")
        print("Party was cancelled :(")
        print("Let's see....")
        print("AH!")
        print(info)
        sys.exit(0)

    if  main_state.getState() == "END_GAME" and not winner_sent:
        logger.log(1,f'The game ended, outcome sharing process will start now')
        print("Game has ended. Looking for the winner.... (hopefully not in the bathroom)")
        _cards = {}
        for key in cards.keys():
            _cards[key] = Deck.decrypt_deck([symmetric.bytes_from_string(c) for c in cards[key]],keys[key]) # type: ignore

        ks : list[tuple[int, bytes]] = [(key,keys[key]) for key in keys.keys()]
        ks.sort(key= lambda x: x[0])

        tempVal = decks.retrieve_decrypted_deck(ks)
        finalDeck = tempVal[-1].deck # type: ignore
        cheated = False
        scores = []
        for key in _cards.keys():
            bingo = Bingo(N,M,_cards[key])
            if key == myseq:            
                rand = randint(0,100)
                if cheated == False and rand < cheat:
                    scores.append((key,1)) # winner be meself :)
                    print("cheated winner\nwinner be meself :)")
                    cheated = True #can only cheat once
                    continue
            
            scores.append((key,bingo.first_winning_position(finalDeck))) # type: ignore

        scores.sort(key=lambda x: x[1])
        winnerScore = scores[0][1]
        winners = []

        for score in scores:
            if score[1] == winnerScore:
                winners.append(score[0])

        await share_winner(writer,winners)
        winner_sent = True
        if request_state.getState() != "WAITING_FOR_RESPONSE":
            request_state.apply('WAITING_FOR_RESPONSE')

    if 'type' in msg and msg['type'] == 'ban_player':
        playerName = playerNicks.pop(msg["seq"],"Unknown")
        info = msg["info"]
        if msg["info"] == "DISCONNECTED":
            print(f"{playerName} drunk too much and left the party. (Don't worry, he is safe)")
            for key in playerNicks.keys()[:]: # type: ignore
                if key > msg["seq"]:
                    playerNicks[key - 1] = playerNicks.pop(key)

            if myseq > msg["seq"]:
                myseq -= 1
        else:
            print(f"Oh no, {playerName} was banned!\nA detective investigated and concluded: {info}")

        print("Party ended. (Tip: invite better friends next time)")  
        banned_players.append(msg["seq"])
        logger.log(1,f"The user with sequence number {msg['seq']} was banned due the following reason: \n\t {msg['info']}")
        sys.exit(0)

    if 'type' in msg and msg['type'] == 'share_winner' and msg["seq"] == 0:
        print("Looks like we have a winner(s)!!")    
        player : dict[int,PlayerValues] = {}
        for key in cards.keys():
            #only seq and nick matter
            #the others are dummy values to avoid the exception
            p = PlayerValues(key,playerNicks[key],PA_pubkey,writer,reader) # type: ignore
            p.set_cards(Deck.decrypt_deck([symmetric.bytes_from_string(c) for c in cards[key]],keys[key])) # type: ignore
            player[key] = p

        #only nick matters
        #the others are dummy values to avoid the exception
        caller : CallerValues = CallerValues(playerNicks[0],PA_pubkey,writer,reader) # type: ignore
        caller.set_seq(0)

        string = await print_players_cards_and_deck(player,caller,msg["winner"],N,finalDeck) # type: ignore
        print(f"\t{string}")
        logger.log(1,f'User with sequence number {msg["seq"]} stated that {str(msg["winner"])} won')
        await handle_player_inputs(writer)

        #exit(0)
    try:
        # if request_state.getState() == "WAITING_FOR_RESPONSE" or uuid_buffer != []:

        if main_state.getState() == "IDLE" and 'type' in msg and msg['type'] == "get_nonce":
            if msg['code'] != 0:
                logger.error(msg['info'])
                info = msg["info"]
                print(f"Something bad happened, apparentely {info}")
            else:
                logger.log(1,'Received nonce from the server')
                nonce = msg['nonce']
                await login(writer,nonce,nick)
        if main_state.getState() == "IDLE" and 'type' in msg and msg['type'] == "login":
            if msg['code'] != 0:
                logger.error(msg['info'])
                info = msg["info"]
                print(f"Ups, looks like you can't join the party.\nI contacted a friend and apparently {info}")
                sys.exit(1)
            else:
                logger.log(1,'login succeded')
                print("You joined the party!!!!!!!!")
                myseq = msg['seq']
                PA_pubkey = asymmetric.public_key_from_string(msg['pubkey'])
                keys[myseq] = SYM_KEY
                nplayers = msg["max_players"]
                N = msg["N"]
                M = int(N / 4)
                await send(writer,{"type": "get_users_list"})
                main_state.apply('WAITING')

        if "users" in msg:
            logger.debug(f"received user list: {msg}")
            for user in msg["users"]:
                playerNicks[user["seq"]] = user["nick"]

            if main_state.getState() == "END_GAME":
                for user in msg["users"]:
                    print(f"\tSeq: %d, Nick: %s"%(user['seq'], user['nick']))
                
                await handle_player_inputs(writer)

        if "log" in msg:
            logger.debug(f"received logs: {msg}")
            if main_state.getState() == "END_GAME":
                if not os.path.exists('./audit_logs'):
                    os.mkdir('./audit_logs')
                logName = r'./audit_logs/' + playerNicks[myseq] + "_" + str(time.time()) + '.log'
                with open(logName, "w") as f:
                    f.write(str(msg))
                print(f"logs saved at {logName}")
                await handle_player_inputs(writer)

        if main_state.getState() == "SUBMIT_CARD" and 'type' in msg and msg['type'] == 'submit_card':
            if msg['code'] == 0:
                cards[msg['seq']] = msg['card']
                logger.log(1,'sucessfully submitted my card!')
                if len(cards.keys()) == nplayers:
                    main_state.apply('SUBMIT_DECK')
            else:
                logger.error(msg['info'])

        if main_state.getState() == "SUBMIT_DECK" and 'type' in msg and msg['type'] == 'submit_deck':
            if msg['code'] != 0:
                logger.error(msg['info'])
            else:
                logger.log(1,msg['info'])

    
        if main_state.getState() == "SUBMIT_KEYS" and 'type' in msg and msg['type'] == 'send_keys':
            
            if msg['code'] != 0:
                logger.error(msg['info'])
            else:
                logger.log(1,msg['info'])

        if main_state.getState() == "END_GAME" and 'type' in msg and msg['type'] == 'share_winner' and msg["seq"] == 0 and "info" in msg:
            if msg['code'] != 0:
                logger.error(msg['info'])
            else:
                logger.log(1,msg['info'])

        # if "UUID" in msg["UUID"] and msg["UUID"] in uuid_buffer:
        #     uuid_buffer.remove(msg["UUID"])

        if request_state.getState() != "IDLE":
            request_state.apply('IDLE')
    except Exception as e:
        logger.error(f"error while processing a request: {str(e)}\nmessage: {msg}")


async def client_life(ipAddr : str, port : int):
    reader, writer = await asyncio.open_connection(
        ipAddr, port)
    await get_nonce(writer,asymmetric.public_key_to_string(pub_key))
    request_state.apply("WAITING_FOR_RESPONSE")
    
    try:
        while True:
            data = await receive(reader)
            logger.debug(data)

            if data == None:
                raise OSError()

            await process_msg(data,writer,reader)
            
    except Exception as e:
        print("No connection with the playing area.")
        logger.debug("Something went wrong: " + str(e))
        writer.close()


async def handle_player_inputs(writer):
        """
        Function used to handle input on the caller
        """
        while(True):
            input_str: str = input("Options avaliable\n\t[1] : Get user list\n\t[2] : Get logs\n\t[3] : Exit game\n")
            opt: int = int(input_str)
            if opt not in [1,2,3]:
                print("Invalid Input")
            
            if opt == 1:         
                msg = {'type': 'get_users_list'}
                await send(writer,msg,False)
                return
                
            elif opt == 2:
                msg = {'type': 'get_audit_log'}
                await send(writer,msg,False)
                return

            elif opt == 3:
                print("Party is over boys!!!\nLet's go home.")
                logger.log(1,"Game Over!")
                exit(0)


def convert_str_bool(val: str | bool) -> bool:
    """
    Function used in arguments to convert a string value into a boolean one
        if needed
    Args:
        - val: Value to test
    Returns:
        - True if the value corresponds to a bool true, false otherwise
    Raises:
        - argparse.ArgumentTypeError: The value is a defined boolean
    """
    if isinstance(val, bool):
        return val
    if val.lower() in ['true', 't', 'y']:
        return True
    elif val.lower() in ['false', 'f', 'n']:
        return False
    else:
        raise argparse.ArgumentTypeError('Expected a boolen value')


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--bind", help="IP address to bind to", default="127.0.0.1")
    parser.add_argument("--port", help="TCP port", type=int, default=8000)
    parser.add_argument("--nick", help="Nick for the player (Max 20 characters)", type=str, default="player")
    parser.add_argument("--log", help="Log threshold (default=INFO)", type=str, default='INFO')
    parser.add_argument("--cheat",help="chance (in %%) to cheat (default 10)",type=int,default=10)
    parser.add_argument("--card",help="boolean to use card", type=convert_str_bool, default=False)
    args = parser.parse_args()

    # check Logger value
    numericLogLeved = getattr(logging, args.log.upper(), None)
    if not isinstance(numericLogLeved, int):
        raise ValueError('Invalid log level: %s' % numericLogLeved)

    if args.cheat > 100 or args.cheat < 0:
        print(f"Invalid cheat value {args.cheat}\nMust be 0 to 100")
        sys.exit(1)



    # Max of 20 characters 
    if len(args.nick) > 20:
        args.nick = args.nick[:20] 

    nick = args.nick

    main_state: State = State(['IDLE','WAITING','SUBMIT_CARD','SUBMIT_DECK','SUBMIT_KEYS','END_GAME'],
        {
            'IDLE' : ['WAITING'],
            'WAITING' : ['IDLE','SUBMIT_CARD'],
            'SUBMIT_CARD' : ['IDLE','SUBMIT_DECK'],
            'SUBMIT_DECK' : ['IDLE','SUBMIT_KEYS'],
            'SUBMIT_KEYS' : ['IDLE' , 'END_GAME'],
            'END_GAME' : ['IDLE']
        },
     'IDLE')

    request_state: State = State(['IDLE','WAITING_FOR_RESPONSE'] ,
        {
            'IDLE' : ['WAITING_FOR_RESPONSE'],
            'WAITING_FOR_RESPONSE' : ['IDLE']
        },
        'IDLE')

    priv_key : rsa.RSAPrivateKeyWithSerialization = asymmetric.generate_private_key(2048)
    pub_key  : rsa.RSAPublicKey = asymmetric.generate_public_key(priv_key)


    # uuid_buffer: list[str] = []
    myseq: int = -1
    PA_pubkey: rsa.RSAPublicKey | None = None
    N: int = 16
    M: int = int(N / 4)
    banned_players : list[int] = []
    finalDeck = []
    winner_sent = False
    cheat = args.cheat

    cards: dict[int, list[bytes]] = {}
    decks: Deck = Deck()

    nplayers: int = 4
    playerNicks: dict[int,str] = {}

    SYM_KEY: bytes = symmetric.generate_key(16)
    keys: dict[int , bytes] = {}

    # Creating an object
    logger: logging.Logger= logging.getLogger("Monitor")
    logger.setLevel(logging.DEBUG)

    # create console handler and set level to log argument
    ch = logging.StreamHandler()
    ch.setLevel(numericLogLeved)
    ch.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))

    # create file handlet and set level to debug
    if not os.path.exists('./logs'):
        os.mkdir('./logs')
    logName = r'./logs/player_' + str(time.time()) + args.nick + '.log'
    fh = logging.FileHandler(logName)
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(logging.Formatter('%(asctime)s - [%(name)s, %(levelname)s]: %(message)s'))

    # add ch to logger
    logger.addHandler(ch)

    # add fh to logger
    logger.addHandler(fh)

    if args.card:
        cardPin: str = input("Please input the authentication pin of the card: ")
        
        asymmetric.close_connection(asymmetric.create_connection(cardPin))
        logger.info(f'Successfully authentication with card')
    else:
        cardPin: str = ''

    try:
        asyncio.run(client_life(args.bind, args.port))
    except KeyboardInterrupt:
        print("\nPlayer Terminated")
    except OSError as e:
        print("No Connection to playing area: " + str(e))