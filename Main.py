
import asyncio
import json
from pathlib import Path

from BookooClient import BookooClient
from BookooFakeClient import BookooFakeClient
from InfluxDbClient import InfluxDBClient

async def main():
    url="http://localhost:8181"
    token_file = Path(__file__).with_name("influxdb3-admin-token.json")
    token = json.loads(token_file.read_text(encoding="utf-8"))["token"]
    if not token or token.startswith("REPLACE_"):
        raise ValueError(f"Set a valid token in {token_file}")
    org="fasp"
    db_name="extractions"
    influxdb_client = InfluxDBClient(url=url, token=token, org=org, bucket=db_name)
    bookoo_client = BookooFakeClient() #BookooClient()
    try:
        await bookoo_client.read_data_from_scale(
            influxdb_client.write_log_entry_to_influxdb
        )
    finally:
        influxdb_client.close()

if __name__ == "__main__":
    asyncio.run(main())
