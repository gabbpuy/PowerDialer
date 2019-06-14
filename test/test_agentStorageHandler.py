from unittest import TestCase

from power_dialer.agent_storage.agent_storage_handler import AgentStorageHandler
from power_dialer.agent_storage.agent_storage import AgentStorage
from power_dialer.dialer_state_machine import AgentState


class TestAgentStorageHandler(TestCase):

    # clean up the singleton
    def setUp(self) -> None:
        AgentStorage.flush()

    def test_agent_storage_constructor(self):
        """
        Test a simple constructor works
        :return:
        """
        handler = AgentStorageHandler()

    def test_agent_storage_set(self):
        """
        Test setting a key works.
        Tests the underlying implementation, not a great test.
        """
        handler = AgentStorageHandler()
        handler['test_id'] = AgentState.idle
        assert 'test_id' in handler._agents

    def test_agent_storage_get(self):
        """
        Test fetching a key works
        """
        handler = AgentStorageHandler()
        handler['test_id'] = AgentState.idle
        result = handler['test_id']
        assert result is AgentState.idle, (AgentState.idle, result)

    def test_agent_storage_get_missing_from_empty(self):
        """
        Test fetching a missing key gives us the 'offline' status
        """
        handler = AgentStorageHandler()
        result = handler['test_id']
        assert result is AgentState.offline, (AgentState.offline, result)

    def test_agent_storage_get_missing(self):
        """
        Test fetching a missing key from a populated cache gives 'offline' status
        """
        handler = AgentStorageHandler()
        handler['test_id'] = AgentState.idle
        result = handler['test_id2']
        assert result is AgentState.offline, (AgentState.offline, result)

