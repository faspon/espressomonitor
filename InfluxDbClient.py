import influxdb_client
from Record_Data import Record_Data
from scale.Scale_Log_Entry import Scale_Log_Entry
from pressure_sensor.PressureLogEntry import Pressure_Log_Entry

class InfluxDBClient:
    def __init__(self, db_url: str, token: str, org: str, db_name:str):
        self.db_url = db_url
        self.token = token
        self.influx_org = org
        self.influx_db_name = db_name
        self.client = influxdb_client.InfluxDBClient(url=db_url, token=token, org=org)
        self.write_api = self.client.write_api()

    def write_scale_entry_to_influxdb(self, record_id: str, scale_data_point: Scale_Log_Entry):
        point = (
            influxdb_client.Point("extractions")
            .tag("record_id", record_id)
            .field("weight", scale_data_point.weight)
            .field("flow_rate", scale_data_point.flow_rate)
        )
        self.write_api.write(
            bucket=self.influx_db_name,
            org=self.influx_org,
            record=point,
        )

    def write_pressure_entry_to_influxdb(self, record_id: str, pressure_data_point: Pressure_Log_Entry):
        point = (
            influxdb_client.Point("extractions")
            .tag("record_id", record_id)
            .field("pressure", pressure_data_point.pressure)
        )
        self.write_api.write(
            bucket=self.influx_db_name,
            org=self.influx_org,
            record=point,
        )

    def write_record_entry_to_influxdb(self, record_data: Record_Data):
        point = influxdb_client.Point("extractions")
        for name, value in vars(record_data).items():
            if name == "record_id":
                point = point.tag(name, str(value))
            elif name == "shot_time":
                point = point.field("shot_time", float(value))
            else:
                point = point.field(name, value)
        # point = (
        #     influxdb_client.Point("extractions")
        #     .tag("recording_id", record_data.record_id)
        #     .tag("beans", record_data.beans)
        #     .tag("temperature", record_data.temperature)
        #)
        self.write_api.write(
            bucket=self.influx_db_name,
            org=self.influx_org,
            record=point,
        )

    def close(self):
        try:
            self.write_api.close()
        finally:
            self.client.close()