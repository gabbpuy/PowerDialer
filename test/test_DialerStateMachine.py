# -*- coding: utf-8 -*-
from unittest import TestCase

from power_dialer.dialer_state_machine import AgentState, DialerStateMachine, AGENT_TRANSITIONS


class TestStateMachine(TestCase):

    def test_constructor(self):
        """
        Test constructor with empty start state
        """
        state_machine = DialerStateMachine(AGENT_TRANSITIONS)
        assert state_machine.state is None

    def test_constructor_with_initial_state(self):
        """
        Test constructor with initial start state.
        """
        state_machine = DialerStateMachine(AGENT_TRANSITIONS, AgentState.offline)
        assert state_machine.state is AgentState.offline

    def test_set_state(self):
        """
        Test set state with no initial state
        """
        state_machine = DialerStateMachine(AGENT_TRANSITIONS)
        result = state_machine.set_state(AgentState.offline)
        assert result is True, (True, result)

    def test_set_state_initial_state(self):
        """
        Test set state with an initial state
        """
        state_machine = DialerStateMachine(AGENT_TRANSITIONS, AgentState.offline)
        result = state_machine.set_state(AgentState.offline)
        assert result is False, (False, result)

    def test_set_state_post_set_state(self):
        """
        Test set state with an initial state
        """
        state_machine = DialerStateMachine(AGENT_TRANSITIONS)
        _result = state_machine.set_state(AgentState.offline)
        result = state_machine.set_state(AgentState.idle)
        assert result is False, (False, result)

    def test_transition(self):
        """
        Test basic transition
        """
        state_machine = DialerStateMachine(AGENT_TRANSITIONS, AgentState.offline)
        result = state_machine.transition(AgentState.idle)
        assert result is True, (True, result)

    def test_bad_transition(self):
        """
        Test forbidden transition
        """
        state_machine = DialerStateMachine(AGENT_TRANSITIONS, AgentState.offline)
        result = state_machine.transition(AgentState.busy)
        assert result is False, (False, result)
