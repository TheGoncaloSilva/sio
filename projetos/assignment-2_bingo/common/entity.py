"""
`entity` package is used for implementing the data structures of
    the various entities envolved 
"""
import asyncio
from cryptography.hazmat.primitives.asymmetric import rsa # type: ignore
from enum import Enum
import copy


class Entity:
    """
    Class to save a entity values
    Attributes:
        - seq: entity sequence number
        - nick: entity nick
        - pubKey: Public key of the entity
        - writer: entity stream to write data
        - reader: entity stream to read data
        - symmetricKey: Symmetric key of the entity
        - cardPin: Pin code of the entity card
    """
    def __init__(self, seq: int , nick: str, pubKey: rsa.RSAPublicKey,
        writer: asyncio.streams.StreamWriter, reader: asyncio.streams.StreamReader) -> None:
        """
        Instanciate Entity class
        Args:
            - seq: entity sequence number
            - nick: entity nick
            - pubKey: Public key of the entity
            - writer: entity stream to write data
            - reader: entity stream to read data
        Returns:
            - TypeError: when one provided value doesn't match assigned type
        """
        
        if (not isinstance(nick, str) or not isinstance(pubKey, rsa.RSAPublicKey) 
                or not isinstance(writer, asyncio.streams.StreamWriter)
                    or not isinstance(reader, asyncio.streams.StreamReader)):
            raise TypeError("Wrong provided type")
            
        self.seq: int = seq
        self.nick: str = nick
        self.publicKey: rsa.RSAPublicKey = pubKey
        self.writer: asyncio.streams.StreamWriter = writer
        self.reader: asyncio.streams.StreamReader = reader
        self.symmetricKey: bytes = b'' # Default value
        self.cardPin: str = ''

    def __str__(self):
        """
        Function used to pass print the reference of this class
        """

        max_len = max(len('seq: ') + len(str(self.seq)), len('nick: ') + len(str(self.nick)))
        top = '┌' + '─' * (max_len + 2) + '┐'
        bottom = '└' + '─' * (max_len + 2) + '┘'
        template = '│ {0:<{1}} │'
        lines = [template.format(f"{attr}: {value}", max_len) for attr, value in {'seq':self.seq,'nick':self.nick}.items()]
        return '\n'.join([top] + lines + [bottom])


    def set_symmetric_key(self, simKey: bytes) -> None:
        """
        Function to store a Entity symmetric key, 
            used to encrypt it's cards
        Args:
            - simKey: Symmetric key of the Entity
        Raises:
            - TypeError: when simKey isn't a bytes object
        """

        if not isinstance(simKey, bytes):
            raise TypeError("Key should be a bytes object")

        self.symmetricKey: bytes = simKey


    def set_seq(self, seq: int) -> None:
        """
        Function to store the Entity sequence number
        Args:
            - seq: Sequence Number
        Raises:
            - TypeError: if seq isn't in 'int' type
        """

        if not isinstance(seq, int):
            raise TypeError("Seq should be in 'int' type")

        self.seq: int = seq


    def set_private_key(self, privKey: rsa.RSAPrivateKeyWithSerialization) -> None:
        """
        Function to set the Primary key of an Entity
        Args:
            - privKey: Private key of the Entity
        Raises:
            - TypeError: when the privKey is not in correct type
        """

        if not isinstance(privKey, rsa.RSAPrivateKeyWithSerialization):
            raise TypeError("Wrong provided type")

        self.privateKey: rsa.RSAPrivateKeyWithSerialization = privKey


    def set_ip_port(self, ip: str, port: int) -> None:
        """
        Function to set the ip and port that a entity operates
        Args:
            - ip: Ip of the Entity
            - port: Port of operation
        Raises:
            - TypeError: if mPlayers isn't in 'int' type
        """

        if (not isinstance(ip, str) or not isinstance(port, int)):
            raise TypeError("Max Players should be a 'int' object")

        self.ip: str = ip
        self.port: int = port


    def set_max_players(self, mPlayers: int) -> None:
        """
        Function that stores the maximum players allowed in the game
        Args:
            - mPlayers: maximum player number
        Raises:
            - TypeError: if mPlayers isn't in 'int' type
        """

        if not isinstance(mPlayers, int):
            raise TypeError("Max Players should be a 'int' object")

        self.maxPlayers: int = mPlayers

    def set_card_pin(self, cardPin: str) -> None:
        """
        Function to store the pin code of a card
        Args:
            - cardPin: Pin code of the card associated with the entity
        Raises:
            - TypeError: if cardPin isn't in 'str' type
        """
        if not isinstance(cardPin, str):
            raise TypeError("Pin of the card should be a 'str' object")

        self.cardPin: str = cardPin


class PlayerValues(Entity):
    """
    Class to store the Player values
    """
    def __init__(self, seq: int , nick: str, pubKey: rsa.RSAPublicKey,
        writer: asyncio.streams.StreamWriter, reader: asyncio.streams.StreamReader) -> None:
        """
        Instanciate PlayerValues class
        Args:
            - seq: sequence number of the player
            - nick: Player nick
            - pubKey: Public key of the player
            - writer: Player stream to write data
            - reader: Player stream to read data
        Raises:
            - TypeError: when one provided value doesn't match assigned type
        """
        Entity.__init__(self, seq ,nick, pubKey, writer, reader)
        self.cards: list[int] | list[bytes] = [] # Default value


    def set_cards(self, cards: list[int] | list[bytes]) -> None:
        """
        Function to associate a set of cards with a player
        Args:
            - cards: Cards of the player
        """
        if not isinstance(cards, list):
            raise TypeError("Cards should be of type 'list'")

        self.cards: list[int] | list[bytes] = cards



class CallerValues(Entity):
    """
    Class to store the Caller values
    """
    def __init__(self, nick: str, pubKey: rsa.RSAPublicKey,
        writer: asyncio.streams.StreamWriter, reader: asyncio.streams.StreamReader) -> None:
        """
        Instanciate CallerValues class
        Args:
            - nick: Caller nick
            - pubKey: Public key of the Caller
            - writer: Caller stream to write data
            - reader: Caller stream to read data
        Raises:
            - TypeError: when one provided value doesn't match assigned type
        """
        Entity.__init__(self, 0 , nick, pubKey, writer, reader)
        self.deck: list[int] | list[bytes] = [] # Default value


    def set_deck(self, deck: list[int] | list[bytes]) -> None:
        """
        Function to associate a deck with a caller
        Args:
            - deck: Deck of the caller
        """
        if not isinstance(deck, list):
            raise TypeError("Deck should be of type 'list'")

        self.deck: list[int] | list[bytes] = deck 


class Banned_Reason(Enum):
    """
    Class used to classify the ban reason of a player
    """
    UNKNOWN = 'UNKNOWN'
    CARDS = 'CARDS'
    BAD_WINNER = 'BAD_WINNER'
    BAD_SIGNATURE = 'BAD_SIGNATURE'
    DISCONNECTED = 'DISCONNECTED'

class Bans():
    """
    Class used to keep track of players and bans
    Attributes:
        - __banned_list: List of banned players
    """

    def __init__(self) -> None:
        """
        Initialize the class
        """
        self.__banned_list: dict[int,Banned_Reason] = {}

    def add_ban(self, seq: int , reason: Banned_Reason) -> None:
        """
        Function to add a player to the ban list
        Args:
            - seq: Seq of the player
            - reason: Banned_Reason type, concerning
            the reason of the player been banned
        """
        if seq in self.__banned_list:
            raise ValueError("User is aldready banned")
        else:
            self.__banned_list[seq] = reason

    def is_banned(self,  seq: int) -> bool:
        """
        Function to verify if a user has been banned
        Args:
            - seq: Seq number of the player
        Returns:
            - True if the user has been banned, else otherwise
        """
        return seq in self.__banned_list

    def ban_reason(self, seq: int) -> Banned_Reason:
        """
        Function to return the ban reason of the player
        Args:
            - seq: Seq number of the player
        Returns:
            - A Banned_Reason object, concerning the reason the player
            was banned
        Raises:
            - ValueError: If the provided Seq is not in the players
            list
        """
        if seq in self.__banned_list:
            return Banned_Reason(self.__banned_list[seq])
        else:
            raise ValueError(f'Invalid sequence number provided ({seq})')

    def get_bans(self) -> dict:
        """
        Function to get all the banned players
        Returns:
            - A dictionary with all banned players 
        """
        return copy.deepcopy(self.__banned_list)

    def clear(self) -> None:
        """
        Function to clear the ban history of players
        """
        self.__banned_list = {}


    
def check_dict_fields(msg: dict , expectedFields: list[str]) -> None:
    """
    Function to check if the given dictionaries has the expected keys
    Args:
        - msg: given dictionary
        - expectedFields: list with the expected keys
    Raises:
        - ValueError: if expectedFields values are not in msg keys
    """
    for f in expectedFields:
        if f not in msg.keys():
            raise ValueError(f"Missing argument {(f)}")


INVALID_SEQ_NUMBER: int = -1

def find_seq_number_by_stream(stream: asyncio.streams.StreamReader, players: dict[int,Entity]) -> int:
    """
    Function to get the seq number of a given StreamReader
    Args:
        - stream: Given Stream Reader
        - players: dictionary of seq and a Entity object
    Returns:
        - integer seq of the Entity
    """
    for seq in players.keys():
        stream_reader : asyncio.streams.StreamReader = players[seq].reader
        if stream_reader == stream:
            return seq
    return INVALID_SEQ_NUMBER


def find_seq_number_by_stream_writer(stream: asyncio.streams.StreamWriter, players: dict[int,Entity]) -> int:
    """
    Function to get the seq number of a given StreamWriter
    Args:
        - stream: Given Strem Writer
        - players: dictionary of seq and a Entity object
    Returns:
        - integer seq of the Entity
    """
    for seq in players.keys():
        stream_writer : asyncio.streams.StreamWriter = players[seq].writer
        if stream_writer == stream:
            return seq
    return INVALID_SEQ_NUMBER


async def check_players_symm_keys(players: dict[int, PlayerValues]) -> bool:
    """
    Function to check if all players have submitted their respective 
        symmetric card encryption keys
    Args:
        - players: dictionary containing the players
    Returns:
        - False if at least one player hasn't submitted his 
        symmetric key, otherwise, True
    """
    for seq, player in players.items():
        if player.symmetricKey == b'':
            return False

    return True


async def check_all_players_cards(players: dict[int, PlayerValues]) -> bool:
    """
    Function to check if all players have submitted their cards
    Args:
        - players: dictionary containing the players
    Returns:
        - False if at least one player hasn't submitted his 
        cards, otherwise, True
    """
    for seq, player in players.items():
        if player.cards == []:
            return False

    return True


async def check_player_cards_number_equal_deck(deck: list[int], cards: list[int]) -> bool:
    """
    Function to assess if a given set of cards contains the same
        exact set of cards as the deck
    Args:
        - deck: Caller Deck
        - cards: Player set of cards
    Returns:
        - True if the set of cards contains de same cards as
        the deck, False otherwise
    Raises:
        - TypeError: if the provided arguments are not of 
        correct type
    """
    if not isinstance(deck, list):
            raise TypeError("Deck should be of type list")

    if not isinstance(cards, list):
        raise TypeError("Cards should be a list object")

    if (not all(isinstance(card, int) for card in cards) 
            or not all(isinstance(card, int) for card in deck)): 
        raise TypeError("Cards and Deck should be of type list of 'bytes'")

    return all(card in deck for card in deck)


async def print_user_list(players: dict[int, PlayerValues], maxPlayers: int, banned: Bans = Bans()) -> str:
    """
    Function to return a formatted string list with the players of the game
    Args:
        - players: dictionary containing the players
        - maxPlayers: Max defined player number
        - banned: Class containing all the banned players (optional)
    Returns:
        - Formatted string
    """
    string = f'|--------------------------------------|\n'
    string += f'      |         Player list                  |\n'
    string += f'      |----------------------------|---------|\n'
    string += f'      | Seq |         Nick         | Status  |\n'
    string += f'      |----------------------------|---------|\n'
    for seq, value in players.items():
        string += f'      | %2d  | '%value.seq
        string += format(value.nick, '^20s')
        if banned.is_banned(seq): 
            string += f' | Banned  |\n'
        else:
            string += f' | Playing |\n'
    string += f'      |----------------------------|---------|\n'
    string += f'      | Max Players:    %2d                   |\n'%maxPlayers
    string += f'      |______________________________________|\n'
    return string


async def print_players_cards_and_deck(players: dict[int, PlayerValues], caller: CallerValues, winners: list[int], N: int, finalDeck: list[int]) -> str:
    """
    Function to return a strin with the cards and deck of everyone in the game
    Args:
        - players: dictionary containing the players
        - caller: caller values, including it's deck
        - N: N card number
        - finalDeck: Final shuffled deck
    Returns:
        - Formatted string
    """
    arrSyzePadding: float = (N * 55)/16
    linesPadding: int = int((N * 86)/16)

    string = f'|'+''.rjust(linesPadding,'-')+'|\n'
    string += f'      |'+'Cards/Decks'.center(linesPadding,' ')+'|\n'
    string += f'      |'+''.rjust(linesPadding,'-')+'|\n'
    string += f'      | Seq |         Nick         | '+'Cards'.center(int(arrSyzePadding),' ')+' |\n'
    string += f'      |'+''.rjust(linesPadding,'-')+'|\n'
    # Caller
    string += f'      | %2d  | '%caller.seq
    string += format(caller.nick, '^20s')
    string += f' | '
    string += f'{str(finalDeck):>{int(arrSyzePadding)}}'
    string += f' |\n'
    # Players
    for key, value in players.items():
        string += f'      | %2d  | '%value.seq
        string += format(value.nick, '^20s')
        string += f' | '
        if key in winners:
            string += f'{str(value.cards):<{int(arrSyzePadding/2)-3}}    '
            if len(winners) > 1: string += f' {"(draw)":^{int(arrSyzePadding/2)-2}} '
            else: string += f' {"(winner)":^{int(arrSyzePadding/2)-2}} '
        else:
            string += f'{str(value.cards):<{int(arrSyzePadding)}}'
        string += f' |\n'
    string += f'      |'+''.rjust(linesPadding,'_')+'|\n'
    return string
