# -*- coding: utf-8 -*-
import datetime
from dataclasses import dataclass


@dataclass
class CallRecord:
    agent_id: str
    number: str
    started: datetime.datetime
    ended: datetime.datetime = None
