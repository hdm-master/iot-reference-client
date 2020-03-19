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
class HeaderV2Mandatory:
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
class HeaderV2Optional:
    assethardwareversion: Optional[str] = None  # from device
    assetmanufacturername: Optional[str] = None  # from device, created in the onbaording process
    assetname: Optional[str] = None  # from device, created in the onbaording process
    assetsoftwareversion: Optional[str] = None  # from device
    assetsubtype: Optional[str] = None  # from device
    sendername: Optional[str] = None  # from device
    sendersoftwareversion: Optional[str] = None  # from device


@dataclass
class HeaderV2Static:
    headerversion: int = 2  # from message
    payloadversion: int = 2  # from message


@dataclass
class GenericHeaderV2Mandatory(HeaderV2Mandatory):
    payload: GenericSignalPayload


@dataclass
class GenericSignalV2(HeaderV2Static, HeaderV2Optional, GenericHeaderV2Mandatory):
    pass
