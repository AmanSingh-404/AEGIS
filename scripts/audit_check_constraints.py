from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "apps" / "api" / "src"))

from sqlalchemy import CheckConstraint
from api.models import Base

sql = Path("schema_v1.sql").read_text(encoding="utf-8")
sql = re.sub(r"--[^\n]*", "", sql)
sql = re.sub(r"/\*.*?\*/", "", sql, flags=re.DOTALL)


def normalize(value: str) -> str:
    value = re.sub(r"\s+", " ", value).strip().lower()
    # Treat insignificant spacing around punctuation as equivalent.
    value = re.sub(r"\s*\(\s*", "(", value)
    value = re.sub(r"\s*\)\s*", ")", value)
    value = re.sub(r"\s*,\s*", ", ", value)
    return value

def extract_parenthesized(source: str, opening: int) -> tuple[str, int]:
    depth = 0
    quote = None
    i = opening

    while i < len(source):
        ch = source[i]

        if quote:
            if ch == quote:
                if i + 1 < len(source) and source[i + 1] == quote:
                    i += 2
                    continue
                quote = None
        elif ch == "'":
            quote = ch
        elif ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0:
                return source[opening + 1:i], i + 1

        i += 1

    raise ValueError(f"Unbalanced parentheses starting at character {opening}")


def split_items(body: str) -> list[str]:
    result = []
    start = 0
    depth = 0
    quote = None
    i = 0

    while i < len(body):
        ch = body[i]

        if quote:
            if ch == quote:
                if i + 1 < len(body) and body[i + 1] == quote:
                    i += 2
                    continue
                quote = None
        elif ch == "'":
            quote = ch
        elif ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        elif ch == "," and depth == 0:
            result.append(body[start:i].strip())
            start = i + 1

        i += 1

    if body[start:].strip():
        result.append(body[start:].strip())

    return result


def extract_sql_checks(source: str) -> dict[str, list[str]]:
    tables = {}
    table_pattern = re.compile(
        r"\bCREATE\s+TABLE\s+(\w+)\s*\(", re.IGNORECASE
    )

    for match in table_pattern.finditer(source):
        table_name = match.group(1)
        body, _ = extract_parenthesized(source, match.end() - 1)
        expressions = []

        for item in split_items(body):
            check_match = re.search(r"\bCHECK\s*\(", item, re.IGNORECASE)
            if not check_match:
                continue

            opening = item.find("(", check_match.start())
            expression, _ = extract_parenthesized(item, opening)
            expressions.append(normalize(expression))

        tables[table_name] = sorted(expressions)

    return tables


sql_checks = extract_sql_checks(sql)
orm_checks = {
    table_name: sorted(
        normalize(str(constraint.sqltext))
        for constraint in table.constraints
        if isinstance(constraint, CheckConstraint)
    )
    for table_name, table in Base.metadata.tables.items()
}

mismatches = 0

for table_name in sorted(set(sql_checks) | set(orm_checks)):
    expected = sql_checks.get(table_name, [])
    actual = orm_checks.get(table_name, [])

    if expected != actual:
        mismatches += 1
        print(f"\nCHECK CONSTRAINT MISMATCH: {table_name}")
        print("  SQL:")
        for expression in expected:
            print("   -", expression)
        print("  ORM:")
        for expression in actual:
            print("   -", expression)

if mismatches == 0:
    print("PASS: SQL and ORM check-expression sets match.")
else:
    print(f"\nTables with check-expression differences: {mismatches}")
    raise SystemExit(1)
