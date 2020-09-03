import logging
from dataclasses import dataclass, field
from typing import Dict

from .iot_client import IoTClient, IoTClientDetails
from .shadow_callback_handler import ShadowCallbackHandler
from .telemetry_callback_handler import TelemetryCallbackHandler

logger = logging.getLogger(__name__)


@dataclass
class SenderDetails:
    sendertype: str
    sendername: str
    sendersoftwareversion: str
    org_id: str
    site_id: str
    client_id: str
    telemetry_topic: str
    state: Dict = field(default_factory=lambda: {})


class Sender:
    """ Sender
    This class handles the connectivity to the IoT Client and the ShadowCallbackHandler
    It represents your IoT gateway
    """

    def __init__(self, sender_options: SenderDetails, iot_client_options: IoTClientDetails,
                 with_telemetry_response: bool = False):
        self.iot_client = IoTClient(iot_client_options)
        self.org_id = sender_options.org_id
        self.site_id = sender_options.site_id
        self.client_id = sender_options.client_id
        self.sendertype = sender_options.sendertype
        self.sendername = sender_options.sendername
        self.sendersoftwareversion = sender_options.sendersoftwareversion
        self.telemetry_topic = sender_options.telemetry_topic
        self.state = sender_options.state
        self.shadow_callback_handler = ShadowCallbackHandler(self.iot_client, self)
        if with_telemetry_response:
            self.telemetry_callback_handler = TelemetryCallbackHandler(self.iot_client, self)

    def connect(self, ssl_tunnel=False):
        """Setup the mqtt connection to use standard port"""
        self.iot_client.connect(ssl_tunnel)

    def publish_telemetry(self, message: str):
        """publish message to dedicated telemetry topic"""
        if self.iot_client.connflag:
            if self.state.get('sendTelemetryData'):
                self.iot_client.publish(f'{self.telemetry_topic}/{self.org_id}/{self.client_id}', message)
            else:
                logger.warning(f'state object sendTelemetryData is: {self.state.get("sendTelemetryData")}')
        else:
            logger.warning("sender not connected")

    def disconnect(self):
        """Disconnects the mqtt iot_assets"""
        self.iot_client.disconnect()

    def get_state(self):
        """The internal state of the device.

        This function is used by the shadow update handler to for
        reporting the current state
        """
        return self.state

    def set_state(self, new_state):
        """Sets a new internal state

        This function gets called by the shadow update handler when a desired
        state update is received
        """
        self.state = new_state
