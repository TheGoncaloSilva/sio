"""
`bingo` package used to handle core game logic
"""
import accessify
import random

class Bingo:
    """
    Class Bingo, allows to create cards and decks,
    as well as discover winning solutions

    Attributes:
        - __N: Number of possible cards in the game
        - __M: Amount of cards that can be played
        - __card: stored set of cards
    """
    def __init__(self , N: int, M: int, card: list[int] | None = None) -> None:
        """
        Initialize 'Bingo' class 
        Args:
            - N: Number of possible cards in the game {1,...N}
            - M: Amount of cards that can be played
            - card: List of cards to be saved. If not defined, it will
            generate a random set of cards based on the N and M parameters
        Raises: 
            - ValueError: if N or M are outside of their range, or they have 'int' type
        """

        if not isinstance(N , int) or not isinstance(M , int):
            raise ValueError("Expected 'int' values")

        if M <= 0 or N <= 0:
            raise ValueError("Invalid M or N")
        if M >= N:
            raise ValueError("M should be smaller than N")
        
        self.__N: int = N
        self.__M: int = M

        if card != None:
            if len(card) != M:
                raise ValueError("Incompatible size, len(card) argument must be equal to M")
            else:
                self.__card: list[int] = card
        else:
            self.__card : list[int] = self.generate_random_card()

    def getCard(self) -> list[int]:
        """
        Obtain player set of card
        Returns: 
            - list of 'int', that corresponds to the player cards
        """
        return self.__card[:]


    @accessify.private
    def generate_random_card(self) -> list[int]:
        """
        Private function to generate a set of cards
        Returns:
            - List of cards
        """
        card: list[int] = []
        available: list[int] = [k for k in range(1,self.__N+1)]
        for iter in range(self.__M):
            index: int = random.randint(0 , self.__N - iter - 1)
            card.append(available[index])
            available = available[0:index] + available[index+1:]
        return card


    @staticmethod
    def __swap(g : list, p1 : int, p2 : int) -> None:
        """
        Static function to two elements of a given list

        `Note:` It manages de swap by reference
        Args:
            - g: provided list
            - p1, p2: elements to swap
        """
        x = g[p1]
        g[p1] = g[p2]
        g[p2] = x

    @accessify.private
    def satisfies(self , solution: list[int]) -> bool:
        """
        Function to check if a give solution is satisfied by the saved
            set of cards
        Args:
            - solution: Deck or solution of the cards
        Returns:
            - True if the cards satisfy the solution, false otherwise
        """
        if not isinstance(solution , list) or len(solution) == 0:
            return False
        for number in self.__card:
            if number not in solution:
                return False
        return True


    @staticmethod
    def generate_random_solution(N: int) -> list[int]: 
        """
        Given an integer, a random solution is generated
        Args:
            - N: solution length
        Returns:
            - list: solution generated
        Raises:
            - ValueError: if N is not an 'int' or N <= 1
        """
        if not isinstance(N, int) or N <= 1:
            raise ValueError("Invalid N")
        else:
            game: list[int] = [k for k in range(1 , N + 1)]
            for index in range(N):
                Bingo.__swap(game , index , random.randint(0 , N-1))
            return game
    

    def first_winning_position(self , solution: list[int]) -> int:
        """
        Find the first index of 'solution' that satisfies the card
        Args:
            - solution: list: the solution
        Returns
            - int: first valid index
        Raises
            - ValueError: if the solution is not a list or the solution is invalid according with the rules
        """
        if not isinstance(solution , list):
            raise ValueError("solution variable should be a 'list'")
        if len(solution) != self.__N:
            raise ValueError(f"solution list size of {len(solution)} should be equal to {self.__N}")
        if not self.satisfies(solution):
            raise ValueError("Invalid solution")

        card = self.__card.copy()

        for index , number in enumerate(solution):
            if not isinstance(number , int):
                raise ValueError("solution variable list should only contain 'int' variables")

            if number in card:
                card.remove(number)
            if len(card) == 0:
                return index

        return -1

    @staticmethod
    def shuffle(_list: list) -> list:
        """
        Returns a copy of _list argument shuffled randomly
        Args:
            - _list: provided list to shuffle
        Returns:
            - The shuffled list
        """
        shuffled_list = _list[:]
        random.shuffle(shuffled_list)
        return shuffled_list


    