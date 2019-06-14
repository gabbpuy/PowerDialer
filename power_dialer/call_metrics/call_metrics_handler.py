# -*- coding: utf-8 -*-
import datetime
import logging
import os
import tempfile
from queue import Queue
from threading import Thread

from .call_metrics_relational_storage import CallMetricsRelationalStorage
from .call_record import CallRecord
from power_dialer.singleton import Singleton

logger = logging.getLogger('power_dialer.call_metrics.handler')

# This would be implemented as a volatile distributed cache ala ElasticCache for the intermediate state and then
# Persisted into something useful like Aurora/Redshift. We're going to use an in-memory dict and sqllite to
# represent that.
# Depending on the call volume this might involve sending it via Kinesis instead of directly persisting it.
DB_NAME = os.path.join(tempfile.gettempdir(), 'powerdialer.db')


#  We're going to keep track of the agent call volume and duration
class CallMetricsHandler(metaclass=Singleton):
    """
    Pretend interface to a distributed cache
    """

    def __init__(self, db_name=DB_NAME, synchronous=False):
        self._volatile = {}
        self._storage_queue = Queue()
        self._relation_client = CallMetricsRelationalStorage(self._storage_queue, db_name)
        # Start a thread that handles storing call info because in testing we'll be making multiple dialers
        self._storage_thread = None
        if not synchronous:
            t = Thread(target=self._relation_client.save_call_records)
            t.daemon = True
            t.start()
            self._storage_thread = t

    def call_started(self, agent_id, number):
        call = CallRecord(agent_id, number, datetime.datetime.utcnow())
        self._volatile[agent_id] = call

    def call_ended(self, agent_id, number):
        call = self._volatile[agent_id]
        if call.number != number:
            # oops something went wrong here.
            logging.error('Call ended for call not in progress: Agent Id: %s, number: %s', agent_id, number)
            del self._volatile[agent_id]
            return
        call.ended = datetime.datetime.utcnow()
        del self._volatile[agent_id]
        self._storage_queue.put(call)

    def shutdown(self):
        logger.info('Shutting Down')
        self._storage_queue.put(None)
        # Uncomment to clean up between runs
        # os.unlink(DB_NAME)

    def __del__(self):
        # Signal to end processing
        self.shutdown()
