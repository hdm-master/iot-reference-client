from __future__ import annotations

import json

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .sender import Sender  # cyclic import problem
from .iot_client import IoTClient

logger = logging.getLogger(__name__)


class ShadowCallbackHandler:
    """
    Handles all state updates between the device and iot core

    The handler keeps a reference to the iot iot_assets and the device.
    Whenever a message is received on a relevant topic for the device,
    the devices state is updated. Each update to the state of the device
    is published to the iot core via the iot iot_assets
    """

    def __init__(self, iot_client: IoTClient, sender: Sender):
        self.iot_client = iot_client
        self.sender = sender
        self.sender.set_state = self.set_state_wrapper(self.sender.set_state)
        self.iot_client.on_connect = self.on_connect_wrapper(
            self.iot_client.on_connect)
        self.iot_client.on_message = self.on_message_wrapper(
            self.iot_client.on_message)
        self.iot_client.on_subscribe = self.on_subscribe_wrapper(
            self.iot_client.on_subscribe)

    def set_state_wrapper(self, func):
        """ a wrapper that catches state updates on the device"""

        def wrapper(new_state):
            logger.info('set_state wrapper function invoked')
            func(new_state)
            self.publish_new_state(self.sender.get_state())

        return wrapper

    def on_connect_wrapper(self, func):
        """A wrapper that subscribes to the state update topics on connect"""

        def wrapper(client, userdata, flags, result_code):
            func(client, userdata, flags, result_code)
            if result_code == 0:
                self.subscribe_to_device_shadow_topics()

        return wrapper

    def on_subscribe_wrapper(self, func):
        """A wrapper that subscribes to the subscription updates topics on subscribe"""

        def wrapper(client, userdata, mid, granted_qos):
            func(client, userdata, mid, granted_qos)
            if self.iot_client.connflag:
                self.request_desired_state()
        return wrapper

    def on_message_wrapper(self, func):
        """A wrapper that listens for state updates for the device from iot core"""

        def wrapper(client, userdata, msg):
            func(client, userdata, msg)
            self.on_message(client, userdata, msg)

        return wrapper

    def request_desired_state(self):
        """This methods requests the current state from the iot core
        It publishes the a message to the relevant topic.
        """
        self.iot_client.publish(
            f"$aws/things/{self.get_thing_name()}/shadow/get",
            None)

    def subscribe_to_device_shadow_topics(self):
        """ This function subscribes to all releveant shadow update topics

        It will receive updates on these topics regarding desired
        state changes
        """

        shadow_update_topics = [
            f"$aws/things/{self.get_thing_name()}/shadow/update/accepted",
            f"$aws/things/{self.get_thing_name()}/shadow/update/delta",
            f"$aws/things/{self.get_thing_name()}/shadow/update/documents",
            f"$aws/things/{self.get_thing_name()}/shadow/get/accepted",
            f"$aws/things/{self.get_thing_name()}/shadow/get/rejected"
        ]

        for topic in shadow_update_topics:
            self.iot_client.subscribe(topic)

    def get_thing_name(self):
        """ proxy to the devices get_thing_name function """
        return self.sender.client_id

    def publish_new_state(self, new_state):
        """ this method publishes the new state to the relevant topic"""
        topic = f"$aws/things/{self.get_thing_name()}/shadow/update"
        update_document = {
            "state": {
                "reported": new_state,
            }
        }
        self.iot_client.publish(topic, json.dumps(update_document))

    def on_message(self, client, userdata, msg):
        """ handler for new messages

        It calls the route function get the matching callback for the message
        """
        callback = self.route(msg)
        if callback is not None:
            callback(msg.payload)

    def on_desired_stage_change(self, shadow_update_json):
        """Filter and update of the device state

        This function checks the contents of the message for a new desired
        state and updates the devices state with the new desired state.
        It only supports full state updates, not delta updates
        """

        shadow_update_doc = json.loads(shadow_update_json)
        if "desired" in shadow_update_doc.get('state'):
            self.sender.set_state(
                shadow_update_doc.get("state").get("desired")
            )

    def route(self, msg):
        """Filters the message for shadow update topic messages"""

        shadow_update_topics = [
            f"$aws/things/{self.get_thing_name()}/shadow/get/accepted",
            f"$aws/things/{self.get_thing_name()}/shadow/update/accepted"
        ]
        if msg.topic in shadow_update_topics:
            return self.on_desired_stage_change

        return None
