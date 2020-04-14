import json
import unittest
from dataclasses import dataclass
from unittest.mock import Mock

from iot_assets.iot_client import IoTClientDetails
from iot_assets.sender import Sender, SenderDetails


@dataclass
class Message:
    topic: str
    payload: str


class TestShadowCallbackHandler(unittest.TestCase):

    def setUp(self):
        self.sender_details = SenderDetails("senderTypeMock", "senderNameMock", "senderSoftwareVersionMock",
                                            "orgIdMock",
                                            "siteIdMock",
                                            "clientIdMock", "telemetryTopicMock")

        self.iot_client_details = IoTClientDetails("mqttEndpointMock", 123, "deviceCertPathMock",
                                                   "devicePrivateKeyPathMock",
                                                   "amazonRootCaPathMock", "thingNameMock")

        self.sender = Sender(self.sender_details, self.iot_client_details)

        self.sender.iot_client.publish_telemetry = Mock()
        self.sender.iot_client.publish = Mock()

        self.get_accepted_topic = f"$aws/things/{self.sender.client_id}/shadow/get/accepted"
        self.update_accepted_topic = f"$aws/things/{self.sender.client_id}/shadow/update/accepted"
        self.update_topic = f"$aws/things/{self.sender.client_id}/shadow/update"

    def test_desired_attribute_change_get_accepted_topic(self):
        payload = json.dumps({"state": {"desired": {"foo": "bar"}}})

        self.sender.iot_client.on_message(
            None,
            None,
            Message(topic=self.get_accepted_topic, payload=payload)
        )

        self.assertEqual(self.sender.get_state()['foo'], 'bar')

    def test_desired_attribute_change_update_accepted_topic(self):
        payload = json.dumps({"state": {"desired": {"foo": "baz"}}})

        self.sender.iot_client.on_message(
            None,
            None,
            Message(topic=self.update_accepted_topic, payload=payload))

        self.assertEqual(self.sender.get_state()['foo'], 'baz')

    def test_state_change_triggers_publish(self):
        payload = json.dumps({"state": {"desired": {"foo": "bar"}}})
        expected = json.dumps({"state": {"reported": {"foo": "bar"}}})

        self.sender.iot_client.on_message(
            None,
            None,
            Message(topic=self.update_accepted_topic, payload=payload))

        self.sender.iot_client.publish.assert_called_with(self.update_topic, expected)
