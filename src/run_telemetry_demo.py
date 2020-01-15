""" Demo script of the reference demo_client implementation

Run this script to simulate some messages between two devices

"""

from time import sleep

from demo_client.device import Device
from util.log import get_logger

logger = get_logger(__name__)


def simulate_telemetry():
    logger.info('Simulating telemetry...')
    device = Device()
    device.connect()
    device.start_publishing()
    sleep(1)
    device.disconnect()
    sleep(1)


if __name__ == '__main__':
    simulate_telemetry()
