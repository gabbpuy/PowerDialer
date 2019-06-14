This project uses a small FSM to identify abnormal conditions in the call flow.
Since the dialer is essentially idempotent it can't really do anything except attempt 
to adjust the current state of things.

These things are logged to a log file which if run from lambda would be monitored by CloudWatch to then set up 
alarms.

The back-end infrastructure is implemented by a group of Singletons pretending to be cloud services.

`python setup.py test` 
will execute the unit tests

```
test_agent_storage_constructor (test.test_agentStorageHandler.TestAgentStorageHandler) ... ok
test_agent_storage_get (test.test_agentStorageHandler.TestAgentStorageHandler) ... ok
test_agent_storage_get_missing (test.test_agentStorageHandler.TestAgentStorageHandler) ... ok
test_agent_storage_get_missing_from_empty (test.test_agentStorageHandler.TestAgentStorageHandler) ... ok
test_agent_storage_set (test.test_agentStorageHandler.TestAgentStorageHandler) ... ok
test_call_ended (test.test_callMetricsHandler.TestCallMetricsHandler) ... ok
test_call_started (test.test_callMetricsHandler.TestCallMetricsHandler) ... ok
test_save_call_records (test.test_callMetricsRelationalStorage.TestCallMetricsRelationalStorage) ... ok
test_bad_transition (test.test_DialerStateMachine.TestStateMachine) ... ok
test_constructor (test.test_DialerStateMachine.TestStateMachine) ... ok
test_constructor_with_initial_state (test.test_DialerStateMachine.TestStateMachine) ... ok
test_set_state (test.test_DialerStateMachine.TestStateMachine) ... ok
test_set_state_initial_state (test.test_DialerStateMachine.TestStateMachine) ... ok
test_set_state_post_set_state (test.test_DialerStateMachine.TestStateMachine) ... ok
test_transition (test.test_DialerStateMachine.TestStateMachine) ... ok
test_expire_entries (test.test_numberManager.TestNumberManager) ... ok
test_get_number (test.test_numberManager.TestNumberManager) ... ok
test_get_number_dupe (test.test_numberManager.TestNumberManager) ... ok
test_normalize_number (test.test_numberManager.TestNumberManager) ... ok
test_normalize_number_normalized (test.test_numberManager.TestNumberManager) ... ok
test_number_listener (test.test_numberManager.TestNumberManager) ... ok
test_warm_cache (test.test_numberManager.TestNumberManager) ... ok
test_on_agent_login (test.test_powerDialer.TestPowerDialer) ... ok
test_on_agent_logout (test.test_powerDialer.TestPowerDialer) ... ok
test_on_call_ended (test.test_powerDialer.TestPowerDialer) ... ok
test_on_call_failed (test.test_powerDialer.TestPowerDialer) ... ok
test_on_call_failed_when_busy (test.test_powerDialer.TestPowerDialer) ... ok
test_on_call_started (test.test_powerDialer.TestPowerDialer) ... ok
test_generateCOC (test.test__generatePhoneNumber.Test_generateCentralOfficeCode) ... ok
test_generate_line_number (test.test__generatePhoneNumber.Test_generateLineNumber) ... ok
test_generateNPA (test.test__generatePhoneNumber.Test_generateNPA) ... ok
----------------------------------------------------------------------
Ran 31 tests in 0.011s

OK

```

If you `pip install coverage` you can get coverage reports with

`coverage run --source power_dialer setup.py test`

To print a quick command line report, maximize your command prompt and type:

`coverage report -m`

```
Name                                                           Stmts   Miss  Cover   Missing
--------------------------------------------------------------------------------------------
power_dialer\__init__.py                                           0      0   100%
power_dialer\agent_storage\__init__.py                             0      0   100%
power_dialer\agent_storage\agent_storage.py                        5      0   100%
power_dialer\agent_storage\agent_storage_handler.py               14      0   100%
power_dialer\call_metrics\__init__.py                              0      0   100%
power_dialer\call_metrics\call_metrics.py                          6      0   100%
power_dialer\call_metrics\call_metrics_handler.py                 39      4    90%   48-50, 63
power_dialer\call_metrics\call_metrics_relational_storage.py      38      3    92%   36-38
power_dialer\call_metrics\call_record.py                           7      0   100%
power_dialer\dialer_state_machine.py                              32      0   100%
power_dialer\number_manager.py                                    62     11    82%   35-38, 49-51, 63-66, 73
power_dialer\power_dialer.py                                      77      9    88%   55-57, 66, 75-79, 86-88, 104
power_dialer\power_dialer_interface.py                            17      5    71%   11, 15, 19, 23, 27
power_dialer\services.py                                          25      0   100%
power_dialer\singleton.py                                          8      0   100%
--------------------------------------------------------------------------------------------
TOTAL                                                            330     32    90%

```

You can exercise the entire suite and see sample call metrics report by running `dialer-sim.py` 

This will spawn a number of threads that create `PowerDialer` instances as if they were being spawned by AWS Lambda

Two logs are created; `dialer.log` which is the output of `PowerDialer` and `agents.log` that logs info from the agent
"clients."
