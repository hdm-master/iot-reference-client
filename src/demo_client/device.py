""" Reference Client Implementation HDM IoT Platform

This is a reference implementation of a python demo_client for the IoT Platform
It supports publishing of telemetry data and syncing of shadow states.

Written by Jörg Sädtler
"""

import json
from time import sleep
from util.connectionHelper import connection_helper_factory, IoTConnectionException
from .iot_client import IoTClient
from .shadow_callback_handler import ShadowCallbackHandler
from .iot_event import IoTEvent
from util.log import get_logger

logger = get_logger(__name__)


class Device:
    """Represents a device

    The device is responsible for instantiating the IoT Client. The
    Device holds the state and has a thing name.

    For the shadow update handler to work, it needs a get_state() and
    set_state() function
    """

    def __init__(self):
        self.state = {}
        self.telemetry_topic = None  # will be overwritten during provisioning
        self.org_id = None  # will be overwritten during provisioning
        self.connection_details = {}
        self.thing_name = None  # will be overwritten during provisioning
        self.iot_client = None
        self.shadow_callback_handler = None

    def provision(self):
        """Call this method to provision the device with the iot system"""
        try:
            con_helper = connection_helper_factory()
            response = con_helper.establish_connection()
            self.thing_name = response['clientId']
            self.org_id = response['orgId']
            telemetry_basic_ingest = response['provisioning']['telemetryTopic']
            self.telemetry_topic = f'{telemetry_basic_ingest}/{self.org_id}/{self.thing_name}'
            logger.info(self.telemetry_topic)
            self.connection_details.update({'clientId': response['clientId']})
            self.connection_details.update({'device_cert_path': response['device_cert_path']})
            self.connection_details.update({'device_private_key_path': response['device_private_key_path']})
            self.connection_details.update({'amazon_root_ca_path': response['amazon_root_ca_path']})
            self.connection_details.update({'endpoint': response['connectivity']['mqttEndPoint']})
            self.connection_details.update({'standard_port': response['connectivity']['mqttPort']})
        except IoTConnectionException as err:
            raise err
        except Exception as err:
            raise DeviceException(message="iot device provisioning failed", details=err)

    def connect(self):
        """Call this method to connect the device to the iot core"""
        self.provision()
        self.iot_client = IoTClient(self, self.connection_details)
        self.shadow_callback_handler = ShadowCallbackHandler(
            self.iot_client,
            self)

        self.iot_client.connect()

    def disconnect(self):
        """Call this method to disconnect the device from the iot core"""

        self.iot_client.disconnect()

    def publish_telemetry(self, message):
        """Publish a message to a mqtt topic"""

        self.iot_client.publish(self.telemetry_topic, message)

    def subscribe(self, topic):
        """Subscribe the iot demo_client to a mqtt topic"""

        self.iot_client.subscribe(topic)

    def get_thing_name(self):
        """The thing name is used as demo_client id for the mqtt connection"""

        return self.thing_name

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

    # Here are some functions that simulate real behavior
    def start_publishing(self):
        """generates some telemetry events"""

        def generate_payload():
            event = IoTEvent(
                self.get_thing_name(),
                "reference-client-test",
                "any-sub-type",
                {"foo": "bar"}
            )
            return json.dumps(event.__dict__)

        for _ in range(3):
            sleep(0.5)
            self.publish_telemetry(generate_payload())


class DeviceException(Exception):
    def __init__(self, message="IoT device failed", status_code=500, details=None):
        super().__init__(message)
        self.status_code = status_code
        self.details = details or {}
