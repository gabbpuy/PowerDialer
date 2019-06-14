# -*- coding: utf-8 -*-
from power_dialer.agent_storage.agent_storage_handler import AgentStorageHandler

AgentStorage = None


def _create_agent_storage():
    global AgentStorage
    AgentStorage = AgentStorageHandler()


_create_agent_storage()
