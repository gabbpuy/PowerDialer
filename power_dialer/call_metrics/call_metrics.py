# -*- coding: utf-8 -*-
from power_dialer.call_metrics.call_metrics_handler import CallMetricsHandler

CallMetrics = None


def _create_call_metrics():
    global CallMetrics
    if not CallMetrics:
        CallMetrics = CallMetricsHandler()


_create_call_metrics()
