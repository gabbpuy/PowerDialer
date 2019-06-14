# -*- coding: utf-8 -*-
import os
import tempfile
from unittest import TestCase
from unittest.mock import patch

from power_dialer.call_metrics.call_metrics_handler import CallMetricsHandler
from power_dialer.call_metrics.call_record import CallRecord

DB_NAME = os.path.join(tempfile.gettempdir(), 'powerdialer_test.db')


class TestCallMetricsHandler(TestCase):

    @patch('power_dialer.call_metrics.call_metrics_handler.CallMetricsRelationalStorage')
    def test_call_started(self, storage):
        handler = CallMetricsHandler(DB_NAME, synchronous=True)
        handler.call_started('test_id', '(212) 555-0100')
        assert 'test_id' in handler._volatile
        record: CallRecord = handler._volatile['test_id']
        assert record.agent_id == 'test_id', ('test_id', record.agent_id)
        assert record.number == '(212) 555-0100', ('(212) 555-0100', record.number)
        assert record.ended is None, (None, record.ended)
        handler.shutdown()

    @patch('power_dialer.call_metrics.call_metrics_handler.CallMetricsRelationalStorage')
    def test_call_ended(self, storage):
        handler = CallMetricsHandler(DB_NAME, synchronous=True)
        handler.call_started('test_id', '(212) 555-0100')
        handler.call_ended('test_id', '(212) 555-0100')
        assert 'test_id' not in handler._volatile
        assert handler._storage_queue.qsize() == 1
        record = handler._storage_queue.get()
        assert record.agent_id == 'test_id'
        assert record.number == '(212) 555-0100'
