# -*- coding: utf-8 -*-
from power_dialer.singleton import Singleton
from power_dialer.dialer_state_machine import AgentState


class AgentStorageHandler(metaclass=Singleton):
    """
    Store information about the agent.

    I would keep this in a volatile key value store like Elasticache, there's not a lot of need to keep it persisted.
    Other metrics can be retrieved from cloudwatch in a basic implementation.

    Dynamo doesn't have the consistency level we'd want and is likely more expensive than we need for a 'state'
    """

    def __init__(self):
        self._agents = {}

    def __getitem__(self, agent_id) -> AgentState:
        try:
            return self._agents[agent_id]
        except KeyError:
            # No agent information, so they're new or their information got expunged, so either way they're offline.
            return AgentState.offline

    def __setitem__(self, agent_id: str, state: AgentState):
        self._agents[agent_id] = state

    def flush(self):
        self._agents = {}
