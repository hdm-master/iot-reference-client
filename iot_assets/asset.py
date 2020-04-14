""" Reference Client Implementation HDM IoT Platform

This is a reference implementation of a python iot_assets for the IoT Platform
It supports publishing of telemetry data and syncing of shadow states.
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
    def __init__(self, asset: AssetDetails):
        self.assetid = asset.assetid
        self.assethardwareversion = asset.assethardwareversion
        self.assetmanufacturername = asset.assetmanufacturername
        self.assetname = asset.assetname
        self.assetserial = asset.assetserial
        self.assetsoftwareversion = asset.assetsoftwareversion
        self.assettype = asset.assettype
        self.assetsubtype = asset.assetsubtype

