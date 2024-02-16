"""
`caller` package to act as the caller entity of the game. It function like
a supervisor or mediator in the game
"""
# Code gathered at https://docs.python.org/3/library/asyncio-stream.html
import argparse
import asyncio
from collections import Counter
import logging
import os
import os.path
import random
import signal
import sys
import threading
import time
import aioconsole # type: ignore
from enum import Enum
from cryptography.hazmat.primitives.asymmetric import rsa  # type: ignore
from termcolor import colored

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

import common.symmetric as symmetric
import common.asymmetric as asymmetric
import common.communication as communication
from common.entity import *
from common.deck import Deck
from common.state import State
from common.bingo import Bingo

class Caller:

    def __init__(self) -> None:
        """
        Initialize Caller class
        Attributes:
            - caller: Class used to save the values associate to the caller
            - players: Dictionary containing the players Seq and a class 
                with their associated values
            - playingAreaPublicKey: Public key of the Playing Area
            - bufferUUID: Store the value of the UUID value of the request made
                to the Playing Area
            - finalDeck: Save the final shuffled deck
            - receivedCallerSymKey: Used to signal if the caller has received
                it's Symmetric key after sending it
            - winners: Save the list of winners of the game
            - playersPredicted: Dictionary with the players seq and their
                predicted game winners list
            - bannedPlayers: Class that functions as a data structure, to save 
                associate a player as being banned
            - minPlayers: Minimum number of players for the game to function
            - N: N value to generate cards
            - cheat: Probability of the caller to cheat on a signature
        """

        self.caller: CallerValues = None # type: ignore
        self.players: dict[int, PlayerValues] = dict() 
        self.playingAreaPublicKey: rsa.RSAPublicKey | None = None 
        self.bufferUUID: tuple | None = None
        self.finalDeck: list[int] = []
        self.receivedCallerSymKey: bool = False
        self.winners: list[int] = []
        self.playersPredicted: dict[int, list[int]] = dict()
        self.bannedPlayers: Bans = Bans()
        self.minPlayers: int = 2
        self.N: int = 16
        self.cheat: int = 0
        self.nonce: str = ''


    async def create_caller(self, ip: str, port: int, nick: str, cheat: int,
            privateKey: rsa.RSAPrivateKeyWithSerialization, publicKey: rsa.RSAPublicKey,
            cardPin: str = '') -> tuple:
        """
        Function that uses class values to create a Caller with the 
            designated Ip address and Port
        Args:
            - ip: Ip address of the Caller
            - port: Port of the Caller to operate on
            - nick: Caller nick
        Returns:
            - A tupple object with the asyncio.streams.StreamReader
            and asyncio.streams.StreamWriter
        Raises:
            - ValueError: if caller was already established
            - TypeError: if supplied  attributes are not of correct type  
            - OSError: if connection wasn't established (handled by 
            asyncio.open_connection function)
        """
        if self.caller != None: raise ValueError(f"Caller already defined")

        if (not isinstance(ip, str) or not isinstance(port, int) 
            or not isinstance(nick, str)):
            raise TypeError("Wrong usage. Use (str, int) types")

        reader, writer  = await asyncio.open_connection(ip, port)
        
        self.caller: CallerValues = CallerValues(nick,publicKey,writer,reader)
        self.caller.set_ip_port(ip, port)
        self.caller.set_private_key(privateKey)
        self.cheat = cheat
        if cardPin != '':
            self.caller.set_card_pin(cardPin)
        
        return (reader, writer)


    async def login_caller_request(self) -> None:
        """
        Function to make the initial request for authentication.
        It only submits the data to the playing area. 
        Raises:
            - ValueError: when the caller hasn't been defined yet
            - OSError: if connection with Playing Area is terminated
        """

        if self.caller == None : raise ValueError("Use the function create_caller first")
        
        # Ask for nonce
        self.bufferUUID = (random.uniform(1.0, 100.0), 'get_nonce')
        # Without card auth
        if self.caller.cardPin == '':
            authInfo = {"type": 'get_nonce', 
                "pubkey": asymmetric.public_key_to_string(self.caller.publicKey), 
                "UUID": self.bufferUUID[0]
                }
        # With card auth
        else:
            cert = asymmetric.get_certificate(self.caller.cardPin)
            authInfo = {"type": 'get_nonce', 
                "certificate": asymmetric.export_certificate(cert), 
                "UUID": self.bufferUUID[0]
                }
        logger.debug(f'Sending: {authInfo}')
        recvData = await communication.send_dict(
                            self.caller.writer, 
                            authInfo , 
                            asymmetric.sign_message(communication.json_to_bytes(authInfo),self.caller.privateKey)
                            )
        if not recvData:
            raise OSError(F'Failed caller authentication')

        infoState.apply('REQUESTED') # Update state

    
    async def login_caller_response(self, msg: dict) -> bool:
        """
        Function to handle the response from the login request by the caller 
        Returns
            - True is the connection was authenticated or False otherwise
        Raises:
            - ValueError: when the caller hasn't been defined yet
            - ValueError: when response from playing area doesn't come 
            with correct fields
        """
        if self.caller == None : raise ValueError("Use the function create_caller first")

        if not isinstance(msg, dict):
            raise ValueError(f"Message must be of type 'dict'")

        if 'code' in msg:
            if msg['code'] == 0:
                check_dict_fields(msg, ['seq','pubkey','max_players', 'N'])
                    
                self.caller.set_seq(msg['seq'])
                self.caller.set_max_players(int(msg['max_players']))
                self.playingAreaPublicKey = asymmetric.public_key_from_string(msg['pubkey'])
                self.N = int(msg['N'])
                if self.playingAreaPublicKey == None:
                    raise ValueError(f"Playing Area public key not properly formatted")
                return True
            else:
                if 'info' in msg.keys():
                    logger.info(f'Denied authentication, hint: {msg["info"]}')
                    return False
                else:
                    raise ValueError(f"Received response should have a 'info' field")
        else:
            raise ValueError(f"Received data should have a 'type' field")


    async def manage_players(self, action: str, playerData: dict) -> dict | bool:
        """
        Function to manage acceptance and removal of players from the game
        Args:
            - action: action for player data. Values can be 'add', 
            'remove' or 'check'
            - playerData: information of the player
        Returns: 
            - bool value signalling if the action was executed.
            In the case of check, it will return True if the player exists.
            - dict type message to send to the PA. Generally, this is used 
            for when the game can't continue because of not enough players, 
            or a player was banned in the important steps
        """

        try:
            if action == 'add':
                if (len(self.players) == self.caller.maxPlayers):
                    return False
                try:
                    check_dict_fields(playerData, ['type', 'nick', 'pubkey', 'seq'])
                except ValueError as e:
                    return False
                logger.info(f"Adding player with seq: {playerData['seq']}, nick: {playerData['nick']}")

                if playerData['seq'] not in self.players.keys():
                    __newPlayer = PlayerValues(int(playerData['seq']),
                                            playerData['nick'], 
                                            asymmetric.public_key_from_string(playerData['pubkey']), 
                                            self.caller.writer, 
                                            self.caller.reader
                                            )
                    self.players[int(playerData['seq'])] = __newPlayer
                    return True

            # Remove a player should only be done while waiting for game to start
            elif action == 'remove':
                try:
                    check_dict_fields(playerData, ['seq'])
                except ValueError as e:
                    return False
                temp: PlayerValues = self.players.pop(playerData['seq'])
                logger.warning(colored(f'Removing Player with seq: {temp.seq}, nick: {temp.nick}', 'cyan'))

                # Adjust other players sequences
                tempDict: dict = {}
                for key, value in self.players.items():
                    if key > playerData['seq']:
                        value.seq -= 1
                        tempDict[key-1] = value
                    else:
                        tempDict[key] = value

                self.players = tempDict
                        
                return True

            elif action == 'ban':
                try:
                    check_dict_fields(playerData, ['seq', 'info'])

                    # Test for enum ban_reason
                    banReason: Banned_Reason = getattr(Banned_Reason, playerData['info'])
                except ValueError as e:
                    return False
                except AttributeError:
                    banReason: Banned_Reason = Banned_Reason.UNKNOWN

                # Player doesn't exist or is already banned
                if (self.bannedPlayers.is_banned(playerData['seq'])
                        or not self.manage_players('check', playerData)): 
                    return False

                logger.error(colored(f'Banning Player with seq {playerData["seq"]}, because of {playerData["info"]}', 'red', attrs=['bold']))

                self.bannedPlayers.add_ban(playerData['seq'], banReason)

                # Pre-condition for the game to contine
                if len(self.players) - len(self.bannedPlayers.get_bans()) < self.minPlayers:
                    return {'type' : 'abort_game' , 
                            'info' : 'Not enough players to carry the game'}

                # Last state, no need to do anything
                if state.getState() == 'END_GAME': return True

                if banReason == Banned_Reason.BAD_WINNER or state.getState() == "EVALUATION":
                    # The game already progressed, so the cards are OK
                    # which means that we only have to make sure he is the winner
                    # If there were no winners left, we should recalculate
                    if playerData['seq'] in self.winners:
                        self.winners.remove(playerData['seq'])
                    if self.winners == []:
                        await self.determine_winner()
                        return await self.notify_winner()
                    else: return True

                else:

                    return {'type' : 'abort_game' , 
                            'info' : 'Player was banned on a ongoing game'}
                    


            elif action == 'check':
                try: 
                    check_dict_fields(playerData, ['seq'])
                except ValueError as e:
                    return False

                if playerData['seq'] in self.players.keys():
                    return True

        except ValueError:
            # If the received data doesn't have the correct fields
            logging.error(colored("Wrong dictionary headers received", 'red', attrs=['bold']))
            return False

        return False


    async def start_game(self) -> dict | None:
        """
        Function that handles the start of the game
        Returns:
            - None if there's not enough players to start the game, 
            otherwise the message to be sent to the playing area
        """
        if len(self.players) < self.minPlayers: # Pre-condition to start game
            return None

        return {'type': 'start_game'}


    async def send_caller_deck(self) -> dict:
        """
        Function to send te caller's deck
        Returns
            - Message to be sent to the playing area with the encrypted 
            deck
        """

        # Generate symmetric key
        self.caller.set_symmetric_key(symmetric.generate_key(16))
        # Generate deck
        self.caller.set_deck(Bingo.generate_random_solution(self.N))

        return {'type': 'submit_deck',
                'deck': [ symmetric.bytes_to_string(card) 
                            for card in Deck.encrypt_deck
                                    (
                                    self.caller.deck, self.caller.symmetricKey # type: ignore
                                    )
                        ] 
            }


    async def send_caller_symmetric_key(self) -> dict:
        """
        Function that returns the caller symmetric key, to be sent to 
            the Playing Area
        Returns:
            - dictionary with the key to send
        Raises:
            - ValueError: if the symmetric key hasn't been defined
        """

        if self.caller.symmetricKey == b'':
            raise ValueError("The symmetric key should be defined")

        self.bufferUUID = (random.uniform(1.0, 100.0), 'key_submit')
        infoState.apply('REQUESTED') # Update state
        
        return {'type': 'send_keys',
                'key': symmetric.bytes_to_string(self.caller.symmetricKey),
                'UUID': self.bufferUUID[0]
            }

    async def start_send_keys(self) -> dict | None:
        """
        Function to return a message to the Playing Area,
            informing it that players and caller can start
            exchanging keys
        Returns:
            - message to send to the playing area
        """

        return {'type': 'start_send_keys'}

    
    async def player_card_submission(self, msg: dict) -> None:
        """
        Function to associate a set of cards with a player
        Args:
            - msg: message that the player sent with his cards
        Raises:
            - TypeError: if the provided msg is not a dictionary
            object
        """
        
        if not isinstance(msg, dict):
            raise TypeError("Message should be of type 'dict'")

        # Check dict fields
        try:
            check_dict_fields(msg, ['code', 'info', 'seq', 'card'])
        except ValueError as e:
            logger.critical(colored("The provided cards are not correct", 'red', attrs=['bold']))
            return None

        # Check if the player exists
        if not await self.manage_players('check', msg):
            logger.error(colored(f"Player with seq %d doesn't exist"%msg['seq'], 'red', attrs=['bold']))
            return None

        # set the player deck
        # msg['card'] is of type str
        deck = [symmetric.bytes_from_string(card) for card in msg['card']]

        self.players[msg['seq']].set_cards(deck)


    async def player_key_exchange(self, msg: dict) -> None:
        """
        Function to save a player exchanged symmetric key 
        Args:
            - msg: Message sent by the playing area
        Raises:
            - TypeError: if the provided msg is not a dictionary
            object
        """

        if not isinstance(msg, dict):
            raise TypeError("Message should be of type 'dict'")

        try:
            check_dict_fields(msg, ['type', 'key', 'seq'])
        except ValueError as e:
            logger.critical(colored("The provided cards are not correct", 'red', attrs=['bold']))
            return None

        # Check if the player exists
        if not await self.manage_players('check', msg):
            logger.error(colored(f"Player with seq %d doesn't exist"%msg['seq'], 'red', attrs=['bold']))
            return None

        # Set the player symmetric key
        self.players[msg['seq']].set_symmetric_key(
                                    symmetric.bytes_from_string(
                                        msg['key']
                                    )
                                )


    async def process_shuffle_submission(self, msg: dict) -> bool:
        """
        Function to record and proccess every player and caller 
            shuffled deck submission
        Args:
            - msg: Message sent by the playing area
        Returns:
            - True if everyone shuffled, False otherwise
        """

        try:
            check_dict_fields(msg, ['seq', 'deck'])
        except ValueError as e:
            logger.critical(colored("The provided deck isn't correct", 'red', attrs=['bold']))
            return False

        # msg['deck'] is of type list[str]
        deck = [symmetric.bytes_from_string(card) for card in msg['deck']]

        if not hasattr(self, "shuffleDeck"):
            self.shuffleDeck: Deck = Deck(deck, msg['seq'])
        else:
            self.shuffleDeck.add_deck(deck, msg['seq'])

        return self.shuffleDeck.check_everyone_submitted_deck(list(self.players.keys()) + [0])

    
    async def analyze_shuffling_and_cards(self) -> dict | None:
        """
        Function to analyze the shuffling of cards and players submitted cards,
            then determine if there was a cheater
        Returns:
            - dictionary to send, informing about the cheater
            or None if there isn't any
        Raises:
            - ValueError: If the shuffled deck hasn't been supplied or 
            not every player has shuffled the deck
        """
        if not hasattr(self, "shuffleDeck"):
            raise ValueError("The deck should be defined")

        if not self.shuffleDeck.check_everyone_submitted_deck(list(self.players.keys()) + [0]):
            raise ValueError("Everyone should submit the shuffled deck")

        seqKeys: list[tuple[int, bytes]] = [(self.caller.seq, self.caller.symmetricKey)]# Addind caller
        seqKeys.extend([(s, p.symmetricKey) for s, p in self.players.items()])


        # Decrypt each player cards
        for (seq, player) in self.players.items():
            try:
                cards: list[int] = Deck.decrypt_deck(
                    player.cards, # type: ignore
                    player.symmetricKey
                )
                player.cards = cards
            # Spaguetti exception handling (catch errors while decrypring)
            except Exception as e:
                if isinstance(e, OSError):
                    raise e
                else:
                    return {'type': 'ban_player',
                        'info': Banned_Reason.CARDS.value,
                        'seq': seq}
            

        # Analyze shuffle deck
        tempVal = self.shuffleDeck.retrieve_decrypted_deck(seqKeys)
        if isinstance(tempVal, int):
            # Cheat found
            logger.critical(colored(("Cheater found in shuffle with seq %d"%tempVal), 'red', attrs=['bold']))
            return {'type': 'ban_player',
                    'info': Banned_Reason.CARDS.value,
                    'seq': tempVal}

        elif isinstance(tempVal, list):
            self.finalDeck = tempVal[-1].deck # type: ignore

        # Analyze submitted cards
        for (seq, player) in self.players.items():
            if not await check_player_cards_number_equal_deck(self.caller.deck, player.cards): # type: ignore
                logger.critical(colored(("Cheater found in cards with seq %d"%seq), 'red', attrs=['bold']))
                return {'type': 'ban_player',
                        'info': Banned_Reason.CARDS.value,
                        'seq': seq}
        
        return None


    async def determine_winner(self) -> None:
        """
        Function to determine which player has the winning cards

        `Note:` it saves the list of winners in an internal attribute
        """
        scores: list[tuple[int, int]] = []

        for seq, player in self.players.items():
            # Not take into account banned players
            if not self.bannedPlayers.is_banned(seq):
                bingo = Bingo(self.N,int(self.N//4), player.cards) #type: ignore
                scores.append((seq, bingo.first_winning_position(self.finalDeck)))

        # Order the list by scores (Minimum score is winner)
        scores.sort(key=lambda x:x[1]) # type: ignore

        # Start with the first score
        winnerScores = scores[0][1]

        # save the seq with the same initial score
        for score in scores:
            if score[1] == winnerScores:
                self.winners.append(score[0])
            else:
                break

        # check if the first and second place are tied
        if len(self.winners) > 1:
            logger.warning(colored("There has been a draw, the players with the following seq won: " + str(self.winners), 'yellow', attrs=['bold']))
        else:
            logger.warning(colored(f'The player with seq %d has won'%self.winners[0], 'yellow', attrs=['bold']))


    async def player_winning_predicition(self, msg: dict) -> list[int] | None:
        """
        Function to save a player winning prediction. If all
            players have submitted their prediction, analyze
            and ban those who made a bad prediction
        Args:
            - msg: Message sent by the player
        Returns:
            - list with banned players, empty list
            if there weren't any
            - None if not all players
            have submitted predictions yet or a pre-condition
            failed
        """
        
        try:
            check_dict_fields(msg, ['seq', 'winner'])
        except ValueError as e:
            logger.critical(colored("The provided estimate isn't correct, from seq", 'red', attrs=['bold']))
            return None

        if msg['seq'] in list(self.playersPredicted.keys()):
            logger.warning(colored('Player already made an estimate', 'yellow', attrs=['bold']))
            return None

        if msg['seq'] not in [s for s, p in self.players.items()]:
            logger.warning(colored('Unknown player with seq %d'%msg['seq'], 'yellow', attrs=['bold']))
            return None

        self.playersPredicted[msg['seq']] = msg['winner']

        if len(self.playersPredicted.keys()) == len(self.players):
            banned: list[int] = []
            for seq, winners in self.playersPredicted.items():
                # Ban every player that made a bad prediction
                if Counter(self.winners) != Counter(winners):
                    banned.append(seq)
                    sendData: dict = {'type': 'ban_player',
                            'info': Banned_Reason.BAD_WINNER.value,
                            'seq': seq}
                    logger.debug(f'Sending: {sendData}\n')
                    await communication.send_dict(
                            self.caller.writer, 
                            sendData , 
                            asymmetric.sign_message(communication.json_to_bytes(sendData),self.caller.privateKey)
                            )

            return banned

    
    async def notify_winner(self) -> dict:
        """
        Function that creates a response to inform the players
            about the correct winners of the game.

        `Note:` this function should be used after determining the winners
        and waiting for the clients to give their predictions
        Returns:
            - Message with the winning players/s
        """

        return {'type': 'share_winner',
                'winner': self.winners
            }
        

    async def determine_action(self, msg: dict) -> dict | None:
        """
        Function to determine the action to execute, based on the incomming data
        Args:
            - msg: incomming message no analyze
        Returns:
            - message to send or None if there isn't any to send
        """

        if not ('type' in msg.keys() or 'code' in msg.keys()): 
            return None # handle this error
        
        currentInfoState: str = infoState.getState()
        currentState : str = state.getState()
        error: bool = False

        # Remove or ban Player 
        if ('type' in msg.keys() and (msg['type'] == 'disconnect'
                or msg['type'] == 'ban_player')):
            if currentState == 'IDLE':
                status = await self.manage_players('remove', msg)
            else:  
                status = await self.manage_players('ban', msg)
            
            logger.info(await print_user_list(self.players, self.caller.maxPlayers, self.bannedPlayers))
            if isinstance(status, dict):
                    return status

        # Game was aborted
        elif ('code' in msg.keys() and msg['code'] == 0
                and 'type' in msg.keys() and msg['type'] == 'abort_game'):
            logger.warning(colored("The game was aborted, because: " + str(msg['info']), 'yellow', attrs=['bold']))
            exit(0)

        elif (currentInfoState == 'FREE' or (currentInfoState == 'REQUESTED' 
                and 'UUID' in msg.keys() and self.bufferUUID != None 
                    and msg['UUID'] != self.bufferUUID[0])):

            if currentState == 'IDLE':
                # New Player
                if 'type' in msg.keys() and msg['type'] == 'new_client':
                    await self.manage_players('add', msg)
                    logger.info(await print_user_list(self.players, self.caller.maxPlayers, self.bannedPlayers))
                    if len(self.players) == self.caller.maxPlayers:
                        status = await self.start_game()
                        logger.warning(colored(f'Sent request to start game', 'yellow', attrs=['bold']))
                        return status
                
                # Notice of game starting
                elif ('code' in msg.keys() and msg['code'] == 0 and 'type' 
                        in msg.keys() and msg['type'] == 'game_started'):
                    logger.info(f'Game has officially started')
                    state.apply('SUBMIT_CARD')

                else: 
                    error = True

            elif currentState == 'SUBMIT_CARD':
                # Player card submisstion
                if 'code' in msg.keys() and msg['code'] == 0 and 'card' in msg.keys():
                    await self.player_card_submission(msg)

                    # check if all players sent their symmetric keys
                    if await check_all_players_cards(self.players):
                        # call start_key_exchange_function
                        logger.warning(colored("All cards received, starting deck shuffling", 'yellow', attrs=['bold']))
                        state.apply('SUBMIT_DECK')
                        return await self.send_caller_deck()

                else:
                    error = True

            elif currentState == 'SUBMIT_DECK':
                # Deck shuffle submission
                if ('code' in msg.keys() and msg['code'] == 0 and 'type' 
                        in msg.keys() and msg['type'] == 'submit_deck'):
                    # Is everyone submitted the shuffled deck
                    if await self.process_shuffle_submission(msg):
                        state.apply('SUBMIT_KEYS')
                        return await self.start_send_keys()

                else:
                    error = True

            elif currentState == 'SUBMIT_KEYS':
                # Received players key
                if 'type' in msg.keys() and msg['type'] == 'send_keys':
                    await self.player_key_exchange(msg)

                    # check if all players sent their symmetric keys
                    if await check_players_symm_keys(self.players) and self.receivedCallerSymKey:
                        logger.warning(colored("All keys received, starting shuffling evaluation", 'yellow', attrs=['bold']))
                        state.apply('EVALUATION')

                        status = await self.analyze_shuffling_and_cards()
                        if status != None:
                            return status
                        else:
                            logger.info("No cheaters, starting winner evaluation")
                            return await self.determine_winner()

                # Response received from server
                elif (msg['type'] == 'start_send_keys' and 'code' in msg.keys() 
                        and currentState == 'SUBMIT_KEYS'):
                    logger.warning(colored("Sending caller symmetric keys", 'yellow', attrs=['bold']))
                    return await self.send_caller_symmetric_key()

                else:
                    error = True

            elif currentState == 'EVALUATION':
                    
                # Process game evaluation
                if ('code' in msg.keys() and msg['code'] == 0 and 'type' 
                        in msg.keys() and msg['type'] == 'share_winner' and 'winner' in msg.keys()):
                    
                    if await self.player_winning_predicition(msg) == []:
                        # No cheaters detected
                        state.apply('END_GAME')
                        return await self.notify_winner()                        

                else:
                    error = True

            elif currentState == 'END_GAME':
                # Show who won
                if ('code' in msg.keys() and msg['code'] == 0 and 'type' 
                        in msg.keys() and msg['type'] == 'share_winner' 
                            and 'seq' in msg.keys() and msg['seq'] == 0):
                    logger.info(await print_players_cards_and_deck(self.players, self.caller, msg['winner'], self.N, self.finalDeck))
                    
                    return self.handle_caller_inputs()

                else:
                    error = True
                
            else:
                logger.error(colored("Message received not appropriate for the current state " + currentState, 'red', attrs=['bold']))

            if error:
                if 'code' in msg.keys() and 'info' in msg.keys():
                    logger.error(colored("Bad response received with code %d in state %s: %s"%(msg['code'], currentState, msg['info']), 'red', attrs=['bold']))
                else:
                    logger.error(colored("Invalid request for current state '%s'"%currentState, 'red', attrs=['bold']))

        # Proccess Responses
        if (currentInfoState == 'REQUESTED' and 'UUID' in msg.keys() 
            and self.bufferUUID != None and msg['UUID'] == self.bufferUUID[0]):

            if 'code' in msg.keys() and msg['code'] == 0:
                # Get nonce for authentication
                if (self.bufferUUID[1] == 'get_nonce' and currentState == 'AUTH'
                        and 'nonce' in msg.keys()): # Login response
                    self.nonce = msg['nonce']
                    self.bufferUUID = (random.uniform(1.0, 100.0), 'login')
                    # With card auth
                    if self.caller.cardPin != '':     
                        return {"type": 'login', 
                            "role": 'caller',
                            "pubkey": asymmetric.public_key_to_string(self.caller.publicKey),
                            "nick": self.caller.nick,
                            "nonce": self.nonce,
                            "UUID": self.bufferUUID[0]
                            }
                    # Without card auth
                    else:
                        return {"type": 'login', 
                            "role": 'caller',
                            "nick": self.caller.nick,
                            "nonce": self.nonce,
                            "UUID": self.bufferUUID[0]
                            }
                    
                # Authenticate caller login attempt
                if self.bufferUUID[1] == 'login' and currentState == 'AUTH': # Login response
                    if await self.login_caller_response(msg):
                        state.apply('IDLE')
                        logger.info(colored(f'caller authenticated\n', 'green'))
                    else:
                        raise OSError("Playing Area denied authentication")

                # Response from key submission
                elif (self.bufferUUID[1] == 'key_submit') and currentState == 'SUBMIT_KEYS':
                    logger.info("Caller symmetric key was exchanged")
                    self.receivedCallerSymKey = True
                    # check if all players sent their symmetric keys
                    if await check_players_symm_keys(self.players) and self.receivedCallerSymKey:
                        logger.warning(colored("All keys received, starting shuffling evaluation", 'yellow', attrs=['bold']))
                        state.apply('EVALUATION')
                        
                        status = await self.analyze_shuffling_and_cards()
                        if status != None:
                            return status
                        else:
                            logger.info("No cheaters, starting winner evaluation")
                            await self.determine_winner()

                # Show audit logs
                elif (self.bufferUUID[1] == 'get_users_list') and 'users' in msg.keys() and currentState == 'END_GAME':
                    
                    string = "Received Users list: \n"
                    for user in  msg['users']:
                        string += f"\tSeq: %d, Nick: %s\n"%(user['seq'], user['nick'])
                    logger.info(string)

                    self.bufferUUID = None
                    infoState.apply('FREE')
                    return self.handle_caller_inputs()
                
                # Show get users list
                elif (self.bufferUUID[1] == 'get_audit_log') and 'log' in msg.keys() and currentState == 'END_GAME':

                    if not os.path.exists('./audit_logs'):
                        os.mkdir('./audit_logs')
                    logName = r'./audit_logs/' + self.caller.nick + "_" + str(time.time()) + '.log'
                    with open(logName, "w") as f:
                        f.write(str(msg))
                    
                    logger.info(colored(f'Received audit log file saved at {logName}', 'green'))

                    self.bufferUUID = None
                    infoState.apply('FREE')
                    return self.handle_caller_inputs()
                
                else:
                    logger.error(colored(f'Unknown or not appropriate message received: ' + str(msg), 'red', attrs=['bold']))

            else:
                logger.error(colored(f"Error Code %d: %s"%(msg['code'], msg['info']), 'red', attrs=['bold']))

            self.bufferUUID = None
            infoState.apply('FREE')
            

        return None


    async def caller_life(self) -> None:
        """ 
        Main function used to handle the caller. It receives
        and sends information from and to the Playing Area 
        """

        await self.login_caller_request()

        while True:
            
            if self.playingAreaPublicKey == None:
                recvData = await communication.recv_dict(self.caller.reader)
            else:
                try:
                    recvData = await communication.recv_dict(self.caller.reader , self.playingAreaPublicKey)
                except SyntaxError as e:
                    raise OSError(f"Playing area signature is wrong, aborting caller ...")

                    

            if recvData == None: # Disconnected
                raise OSError("Connection with Playing Area terminated")

            logger.debug(f'Received: {recvData}\n')            

            sendData = await self.determine_action(recvData)

            if sendData != None and sendData != {}: # It's not always necessary to transmit data
                cheatSignature = False
                rand = random.randint(0,100)

                if rand < self.cheat and (self.bufferUUID == None or self.bufferUUID != None and self.bufferUUID[1] != 'login'):
                    cheatSignature = True
                    logger.warning(colored(f'Just cheated in sending my signature', 'yellow', attrs=['bold']))
                logger.debug(f'Sending: {sendData}\n')
                # No card or not authentication
                if self.caller.cardPin != '' and state.getState() == 'AUTH':
                    await communication.send_dict(
                                    self.caller.writer, 
                                    sendData , 
                                    asymmetric.sign_message_cc(self.caller.cardPin, communication.json_to_bytes(sendData)), 
                                    cheatSignature
                                )
                else:
                    
                    await communication.send_dict(
                                    self.caller.writer, 
                                    sendData , 
                                    asymmetric.sign_message(communication.json_to_bytes(sendData),self.caller.privateKey), 
                                    cheatSignature
                                )
                    
            

    def handle_caller_inputs(self):
        """
        Function used to handle input on the caller
        """
        while(True):
            input_str: str = input("Options avaliable\n\t[1] : Get user list\n\t[2] : Get logs\n\t[3] : Exit game\n")
            try:
                opt: int = int(input_str)
                if opt not in [1,2,3]:
                    raise Exception
            except Exception as e:
                logger.warning(colored('Invalid Input!', 'yellow', attrs=['bold']))
                continue
            
            if opt == 1:
                self.bufferUUID = (random.uniform(1.0, 100.0), 'get_users_list')
                infoState.apply('REQUESTED') # Update state
                
                return {'type': 'get_users_list',
                        'UUID': self.bufferUUID[0]
                    }
                
            elif opt == 2:
                self.bufferUUID = (random.uniform(1.0, 100.0), 'get_audit_log')
                infoState.apply('REQUESTED') # Update state
                
                return {'type': 'get_audit_log',
                        'UUID': self.bufferUUID[0]
                    }
            elif opt == 3:
                logger.info(colored("Game Over!", "green", attrs=["reverse", "blink", "bold"]))
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
    parser.add_argument("--nick", help="Nick for the caller", type=str, default="caller")
    parser.add_argument("--rsasize", help="Size of the RSA keypair", type=int, default=2048)
    parser.add_argument("--log", help="Log threshold (default=INFO)", type=str, default='INFO')
    parser.add_argument("--cheat", help="Chance (in %%) to cheat, default is 10", type=int, default=10)
    parser.add_argument("--card",help="boolean to use card", type=convert_str_bool, default=False)
    args = parser.parse_args()

    # check Logger value
    numericLogLeved = getattr(logging, args.log.upper(), None)
    if not isinstance(numericLogLeved, int):
        raise ValueError('Invalid log level: %s' % numericLogLeved)

    # Generate key pair
    privKey: rsa.RSAPrivateKeyWithSerialization = asymmetric.generate_private_key(args.rsasize)
    pubKey: rsa.RSAPublicKey = asymmetric.generate_public_key(privKey)

    asymmetric.save_key("private.pem",privKey)
    asymmetric.save_key("public.pem",pubKey)

    state: State = State(['AUTH','IDLE','SUBMIT_CARD','SUBMIT_DECK','SUBMIT_KEYS', 'EVALUATION', 'END_GAME'],
        {
            'AUTH' : ['IDLE'], # Initial authentication
            'IDLE' : ['SUBMIT_CARD'], # Caller authenticated and waiting to start game
            'SUBMIT_CARD' : ['IDLE','SUBMIT_DECK'], # Game started
            'SUBMIT_DECK' : ['IDLE','SUBMIT_KEYS'], # Game ongoing
            'SUBMIT_KEYS' : ['IDLE' , 'EVALUATION'], # Game ongoing
            'EVALUATION': ['IDLE', 'END_GAME'], # Evaluate plays and discover cheater
            'END_GAME' : ['IDLE'] # Game has finished, announce winner
        },
        'AUTH'
        )


    infoState: State = State(['FREE','REQUESTED'], 
                    {
                        'FREE': ['REQUESTED'], 
                        'REQUESTED': ['FREE']
                    },
                    'FREE'
                    )

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
    logName = r'./logs/caller_' + str(time.time()) + '.log'
    fh = logging.FileHandler(logName)
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(logging.Formatter('%(asctime)s - [%(name)s, %(levelname)s]: %(message)s'))

    # add ch to logger
    logger.addHandler(ch)

    # add fh to logger
    logger.addHandler(fh)

    async def main(ip: str, port: int, nick: str, cheat: int,
        privKey: rsa.RSAPrivateKeyWithSerialization, pubKey: rsa.RSAPublicKey,
        cardPin: str = '') -> None:
        
        # Create the caller class
        caller = Caller()

        # Check and resize caller nick (max characters of 20)
        if len(nick) > 20:
            nick = nick[:20]
        
        # Connect the caller to the playing_area (server)
        await caller.create_caller(ip, port, nick, cheat, privKey, pubKey, cardPin)

        logger.info(colored(f'Listenning on {ip}:{port}', 'green'))

        await caller.caller_life()

    try:
        if args.card:
            pin = str(input("Please input the authentication pin of the card: "))
        
            asymmetric.close_connection(asymmetric.create_connection(pin))
            logger.info(colored(f'Successfully authentication with card', 'green'))
            asyncio.run(main(args.bind, args.port, args.nick, args.cheat, privKey, pubKey, pin))
        else:
            asyncio.run(main(args.bind, args.port, args.nick, args.cheat, privKey, pubKey))
    except KeyboardInterrupt:
        logger.error("\nCaller Terminated")
    except OSError as e:
        logger.error("No Connection to playing area: " + str(e))
    #except ValueError and TypeError as e:
    #    print("Error: " + str(e))
