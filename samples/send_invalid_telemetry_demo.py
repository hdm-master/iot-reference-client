""" Demo script of the reference iot_assets telemetry implementation

Run this script to simulate invalid telemetry message use case

"""
import sys

sys.path.insert(0, ".")
import json
import logging
from time import sleep
from iot_assets.asset import Asset, AssetDetails
from iot_assets.iot_client import IoTClientDetails
from iot_assets.sender import Sender, SenderDetails
from onboarding.onboarding_manager import OnboardingManager, ConnectionDetails

logging.basicConfig(format='[%(asctime)s][%(levelname)s][%(filename)s:%(lineno)d] %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


def simulate_invalid_telemetry():
    """"
    This demo does the following:
    1. Creates Onboarding Manager to handle directory and provisioning tasks
    2. Creates a sender with MQTT connection capabilities and an asset
    3. Sends a invalid message to simulate the response canal for invalid messages.
    """
    try:
        onboard_manager = OnboardingManager()
        connection_details = onboard_manager.onboard()
        sender = generate_sender(connection_details)
        sender.connect(ssl_tunnel=False)  # set to True to use port 443
        sleep(2)  # wait a few seconds after initial connection
        sender.publish_telemetry(generate_invalid_signal())
        sleep(10)
        sender.disconnect()
    except Exception as err:
        logger.error(err)
        raise err


def generate_sender(cd: ConnectionDetails) -> Sender:
    """
    Returns sender instance
    Input:
    cd : Connection Details which a provided by the onboarding manager
    Other details "strings" are demo values which should be changed accordingly
    """

    iot_client_details = IoTClientDetails(cd.mqtt_endpoint, cd.standard_port, cd.device_cert_path,
                                          cd.device_private_key_path, cd.amazon_root_ca_path, cd.client_id)

    sender_details = SenderDetails('system', 'senderNameDemo', 'sendersoftwareversionDemo', cd.org_id,
                                   cd.site_id, cd.client_id, cd.telemetry_topic)

    return Sender(sender_details, iot_client_details, True)


def generate_asset(cd: ConnectionDetails) -> Asset:
    """
    Returns asset instance
    Input:
    cd : Connection Details (machine ID) which a provided by the onboarding manager
    Other details "strings" are demo values which should be changed accordingly
    """
    asset_details = AssetDetails(cd.machine_id, 'assetHardwareVersionDemo', 'assetmanufacturernameDemo',
                                 'assetnameDemo',
                                 'assetserialDemo', 'assetsoftwareversionDemo', 'BoxPacker', 'Speedmaster',
                                 cd.site_id, 'siteNameOfDirectory')

    return Asset(asset_details)


def generate_invalid_signal() -> str:
    """Builds a invalid message"""
    invalid_message = {
        "assetid": "0a771c72-edbb-4a17-a5c9-68f472def401",
        "assetserial": "assetserialDemo",
        "assettimestamp": "2020-09-01T13:08:23.657473+00:00",
        "assettype": "BoxPacker",
        "eventtype": "This should not exits",
        "eventsubtype": "Status",
        "sendereventuuid": "374014d8-ec54-11ea-a227-f2189848ef14",
        "sendertype": "system",
        "sendertimestamp": "2020-09-01T13:08:23.657473+00:00",
        "assethardwareversion": "assetHardwareVersionDemo",
        "assetmanufacturername": "assetmanufacturernameDemo",
        "assetname": "assetnameDemo",
        "assetsoftwareversion": "assetsoftwareversionDemo",
        "assetsubtype": "Speedmaster",
        "sendername": "senderNameDemo",
        "sendersoftwareversion": "sendersoftwareversionDemo",
        "siteid": "d9648740-8513-49c5-bf14-407b286e3065",
        "sitename": "siteNameOfDirectory",
        "headerversion": 3,
        "payloadversion": 2,
        "payload": "{'invalid': 'payload'}"
    }
    return json.dumps(invalid_message)


if __name__ == '__main__':
    simulate_invalid_telemetry()
