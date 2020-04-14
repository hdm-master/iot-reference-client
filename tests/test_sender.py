import unittest
from unittest.mock import Mock

from iot_assets.iot_client import IoTClientDetails
from iot_assets.sender import Sender, SenderDetails


class SenderTests(unittest.TestCase):
    def setUp(self):
        self.sender_details = SenderDetails("senderTypeMock", "senderNameMock", "senderSoftwareVersionMock",
                                            "orgIdMock",
                                            "siteIdMock",
                                            "clientIdMock", "telemetryTopicMock")

        self.iot_client_details = IoTClientDetails("mqttEndpointMock", 123, "deviceCertPathMock",
                                                   "devicePrivateKeyPathMock",
                                                   "amazonRootCaPathMock", "thingNameMock")
        self.sender = Sender(self.sender_details, self.iot_client_details)

    def test_init(self):
        self.assertIsInstance(self.sender, Sender)

    def test_publish_telemetry(self):
        sender = Sender(self.sender_details, self.iot_client_details)
        sender.iot_client = Mock()
        sender.iot_client.connflag = True
        sender.state = {"sendTelemetryData": True}

        err = False
        try:
            sender.publish_telemetry("mockMessage")
        except Exception:
            err = True

        self.assertEqual(err, False)
        sender.iot_client.publish.assert_called_with(f'{self.sender_details.telemetry_topic}/'
                                                     f'{self.sender_details.org_id}/{self.sender_details.client_id}',
                                                     "mockMessage")
