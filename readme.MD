# Real Time Espresso Monitor and Logger
Logs espresso extraction data and provides visualisations to help you analyze the extraction profile
* uses an Influx DB and a Grafana dashboard from a docker image
* ready to use a Bookoo bluetooth scale and pressure monitor
* includes test fakes for simulations when the hardware sensors are not available

![grafana screenshot](/assets/grafana.gif)

## Setup
### Docker images for Influx DB and Grafana
* Adapt the credentials in influxdb3-admin-token.js
* run `./start_influx.sh` to build the containers from the attached compose file
### URLs
* Influx DB connection: http://localhost:8181
* Grafana: http://localhost:3000

(as defined in the docker compose file)

### DB registration
In Grafana, connect against the Influx DB:
* url: http://influxdb3:8181
* Product: InfluxDB Enterprise 3.x
* Query language: SQL
* Database: extractions

### Grafana Setup
Use `grafana-dashboard.json` for the dashboard definition

### Cleanup: delete table from the influx db:

````
TOKEN="$(python3 -c 'import json; print(json.load(open("influxdb3-admin-token.json"))["token"])')"
docker compose exec -T influxdb3 influxdb3 delete table \
  --database extractions \
  --token "$TOKEN" \
  --hard-delete now \
  extractions
unset TOKEN
````
