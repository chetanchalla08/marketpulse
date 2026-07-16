#!/usr/bin/env bash
# Local dev helper: derives Spring's datasource env vars from the repo's
# existing .env (Python's DATABASE_URL) and runs the API. Not used in any
# deployed/CI context — local verification only.
set -euo pipefail
cd "$(dirname "$0")"

DATABASE_URL=$(grep '^DATABASE_URL=' ../.env | cut -d'=' -f2-)

# postgresql://user:pass@host:port/db -> split into JDBC url + user + pass
python3 - "$DATABASE_URL" <<'EOF' > /tmp/marketpulse-datasource.env
import sys
from urllib.parse import urlparse

u = urlparse(sys.argv[1])
print(f"SPRING_DATASOURCE_URL=jdbc:postgresql://{u.hostname}:{u.port}{u.path}")
print(f"SPRING_DATASOURCE_USERNAME={u.username}")
print(f"SPRING_DATASOURCE_PASSWORD={u.password}")
EOF

set -a
source /tmp/marketpulse-datasource.env
set +a
rm -f /tmp/marketpulse-datasource.env

exec mvn spring-boot:run
