import uuid
import datetime
from util.log import get_logger

logger = get_logger(__name__)


class IoTEvent:
    """Events that can be serialized to mqtt payloads"""

    def __init__(self, thing_name, event_type, event_subtype, payload):
        logger.debug(f"IoT Event for thing name: {thing_name} invoked")
        """pass the parameters to generate a demo event"""

        iso_timestamp = datetime.datetime.utcnow().replace(
            tzinfo=datetime.timezone.utc
        ).isoformat()

        self.senderId = thing_name
        self.senderType = "prinect"
        self.senderEventUuid = str(uuid.uuid1())
        self.senderTimestamp = iso_timestamp
        self.assetId = thing_name  # this should be the device id if present
        self.assetType = "Press"
        self.assetTimestamp = iso_timestamp
        self.assetSoftwareVersion = "19.04"
        self.assetHardwareVersion = "44.2"
        self.assetSerial = thing_name  # this should be the device serial
        self.eventType = event_type
        self.eventSubtype = event_subtype
        self.payloadVersion = 1
        self.customer = "reference demo_client"
        self.payload = payload
