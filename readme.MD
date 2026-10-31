# Real Time Espresso Monitor and Logger

* uses an Influx DB and a Grafana dashboard from a docker image
* ready to use a Bookoo scale and pressure monitor
* includes test fakes for simulations when the hardware sensors are not available

![grafana screenshot](/assets/grafana.png)


## URLs
* Influx DB connection: http://localhost:8181
* Grafana: http://localhost:3000

(as defined in the docker compose file)

## Tricks
Delete all data from the influx db:

````
TOKEN="$(python3 -c 'import json; print(json.load(open("influxdb3-admin-token.json"))["token"])')"
docker compose exec -T influxdb3 influxdb3 delete table \
  --database extractions \
  --token "$TOKEN" \
  --hard-delete now \
  extractions
unset TOKEN
````