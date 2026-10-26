from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "apps" / "api" / "src"))

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
    raise ValueError("Unbalanced parentheses")


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


def normalize_default(value):
    if value is None:
        return None
    value = re.sub(r"\s+", " ", value).strip().lower()
    value = re.sub(r"\s*\(\s*", "(", value)
    value = re.sub(r"\s*\)\s*", ")", value)
    return value


def parse_defaults(source):
    result = {}
    pattern = re.compile(r"\bCREATE\s+TABLE\s+(\w+)\s*\(", re.I)

    for match in pattern.finditer(source):
        table = match.group(1)
        body = extract_parenthesized(source, match.end() - 1)

        for item in split_items(body):
            if re.match(
                r"\s*(?:CONSTRAINT\b|PRIMARY\s+KEY\b|FOREIGN\s+KEY\b|"
                r"UNIQUE\b|CHECK\b)",
                item,
                re.I,
            ):
                continue

            col_match = re.match(r'^\s*"?(\w+)"?\s+(.+)$', item, re.S)
            if not col_match:
                continue

            column, definition = col_match.groups()
            default_match = re.search(r"\bDEFAULT\s+", definition, re.I)
            if not default_match:
                result[(table, column)] = None
                continue

            value_start = default_match.end()
            remainder = definition[value_start:]
            end_match = re.search(
                r"\s+(?=(?:NOT\s+NULL|NULL|PRIMARY\s+KEY|UNIQUE|"
                r"REFERENCES|CHECK)\b)",
                remainder,
                re.I,
            )
            value = remainder[:end_match.start()] if end_match else remainder
            result[(table, column)] = normalize_default(value)

    return result


sql_defaults = parse_defaults(sql)
issues = 0

for table_name, table in sorted(Base.metadata.tables.items()):
    for column in table.columns:
        expected = sql_defaults.get((table_name, column.name))
        actual = (
            normalize_default(str(column.server_default.arg))
            if column.server_default is not None
            else None
        )

        if expected != actual:
            print(
                f"DEFAULT: {table_name}.{column.name}: "
                f"SQL={expected!r}, ORM={actual!r}"
            )
            issues += 1

if issues == 0:
    print("PASS: SQL and ORM server-default expressions match.")
else:
    print(f"Potential default mismatches: {issues}")
    raise SystemExit(1)
