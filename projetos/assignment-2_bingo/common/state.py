"""
`state` package is used to manage the states of execution of the 
    various entities of the game
"""
class State:
    """
    Class to hold and transition between states
    
    Attributes:
        - __valid_states: List of the various states
        - __valid_transitions: dict with the states and their possible transitions
        - __state: Current State
    """
    def __init__(self , states: list[str], transitions: dict[str,list[str]], initial_state: str) -> None:
        """
        Initialize the State class
        Args:
            - states: list of all the states
            - transitions: Dictionary the each state and it's
            possible transitions to other states
            - initial_state: Starting state
        Raises:
            - ValueError: if the initial state isn't contained in the
            list of possible states
        """
        self.__valid_states = states
        self.__valid_transitions : dict[str,list[str]] = transitions

        if initial_state not in states:
            raise ValueError("Invalid initial state")

        self.__state = initial_state

    def getState(self) -> str:
        """
        Function to return the current state
        Returns:
            - String representing the current state
        """
        return self.__state

    def apply(self , newState : str) -> None:
        """
        Function to change state. It applies a transition for 
            a state according to the current state
        Args:
            - newState: The new state to transition
        Raises:
            - ValueError: if the new state isn't contained in the list
            of states or the new state isn't a valid transition,
            according to the current state
        """
        if newState not in self.__valid_states:
            raise ValueError(f"newState ({newState}) is invalid")
        if newState not in self.__valid_transitions[self.__state]:
            raise ValueError(f"Invalid transition ({self.__state} -> {newState})")

        self.__state = newState