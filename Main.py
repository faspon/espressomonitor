
import asyncio

from BookooClient import BookooClient
from BookooFakeClient import BookooFakeClient
from InfluxDbClient import InfluxDBClient

async def main():
    url="http://localhost:8086"
    token="admin-token"
    org="fasp"
    bucket="extractions"
    influxdb_client = InfluxDBClient(url=url, token=token, org=org, bucket=bucket)
    bookoo_client = BookooFakeClient() #BookooClient()
    try:
        await bookoo_client.read_data_from_scale(
            influxdb_client.write_log_entry_to_influxdb
        )
    finally:
        influxdb_client.close()

if __name__ == "__main__":
    asyncio.run(main())
