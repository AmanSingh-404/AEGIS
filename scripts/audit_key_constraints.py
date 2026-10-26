from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "apps" / "api" / "src"))

from sqlalchemy import UniqueConstraint
from api.models import Base

sql = Path("schema_v1.sql").read_text(encoding="utf-8")
sql = re.sub(r"--[^\n]*", "", sql)
sql = re.sub(r"/\*.*?\*/", "", sql, flags=re.DOTALL)


def extract_parenthesized(source, opening):
    depth, quote, i = 0, None, opening
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
                return source[opening + 1:i]
        i += 1
    raise ValueError(f"Unbalanced parentheses at offset {opening}")


def split_items(body):
    items, start, depth, quote, i = [], 0, 0, None, 0
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
            items.append(body[start:i].strip())
            start = i + 1
        i += 1
    if body[start:].strip():
        items.append(body[start:].strip())
    return items


def parse_columns(text):
    return tuple(part.strip().strip('"') for part in text.split(","))


def sql_keys(source):
    primary_keys = set()
    unique_keys = set()
    pattern = re.compile(r"\bCREATE\s+TABLE\s+(\w+)\s*\(", re.I)

    for match in pattern.finditer(source):
        table = match.group(1)
        body = extract_parenthesized(source, match.end() - 1)

        for item in split_items(body):
            # Remove a table-level constraint label before reading its definition.
            normalized = re.sub(
                r"^\s*CONSTRAINT\s+\w+\s+",
                "",
                item,
                flags=re.I,
            ).strip()

            pk = re.search(r"\bPRIMARY\s+KEY\s*\(([^)]*)\)", normalized, re.I)
            uq = re.search(r"\bUNIQUE\s*\(([^)]*)\)", normalized, re.I)

            if pk:
                primary_keys.add((table, parse_columns(pk.group(1))))
            if uq:
                unique_keys.add((table, parse_columns(uq.group(1))))

            # Inline column-level PRIMARY KEY or UNIQUE.
            if not re.match(
                r"^(PRIMARY\s+KEY|FOREIGN\s+KEY|UNIQUE|CHECK)\b",
                normalized,
                re.I,
            ):
                col = re.match(r'^\s*"?(\w+)"?\s+(.+)$', normalized, re.S)
                if col:
                    name, definition = col.groups()
                    if re.search(r"\bPRIMARY\s+KEY\b", definition, re.I):
                        primary_keys.add((table, (name,)))
                    if re.search(r"\bUNIQUE\b", definition, re.I):
                        unique_keys.add((table, (name,)))

    return primary_keys, unique_keys

def orm_keys():
    primary_keys = set()
    unique_keys = set()

    for table in Base.metadata.tables.values():
        primary_keys.add(
            (table.name, tuple(column.name for column in table.primary_key.columns))
        )
        for constraint in table.constraints:
            if isinstance(constraint, UniqueConstraint):
                unique_keys.add(
                    (table.name, tuple(column.name for column in constraint.columns))
                )

    return primary_keys, unique_keys


sql_pk, sql_unique = sql_keys(sql)
orm_pk, orm_unique = orm_keys()

def report(label, expected, actual):
    missing = expected - actual
    extra = actual - expected

    if not missing and not extra:
        print(f"PASS: {label} match exactly ({len(expected)} definitions).")
        return 0

    print(f"\n{label} mismatch:")
    for item in sorted(missing):
        print("  Missing in ORM:", item)
    for item in sorted(extra):
        print("  Extra in ORM:", item)
    return len(missing) + len(extra)


issues = report("Primary keys", sql_pk, orm_pk)
issues += report("Unique constraints", sql_unique, orm_unique)

if issues:
    print(f"\nPotential key-constraint differences: {issues}")
    raise SystemExit(1)

print("\nPASS: primary-key and unique-constraint audit completed.")
