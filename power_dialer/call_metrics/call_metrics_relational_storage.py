# -*- coding: utf-8 -*-
import logging
from queue import Queue, Empty
import sqlite3

from .call_record import CallRecord
from power_dialer.singleton import Singleton

logger = logging.getLogger('power_dialer.call_metrics.relational_storage')

INSERT_QUERY = """INSERT INTO CALL_RECORDS
                  VALUES(?, ?, ?, ?)
               """


class CallMetricsRelationalStorage(metaclass=Singleton):
    """
    Pretend interface to persistence layer
    """

    def __init__(self, storage_queue: Queue, database: str):
        logging.info('Database is %s', database)
        self.database = database
        self.queue = storage_queue
        self._create_schema()

    def save_call_records(self):
        # Can only talk on the thread the connection was made on...
        connection = sqlite3.connect(self.database)
        while True:
            try:
                record: CallRecord = self.queue.get(timeout=1.0)
                if record is None:
                    logger.info('Shutting down relational storage')
                    return
            except Empty:
                continue
            self.save_call_record(connection, record)

    @staticmethod
    def save_call_record(connection, record):
        cursor = connection.cursor()
        agent_id = record.agent_id
        number = record.number
        start = record.started.timestamp()
        ended = record.ended.timestamp()
        cursor.execute(INSERT_QUERY, (agent_id, number, start, ended))
        connection.commit()

    def _create_schema(self):
        connection = sqlite3.connect(self.database)
        cursor = connection.cursor()
        # SQL LITE has a rowid, so no need to keep an explicit autoincrement primary key
        cursor.executescript("""
        CREATE TABLE IF NOT EXISTS CALL_RECORDS(
        agent_id TEXT NOT NULL,
        called_number TEXT NOT NULL,
        call_start INTEGER NOT NULL,
        call_end INTEGER NOT NULL
        );
        CREATE INDEX IF NOT EXISTS agent_idx ON CALL_RECORDS(agent_id);
        """)

        connection.commit()
        connection.close()
