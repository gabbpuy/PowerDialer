import datetime
from unittest import TestCase
from unittest.mock import patch, MagicMock

from power_dialer.call_metrics.call_record import CallRecord
from power_dialer.call_metrics.call_metrics_relational_storage import CallMetricsRelationalStorage, INSERT_QUERY


class TestCallMetricsRelationalStorage(TestCase):

    @patch('power_dialer.call_metrics.call_metrics_relational_storage.sqlite3')
    def test_save_call_records(self, mocksql):
        mocksql.connect().cursor().execute().return_value = True
        test_queue = MagicMock()
        now = datetime.datetime.utcnow()
        then = now + datetime.timedelta(seconds=60)
        record = CallRecord('test_id', '(212) 555-0100', now, then)
        test_queue.get().side_effect = (record,)
        storage = CallMetricsRelationalStorage(test_queue, 'foo.db')
        connection = MagicMock()
        connection.cursor = MagicMock()
        storage.save_call_record(connection, record)

        connection.cursor().execute.assert_called_once_with(
            INSERT_QUERY,
            ('test_id', '(212) 555-0100', now.timestamp(), then.timestamp())
        )
