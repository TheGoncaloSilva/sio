"""
`deck` package used for implementing multiple deck shuffling.
"""
from dataclasses import dataclass
from .symmetric import decrypt_values, encrypt_values, bytes_from_string, bytes_to_string
from collections import Counter


@dataclass
class DeckValues:
    """
    A data class for storing a deck and its associated sequence number.
    
    Attributes:
        - deck: a list of bytes or integers representing the deck
        - seq: the sequence number of the deck
    """
    deck: list[bytes] | list[int]
    seq: int


class Deck:
    """
    A class for storing and manipulating a history of decks.
    
    Attributes:
        - __deckHistory: a list of DeckValues objects, representing the history of decks
        - errorSeq: If there was a error decrypting and which seq caused it
    
    Methods:
        - __init__: initializes the default deck (the first deck iteration)
        - add_deck: adds a new deck iteration to the history
        - retrieve_deck: returns the history of decks
        - retrieve_decrypted_deck: returns the history of decks, decrypted with a provided list of keys
        - check_everyone_submitted_deck: checks if all sequence numbers are present in the history of decks
        - check_contains_all_cards: check if the final shuffled contains all the cards of the initial deck
        - decrypt_deck: decrypts a deck with a given key
        - encrypt_deck: encrypts a deck with a given key
    """
    def __init__(self, deck: list[bytes] | list[int] | None = None, seq: int | None = None) -> None:
        """
        Function to initialize the default deck (The first deck iteration)
        Args:
            - param deck: deck created by the entity with the seq
            - param seq: entity who created/shuffled the deck
        Raises:
            - TypeError: if deck or seq are not a list or integer,
            respectfully
        """

        if deck == None and seq == None:
            self.__deckHistory = []
            return

        if not isinstance(deck, list):
            raise TypeError(f"Deck should be of type 'list' of 'bytes' or 'int'")

        if not isinstance(seq, int):
            raise TypeError(f"Seq should be of type 'int'")


        self.__deckHistory: list[DeckValues] = [DeckValues(deck, seq)]


    def add_deck(self, deck: list[bytes] | list[int], seq: int) -> None:
        """
        Function to add a deck iteration to the deck
        Args:
            - deck: deck suffled by the last entity with the seq
            - seq: entity who shuffled the deck
        Raises:
            - TypeError: if deck or seq are not a list or integer,
            respectfully
        """
        if not isinstance(deck, list):
            raise TypeError(f"Deck should be of type 'list' of 'bytes' or 'int'")

        if not isinstance(seq, int):
            raise TypeError(f"Seq should be of type 'int'")

        self.__deckHistory.append(DeckValues(deck, seq))
    

    def retrive_deck(self) -> list[DeckValues]:
        """
        Function that returns the decks stored and who shuffled it
        Returns:
            - The list of decks and seq of who shuffled it
        """
        return self.__deckHistory.copy()


    def retrieve_decrypted_deck(self, entities: list[tuple[int, bytes]]) -> list[DeckValues] | None | int:
        """
        Function that given a list of keys with their associated seq and returns the 
            decrypted deck history
        Args:
            - entities: tupple list of seq with their respective key
        Returns:
            - List with the decrypted decks (Ascending based on seq)
            - None if the provided keys don't correspond with the size of the 
            deck history
            - Int if one of the provided Seq is a cheater
        Raises:
            - ValueError: when a given key can't decrypt it's associated deck
            The player Seq of the faulty key can also be acessed at errorSeq 
            attribute
            - TypeError: if entities is not of type list
        """

        if not isinstance(entities, list):
            raise TypeError("Provided entities should be of type list")

        # Check if all seq exist on deck history
        if (len(self.__deckHistory) != len(entities) and
                not self.check_everyone_submitted_deck([ent[0] for ent in entities])):
            return None

        # Backup list to be used
        deckBackup: list[DeckValues] = self.__deckHistory.copy()

        #entities.sort() # Guarantee that the first shuffler is the first in the list
        deckIndex = 1

        deckBackup.sort(key=lambda x: x.seq)
        deckBackup.reverse()
        
        for (seq, key) in entities:
            try:
                currentDeck = deckBackup[-deckIndex]
                if seq != currentDeck.seq:
                    raise TypeError(
                        "The Seq %d is not compatible with the %d saved seq"%
                            (seq, currentDeck.seq)
                        )

                for i in range(seq , -1 , -1):
                    currentDeck.deck = Deck.decrypt_deck(currentDeck.deck , entities[i][1]) # type: ignore
                self.errorSeq = seq

            # Spaguetti exception handling (catch errors with provided keys and values)
            except Exception as e:
                if isinstance(e, OSError):
                    raise e
                else:
                    return seq

            deckIndex -= -1 # Increment deck

        for i in range(1, len(self.__deckHistory)):
            if Counter(self.__deckHistory[0].deck) != Counter(self.__deckHistory[i].deck):
                self.errorSeq = i
                return self.errorSeq
        
        # Decryption was a success, update the deck history
        deckBackup.reverse()
        self.__deckHistory = deckBackup

        return self.__deckHistory


    def check_everyone_submitted_deck(self, players: list[int]) -> bool:
        """
        Function to check if caller and all players have submitted 
        the shuffled deck

        `Note:` the caller is assumed to have a seq=0. The caller 
        will be accounted for, even if not added

        Args:
            - players: list containing the players seq
        Returns:
            - True if everyone shuffled the deck, false otherwise
        Raises:
            - TypeError: if player is not a list of 'int'
        """
        if not isinstance(players, list):
            raise TypeError("Players needs to be a list with 'int' as values")

        # If caller doesn't exist in players already
        if 0 not in players: 
            players.append(0)

        
        submittedSeq = [val.seq for val in self.retrive_deck()]

        players.sort(); submittedSeq.sort() # Sort the lists

        return submittedSeq == players


    def check_contains_all_cards(self, initialDeck: list[int]) -> bool:
        """
        Function to check if the initial deck cards are contained in the 
            final shuffled decrypted deck, most probably in a different 
            order

        `Note:` that this function requires the deck history to be decrypted

        Args:
            - initialDeck: initial deck created by the caller
        Returns:
            - True if all cards from the initial deck are in the 
            final deck, False otherwise
        Raises:
            - TypeError: if initial deck is not a list of 'int'
        """
        if not isinstance(initialDeck, list):
            raise TypeError("The initial Deck needs to be a list of 'int'")

        for card in initialDeck:
            # Get final/last deck
            if card not in self.__deckHistory[-1].deck:
                return False

        return True


    @staticmethod
    def decrypt_deck(deck: list[bytes], key: bytes) -> list[int] | list[bytes]:
        """
        Function to decrypt a deck or a set of cards
        Args:
            - deck: deck or list of cards to be decrypted. Must
            be in bytes format
            - key: key to decrypt the cards/deck
        Returns:
            - list of 'int' or 'bytes' containing all the decrypted cards 
            in the provided order
        Raises:
            - TypeError: if one of the provided arguments isn't 
            of correct type
            - Cryptography.exceptions: If there was a error decrypting
        """
        if not isinstance(deck, list):
            raise TypeError("Deck should be of type list")

        if not isinstance(key, bytes):
            raise TypeError("Key should be a bytes object")

        if not all(isinstance(card, bytes) for card in deck): 
            raise TypeError("Deck should be of type list of 'bytes'")

        # Decrypt the cards
        cards = [ decrypt_values(bytes(card), key)
                    for card in deck ]

        if not cards[0].isdigit():
            # Decrypt the cards to bytes
            return [ bytes_from_string(card)
                    for card in cards ]
        else: 
            # Decrypt the cards to interger
            return [ int(card) for card in cards ]
        

    @staticmethod
    def encrypt_deck(deck: list[int] | list[bytes], key: bytes) -> list[bytes]:
        """
        Function to encrypt a deck or a set of cards
        Args:
            - deck: deck or list of cards to be encrypted. Must
            be in int or bytes format
            - key: key to encrypt the cards/deck
        Returns:
            - list of 'bytes' containing all the encrypted cards 
            in the provided order
        Raises:
            - TypeError: if one of the provided arguments isn't 
            of correct type
            - Cryptography.exceptions: If there was a error encrypting
        """
        if not isinstance(deck, list):
            raise TypeError("Deck should be of type list")

        if not isinstance(key, bytes):
            raise TypeError("Key should be a bytes object")

        if all(isinstance(card, int) for card in deck): 
            # Encrypt the cards if they're in int format
            return [ encrypt_values(str(card), key)
                        for card in deck ]

        elif all(isinstance(card, bytes) for card in deck):
            # Encrypt the cards if they're in bytes format            
            return [ encrypt_values(bytes_to_string(bytes(card)), key)
                    for card in deck ]

        else:
            raise TypeError("Deck should be of type list of 'bytes'/'int'")