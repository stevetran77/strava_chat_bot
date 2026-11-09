"""Pre-checks for model-written SQL. The database role is the real defence; this gives clear errors.

A query passes when it is one SELECT (or WITH ... SELECT) statement with no comments and no
write, DDL, session or file/network keywords. Quoted text is ignored when scanning keywords.
"""
import re

BANNED_WORDS = {
    "insert", "update", "delete", "drop", "alter", "create", "grant", "revoke", "truncate", "copy",
    "into", "call", "do", "set", "reset", "vacuum", "analyze", "lock", "listen", "notify", "execute",
    "prepare", "refresh", "comment", "security", "declare", "fetch", "load",
}
BANNED_PREFIXES = ("pg_", "lo_", "dblink", "set_config", "current_setting")


class UnsafeSql(ValueError):
    pass


def strip_quoted(sql):
    sql = re.sub(r"'(?:[^']|'')*'", "''", sql)
    return re.sub(r'"[^"]*"', '""', sql)


def check_select(sql):
    """Return the query without a trailing semicolon, or raise UnsafeSql."""
    text = sql.strip()
    if text.endswith(";"):
        text = text[:-1].rstrip()
    bare = strip_quoted(text)
    if not text:
        raise UnsafeSql("empty query")
    if ";" in bare:
        raise UnsafeSql("only one statement is allowed")
    if "--" in bare or "/*" in bare:
        raise UnsafeSql("comments are not allowed")
    words = re.findall(r"[a-z_][a-z0-9_]*", bare.lower())
    if words[0] not in ("select", "with"):
        raise UnsafeSql("query must start with SELECT or WITH")
    for word in words:
        if word in BANNED_WORDS or word.startswith(BANNED_PREFIXES):
            raise UnsafeSql(f"keyword or function not allowed: {word}")
    return text
