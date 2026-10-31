import logging
import sys
from typing import Callable
import csv
import asyncio
import time
from pressure_sensor.PressureLogEntry import Pressure_Log_Entry
class FakePressureClient:

    def __init__(self):
        self.previous_weight = sys.float_info.min
        self.device = None

    def __read_csv(self, file: str):
        log_entries = []
        with open(file, newline="") as f:
            for row in csv.DictReader(f):
                log_entries.append(
                    Pressure_Log_Entry(
                        float(row["pressure"])
                    )
                )
        return log_entries
    
    async def read_data_from_pressure_sensor(self,
                                   on_logging: Callable[[str, Pressure_Log_Entry], None]
                                   ) -> None:
        log_entries = self.__read_csv("fake_measurements.csv")
        for entry in log_entries:
            on_logging(entry)
            await asyncio.sleep(1.0)  # Simulate a delay between readings