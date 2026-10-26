import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "apps" / "api" / "src"))

from api.models import Base  # noqa: E402


SQL_PATH = ROOT / "schema_v1.sql"
sql = SQL_PATH.read_text(encoding="utf-8")


def extract_create_table_blocks(source: str) -> dict[str, str]:
    blocks = {}
    pattern = re.compile(r"\bCREATE\s+TABLE\s+(\w+)\s*\(", re.IGNORECASE)

    for match in pattern.finditer(source):
        name = match.group(1)
        opening = match.end() - 1
        depth = 0
        quote = None
        closing = None
        i = opening

        while i < len(source):
            char = source[i]

            if quote:
                if char == quote:
                    if i + 1 < len(source) and source[i + 1] == quote:
                        i += 2
                        continue
                    quote = None
            elif char in ("'", '"'):
                quote = char
            elif char == "(":
                depth += 1
            elif char == ")":
                depth -= 1
                if depth == 0:
                    closing = i
                    break

            i += 1

        if closing is None:
            raise ValueError(f"Could not parse CREATE TABLE block: {name}")

        blocks[name] = source[opening + 1 : closing]

    return blocks


def split_top_level_items(body: str) -> list[str]:
    items = []
    start = 0
    depth = 0
    quote = None
    i = 0

    while i < len(body):
        char = body[i]

        if quote:
            if char == quote:
                if i + 1 < len(body) and body[i + 1] == quote:
                    i += 2
                    continue
                quote = None
        elif char in ("'", '"'):
            quote = char
        elif char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
        elif char == "," and depth == 0:
            items.append(body[start:i].strip())
            start = i + 1

        i += 1

    tail = body[start:].strip()
    if tail:
        items.append(tail)

    return items


sql_tables = extract_create_table_blocks(sql)
orm_tables = set(Base.metadata.tables)

print("AEGIS schema parity audit — read-only")
print(f"SQL source: {SQL_PATH}")
print(f"SQL tables: {len(sql_tables)}")
print(f"ORM tables: {len(orm_tables)}")
print()

issues = 0

sql_table_names = set(sql_tables)
if sql_table_names != orm_tables:
    issues += 1
    print("TABLE SET MISMATCH")
    print("  SQL-only:", sorted(sql_table_names - orm_tables))
    print("  ORM-only:", sorted(orm_tables - sql_table_names))
    print()
else:
    print("PASS: table names match exactly.")
    print()

for table_name in sorted(sql_table_names & orm_tables):
    sql_columns = set()

    for item in split_top_level_items(sql_tables[table_name]):
        normalized = item.strip()
        if not normalized:
            continue

        upper = normalized.upper()
        if upper.startswith(
            ("CONSTRAINT ", "PRIMARY KEY", "FOREIGN KEY", "UNIQUE ", "CHECK ")
        ):
            continue

        match = re.match(r'(?:"([^"]+)"|(\w+))\s+', normalized)
        if match:
            sql_columns.add(match.group(1) or match.group(2))

    orm_columns = set(Base.metadata.tables[table_name].columns.keys())

    if sql_columns != orm_columns:
        issues += 1
        print(f"COLUMN SET MISMATCH: {table_name}")
        print("  SQL-only:", sorted(sql_columns - orm_columns))
        print("  ORM-only:", sorted(orm_columns - sql_columns))

sql_indexes = set(
    re.findall(
        r"\bCREATE\s+(?:UNIQUE\s+)?INDEX\s+(\w+)",
        sql,
        re.IGNORECASE,
    )
)
orm_indexes = {
    index.name
    for table in Base.metadata.tables.values()
    for index in table.indexes
    if index.name
}

if sql_indexes != orm_indexes:
    issues += 1
    print("\nINDEX NAME MISMATCH")
    print("  SQL-only:", sorted(sql_indexes - orm_indexes))
    print("  ORM-only:", sorted(orm_indexes - sql_indexes))
else:
    print("PASS: named index sets match exactly.")

# Ignore SQL comments so words in comments are not treated as constraints.
sql_without_comments = re.sub(r"--[^\n]*", "", sql)
sql_without_comments = re.sub(
    r"/\*.*?\*/", "", sql_without_comments, flags=re.DOTALL
)
sql_constraint_names = set(
    re.findall(
        r"\bCONSTRAINT\s+(\w+)",
        sql_without_comments,
        re.IGNORECASE,
    )
)
orm_constraint_names = {
    constraint.name
    for table in Base.metadata.tables.values()
    for constraint in table.constraints
    if constraint.name
}

# SQLAlchemy names inline CHECK constraints that are unnamed in schema_v1.sql.
# Their expressions are audited separately by audit_check_constraints.py.
inline_check_names = {
    "approval_events_event_type_check",
    "chunks_chunk_index_check",
    "decision_log_confidence_check",
    "decision_log_question_type_check",
    "project_members_role_check",
    "runs_attempt_check",
    "tool_audit_events_event_type_check",
    "tools_origin_check",
    "tools_timeout_seconds_check",
}
orm_constraint_names -= inline_check_names

if sql_constraint_names != orm_constraint_names:
    issues += 1
    print("\\nNAMED CONSTRAINT MISMATCH")
    print("  SQL-only:", sorted(sql_constraint_names - orm_constraint_names))
    print("  ORM-only:", sorted(orm_constraint_names - sql_constraint_names))
else:
    print("PASS: named constraint sets match exactly.")

print()
print(f"Structural mismatches detected: {issues}")
print(
    "NOTE: This initial report compares table/column names, index names, "
    "and named constraint names only. It does NOT yet validate column types, "
    "defaults, nullability, constraint expressions, foreign-key actions, "
    "or deferrability."
)

if issues:
    raise SystemExit(1)
