import asyncio
import logging
import os
from enum import Enum
from functools import partial
from itertools import count
from typing import AsyncIterator
from bleak import BleakClient, BleakScanner

async def generate_synthetic_weights(
    interval_seconds: float = 1.0,
) -> AsyncIterator[float]:
    """Yield repeating simulated brew weights, from zero to 250 g and back."""
    if interval_seconds <= 0:
        raise ValueError("interval_seconds must be greater than zero")

    for step in count():
        phase = (step * interval_seconds) % 60
        if phase < 5:
            weight = 0.0
        elif phase < 35:
            weight = (phase - 5) / 30 * 250
        elif phase < 45:
            weight = 250.0
        else:
            weight = (60 - phase) / 15 * 250

        yield round(weight, 1)
        await asyncio.sleep(interval_seconds)


async def run_synthetic_scale(write_api, interval_seconds: float = 1.0) -> None:
    logging.warning("Physical scale unavailable; writing synthetic readings")
    async for weight in generate_synthetic_weights(interval_seconds):
        logging.info("Synthetic weight: %.1f g", weight)
        #write_weight_to_influxdb(write_api, weight, source="synthetic")
