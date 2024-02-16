import pytest
from common.bingo import *

M = 55
N = 89

def test_bingo_creation():
    b1 : Bingo = Bingo(N, M)
    card : list = b1.getCard()
    assert isinstance(card , list)
    
    seen : set = set()
    assert len(card) == M
    for number in card:
        assert number >= 1 and number <= N
        assert number not in seen
        seen.add(number)

    b2: Bingo = Bingo(10,5,[1,2,3,4,5])
    assert b2.getCard() == [1,2,3,4,5]

    with pytest.raises(ValueError):
        b3: Bingo = Bingo(10,5,[1,2,3])
        
        

def test_generate_random_solution():
    game : list = Bingo.generate_random_solution(N)
    assert isinstance(game , list) and len(game) == N
    for number in game: assert isinstance(number , int) and number >= 1 and number <= N


def test_first_winning_position():
    b1: Bingo = Bingo(10,5,[1,2,3,4,5])
    solution: list[int] = [10,9,8,7,6,5,4,3,2,1]
    assert b1.first_winning_position(solution) == 9

    b2: Bingo = Bingo(10,5,[5,4,7,3,10])
    assert b2.first_winning_position(solution) == 7

    solution = [13, 6, 3, 12, 9, 15, 8, 5, 7, 16, 1, 4, 2, 14, 10, 11]
    b3: Bingo = Bingo(16 , 4 , [8, 5, 10, 16])
    b4: Bingo = Bingo(16 , 4,  [13 , 9 , 15 , 11])
    b5: Bingo = Bingo(16 , 4,  [2,16,12,1])
    b6: Bingo = Bingo(16 , 4,  [1,10,11,13])

    assert b3.first_winning_position(solution) == 14
    assert b4.first_winning_position(solution) == 15
    assert b5.first_winning_position(solution) == 12
    assert b6.first_winning_position(solution) == 15


def test_first_winning_position_randonmy():
    b1 : Bingo = Bingo(N,M)

    card : list = b1.getCard()
    
    solution : list = Bingo.generate_random_solution(N)

    index : int = b1.first_winning_position(solution)

    for iter in range(0,N-1):
        valid = all([value in solution[:iter+1] for value in card])
        if iter < index:
            assert not valid
        else:
            assert valid

    assert isinstance(index , int) and index >= 0 and index <= N - 1


def test_shuffle():

    lst = [1, 2, 3]
    shuffled_list = Bingo.shuffle(lst)
    assert len(shuffled_list) == 3, f"Expected 3 elements, got {len(shuffled_list)}"
    assert set(shuffled_list) == set(lst), f"Expected {lst}, got {shuffled_list}"

    lst = list(range(1000))
    shuffled_list = Bingo.shuffle(lst)
    assert len(shuffled_list) == 1000, f"Expected 1000 elements, got {len(shuffled_list)}"
    assert set(shuffled_list) == set(lst), f"Expected {lst}, got {shuffled_list}"

    lst = []
    shuffled_list = Bingo.shuffle(lst)
    assert len(shuffled_list) == 0, f"Expected 0 elements, got {len(shuffled_list)}"