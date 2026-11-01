
import asyncio
from collections.abc import Callable
import sys
from bookoo.Bookoo import BYTE_ORDER
from bookoo.pressure_sensor.Abstract_Pressure_Sensor import AbstractPressureSensor
import logging
from bleak import BleakClient
from functools import partial
import asyncio

from scale import Scale_Log_Entry

class BookooPressureClient(AbstractPressureSensor):

    COMMAND_CHARACTERISTIC_UUID = "0000FF01-0000-1000-8000-00805F9B34FB"
    PRESSURE_CHARACTERISTIC_UUID = "0000FF02-0000-1000-8000-00805F9B34FB"

    def __init__(self):
        self.previous_pressure = sys.float_info.min
        self.device = None

    async def read_pressure_data(self,
                                   on_logging: Callable[[float], None]
                                   ) -> None:
        if self.device is None:
            await self.__get_bookoo_device()
        if self.device is None:
            return

        async with BleakClient(self.device.address) as client:
                    logging.info("Connected to scale; listening for pressure data...")
                    #await client.start_notify(COMMAND_CHARACTERISTIC_UUID, handle_command_data)
                    await client.start_notify(
                        self.PRESSURE_CHARACTERISTIC_UUID,
                        partial(self.__handle_pressure_data, on_logging=on_logging),
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
        
        def __handle_pressure_data(self, _sender, data: bytearray, on_logging) -> None:
            logging.debug("Pressure notification received from %s", _sender)
            packet = bytes(data)
            if len(packet) != 20:
                logging.warning("Ignoring pressure packet with unexpected length: %d", len(packet))
                return
            if packet[0] != 0x03 or packet[1] != 0x0B:
                logging.warning("Ignoring unrecognized pressure packet header: %s", packet[:2].hex())
                return
    
            checksum = 0
            for byte in packet[:-1]:
                checksum ^= byte
            if checksum != packet[-1]:
                logging.warning("Ignoring weight packet with invalid checksum")
                return
    
            elapsed_ms = int.from_bytes(packet[2:5], BYTE_ORDER.BIG_ENDIAN.value)
            pressure_bar = int.from_bytes(packet[7:10], BYTE_ORDER.BIG_ENDIAN.value) / 100
            flow_rate = int.from_bytes(packet[11:13], BYTE_ORDER.BIG_ENDIAN.value) / 100
            standby_minutes = int.from_bytes(packet[14:16], BYTE_ORDER.BIG_ENDIAN.value) / 10
    
            #if previous_weight is None or weight_grams != previous_weight:
            #    handle_weight_data.previous_weight = weight_grams
            if pressure_bar != self.previous_pressure:
                logging.info("\033[92m%s\033[0m", pressure_bar)
                logging.info(
                    "Scale data: elapsed=%d ms, pressure=%g bar (sign code=0x%02X, unit=0x%02X), "
                    "flow_rate=%g (sign code=0x%02X), battery=%d%%, standby=%g min, "
                    "buzzer=0x%02X, flow_smoothing=0x%02X",
                    elapsed_ms,
                    pressure_bar,
                    packet[6],
                    packet[5],
                    flow_rate,
                    packet[10],
                    packet[13],
                    standby_minutes,
                    packet[16],
                    packet[17],
                )
                self.previous_pressure = pressure_bar       
            on_logging(
                    Scale_Log_Entry(
                                        float(pressure_bar),
                                        float(flow_rate),
                                    )
            )