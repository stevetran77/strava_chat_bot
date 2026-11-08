#!/bin/sh
# One-screen health check: Ollama, models, Postgres container, tables, Python.
# Usage: scripts/status.sh      Exit code 1 if anything needed is not OK.
root=$(cd "$(dirname "$0")/.." && pwd)
cd "$root" || exit 1
set -a
. ./.env
set +a
failed=0
ok() { echo "[OK]   $1"; }
fail() { echo "[FAIL] $1"; failed=1; }

if curl -s -m 3 "$OLLAMA_URL/api/version" >/dev/null 2>&1; then
    ok "Ollama server answers at $OLLAMA_URL"
    models=$(curl -s -m 5 "$OLLAMA_URL/api/tags" | .venv/bin/python -c "import json,sys; print(' '.join(m['name'] for m in json.load(sys.stdin)['models']))")
    case " $models " in
        *" $OLLAMA_EMBED_MODEL:latest "*|*" $OLLAMA_EMBED_MODEL "*) ok "embedding model $OLLAMA_EMBED_MODEL present" ;;
        *) fail "embedding model $OLLAMA_EMBED_MODEL not found (have: $models)" ;;
    esac
else
    fail "Ollama server not reachable at $OLLAMA_URL (brew services start ollama)"
fi

state=$(docker inspect -f '{{.State.Status}}' "$POSTGRES_CONTAINER" 2>/dev/null)
if [ "$state" = "running" ]; then
    ok "container $POSTGRES_CONTAINER running"
    counts=$("$root/scripts/psql.sh" -tA -c "SELECT 'activities='||(SELECT count(*) FROM activities)||' laps='||(SELECT count(*) FROM laps)||' daily_metrics='||(SELECT count(*) FROM daily_metrics)||' embeddings='||(SELECT count(*) FROM embeddings)||' guidance_cards='||(SELECT count(*) FROM guidance_cards)" 2>&1)
    if [ $? -eq 0 ]; then ok "database reachable: $counts"; else fail "database query failed: $counts"; fi
else
    fail "container $POSTGRES_CONTAINER state: ${state:-not found} (start Docker Desktop, then: docker start $POSTGRES_CONTAINER)"
fi

if [ -x .venv/bin/python ]; then ok "venv Python $(.venv/bin/python --version 2>&1 | cut -d' ' -f2)"; else fail ".venv missing (uv venv .venv; uv pip install -r requirements.txt)"; fi
exit $failed
