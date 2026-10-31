import logging
import sys
from typing import Callable
import csv
import asyncio
from .Scale_Log_Entry import Scale_Log_Entry
import time

class FakeBookooScaleClient:

    previous_weight = sys.float_info.min
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
                    Scale_Log_Entry(
                        float(row["weight"]),
                        float(row["flowrate"]),
                    )
                )
        return log_entries
    
    async def read_data_from_scale(self,
                                   on_logging: Callable[[str, Scale_Log_Entry], None]
                                   ) -> None:
        log_entries = self.__read_csv("fake_measurements.csv")
        for entry in log_entries:
            on_logging(entry)
            await asyncio.sleep(1.0)  # Simulate a delay between readings