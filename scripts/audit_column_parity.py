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
    raise ValueError(f"Unbalanced parentheses at character {opening}")


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


def parse_sql_columns(source):
    tables = {}
    pattern = re.compile(r"\bCREATE\s+TABLE\s+(\w+)\s*\(", re.I)

    for match in pattern.finditer(source):
        table_name = match.group(1)
        body = extract_parenthesized(source, match.end() - 1)
        columns = {}

        for item in split_items(body):
            if re.match(
                r"\s*(?:CONSTRAINT\b|PRIMARY\s+KEY\b|FOREIGN\s+KEY\b|"
                r"UNIQUE\b|CHECK\b)",
                item,
                re.I,
            ):
                continue

            column_match = re.match(r'^\s*"?(\w+)"?\s+(.+)$', item, re.S)
            if not column_match:
                continue

            name, definition = column_match.groups()
            type_match = re.match(
                r"(UUID|TEXT|INTEGER|BIGINT|BOOLEAN|JSONB|"
                r"DOUBLE\s+PRECISION|NUMERIC\s*\([^)]*\)|"
                r"TIMESTAMPTZ|TIMESTAMP(?:\s+WITH(?:OUT)?\s+TIME\s+ZONE)?|"
                r"VECTOR(?:\s*\([^)]*\))?)",
                definition,
                re.I,
            )
            if not type_match:
                columns[name] = {
                    "type": "UNPARSED",
                    "nullable": None,
                    "default": None,
                    "raw": definition,
                }
                continue

            sql_type = re.sub(r"\s+", " ", type_match.group(1)).upper()
            remainder = definition[type_match.end():]

            default_match = re.search(
                r"\bDEFAULT\s+(.+?)(?=\s+(?:NOT\s+NULL|NULL|PRIMARY\s+KEY|"
                r"UNIQUE|REFERENCES|CHECK)\b|$)",
                remainder,
                re.I,
            )
            default = default_match.group(1).strip() if default_match else None

            nullable = not bool(re.search(r"\bNOT\s+NULL\b", remainder, re.I))
            if re.search(r"\bPRIMARY\s+KEY\b", remainder, re.I):
                nullable = False

            columns[name] = {
                "type": sql_type,
                "nullable": nullable,
                "default": default,
                "raw": definition,
            }

        tables[table_name] = columns

    return tables


def orm_type(column):
    t = column.type
    name = type(t).__name__.upper()

    if name == "UUID":
        return "UUID"
    if name == "TEXT":
        return "TEXT"
    if name in {"INTEGER", "INT"}:
        return "INTEGER"
    if name in {"BIGINT", "BIGINTEGER"}:
        return "BIGINT"
    if name == "BOOLEAN":
        return "BOOLEAN"
    if name == "JSONB":
        return "JSONB"
    if name in {"FLOAT", "DOUBLE"}:
        return "DOUBLE PRECISION"
    if name == "NUMERIC":
        return f"NUMERIC({t.precision},{t.scale})"
    if name == "TIMESTAMP":
        return "TIMESTAMPTZ" if getattr(t, "timezone", False) else "TIMESTAMP"
    if name == "VECTOR":
        return "VECTOR" if getattr(t, "dim", None) is None else f"VECTOR({t.dim})"
    return name


sql_tables = parse_sql_columns(sql)
issues = 0
type_aliases = {
    ("TIMESTAMPTZ", "TIMESTAMPTZ"),
    ("TIMESTAMP WITH TIME ZONE", "TIMESTAMPTZ"),
}

for table_name in sorted(set(sql_tables) & set(Base.metadata.tables)):
    orm_table = Base.metadata.tables[table_name]

    for column_name in sorted(set(sql_tables[table_name]) & set(orm_table.columns.keys())):
        expected = sql_tables[table_name][column_name]
        actual = orm_table.columns[column_name]

        expected_type = re.sub(r"\s+", "", expected["type"]).upper()
        actual_type = re.sub(r"\s+", "", orm_type(actual)).upper()
        if expected_type != actual_type and (expected_type, actual_type) not in type_aliases:
            print(
                f"TYPE: {table_name}.{column_name}: "
                f"SQL={expected_type}, ORM={actual_type}"
            )
            issues += 1

        if expected["nullable"] is not None and expected["nullable"] != actual.nullable:
            print(
                f"NULLABILITY: {table_name}.{column_name}: "
                f"SQL nullable={expected['nullable']}, ORM nullable={actual.nullable}"
            )
            issues += 1

        if expected["default"] is not None:
            orm_default = (
                str(actual.server_default.arg)
                if actual.server_default is not None
                else None
            )
            if orm_default is None:
                print(
                    f"SERVER DEFAULT: {table_name}.{column_name}: "
                    f"SQL={expected['default']}, ORM=None"
                )
                issues += 1

print()
if issues == 0:
    print("No type, nullability, or present-SQL-default mismatches detected.")
else:
    print(f"Potential column mismatches detected: {issues}")

print(
    "NOTE: This is a first-pass parser. Review reported differences against "
    "the source SQL; absence of a report does not prove every default matches."
)
if issues:
    raise SystemExit(1)
