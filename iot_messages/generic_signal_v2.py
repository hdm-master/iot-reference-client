from dataclasses import dataclass
from typing import List, Any, Optional

"""The following classes represent the iot events
Currently implemented: 
Generic.Signal in Version 2
"""

@dataclass
class GenericSignalDeviceInfoJobPhasePart:
    side: str
    sheetname: str


@dataclass
class GenericSignalDeviceInfoJobPhase:
    amount: int
    jobid: str
    status: str
    statusdetails: str
    costcenterid: Optional[str] = None
    jobpartid: Optional[str] = None
    part: Optional[List[GenericSignalDeviceInfoJobPhasePart]] = None
    percentcompleted: Optional[str] = None
    starttime: Optional[str] = None
    waste: Optional[str] = None
    workstepid: Optional[str] = None


@dataclass
class GenericSignalDeviceInfoEvent:
    eventvalue: str
    eventid: str


@dataclass
class GenericSignalDeviceInfo:
    speed: int
    status: str
    statusdetails: str
    totalproductioncounter: int
    productioncounter: Optional[int] = None
    jobphase: Optional[List[GenericSignalDeviceInfoJobPhase]] = None
    event: Optional[GenericSignalDeviceInfoEvent] = None


@dataclass
class GenericSignalSignalStatus:
    deviceinfo: GenericSignalDeviceInfo


@dataclass
class GenericSignalPayload:
    signalstatus: GenericSignalSignalStatus


@dataclass
class HeaderV3Mandatory:
    assetid: str  # from device
    assetserial: str  # from device, created in the onbaording process
    assettimestamp: str  # from message
    assettype: str  # from device
    eventtype: str  # from message
    eventsubtype: str  # from message
    sendereventuuid: str  # from message
    sendertype: str  # from device
    sendertimestamp: str  # from message
    payload: Any


@dataclass
class HeaderV3Optional:
    assethardwareversion: Optional[str] = None  # from asset
    assetmanufacturername: Optional[str] = None  # from asset, created in the onbaording process
    assetname: Optional[str] = None  # from asset, created in the onbaording process
    assetsoftwareversion: Optional[str] = None  # from asset
    assetsubtype: Optional[str] = None  # from asset
    sendername: Optional[str] = None  # from asset
    sendersoftwareversion: Optional[str] = None  # from asset
    siteid: Optional[str] = None  # from asset, created in zaikio
    sitename: Optional[str] = None  # from asset, created in zaikio


@dataclass
class HeaderStatic:
    headerversion: int = 3  # from message
    payloadversion: int = 2  # from message


@dataclass
class GenericHeaderMandatory(HeaderV3Mandatory):
    payload: GenericSignalPayload


@dataclass
class GenericSignalV2(HeaderStatic, HeaderV3Optional, GenericHeaderMandatory):
    pass
