# -*- coding: utf-8 -*-
import time
import random
from unittest import TestCase
from unittest.mock import patch, MagicMock

from power_dialer.number_manager import NumberManager
from power_dialer.services import get_lead_phone_number_to_dial


class TestNumberManager(TestCase):
    def test_normalize_number(self):
        """
        Test Removal of our number formatting
        """
        client = NumberManager(10, synchronous=True)
        n = '(212) 555-0100'
        result = client.normalize_number(n)
        assert result == '2125550100', ('2125550100', result)

    def test_normalize_number_normalized(self):
        """
        Test normalizing a normalized numbeer
        """
        client = NumberManager(10, synchronous=True)
        n = '2125550100'
        result = client.normalize_number(n)
        assert result == '2125550100', ('2125550100', result)

    def test_expire_entries(self):
        """
        Test cache expiry
        """
        # 5 second time out
        client = NumberManager(5, synchronous=True)
        numbers = (get_lead_phone_number_to_dial() for _ in range(100))
        now = time.time()
        # Sync the cache to our test
        client.last_expiry_time = now
        # generate times from -10 seconds ago to now
        times = (now + random.randint(-10, 0) for _ in range(100))
        cache = dict(zip(numbers, times))
        client.warm_cache(cache)
        times = [now - v for v in client.calls.values()]
        assert all(t <= 5 for t in times), (times, )
        # expired = set(k for k, v in cache.items() if now - v > 5)
        live = set(client.normalize_number(k) for k, v in cache.items() if now - v <= 5)
        calls = set(client.calls.keys())
        assert live.intersection(calls) == calls, (live, calls)

    def test_warm_cache(self):
        """
        Test cache warming
        """
        # 5 second time out
        client = NumberManager(5, synchronous=True)
        numbers = (get_lead_phone_number_to_dial() for _ in range(100))
        now = time.time()
        # Sync the cache to our test
        client.last_expiry_time = now
        # generate times from -10 seconds ago to now
        times = (now + random.randint(-10, 0) for _ in range(100))
        cache = dict(zip(numbers, times))
        client.warm_cache(cache)
        times = [now - v for v in client.calls.values()]
        assert all(t <= 5 for t in times), (times, )

    @patch('power_dialer.number_manager.time')
    def test_number_listener(self, mock_time):
        """
        Test the listener
        """
        mock_time.time = MagicMock()
        mock_time.time.return_value = 5

        client = NumberManager(5, synchronous=True)
        client.CALL_QUEUE.put('(212) 555-0100')
        client.CALL_QUEUE.put(None)
        client.number_listener()
        assert '2125550100' in client.calls
        assert client.calls['2125550100'] == 5

    @patch('power_dialer.number_manager.get_lead_phone_number_to_dial')
    def test_get_number(self, mock_number_maker):
        mock_number_maker.return_value = '(212) 555-0100'
        client = NumberManager(5, synchronous=True)
        number = client.get_number()
        assert number == '(212) 555-0100'

    @patch('power_dialer.number_manager.get_lead_phone_number_to_dial')
    def test_get_number_dupe(self, mock_number_maker):
        mock_number_maker.side_effect = '(212) 555-0100', '(212) 555-0100', '(212) 555-0101'
        client = NumberManager(5, synchronous=True)
        number = client.get_number()
        assert number == '(212) 555-0100'
        client.CALL_QUEUE.put(None)
        client.number_listener()
        number = client.get_number()
        # The duplicate should be ignored, and we should get the next unique number
        assert number == '(212) 555-0101', ('(212) 555-0101', number)
