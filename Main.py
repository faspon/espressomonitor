
import asyncio
import json
from pathlib import Path
import time
from Record_Data import Record_Data
from scale.FakeBookooScaleClient import FakeBookooScaleClient
from scale.Scale_Log_Entry import Scale_Log_Entry
from pressure_sensor.PressureLogEntry import Pressure_Log_Entry
from pressure_sensor.FakePressureClient import FakePressureClient
#from scale.BookooScaleClient import Bookoo_Scale_Client
from InfluxDbClient import InfluxDBClient

import asyncio

influxdb_client = None

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
    record_data = Record_Data(record_id=str(int(time.time())), beans="San Augustin - Geisha Trincheras", temperature=91.5)
    write_record_data_to_influxdb(record_data)
    try:
        await asyncio.gather(
            scale_client.read_data_from_scale(
                lambda scale_data_point: influxdb_client.write_scale_entry_to_influxdb(record_data.record_id, scale_data_point)
            ),
            pressure_client.read_data_from_pressure_sensor(
                lambda pressure_data_point: influxdb_client.write_pressure_entry_to_influxdb(record_data.record_id, pressure_data_point)
            )
        )
    finally:
        influxdb_client.close()

def write_record_data_to_influxdb(record_data: Record_Data):
    print(record_data)
    influxdb_client.write_record_entry_to_influxdb(record_data)
           
if __name__ == "__main__":
    asyncio.run(main())
