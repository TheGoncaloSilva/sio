#handle playing area calls
import asyncio
import sys
import os
from typing import Callable, Optional, Any, Type, Union
import threading
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
from common.state import State
from common.entity import Entity, INVALID_SEQ_NUMBER, find_seq_number_by_stream , Bans , Banned_Reason
from cryptography.hazmat.primitives.asymmetric import rsa# type: ignore
import common.asymmetric as asymmetric
from common.logger import Logger
from typing import NamedTuple
import termcolor
from random import random

class AuthInfo(NamedTuple):
    """
    Holds information used in authentication process
    """
    method: str     # 'certificate' or 'pubkey'
    auth_data: str  # associated data (public key or certificate)
    nonce: str      # associated nonce

class CallAction:
    """
    This class is used to handle requests redirection
    """
    def __init__(self , broadcast_rule: str , awnser: dict , change_state : Optional[str] = None , reawnser: Optional[dict] = None):
        """
        @param broadcast_rule: Broadcast rule defined (view README.md for more detail)
        @param awnser: Awnser forwarded according to broadcast rule
        @param (optional) change_state: Used if the action produces a state transition
        @param (optional) reawnser: optional 'dict' sent to everyone except sender (useful when awnser and reawnser are different)
        """
        if broadcast_rule not in ['none' , 'sender' , 'all_except_sender' , 'all']:
            raise ValueError(f"Invalid broadcast rule ({broadcast_rule})")
        self.broadcast_rule = broadcast_rule
        self.awnser = awnser
        self.change_state = change_state
        self.reawnser = reawnser
    

    __color_counter: int = 0
    __info_colors: list[str] = ["blue"] #add more colors if necessary

    """
    Returns a brief string representation of the call action
    """
    def brief_as_str(self) -> str:
        brief: str = CallAction.__brief_dict_as_str(self.awnser , self.broadcast_rule)
        if self.reawnser != None:
            brief += "\n" + CallAction.__brief_dict_as_str(self.reawnser , 'all_except_sender') + "\n"
        return brief
    
    @staticmethod
    def __brief_dict_as_str(dict: dict , broascast_rule: str) -> str:
        message_color: str = CallAction.__info_colors[CallAction.__color_counter]
        CallAction.__color_counter = (CallAction.__color_counter + 1) % len(CallAction.__info_colors) 

        brief: str = "Sending message "
        if 'code' in dict and dict['code'] != 0:
            message_color = "red"
            if 'info' in dict:
                brief += "with the following error " + dict['info']
        else:
            if 'type' in dict:
                brief += "of type " + dict['type']

        brief += " to " + broascast_rule
        return termcolor.colored(brief , message_color)



class Call:
    def __init__(self , state : State, players : dict[int,Entity] , logger : Logger , pubkey : str, bans: Bans , max_players: int , N: int):

        self.__calls : dict[str , Callable[[dict,asyncio.StreamWriter,asyncio.StreamReader],CallAction]]  = {
        "get_nonce"         : self.__getNonce,
        "login"             : self.__handleLogin,
        "get_users_list"    : self.__handleGetUsersList,
        "get_audit_log"     : self.__getAuditLog,
        "start_game"        : self.__startGame,
        "submit_card"       : self.__submitCard,
        "submit_deck"       : self.__submitDeck,
        "start_send_keys"   : self.__startSendKeys,
        "send_keys"         : self.__sendKeys,
        "ban_player"        : self.banPlayer,
        "share_winner"      : self.__shareWinner,
        "abort_game"        : self.__abortGame,
        }

        self.state = state
        self.players = players
        self.logger = logger
        self.pubkey = pubkey
        self.bans = bans

        self.MAX_PLAYERS = max_players
        self.N = N

        self.received_cards: dict[int,list[bytes]] = {}
        self.received_decks: list[list[bytes]] = []
        self.received_keys: dict[int,bytes] = {}
        self.received_outcomes: dict[int, list[int]] = {}

        # associate stream reader to a tuple containing pubkey and his associated nonce
        self.nonce_cache : dict[asyncio.streams.StreamReader,AuthInfo] = {}
        
    def reload(self):
        self.received_cards = {}
        self.received_decks = []
        self.received_keys = {}
        self.received_outcomes = {}
        self.players = {}
        self.nonce_cache = {}
        self.bans = Bans()




    def removeClient(self, seq_number: int , allow_remove: bool = True) -> CallAction | None:
        if seq_number not in self.players.keys():
            raise ValueError("Invalid seq_number provided")
        else:
            cstate: str = self.state.getState()
            self.players[seq_number].writer.close()
            del self.players[seq_number]
            if seq_number == 0:
                if allow_remove:
                    for player in self.players.values():
                        player.writer.close()
                return None
            else:
                if cstate == "WAITING":
                    for i in range(seq_number, len(self.players)):
                        self.players[i] = self.players[i+1]
                        del self.players[i+1]
                    return CallAction("all",{'type':'disconnect','seq':seq_number})
                elif cstate != "IDLE":
                    self.bans.add_ban(seq_number , Banned_Reason.DISCONNECTED)
                    return CallAction("all",{'type':'ban_player','info':"DISCONNECTED",'seq':seq_number})



    def __getNonce(self, call : dict , writer: asyncio.StreamWriter , reader: asyncio.StreamReader) -> CallAction:
        has_cert: bool = 'certificate' in call
        has_pubkey: bool = 'pubkey' in call

        if has_cert and has_pubkey:
            return CallAction('sender' , {'code' : 1 , 'type' : 'get_nonce' , 'info' : 'Received both "certificate" and "pubkey" fields, only one of them is expected'})

        if not has_cert and not has_pubkey:
            return CallAction('sender' , {'code' : 1 , 'type' : 'get_nonce', 'info' : 'Expected "certificate" or "pubkey" field'})

        if self.state.getState() not in ['IDLE' , 'WAITING']:
            return CallAction('sender' , {'code' : 4 ,'type' : 'get_nonce' , 'info' : 'This call only works in "IDLE" or "WAITING" states'})

        if has_cert and not asymmetric.validate_certificate(asymmetric.import_certificate(call['certificate'])):
            return CallAction('sender' , {'code' : 2 , 'type' : 'get_nonce' , 'info' : 'Invalid certificate'})

        auth_method: str = 'certificate' if has_cert else 'pubkey'
        auth_data:   str = call['certificate'] if has_cert else call['pubkey']
        auth_nonce:  str = uuid.uuid4().hex

        self.nonce_cache[reader] = AuthInfo(auth_method, auth_data, auth_nonce)
        
        return CallAction('sender' , {'code' : 0 , 'nonce' : auth_nonce , 'type' : 'get_nonce'})



    def validCallType(self,type : str) -> bool:
        return type in self.__calls.keys()
            

    def handleCall(self, call : dict , writer: asyncio.StreamWriter , reader: asyncio.StreamReader) -> CallAction:
        return self.__calls[call["type"]](call,writer,reader)

    def __checkPAfields(self, call : dict , expected_fields : list[str]) -> None:
        """
        Raise ValueError iff expected_fields argument is not a subset of call.keys()
        """
        for f in expected_fields:
            if f not in call:
                raise ValueError(f"Missing argument {(f)}")

    def __handleLogin(self,call: dict , writer: asyncio.StreamWriter , reader: asyncio.StreamReader) -> CallAction:
        if reader not in self.nonce_cache:
            return CallAction('sender' , {'code' : 2 , 'type' : 'login' , 'info' : 'You must request nonce before login'})

        using_cc: bool = self.nonce_cache[reader].method == 'certificate'

        try:
            if using_cc:
                self.__checkPAfields(call , ['type' , 'role' , 'nick' , 'nonce' , 'pubkey'])
            else:
                self.__checkPAfields(call , ['type' , 'role' , 'nick' , 'nonce'])

        except ValueError as e:
            return CallAction('sender' , {'code' : 1 , 'info' : str(e)})

        if self.nonce_cache[reader].nonce != call['nonce']:
            return CallAction('sender' , {'code' : 2 , 'type' : 'login' , 'info' : 'The nonce provided is wrong'})

        if call['role'] not in ['caller' , 'player']:
            return CallAction('sender' , {'code' : 2 , 'info' : "'role' field is invalid" , 'type' : 'login'})

        nick : str = call['nick']
        role : str = call['role']

        pkey: rsa.RSAPublicKey = asymmetric.public_key_from_string(self.nonce_cache[reader].auth_data if not using_cc else call['pubkey'])
        
        cstate : str = self.state.getState()

        if cstate != 'IDLE' and cstate != 'WAITING':
            return CallAction('sender' , {'code' : 4 , 'type' : 'login' , 'info' : "Login only works in 'IDLE' or 'WAITING' state"})
        
        if cstate == 'IDLE' and role != 'caller':
            return CallAction('sender' , {'code' : 4 , 'type' : 'login' , 'info' : 'the first user must be a "caller"'})
        
        if (cstate == 'WAITING' and role == 'caller'):
            return CallAction('sender' , {'code' : 4 , 'info' : 'Caller has aldready been registered','type' : 'login'})

        if (cstate == 'IDLE' and role == 'caller') or (cstate == 'WAITING' and role == 'player'):
            if len(self.players) >= self.MAX_PLAYERS + 1:
                return CallAction('sender' , {'code' : 4 , 'info' : "Playing area is full",'type' : 'login'})

            entity: Entity = Entity(len(self.players.keys()) , nick , pkey , writer , reader)
            self.players[len(self.players.keys())] = entity

            if len(self.players.keys()) == 1:
                return CallAction('sender' ,
                 {'code' : 0 , 'seq' : entity.seq , 'N' : self.N , 'pubkey' : self.pubkey , 'max_players': self.MAX_PLAYERS , 'type' : 'login'} , 
                 change_state='WAITING',
                 reawnser={'type' : 'new_client' , 'seq': entity.seq, 'nick': entity.nick , 'pubkey' : asymmetric.public_key_to_string(entity.publicKey)}
                 )
            else:
                return CallAction('sender' , {'code' : 0 ,  'N' : self.N  ,  'type' : 'login' , 'seq' : len(self.players.keys()) - 1, 'pubkey' :  self.pubkey , 'max_players': self.MAX_PLAYERS},
                reawnser={'type' : 'new_client' , 'seq': entity.seq, 'nick': entity.nick , 'pubkey' : asymmetric.public_key_to_string(entity.publicKey)})

        return CallAction('sender',{'code' : 4, 'info' : 'PA is occupied'})



    def __handleGetUsersList(self,call: dict , writer: asyncio.StreamWriter , reader: asyncio.StreamReader) -> CallAction:
        try:
            self.__checkPAfields(call , ['type'])
        except ValueError as e:
            return CallAction('sender' , {'code' : 1 , 'info' : str(e)})

        user_arr : list = [{'seq': player.seq , 'nick': player.nick, 'pubkey': asymmetric.public_key_to_string(player.publicKey)} for player in self.players.values()]
        return CallAction('sender', {'code' : 0 , 'type' : 'get_users_list' , 'users' : user_arr})


    def __getAuditLog(self,call: dict , writer: asyncio.StreamWriter , reader: asyncio.StreamReader) -> CallAction:

        return CallAction('sender', {'code' : 0 , 'type' : 'get_audit_log' , 'log' : self.logger.getLog()})

    def __startGame(self, call: dict , writer: asyncio.StreamWriter, reader: asyncio.StreamReader) -> CallAction:
        try:
            self.__checkPAfields(call , ['type'])
        except ValueError as e:
            return CallAction('sender' , {'code' : 1 , 'info' : str(e)})

        if self.state.getState() != "WAITING":
            return CallAction('sender', {'code' : 4, 'info': 'Start game call only works in "WAITING" state' , 'type' : 'start_game'})
        else:
            if self.players[0].reader == reader:
                return CallAction('all', {'code' : 0 , 'type' : 'game_started'}, "SUBMIT_CARD")
            else:
                return CallAction('sender',{'code': 5 , 'info': 'A player cannot start a game' , 'type' : 'start_game'})

    def __submitCard(self, call: dict , writer: asyncio.StreamWriter, reader: asyncio.StreamReader) -> CallAction:
        try:
            self.__checkPAfields(call , ['type','card'])
        except ValueError as e:
            return CallAction('sender' , {'code' : 1 , 'info' : str(e)})

        state: str = self.state.getState()

        if state != 'SUBMIT_CARD':
            return CallAction('sender', {'code': 4 ,'info' : 'This call is restricted to "SUBMIT_CARD" state' , 'type' : 'submit_card'})
        else:
            seq_n: int = find_seq_number_by_stream(reader , self.players)
            if seq_n == 0:
                return CallAction('sender', {'code': 5 , 'info' : 'Only players can submit cards' , 'type' : 'submit_card'})

            else:
                if seq_n in self.received_cards:
                    return CallAction('sender' , {'code' : 3 , 'info' : 'You aldready submitted your card'})
                else:
                    self.received_cards[seq_n] = call['type']
                    if len(self.received_cards) == len(self.players) - 1:
                        return CallAction('all' , {'type' : 'submit_card' , 'code': 0 , 'type' : 'submit_card' , 'info' : 'Player sucessfully sent his card' , 'seq': seq_n , 'card' : call['card']},change_state='SUBMIT_DECK')
                    else:
                        return CallAction('all' , {'type' : 'submit_card' , 'code': 0 , 'type' : 'submit_card' , 'info' : 'Player sucessfully sent his card' , 'seq': seq_n , 'card' : call['card']})

    def __submitDeck(self, call: dict , writer: asyncio.StreamWriter, reader: asyncio.StreamReader) -> CallAction:
        try:
            self.__checkPAfields(call , ['type','deck'])
        except ValueError as e:
            return CallAction('sender' , {'code' : 1 , 'info' : str(e)})

        state: str = self.state.getState()

        if state != 'SUBMIT_DECK':
            return CallAction('sender' ,{'code' : 5 , 'info' : 'This call is restricted to "SUBMIT_DECK" state' , 'type' : 'submit_deck'})

        else:
            seq_n: int = find_seq_number_by_stream(reader , self.players)
            if seq_n != len(self.received_decks):
                return CallAction('sender', {'code': 5 , 'info' : 'Wait for your turn to send the deck' , 'type' : 'submit_deck'})
            else:
                self.received_decks.append(call['deck'])
                return CallAction('all' , {'code': 0 , 'type' : 'submit_deck' , 'info' : 'Player sucessfully shuffled the deck' , 'seq': seq_n , 'deck' : call['deck']})

    def __startSendKeys(self, call: dict , writer: asyncio.StreamWriter, reader: asyncio.StreamReader) -> CallAction:
        try:
            self.__checkPAfields(call , ['type'])
        except ValueError as e:
            return CallAction('sender' , {'code': 1 , 'info' : str(e)})

        state: str = self.state.getState()

        seq: int = find_seq_number_by_stream(reader, self.players)

        if seq != 0:
            return CallAction('sender' , {'code' : 5 , 'info' : "sendKeys can only be sent by the caller"})

        if state != "SUBMIT_DECK":
            return CallAction('sender', {'code' : 4 , 'info' : "Send keys only works in 'SUBMIT_DECK' state"})

        if len(self.received_decks) != len(self.players):
            return CallAction('sender' , {'code' : 4 , 'info' : "Wait for all users send their shuffled decks"})

        return CallAction('all' , {'code': 0 , 'type' : 'start_send_keys'} , change_state="SUBMIT_KEYS")

    def __sendKeys(self, call: dict, writer: asyncio.StreamWriter, reader:asyncio.StreamReader) -> CallAction:
        try:
            self.__checkPAfields(call , ['type' , 'key'])
        except ValueError as e:
            return CallAction('sender' , {'code': 1 , 'info' : str(e)})
        
        state: str = self.state.getState()
        seq: int = find_seq_number_by_stream(reader, self.players)

        if state != "SUBMIT_KEYS":
            return CallAction('sender', {'code' : 4 , 'info' : "the caller didn't called 'start_send_keys' yet"})
        else:
            if seq in self.received_keys:
                return CallAction('sender' , {'code' : 3 , 'info' : 'You aldready broadcasted your key'})
            else:
                self.received_keys[seq] = call['key']
                if len(self.received_keys.keys()) == len(self.players):
                    return CallAction('all' , {'code': 0, 'type' : 'send_keys' , 'info' : "Sucessfully received key" , 'key' : call['key'] , 'seq' : seq},
                    change_state="SHARE_WINNERS")
                else:
                    return CallAction('all' , {'code': 0, 'type' : 'send_keys' , 'info' : "Sucessfully received key" , 'key' : call['key'] , 'seq' : seq})

        
    def banPlayer(self, call: dict, writer: asyncio.StreamWriter, reader: asyncio.StreamReader , local: bool = False) -> CallAction:
        
        try:
            self.__checkPAfields(call , ['type','seq','info'])
        except ValueError as e:
            return CallAction('sender', {'code' : 1 , 'info' : str(e)})
    
        seq: int = find_seq_number_by_stream(reader,self.players)

        if seq != 0 and not local:
            return CallAction('sender' , {'code' : 5 , 'info' : 'This call is restricted to the caller'})

        if call['seq'] not in self.players:
            return CallAction('sender' , {'code' : 4 , 'info' : 'Invalid sequence number'})

        if call['seq'] == 0 and not local:
            return CallAction('sender' , {'code' : 4 , 'info' : "You can't ban yourself"})

        if call['seq'] == 0 and local:
            return CallAction('all' , {'code' : 0 , 'type' : 'abort_game' , 'info' : "Caller cheated signature"} , change_state="IDLE")

        state: str = self.state.getState()


        self.bans.add_ban(call['seq'] , Banned_Reason(call['info']))
        self.players[call['seq']].writer.close()

        return CallAction('all',{'code' : 0 , 'type' : call['type'] , 'seq': call['seq'] , 'info' : call['info']})

    def __shareWinner(self, call: dict, writer: asyncio.StreamWriter, reader: asyncio.StreamReader) -> CallAction:
        try:
            self.__checkPAfields(call, ['type','winner'])
        except ValueError as e:
            return CallAction('sender' , {'code' : 1, 'info' : str(e)})

        seq: int = find_seq_number_by_stream(reader,self.players)

        state: str = self.state.getState()

        if state != "SHARE_WINNERS":
            return CallAction('sender' , {'code' : 4 , 'type' : 'share_winner' , 'info' : 'This call is restricted to "SHARE_WINNERS" state'})

        if seq in self.received_outcomes:
            return CallAction('sender' , {'code' : 3 , 'type' : 'share_winner' , 'info' : 'You aldready submitted your outcome.'})

        if seq == 0:
            if any([k not in self.received_outcomes for k in range(1, len(self.players))]):
                return CallAction('sender' , {'code' : 6 , 'type' : 'share_winner' , 'info' : 'The caller must wait for all players send their outcome'})

            else:
                self.received_outcomes[0] = call['winner']
                return CallAction('all' , {'code' : 0 , 'type' : 'share_winner' , 'seq' : 0 , 'winner' : call['winner']},change_state="AUDIT")

        else:
            self.received_outcomes[seq] = call['winner']
            return CallAction('all' , {'code' : 0 , 'type' : 'share_winner' , 'seq' : seq , 'winner' : call['winner']})
        
    def __abortGame(self, call: dict, writer: asyncio.StreamWriter, reader: asyncio.StreamReader) -> CallAction:
        try:
            self.__checkPAfields(call, ['type','info'])
        except ValueError as e:
            return CallAction('sender' , {'code' : 1, 'info' : str(e)})

        seq: int = find_seq_number_by_stream(reader,self.players)

        state: str = self.state.getState()

        if seq != 0:
            return CallAction('sender' , {'code' : 5 , 'type' : 'abort_game' , 'info' : 'This call is restricted to the caller'})

        if state == 'IDLE' or state == 'WAITING':
            return CallAction('sender' , {'code' : 4 , 'type' : 'abort_game' , 'info' : "This call doesn't work in 'IDLE' or 'WAITING' states"})

        return CallAction('all' , {'code' : 0 , 'type' : 'abort_game' , 'info' : call['info']} , change_state='IDLE')