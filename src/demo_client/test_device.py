import json
import unittest
from unittest.mock import Mock

from demo_client.device import Device
from demo_client.iot_client import IoTClient
from demo_client.shadow_callback_handler import ShadowCallbackHandler


class Message:
    def __init__(self, topic, payload):
        self.topic = topic
        self.payload = payload


class MqttDevice(unittest.TestCase):

    def setUp(self):
        self.subject = Device()
        self.subject.thing_name = "mock"
        self.subject.provision = Mock()
        self.subject.publish_telemetry = Mock()

        connection_details = {
            'endpoint': 'endpointMock',
            'standard_port': 'standard_portMock',
            'clientId': 'clientIdMock',
            'device_cert_path': 'device_cert_path_Mock',
            'device_private_key_path': 'device_private_key_path_Mock',
            'amazon_root_ca_path': 'amazon_root_ca_path_Mock'
        }
        iot_client = IoTClient(self.subject, connection_details)
        self.subject.iot_client = iot_client
        self.subject.shadow_callback_handler = ShadowCallbackHandler(iot_client, self.subject)
        self.get_accepted_topic = f"$aws/things/mock/shadow/get/accepted"
        self.update_accepted_topic = f"$aws/things/mock/shadow/update/accepted"
        self.update_topic = f"$aws/things/mock/shadow/update"

    def test_desired_attribute_change_get_accepted_topic(self):
        payload = json.dumps({"state": {"desired": {"color": "red"}}})

        self.subject.iot_client.on_message(
            None,
            None,
            Message(topic=self.get_accepted_topic, payload=payload)
        )

        res = self.subject.get_state()

        self.assertEqual(res['color'], 'red')

    def test_desired_attribute_change_update_accepted_topic(self):
        payload = json.dumps({"state": {"desired": {"color": "blue"}}})

        self.subject.iot_client.on_message(
            None,
            None,
            Message(topic=self.update_accepted_topic, payload=payload))

        self.assertEqual(self.subject.get_state()['color'], 'blue')

    def test_state_change_triggers_publish(self):

        payload = json.dumps({"state": {"desired": {"color": "blue"}}})
        expected = json.dumps({"state": {"reported": {"color": "blue"}}})

        self.subject.iot_client.publish = Mock()

        self.subject.iot_client.on_message(
            None,
            None,
            Message(topic=self.update_accepted_topic, payload=payload))

        self.subject.iot_client.publish.assert_called_with(self.update_topic, expected)


if __name__ == '__main__':
    unittest.main()
