from __future__ import annotations
import logging
import json
from typing import TYPE_CHECKING
import os
if TYPE_CHECKING:
    from .sender import Sender  # cyclic import problem
from .iot_client import IoTClient

logger = logging.getLogger(__name__)


class TelemetryCallbackHandler:
    """
    Handles Telemetry Response between the device and iot core
    All logic regarding the telemetry response and the messages should be handled here
    """

    def __init__(self, iot_client: IoTClient, sender: Sender):
        self.iot_client = iot_client
        self.stage = os.environ['stage']
        self.sender = sender
        self.telemetry_rejected_topic = f"{self.stage}/telemetryData/{self.get_thing_name()}/rejected"
        self.iot_client.on_message = self.on_message_wrapper(
            self.iot_client.on_message)
        self.iot_client.on_connect = self.on_connect_wrapper(
            self.iot_client.on_connect)

    def on_connect_wrapper(self, func):
        """A wrapper that subscribes to connect event"""
        logger.info('on_connect_wrapper invoked')

        def wrapper(client, userdata, flags, result_code):
            func(client, userdata, flags, result_code)
            if result_code == 0:
                self.subscribe_to_telemetry_topics()

        return wrapper

    def on_message_wrapper(self, func):
        """A wrapper that listens for messages for the device from iot core"""
        def wrapper(client, userdata, msg):
            func(client, userdata, msg)
            self.on_message(client, userdata, msg)

        return wrapper

    def on_message(self, client, userdata, msg):
        """ handler for new messages """
        if msg.topic == self.telemetry_rejected_topic:
            m = json.loads(msg.payload)
            logger.info("Message got rejected")
            logger.info(m)

    def subscribe_to_telemetry_topics(self):
        """ This function subscribes to all telemetry response topics """
        self.iot_client.subscribe(self.telemetry_rejected_topic)

    def get_thing_name(self):
        """ proxy to the devices get_thing_name function """
        return self.sender.client_id