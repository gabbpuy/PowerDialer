# *-* coding: utf-8 -*-
from unittest import TestCase
from unittest.mock import patch

from power_dialer.dialer_state_machine import AgentState
from power_dialer.power_dialer import PowerDialer
from power_dialer.call_metrics.call_metrics import CallMetrics


class TestPowerDialer(TestCase):

    def tearDown(self):
        CallMetrics.shutdown()

    @patch('power_dialer.power_dialer.AgentStorage')
    @patch('power_dialer.power_dialer.CallMetrics')
    def test_on_agent_login(self, call_metrics, agent_storage):
        agent_storage.__getitem__.return_value = AgentState.offline
        pd = PowerDialer('test_id')
        pd.on_agent_login()
        # We loaded the agent
        assert agent_storage.__getitem__.called
        # The auto-save decorator triggered
        assert agent_storage.__setitem__.called
        assert len(pd.numbers) == 2, (2, len(pd.numbers))

    @patch('power_dialer.power_dialer.AgentStorage')
    @patch('power_dialer.power_dialer.CallMetrics')
    def test_on_agent_logout(self, call_metrics, agent_storage):
        agent_storage.__getitem__.return_value = AgentState.idle
        pd = PowerDialer('test_id')
        pd.on_agent_logout()
        # The auto-save decorator triggered and stored agent offline
        agent_storage.__setitem__.assert_called_once_with('test_id', AgentState.offline)

    @patch('power_dialer.power_dialer.AgentStorage')
    @patch('power_dialer.power_dialer.CallMetrics')
    def test_on_call_started(self, call_metrics, agent_storage):
        agent_storage.__getitem__.return_value = AgentState.idle
        pd = PowerDialer('test_id')
        pd.on_call_started('(212) 555-0100')
        # The auto-save decorator triggered and stored agent offline
        agent_storage.__setitem__.assert_called_once_with('test_id', AgentState.busy)
        # We started our call metrics
        call_metrics.call_started.assert_called_once_with('test_id', '(212) 555-0100')

    @patch('power_dialer.power_dialer.AgentStorage')
    @patch('power_dialer.power_dialer.CallMetrics')
    def test_on_call_failed(self, call_metrics, agent_storage):
        agent_storage.__getitem__.return_value = AgentState.idle
        pd = PowerDialer('test_id')
        pd.on_call_failed('(212) 555-0101')
        # The auto-save decorator triggered
        assert agent_storage.__setitem__.called
        assert len(pd.numbers) == 1, (1, len(pd.numbers))

    @patch('power_dialer.power_dialer.AgentStorage')
    @patch('power_dialer.power_dialer.CallMetrics')
    def test_on_call_failed_when_busy(self, call_metrics, agent_storage):
        agent_storage.__getitem__.return_value = AgentState.busy
        pd = PowerDialer('test_id')
        pd.on_call_failed('(212) 555-0101')
        # The auto-save decorator triggered
        assert agent_storage.__setitem__.called
        # The Agent is busy, so do not trigger a new call
        assert len(pd.numbers) == 0, (0, len(pd.numbers))

    @patch('power_dialer.power_dialer.AgentStorage')
    @patch('power_dialer.power_dialer.CallMetrics')
    def test_on_call_ended(self, call_metrics, agent_storage):
        agent_storage.__getitem__.return_value = AgentState.busy
        pd = PowerDialer('test_id')
        pd.on_call_ended('(212) 555-0100')
        # The auto-save decorator triggered and stored agent offline
        agent_storage.__setitem__.assert_called_once_with('test_id', AgentState.idle)
        # We started our call metrics
        call_metrics.call_ended.assert_called_once_with('test_id', '(212) 555-0100')
        # Agent is idle, we should be starting two calls
        assert len(pd.numbers) == 2, (2, len(pd.numbers))
