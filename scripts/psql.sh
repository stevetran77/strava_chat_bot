#!/bin/sh
# Run psql inside the project's Postgres container, using settings from .env.
# Usage:
#   scripts/psql.sh "SELECT count(*) FROM activities"   one SQL statement
#   scripts/psql.sh -tA -c "SELECT 1"                     any psql flags, passed through
#   scripts/psql.sh < file.sql                            SQL from stdin
# The container name, user and database come from .env (never printed here).
set -eu
root=$(cd "$(dirname "$0")/.." && pwd)
set -a
. "$root/.env"
set +a
# A single argument that does not start with "-" is treated as SQL.
if [ "$#" -eq 1 ] && [ "${1#-}" = "$1" ]; then
    set -- -c "$1"
fi
# -i is required: without it docker drops stdin and SQL piped in silently never runs.
exec docker exec -i "$POSTGRES_CONTAINER" psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" "$@"
