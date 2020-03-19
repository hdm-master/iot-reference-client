import unittest

from iot_assets.asset import Asset, AssetDetails
from iot_assets.sender import Sender, SenderDetails


class DeviceTests(unittest.TestCase):

    def test_init(self):
        sender_details = SenderDetails('endpointMock', 123, 'deviceCertPathMock', 'devicePrivateKeyMock',
                                       'amazonRootMock', 'senderTypeMock', 'senderNameMock',
                                       'senderSoftwareVersionMock', 'topicMock', 'orgIdMock', 'siteIdMock',
                                       'thingNameMock')

        sender = Sender(sender_details)

        self.assertIsInstance(sender, Sender)

        asset_details = AssetDetails('machineIdMock', 'assetHardwareVersionDemo', 'assetmanufacturernameDemo',
                                     'assetnameDemo',
                                     'assetserialDemo', 'assetsoftwareversionDemo', 'BoxPacker', 'Speedmaster')

        asset = Asset(asset_details, sender)
        self.assertIsInstance(asset, Asset)


if __name__ == '__main__':
    unittest.main()
