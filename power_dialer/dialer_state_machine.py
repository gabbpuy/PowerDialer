# -*- coding: utf-8 -*-
from collections import defaultdict
from dataclasses import dataclass
from enum import Enum, auto
from typing import List


class AgentState(Enum):
    # This is the default state, new agents will get this state
    offline = auto()
    idle = auto()
    busy = auto()


@dataclass
class Transition:
    from_state: AgentState
    to_state: AgentState


AGENT_TRANSITIONS = (
    Transition(AgentState.offline, AgentState.idle),
    Transition(AgentState.idle, AgentState.idle),
    Transition(AgentState.idle, AgentState.busy),
    Transition(AgentState.idle, AgentState.offline),
    Transition(AgentState.busy, AgentState.idle)
)


class DialerStateMachine:
    """
    A mini finite state machine to control the state of an agent.
    """
    def __init__(self, transitions: List[Transition], startState: AgentState = None):
        self.__transitions = defaultdict(set)
        self.__process_transitions(transitions)
        self.__current_state: AgentState = startState

    @property
    def state(self):
        return self.__current_state

    def set_state(self, state: AgentState) -> bool:
        """
        Set the machine state, this can only be called when current state is None, otherwise
        all states changes have to use `transition`

        :param state: State to set to.
        :return: True if the state can be set
        """
        if self.__current_state is None:
            self.__current_state = state
            return True
        return False

    def transition(self, new_state: AgentState) -> bool:
        """
        Transition to a new state

        :param new_state: The state to change to
        :return: True if the new state can be obtained.
        """
        if new_state in self.__transitions[self.__current_state]:
            self.__current_state = new_state
            return True
        return False

    def __process_transitions(self, transitions: List[Transition]):
        """
        Build a reverse look-up table of states.

        :param transitions: A list of transitions to keep
        :return:
        """
        for t in transitions:
            self.__transitions[t.to_state].add(t.from_state)
