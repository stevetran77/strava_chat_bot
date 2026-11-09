"""Guard check: the chatbot role must be able to read and nothing else.

Usage: .venv/bin/python src/checks/check_readonly.py      Exit code 1 if any check fails.
Logs in as chatbot_ro (password from .env) and checks:
  1. It is not a superuser and cannot create databases or roles.
  2. It holds no write privilege on any table in schema public, and cannot create objects.
  3. A real write is refused even after switching off the read-only default.
  4. A statement timeout is set.
"""
import logging
import sys
from pathlib import Path

import psycopg
from psycopg import errors

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from queries import connect  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger("check_readonly")

WRITE_PRIVILEGES = "INSERT,UPDATE,DELETE,TRUNCATE,REFERENCES,TRIGGER"


def role_flags(conn):
    row = conn.execute(
        "SELECT rolsuper OR rolcreatedb OR rolcreaterole AS powerful FROM pg_roles WHERE rolname = current_user"
    ).fetchone()
    return [] if not row["powerful"] else ["role is superuser, createdb or createrole"]


def write_privileges(conn):
    tables = [r["tablename"] for r in conn.execute("SELECT tablename FROM pg_tables WHERE schemaname = 'public'")]
    problems = [f"write privilege on {t}" for t in tables
                if conn.execute("SELECT has_table_privilege(current_user, %s, %s) AS h",
                                (f"public.{t}", WRITE_PRIVILEGES)).fetchone()["h"]]
    if conn.execute("SELECT has_schema_privilege(current_user, 'public', 'CREATE') AS h").fetchone()["h"]:
        problems.append("CREATE on schema public")
    return problems


def real_write_refused(conn):
    conn.rollback()
    conn.execute("SET default_transaction_read_only = off")
    conn.commit()  # the setting applies from the next transaction
    problems = []
    for name, sql in (("DELETE", "DELETE FROM activities WHERE false"), ("DROP", "DROP TABLE laps")):
        try:
            conn.execute(sql)
            problems.append(f"{name} was accepted")
        except errors.InsufficientPrivilege:
            pass
        except psycopg.Error as exc:
            problems.append(f"{name} failed for another reason: {type(exc).__name__}")
        conn.rollback()
    return problems


def timeout_set(conn):
    value = conn.execute("SHOW statement_timeout").fetchone()["statement_timeout"]
    return ["no statement_timeout"] if value in ("0", "0ms") else []


CHECKS = {
    "role has no elevated attributes": role_flags,
    "no write privilege on any public table": write_privileges,
    "real DELETE and DROP are refused": real_write_refused,
    "statement timeout is set": timeout_set,
}


def main():
    failed = 0
    with connect() as conn:
        for name, check in CHECKS.items():
            problems = check(conn)
            conn.rollback()
            if problems:
                failed += 1
                log.error("[FAIL] %s: %s", name, "; ".join(problems))
            else:
                log.info("[OK] %s", name)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
