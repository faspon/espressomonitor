import sys
import asyncio
import logging
from enum import Enum
from typing import Callable
from bleak import BleakClient, BleakScanner
from functools import partial
from bookoo.scale import Scale_Log_Entry
from scale.Abstract_Scale import AbstractScale
from bookoo import Bookoo
from bookoo.Bookoo import BYTE_ORDER

class Bookoo_Scale_Client(AbstractScale):

    previous_weight = sys.float_info.min

    TARGET_SCALE_ADDRESS = '9EC74734-0879-B152-3029-96FC21A21CF3'
    WEIGHT_CHARACTERISTIC_UUID = "0000ff11-0000-1000-8000-00805f9b34fb"
    COMMAND_CHARACTERISTIC_UUID = "0000ff12-0000-1000-8000-00805f9b34fb"

    device = None

    def __init__(self):
        self.previous_weight = sys.float_info.min
        self.device = None

    async def read_scale_data(self,
                                   on_logging: Callable[[float], None]
                                   ) -> None:
        if self.device is None:
            await Bookoo.get_bookoo_device()
        if self.device is None:
            return

        async with BleakClient(self.device.address) as client:
            logging.info("Connected to scale; listening for weight data...")
            #await client.start_notify(COMMAND_CHARACTERISTIC_UUID, handle_command_data)
            await client.start_notify(
                self.WEIGHT_CHARACTERISTIC_UUID,
                partial(self.__handle_weight_data, on_logging=on_logging),
            )

            # COMMAND_TARE=0x01
            # COMMAND_BEEP=0x02
            # COMMAND_TARE_START_TIMER=0x07
            # command = bytearray([0x03, 0x0A, COMMAND_TARE_START_TIMER, 0x00, 00])

            # beeper_level = 0
            # #command = bytearray([0x03, 0x0A, 0x02, 0x00, beeper_level])
            # checksum = 0
            # for byte in command:
            #     checksum ^= byte
            # command.append(checksum)
            # await client.write_gatt_char(self.COMMAND_CHARACTERISTIC_UUID, command)

            await asyncio.Event().wait()

    def __handle_weight_data(self, _sender, data: bytearray, on_logging) -> None:
        logging.debug("Weight notification received from %s", _sender)
        packet = bytes(data)
        if len(packet) != 20:
            logging.warning("Ignoring weight packet with unexpected length: %d", len(packet))
            return
        if packet[0] != 0x03 or packet[1] != 0x0B:
            logging.warning("Ignoring unrecognized weight packet header: %s", packet[:2].hex())
            return

        checksum = 0
        for byte in packet[:-1]:
            checksum ^= byte
        if checksum != packet[-1]:
            logging.warning("Ignoring weight packet with invalid checksum")
            return

        elapsed_ms = int.from_bytes(packet[2:5], BYTE_ORDER.BIG_ENDIAN.value)
        weight_grams = int.from_bytes(packet[7:10], BYTE_ORDER.BIG_ENDIAN.value) / 100
        flow_rate = int.from_bytes(packet[11:13], BYTE_ORDER.BIG_ENDIAN.value) / 100
        standby_minutes = int.from_bytes(packet[14:16], BYTE_ORDER.BIG_ENDIAN.value) / 10

        #if previous_weight is None or weight_grams != previous_weight:
        #    handle_weight_data.previous_weight = weight_grams
        if weight_grams != self.previous_weight:
            logging.info("\033[92m%s\033[0m", weight_grams)
            logging.info(
                "Scale data: elapsed=%d ms, weight=%g g (sign code=0x%02X, unit=0x%02X), "
                "flow_rate=%g (sign code=0x%02X), battery=%d%%, standby=%g min, "
                "buzzer=0x%02X, flow_smoothing=0x%02X",
                elapsed_ms,
                weight_grams,
                packet[6],
                packet[5],
                flow_rate,
                packet[10],
                packet[13],
                standby_minutes,
                packet[16],
                packet[17],
            )
            self.previous_weight = weight_grams
        on_logging(
                   Scale_Log_Entry(
                                    float(weight_grams),
                                    float(flow_rate),
                                )
        )

    # async def handle_command_data(_sender, data: bytearray) -> None:
    #     logging.debug("Command notification received from %s", _sender)
    #     packet = bytes(data)
    #     if len(packet) != 20:
    #         logging.warning("Ignoring command packet with unexpected length: %d", len(packet))
    #         return
    #     if packet[0] != 0x03 or packet[1] != 0x0A:
    #         logging.warning("Ignoring unrecognized command packet header: %s", packet[:2].hex())
    #         return

    #     checksum = 0
    #     for byte in packet[:-1]:
    #         checksum ^= byte
    #     if checksum != packet[-1]:
    #         logging.warning("Ignoring command packet with invalid checksum")
    #         return

    #     command_code = packet[2]
    #     command_data = packet[3:19]
    #     logging.info(
    #         "Command data: code=0x%02X, data=%s",
    #         command_code,
    #         command_data.hex(),
    #     )
