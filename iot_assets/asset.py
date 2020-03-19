""" Reference Client Implementation HDM IoT Platform

This is a reference implementation of a python iot_assets for the IoT Platform
It supports publishing of telemetry data and syncing of shadow states.

Written by Jörg Sädtler
"""
import logging
from dataclasses import dataclass
from .sender import Sender

logger = logging.getLogger(__name__)


@dataclass
class AssetDetails:
    assetid: str
    assethardwareversion: str
    assetmanufacturername: str
    assetname: str
    assetserial: str
    assetsoftwareversion: str
    assettype: str
    assetsubtype: str


class Asset:
    """Represents an asset and communicates with the sender
    """

    def __init__(self, asset: AssetDetails, sender: Sender):
        self.assetid = asset.assetid
        self.assethardwareversion = asset.assethardwareversion
        self.assetmanufacturername = asset.assetmanufacturername
        self.assetname = asset.assetname
        self.assetserial = asset.assetserial
        self.assetsoftwareversion = asset.assetsoftwareversion
        self.assettype = asset.assettype
        self.assetsubtype = asset.assetsubtype
        self.sender = sender

    def connect(self, ssl_tunnel=False):
        """Call this method to connect the device to the iot core"""
        self.sender.connect(ssl_tunnel=ssl_tunnel)

    def disconnect(self):
        """Call this method to disconnect the device from the iot core"""
        self.sender.disconnect()

    def publish_telemetry(self, message):
        """Publish a message to a mqtt topic"""
        self.sender.publish_telemetry(message)

    def subscribe(self, topic):
        """Subscribe the iot iot_assets to a mqtt topic"""
        self.sender.subscribe(topic)

