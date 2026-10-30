import influxdb_client

import Log_Entry

class InfluxDBClient:
    def __init__(self, url: str, token: str, org: str, bucket:str):
        self.url = url
        self.token = token
        self.influx_org = org
        self.influx_bucket = bucket
        self.client = influxdb_client.InfluxDBClient(url=url, token=token, org=org)
        self.write_api = self.client.write_api()

    def write_log_entry_to_influxdb(self, data_point: Log_Entry):
        point = (
            influxdb_client.Point("scale")
            #.tag("drink", "Espresso")
            .field("weight", data_point.weight)
            .field("temperature", data_point.temperature)
            .field("pressure", data_point.pressure)
            .field("flow rate", data_point.flow_rate)
        )
        self.write_api.write(
            bucket=self.influx_bucket,
            org=self.influx_org,
            record=point,
        )

    def close(self):
        try:
            self.write_api.close()
        finally:
            self.client.close()