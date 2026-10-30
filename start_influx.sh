#!/bin/sh
set -a
. "$(dirname "$0")/.env"
set +a

cd "$(dirname "$0")"
exec docker compose -f compose.yml up influxdb2