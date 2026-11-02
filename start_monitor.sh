#!/bin/sh
set -a
. "$(dirname "$0")/.env"
set +a

cd "$(dirname "$0")"
INFLUXDB3_ADMIN_TOKEN="$(python3 -c 'import json; from pathlib import Path; print(json.loads(Path("influxdb3-admin-token.json").read_text(encoding="utf-8"))["token"])')"
export INFLUXDB3_ADMIN_TOKEN
exec docker compose -f compose.yml up -d