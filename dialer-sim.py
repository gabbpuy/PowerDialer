#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import sys
import threading
import time
from dataclasses import dataclass
import logging
import os
import random
import sqlite3
import tempfile
from typing import List

from power_dialer.power_dialer import PowerDialer
from power_dialer.call_metrics.call_metrics import CallMetrics
from power_dialer.number_manager import NumberManager

DB_NAME = os.path.join(tempfile.gettempdir(), 'powerdialer.db')


@dataclass
class ReportRecord:
    agent_id: str
    number_of_calls: int
    average_call_time: float

    def __repr__(self):
        return f'Agent: {self.agent_id:10s} # Calls: {self.number_of_calls:-3d}, Avg Call Time: {self.average_call_time:5.2f}s'


def report_row_factory(cursor, row: tuple) -> ReportRecord:
    """
    Return a Report Record
    :param cursor: DB cursor
    :param row: db row
    :return: `ReportRecord` object
    """
    return ReportRecord(*row)


def get_command_line_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--num-agents', '-n', type=int, default=50, help='number of agents to run')
    parser.add_argument('--call-fail', '-f', type=int, default=50, help='chance of call fail 0-100')
    parser.add_argument('--call-length', '-l', type=int, default=10, help='average call length in seconds')
    parser.add_argument('--time-to-run', '-t', type=int, default=300, help='time to run sim')
    parser.add_argument('--clean-start', '-c', action='store_true', default=False, help='wipe db first')
    return parser.parse_args()


class Agent:
    def __init__(self, agent_id, options):
        self.agent_id = agent_id
        self.failure_rate = options.call_fail
        self.call_length = options.call_length
        self.running = True
        self.logger = logging.getLogger(f'agent.{agent_id}')

    def login(self) -> List[str]:
        dialer = PowerDialer(self.agent_id)
        dialer.on_agent_login()
        return dialer.numbers

    def logout(self):
        dialer = PowerDialer(self.agent_id)
        dialer.on_agent_logout()

    def dial_numbers(self, numbers: List[str]):
        good = []
        fail = []
        for n in numbers:
            if random.randint(1, 100) <= self.failure_rate:
                fail.append(n)
            else:
                good.append(n)
        return good, fail

    def fail_numbers(self, failed: List[str]) -> List[str]:
        numbers = []
        for n in failed:
            dialer = PowerDialer(self.agent_id)
            dialer.on_call_failed(n)
            numbers.extend(dialer.numbers)
        return numbers

    def good_calls(self, good: List[str]) -> str:
        good_number = good.pop(0)
        dialer = PowerDialer(self.agent_id)
        dialer.on_call_started(good_number)
        # Secondary calls fail
        for n in good:
            dialer = PowerDialer(self.agent_id)
            dialer.on_call_failed(n)
        return good_number

    def end_call(self, number):
        dialer = PowerDialer(self.agent_id)
        dialer.on_call_ended(number)
        return dialer.numbers

    def run_one_agent(self):
        total = 0
        total_failed = 0
        logger = self.logger
        logger.info('Logging in')
        numbers = self.login()
        successful, failed = self.dial_numbers(numbers)
        total += len(numbers)

        while self.running:
            total_failed += len(failed)
            new_calls = self.fail_numbers(failed)
            total += len(new_calls)
            if successful:
                logger.info('Moving onto call')
                self.fail_numbers(new_calls)
                total_failed += len(new_calls)
                good_number = self.good_calls(successful)
                ttl = self.call_length * random.uniform(.9, 1.25)
                logger.info('Call length to be %s s', ttl)
                time.sleep(ttl)
                new_calls = self.end_call(good_number)
                total += len(new_calls)
            successful, failed = self.dial_numbers(new_calls)
        logger.info(f'Total calls: {total}. Failure Rate: {total_failed / total:.2f}')
        self.logout()
        logger.info('Done.')

    def stop(self):
        self.logger.info('Setting running to false.')
        self.running = False


def shutdown():
    print('Shutting down.')
    CallMetrics.shutdown()
    client = NumberManager()
    client.shutdown()
    print('Done.')


def clean_start():
    connection = sqlite3.connect(DB_NAME)
    with connection:
        cursor = connection.cursor()
        cursor.execute('DELETE FROM CALL_RECORDS')


def report():
    connection = sqlite3.connect(DB_NAME)
    connection.row_factory = report_row_factory
    cursor = connection.cursor()
    cursor.execute('SELECT agent_id, COUNT(agent_id), AVG(call_end - call_start) FROM CALL_RECORDS GROUP BY agent_id')
    for row in cursor.fetchall():
        print(row)


if __name__ == '__main__':
    logger = logging.getLogger('agent')
    logger.setLevel(logging.DEBUG)
    logger.propagate = False
    format = "%(name)-25s | %(levelname)-10s %(message)s"
    handler = logging.StreamHandler(open('agents.log', 'wt', encoding='utf-8'))
    handler.setFormatter(logging.Formatter(format))
    logger.addHandler(handler)

    logger = logging.getLogger('power_dialer')
    logger.setLevel(logging.DEBUG)
    logger.propagate = False
    handler = logging.StreamHandler(open('dialer.log', 'wt', encoding='utf-8'))
    handler.setFormatter(logging.Formatter(format))
    logger.addHandler(handler)

    options = get_command_line_arguments()
    if options.clean_start:
        clean_start()

    print('Starting {} agents for {} seconds'.format(options.num_agents, options.time_to_run))
    try:
        agents = []
        for i in range(1, options.num_agents + 1):
            agent_id = 'agent_{:04d}'.format(i)
            agent = Agent(agent_id, options)
            t = threading.Thread(target=agent.run_one_agent, name=agent_id)
            t.start()
            agents.append(agent)

        time_to_end = time.time() + options.time_to_run
        while time.time() < time_to_end:
            time.sleep(1)
            print('Time Remaining: {:4d} s\r'.format(int(time_to_end - time.time())), end='')
            sys.stdout.flush()
        for agent in agents:
            agent.stop()
        report()
    finally:
        shutdown()
    exit(0)
