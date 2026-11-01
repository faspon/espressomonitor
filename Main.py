
import asyncio
import json
from pathlib import Path
import time
from Record_Data import Record_Data
from bookoo.scale.FakeBookooScaleClient import FakeBookooScaleClient
from bookoo.scale.Scale_Log_Entry import Scale_Log_Entry
from bookoo.pressure_sensor.PressureLogEntry import Pressure_Log_Entry
from bookoo.pressure_sensor.FakePressureClient import FakePressureClient
from InfluxDbClient import InfluxDBClient
import asyncio

influxdb_client = None

PRESSURE_THRESHOLD = 0.01
FLOW_THRESHOLD = 0.1

shot_start_time = None
shot_time = 0.0
flow_has_started = False

async def main():
    scale_client = FakeBookooScaleClient() #BookooScaleClient()
    pressure_client = FakePressureClient()
    token_file = Path(__file__).with_name("influxdb3-admin-token.json")
    db_url=json.loads(token_file.read_text(encoding="utf-8"))["db_url"]
    token = json.loads(token_file.read_text(encoding="utf-8"))["token"]
    if not token or token.startswith("REPLACE_"):
        raise ValueError(f"Set a valid token in {token_file}")
    org="fasp"
    db_name="extractions"
    global influxdb_client
    influxdb_client = InfluxDBClient(db_url=db_url, token=token, org=org, db_name=db_name)
    
    record_data = Record_Data(record_id=str(int(time.time())), beans="San Augustin - Geisha Trincheras", temperature=91.5, shot_time=0.0)
    write_record_data_to_influxdb(record_data)
    try:
        await asyncio.gather(
            scale_client.read_scale_data(
                lambda scale_data_point: manage_scale_data_point(record_data, scale_data_point)
            ),
            pressure_client.read_pressure_data(
                lambda pressure_data_point: manage_pressure_data_point(record_data, pressure_data_point)
            )
        )
    finally:
        influxdb_client.close()

def manage_scale_data_point(record_data: Record_Data, scale_data_point: Scale_Log_Entry):
    global shot_start_time, shot_time, flow_has_started

    #if scale_data_point.flow_rate > FLOW_THRESHOLD and shot_start_time is not None:
    #    flow_has_started = True

    if shot_start_time is not None:
        shot_time = time.time() - shot_start_time
        if scale_data_point.flow_rate > FLOW_THRESHOLD:
            flow_has_started = True

    influxdb_client.write_scale_entry_to_influxdb(record_data.record_id, scale_data_point)
    write_record_data_to_influxdb(record_data)

def manage_pressure_data_point(record_data: Record_Data, pressure_data_point: Pressure_Log_Entry):
    global shot_start_time
    if pressure_data_point.pressure > PRESSURE_THRESHOLD and shot_start_time is None:
        shot_start_time = time.time()
    influxdb_client.write_pressure_entry_to_influxdb(record_data.record_id, pressure_data_point)
    influxdb_client.write_pressure_entry_to_influxdb(record_data.record_id, pressure_data_point)
    print("pressure, seconds: "+f" {pressure_data_point.pressure} {shot_time:.1f}")

def write_record_data_to_influxdb(record_data: Record_Data):
    global shot_time
    if shot_time is not None:
        record_data.shot_time = f"{shot_time:.1f}"
    influxdb_client.write_record_entry_to_influxdb(record_data)
           
if __name__ == "__main__":
    asyncio.run(main())
