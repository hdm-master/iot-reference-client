""" Demo script of the reference iot_assets telemetry implementation

Run this script to simulate the telemetry use case

"""
import datetime
import json
import logging
import uuid
from dataclasses import asdict

from time import sleep

import iot_messages.generic_signal_v2 as gen_sig_v2
from event_validator.schema_validator import event_validator_factory, SchemaValidationException
from iot_assets.asset import Asset, AssetDetails
from iot_assets.sender import Sender, SenderDetails
from onboarding.onboarding_manager import OnboardingManager, ConnectionDetails

logging.basicConfig(format='[%(asctime)s][%(levelname)s][%(filename)s:%(lineno)d] %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


def simulate_telemetry_of_generic_signal_v2():
    """"
    This demo does the following:
    1. Creates Onboard Manager to handle directory and provisioning tasks
    2. Creates a sender with MQTT connection capabilities and an asset
    3. Creates a device specific generic signal v2
    4. Validates the generated message against the local json schema
    6. Sends the message to the telemetry topic if validation was successful
    """
    try:
        onboard_manager = OnboardingManager()
        connection_details = onboard_manager.onboard()
        device, sender = generate_devices(connection_details)
        device.connect(ssl_tunnel=False)  # set to True to use port 443
        event_validator = event_validator_factory()
        for _ in range(3):
            try:
                sleep(1)
                message = generate_generic_signal_v2(device, sender)
                event_validator.validate(message)
                device.publish_telemetry(message)
                sleep(1)
            except SchemaValidationException as err:
                logger.error(err)
        device.disconnect()
    except Exception as err:
        logger.error(err)
        raise err


def generate_devices(cd: ConnectionDetails) -> (Asset, Sender):
    """
    Returns asset and sender instance
    Input:
    cd : Connection Details which a provided by the onboarding manager
    Other details "strings" are demo values which should be changed accordingly
    """

    sender_details = SenderDetails(cd.mqtt_endpoint, cd.standard_port, cd.device_cert_path,
                                   cd.device_private_key_path, cd.amazon_root_ca_path, 'system',
                                   'senderNameDemo', 'sendersoftwareversionDemo', cd.telemetry_topic, cd.org_id,
                                   cd.site_id, cd.client_id)

    sender = Sender(sender_details)

    asset_details = AssetDetails(cd.machine_id, 'assetHardwareVersionDemo', 'assetmanufacturernameDemo',
                                 'assetnameDemo',
                                 'assetserialDemo', 'assetsoftwareversionDemo', 'BoxPacker', 'Speedmaster')

    return Asset(asset_details, sender), sender


def generate_generic_signal_v2(asset: Asset, sender: Sender) -> str:
    """Builds a valid generic signal v2 demo object"""
    genericSignalDeviceInfoJobPhasePart1 = gen_sig_v2.GenericSignalDeviceInfoJobPhasePart('sideDemo1', 'sheetNameDemo1')
    genericSignalDeviceInfoJobPhasePart2 = gen_sig_v2.GenericSignalDeviceInfoJobPhasePart('sideDemo2', 'sheetNameDemo2')
    genericSignalDeviceInfoJobPhaseList = [genericSignalDeviceInfoJobPhasePart1, genericSignalDeviceInfoJobPhasePart2]
    genericSignalDeviceInfoJobPhase1 = gen_sig_v2.GenericSignalDeviceInfoJobPhase(11, 'jobIdDemo', 'statusDemo',
                                                                                  'statusDetailsDemo',
                                                                                  'costCenterIdDemo', 'jobPartIdDemo',
                                                                                  genericSignalDeviceInfoJobPhaseList,
                                                                                  'percentcompleted', 'starttime',
                                                                                  'wasteDemo', 'workstepidDemo')
    genericSignalDeviceInfoJobPhase2 = gen_sig_v2.GenericSignalDeviceInfoJobPhase(22, 'jobIdDemo', 'statusDemo',
                                                                                  'statusDetailsDemo',
                                                                                  'costCenterIdDemo', 'jobPartIdDemo',
                                                                                  genericSignalDeviceInfoJobPhaseList,
                                                                                  'percentcompleted', 'starttime',
                                                                                  'wasteDemo', 'workstepidDemo')

    genericSignalDeviceInfoJobPhaseList = [genericSignalDeviceInfoJobPhase1, genericSignalDeviceInfoJobPhase2]
    genericSignalDeviceInfoEvent = gen_sig_v2.GenericSignalDeviceInfoEvent('eventValueDemo', 'eventIdDemo')
    genericSignalDeviceInfo = gen_sig_v2.GenericSignalDeviceInfo(111, 'StatusDemo', 'statusdetailsdemo', 1, 22,
                                                                 genericSignalDeviceInfoJobPhaseList,
                                                                 genericSignalDeviceInfoEvent)
    genericSignalSignalStatus = gen_sig_v2.GenericSignalSignalStatus(genericSignalDeviceInfo)
    genericSignalPayload = gen_sig_v2.GenericSignalPayload(genericSignalSignalStatus)
    iso_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc
    ).isoformat()
    ts_s = str(iso_timestamp)
    sendereventuuid = str(uuid.uuid1())
    genericSignalV2 = gen_sig_v2.GenericSignalV2(asset.assetid, asset.assetserial, ts_s, asset.assettype,
                                                 'generic.signal', 'Status', sendereventuuid,
                                                 sender.sendertype, ts_s, genericSignalPayload,
                                                 asset.assethardwareversion, asset.assetmanufacturername,
                                                 asset.assetname, asset.assetsoftwareversion, asset.assetsubtype,
                                                 sender.sendername, sender.sendersoftwareversion)
    d = asdict(genericSignalV2)
    return json.dumps(d)


if __name__ == '__main__':
    simulate_telemetry_of_generic_signal_v2()
