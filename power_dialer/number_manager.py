# -*- coding: utf-8 -*-
import logging
from queue import Queue, Empty
from threading import Thread, Lock
import time

from .services import get_lead_phone_number_to_dial
from .singleton import Singleton

logger = logging.getLogger('power_dialer.number_manager')


class NumberManager(metaclass=Singleton):
    """
    Try to minimise calling people too often, don't call anyone who has been called within x
    In this case, we're going to use seconds and not days...

    We also want to avoid hammering failed numbers so we're going to keep a volatile cache
    """
    # Emulates an SQS FIFO or SNS Topic
    CALL_QUEUE = Queue()

    def __init__(self, call_exclude_time: int = 60, synchronous: bool = False):
        self.call_exclude_time = call_exclude_time
        self.calls = {}
        # Used to swap the call cache
        self.call_lock = Lock()
        # Testing a set is faster than a range check or checking string.digits
        self.number_digits = set(str(c) for c in range(10))
        # If we haven't cleaned up for a minute, clean up
        self.last_expiry_time = time.time()
        self.running = True
        self.number_thread = None
        if not synchronous:
            t = Thread(target=self.number_listener)
            t.daemon = False
            t.start()
            self.number_thread = t

    def normalize_number(self, number: str) -> str:
        """
        Strip out the punctuation from the numbers
        :param number: A phone number
        :return: A normalized number containing only digits
        """
        return ''.join(c for c in number if c in self.number_digits)

    def shutdown(self):
        logger.info('Shutting down Number Manager')
        self.running = False
        self.CALL_QUEUE.put(None)

    def number_listener(self):
        """
        Emulates a SNS listener. We listen for incoming number
        """
        while self.running:
            try:
                number = NumberManager.CALL_QUEUE.get(timeout=1.0)
                if number is None:
                    logger.info('Exiting number_listener.')
                    return
            except Empty:
                # This would normally be a parallel task, but this is fine for our pretend case
                self.expire_entries()
                continue
            number = self.normalize_number(number)
            with self.call_lock:
                self.calls[number] = time.time()

            # Clean up if we haven't for a while
            if time.time() - self.last_expiry_time > 60:
                self.expire_entries()

    def expire_entries(self):
        """
        Clear out old entries
        """
        expiry = time.time() - self.call_exclude_time
        new_numbers = {number: timestamp for number, timestamp in self.calls.items() if timestamp > expiry}
        with self.call_lock:
            self.calls = new_numbers
            self.last_expiry_time = time.time()

    def warm_cache(self, numbers: dict):
        """
        Update the call list

        :param numbers: Dictionary with numbers as keys and call times as timestamps
        """
        with self.call_lock:
            for k, v in numbers.items():
                self.calls[self.normalize_number(k)] = v

        self.expire_entries()

    def get_number(self) -> str:
        """
        Get a new number that isn't in the recent calls cache
        :return: Phone number
        """
        success = False
        with self.call_lock:
            while not success:
                number = get_lead_phone_number_to_dial()
                success = self.normalize_number(number) not in self.calls
        self.CALL_QUEUE.put(number)
        return number
