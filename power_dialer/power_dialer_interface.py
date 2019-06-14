# -*- coding: utf-8 -*-
from abc import ABC, abstractmethod


class PowerDialerInterface(ABC):
    def __init__(self, agent_id: str):
        self.agent_id = agent_id

    @abstractmethod
    def on_agent_login(self):
        raise NotImplementedError

    @abstractmethod
    def on_agent_logout(self):
        raise NotImplementedError

    @abstractmethod
    def on_call_started(self, lead_phone_number: str):
        raise NotImplementedError

    @abstractmethod
    def on_call_failed(self, lead_phone_number: str):
        raise NotImplementedError

    @abstractmethod
    def on_call_ended(self, lead_phone_number: str):
        raise NotImplementedError
