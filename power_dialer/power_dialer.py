# -*- coding: utf-8 -*-
from functools import wraps
import logging

from power_dialer.agent_storage.agent_storage import AgentStorage
from power_dialer.call_metrics.call_metrics import CallMetrics
from .power_dialer_interface import PowerDialerInterface
from .dialer_state_machine import DialerStateMachine, AGENT_TRANSITIONS, AgentState
from .number_manager import NumberManager
from .services import dial

DIAL_RATIO = 2
logger = logging.getLogger('power_dialer.power_dialer')


class PowerDialerStateMachine(DialerStateMachine):
    """
    Simple helper class
    """

    def __init__(self):
        super().__init__(AGENT_TRANSITIONS)


class PowerDialer(PowerDialerInterface):
    """
    Implementation of the Power Dialer Interface.

    The power dialer uses a happy eyes approach to keep agents utilised. It places a number of calls knowing
    calls will fail with a small chance of a call connecting with no agent available to take the call.
    """

    def __init__(self, agent_id: str, dial_ratio: int = DIAL_RATIO):
        super().__init__(agent_id)
        self._agent = None
        self._agent_state = PowerDialerStateMachine()
        self._dial_ratio = dial_ratio
        self._call_metrics = CallMetrics
        self._agent_client = AgentStorage
        self.numbers = []
        self._get_agent_status()
        self._number_client = NumberManager()

    def auto_state_save(method):
        """
        Decorator to ensure that the agent state is saved without having the boiler plate in every
        method.

        We could use this to lazy-load the state too, but we need it so let the constructor do it.
        """
        @wraps(method)
        def wrapper(self, *args, **kwargs):
            try:
                return method(self, *args, **kwargs)
            except:
                # Monitor (cloudwatch) for failures
                logger.exception('Call to %s(%s, %s) failed', method.__name__, args, kwargs)
            finally:
                self._save_agent_state()
        return wrapper

    @auto_state_save
    def on_agent_login(self):
        if not self._agent_state.transition(AgentState.idle):
            # Log this attempt, monitor (cloudwatch) for these types of issues
            logger.warning('Attempt to login when agent %s already logged in.', self.agent_id)

        for _ in range(self._dial_ratio):
            self._initiate_call()

    @auto_state_save
    def on_agent_logout(self):
        if not self._agent_state.transition(AgentState.offline):
            # This should never happen
            logger.warning('Agent attempted to logout while call active.')
            # We're in a bad spot now, but since we're offlining the agent,
            # we reset the status so the agent status is saved when we leave.
            self._agent_state = PowerDialerStateMachine()
            self._agent_state.set_state(AgentState.offline)

    @auto_state_save
    def on_call_started(self, lead_phone_number: str):
        logger.info('Call start for %s to %s', self.agent_id, lead_phone_number)
        if self._agent_state.state is not AgentState.idle:
            # Monitor (cloudwatch) to find these. They're already on the call...
            logger.warning('Agent %s started call to %s when not idle.', self.agent_id, lead_phone_number)
            # You can always transition to idle
            self._agent_state.set_state(AgentState.idle)
        self._record_call_start(lead_phone_number)
        self._agent_state.transition(AgentState.busy)

    @auto_state_save
    def on_call_failed(self, lead_phone_number: str):
        # Monitor for repeated failures to a number
        logger.info('Call failed for %s to %s', self.agent_id, lead_phone_number)
        if self._agent_state.state is AgentState.idle:
            # If the agent is not on a call, initiate another call
            self._initiate_call()

    @auto_state_save
    def on_call_ended(self, lead_phone_number: str):
        logger.info('Call ended for %s to %s', self.agent_id, lead_phone_number)
        if self._agent_state.state is not AgentState.busy:
            logger.warning('Call ended for agent, but agent was not on a call.')
            # The agent state is now invalid, but can only be 'idle' or 'offline', we can transition to 'idle'

        self._agent_state.transition(AgentState.idle)
        self._record_call_end(lead_phone_number)
        # There is a small window here if a call is initiated and completed successfully before DIAL_RATIO - 1 calls
        # have failed, but we are optimising utilisation. It's unlikely that other calls are inflight, but if so
        # they will fail and be retried.
        for _ in range(self._dial_ratio):
            self._initiate_call()

    def _record_call_start(self, phone_number: str):
        self._call_metrics.call_started(self.agent_id, phone_number)

    def _record_call_end(self, phone_number: str):
        self._call_metrics.call_ended(self.agent_id, phone_number)

    def _initiate_call(self):
        """
        Get a lead an initiate a call
        """
        number = self._number_client.get_number()
        # Store the numbers so the wrapper can find out what numbers were generated.
        self.numbers.append(number)
        dial(self.agent_id, number)

    def _get_agent_status(self):
        """
        Load the current agent status
        """
        state = self._agent_client[self.agent_id]
        self._agent_state.set_state(state)

    def _save_agent_state(self):
        """
        Save the state of the agent
        """
        self._agent_client[self.agent_id] = self._agent_state.state
