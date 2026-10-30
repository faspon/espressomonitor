import logging
import sys
from typing import Callable
import csv
import asyncio
from Log_Entry import Log_Entry

class BookooFakeClient:

    previous_weight = sys.float_info.min

    TARGET_SCALE_ADDRESS = '9EC74734-0879-B152-3029-96FC21A21CF3'
    WEIGHT_CHARACTERISTIC_UUID = "0000ff11-0000-1000-8000-00805f9b34fb"
    COMMAND_CHARACTERISTIC_UUID = "0000ff12-0000-1000-8000-00805f9b34fb"

    device = None

    def __init__(self):
        self.previous_weight = sys.float_info.min
        self.device = None

    async def __get_bookoo_device(self):
        return None
    
    def __read_csv(self, file: str):
        log_entries = []
        with open(file, newline="") as f:
            for row in csv.DictReader(f):
                log_entries.append(
                    Log_Entry(
                        float(row["temperature"]),
                        float(row["pressure"]),
                        float(row["weight"]),
                        float(row["flowrate"]),
                    )
                )
        return log_entries
    
    async def read_data_from_scale(self,
                                   on_logging: Callable[[Log_Entry], None]
                                   ) -> None:
        
        log_entries = self.__read_csv("fake_measurements.csv")
        for entry in log_entries:
            on_logging(entry)
            await asyncio.sleep(1.0)  # Simulate a delay between readings