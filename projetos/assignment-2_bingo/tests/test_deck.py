from typing import Tuple
import pytest
import sys
pytest_plugins = ('pytest_asyncio',)

from common.deck import Deck, DeckValues
from cryptography import exceptions as cryptoException
from common.symmetric import generate_key, encrypt_values, bytes_to_string

def test_init_retrieve_deck():
    d: Deck = Deck([1,2,3], 0)
    assert d.retrive_deck() == [DeckValues([1,2,3], 0)]


def test_add_deck():
    d: Deck = Deck([1,2,3], 0)
    d.add_deck([3,2,1], 1)
    assert d.retrive_deck() == [DeckValues([1,2,3], 0), DeckValues([3,2,1], 1)]


def test_retrieve_decrypted_deck_correct_order():

    original_encryped = Deck.encrypt_deck([1,2,3],b'123456789abcdefg')
    d = Deck(original_encryped, 0)
    
    d.add_deck(Deck.encrypt_deck(original_encryped,b'223456789abcdefg'), 1)

    decrypted = d.retrieve_decrypted_deck([(0, b'123456789abcdefg'), (1, b'223456789abcdefg')])

    assert decrypted == [DeckValues([1,2,3], 0), DeckValues([1,2,3], 1)]


def test_retrieve_decrypted_deck_invalid_key():
    d = Deck(Deck.encrypt_deck([1,2,3],b'123456789abcdefg'), 0)
    d.add_deck(Deck.encrypt_deck([3,2,1],b'223456789abcdefg'), 1)
    assert d.retrieve_decrypted_deck([(0, b'123456789abcdefg'), (1, b'523456789abcdefg')]) == 1


def test_retrieve_decrypted_deck_unknown_seq():
    d = Deck(Deck.encrypt_deck([1,2,3],b'123456789abcdefg'), 0)
    d.add_deck(Deck.encrypt_deck([3,2,1],b'223456789abcdefg'), 1)
    assert d.retrieve_decrypted_deck([(0, b'123456789abcdefg'), (2, b'123456789abcdefg')]) == 2

def test_retrieve_decrypted_bad_entities():
    d = Deck(Deck.encrypt_deck([1,2,3],b'123456789abcdefg'), 0)
    d.add_deck(Deck.encrypt_deck([3,2,1],b'223456789abcdefg'), 1)
    with pytest.raises(TypeError): 
        d.retrieve_decrypted_deck('potatos') # type: ignore

def test_check_everyone_submitted_deck():
    d = Deck([1,2,3], 0)
    d.add_deck([3,2,1], 1)
    assert d.check_everyone_submitted_deck([0,1]) == True
    assert d.check_everyone_submitted_deck([0,1,2]) == False


def test_encryption():
    entities: list[Tuple[int, bytes]] = [   
                (0, b'\xe7g\xa6\xcf\x94\xb1\xd2\x1b*\x9b/\xd2\x82YS\xb5'),
                (1, b'_C\x89\xac+\xfbG\x9dc\x8c(I\x848\xe2\xe3'), 
                (2, b'P\xf0\x96|~\xf8d\\\x07\x7f\xf8*\xc1cY\xf4'), 
                (3, b'7Z\xe4!\xc4/\xe0\xe3X5\xf0\xe1\xdfy\xfc\x1e'), 
                (4, b'X\x90o\xda2]\xd6?\xc0\xb0\x84\xcf\x12\xf0eL')               
            ]
    initialDeck: list[int] = [1,2,3,4,5]
    circularEnc: list[bytes] = Deck.encrypt_deck(initialDeck, entities[0][1])
    deck: Deck = Deck(circularEnc, entities[0][0])
    for seq, key in entities:
        if seq == 0: continue # skip initial setup
        circularEnc = [ encrypt_values(bytes_to_string(card), key)
                    for card in circularEnc ]
        deck.add_deck(circularEnc, seq)

    decrypted_decks: list[DeckValues] | None | int = deck.retrieve_decrypted_deck(entities)

    print(decrypted_decks)
    
    assert isinstance(decrypted_decks, list)
    assert isinstance(decrypted_decks[0], DeckValues)


    assert all([set({1,2,3,4,5}) == set(abc.deck) for abc in decrypted_decks])

    finalDeck: list[int] | list[bytes] = decrypted_decks[0].deck
    assert all([isinstance(value,int) for value in decrypted_decks[0].deck])
    


    initialDeck.sort()
    finalDeck.sort() # Sort both deck to compare
    assert initialDeck == finalDeck



    assert deck.check_contains_all_cards(initialDeck)

def test_encryption_bad_card():
    entities: list[Tuple[int, bytes]] = [   
                (0, b'\xe7g\xa6\xcf\x94\xb1\xd2\x1b*\x9b/\xd2\x82YS\xb5'),
                (1, b'_C\x89\xac+\xfbG\x9dc\x8c(I\x848\xe2\xe3'), 
                (2, b'P\xf0\x96|~\xf8d\\\x07\x7f\xf8*\xc1cY\xf4'), 
                (3, b'7Z\xe4!\xc4/\xe0\xe3X5\xf0\xe1\xdfy\xfc\x1e'), 
                (4, b'X\x90o\xda2]\xd6?\xc0\xb0\x84\xcf\x12\xf0eL')               
            ]
    initialDeck: list[int] = [1,2,3,4,5]
    badDec: list[int] = [5,6,7,8,9,10,11,12]
    circularEnc: list[bytes] = Deck.encrypt_deck(initialDeck, entities[0][1])
    deck: Deck = Deck(circularEnc, entities[0][0])
    for seq, key in entities:
        if seq == 0: continue # skip initial setup
        elif seq == 2:
            circularEnc = Deck.encrypt_deck(badDec, entities[2][1])
        else:
            circularEnc = [ encrypt_values(bytes_to_string(card), key)
                        for card in circularEnc ]
        deck.add_deck(circularEnc, seq)

    decrypted_decks: list[DeckValues] | None | int = deck.retrieve_decrypted_deck(entities)

    print(decrypted_decks)
    
    assert isinstance(decrypted_decks, int)
    assert decrypted_decks == 2

