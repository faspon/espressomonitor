import logging
import sys
from enum import Enum
from bleak import BleakScanner

class BYTE_ORDER(Enum):
    LITTLE_ENDIAN = "little"
    BIG_ENDIAN = "big"

async def get_bookoo_device(self):
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    logging.info("Scanning for Bluetooth devices...")

    devices = await BleakScanner.discover()
    target_address = self.TARGET_SCALE_ADDRESS.casefold()
    self.device = next(
        (device for device in devices if device.address.casefold() == target_address),
        None,
    )

    if self.device is None:
        logging.info("Bluetooth device %s not found", self.TARGET_SCALE_ADDRESS)
        return None

    logging.info(
        "Found Bluetooth device %s (%s)",
        self.device.name or "Unknown",
        self.device.address,
    )
    return self.device