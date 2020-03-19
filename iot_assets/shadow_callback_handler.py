"""The Device Shadow is currently not in use"""

import json
import logging
from time import sleep

logger = logging.getLogger(__name__)


class ShadowCallbackHandler:
    """
    CURRENTLY, NOT USED

    Handles all state updates between the device and iot core

    The handler keeps a reference to the iot iot_assets and the device.
    Whenever a message is received on a relevant topic for the device,
    the devices state is updated. Each update to the state of the device
    is published to the iot core via the iot iot_assets
    """

    def __init__(self, iot_client, device):
        self.iot_client = iot_client
        self.device = device
        self.device.set_state = self.set_state_wrapper(self.device.set_state)
        self.iot_client.on_connect = self.on_connect_wrapper(
            self.iot_client.on_connect)
        self.iot_client.on_message = self.on_message_wrapper(
            self.iot_client.on_message)

    def set_state_wrapper(self, func):
        """ a wrapper that catches state updates on the device"""
        logger.debug('set_state_wrapper invoked')

        def wrapper(new_state):
            logger.debug('set_state wrapper function invoked')
            func(new_state)
            self.publish_new_state(self.device.get_state())

        return wrapper

    def on_connect_wrapper(self, func):
        """A wrapper that subscribes to the state update topics on connect"""
        logger.debug('on_connect_wrapper invoked')

        def wrapper(client, userdata, flags, result_code):
            logger.debug('on_connect wrapper function invoked')
            func(client, userdata, flags, result_code)
            self.subscribe_to_device_shadow_topics()
            sleep(3)
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
            f"$aws/things/{self.get_thing_name()}/shadow/get/accepted",
            f"$aws/things/{self.get_thing_name()}/shadow/get/rejected"
        ]

        for topic in shadow_update_topics:
            self.iot_client.subscribe(topic)

    def get_thing_name(self):
        """ proxy to the devices get_thing_name function """

        return self.device.get_thing_name()

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
            self.device.set_state(
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
