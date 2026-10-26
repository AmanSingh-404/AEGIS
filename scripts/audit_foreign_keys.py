from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "apps" / "api" / "src"))

from sqlalchemy import ForeignKeyConstraint
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
                return source[opening + 1:i], i + 1
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


def parse_identifier_list(text):
    return tuple(part.strip().strip('"') for part in text.split(","))


def sql_foreign_keys(source):
    result = set()
    table_pattern = re.compile(r"\bCREATE\s+TABLE\s+(\w+)\s*\(", re.I)

    for match in table_pattern.finditer(source):
        table = match.group(1)
        body, _ = extract_parenthesized(source, match.end() - 1)

        for item in split_items(body):
            fk_match = re.search(
                r"\bFOREIGN\s+KEY\s*\(([^)]*)\)\s*REFERENCES\s+"
                r"(\w+)\s*\(([^)]*)\)(.*)",
                item,
                re.I | re.S,
            )
            if not fk_match:
                continue

            local_cols = parse_identifier_list(fk_match.group(1))
            ref_table = fk_match.group(2)
            ref_cols = parse_identifier_list(fk_match.group(3))
            tail = fk_match.group(4)

            on_delete = re.search(
                r"\bON\s+DELETE\s+(CASCADE|RESTRICT|SET\s+NULL|SET\s+DEFAULT|NO\s+ACTION)",
                tail,
                re.I,
            )
            deferrable = bool(re.search(r"\bDEFERRABLE\b", tail, re.I))
            initially_deferred = bool(
                re.search(r"\bINITIALLY\s+DEFERRED\b", tail, re.I)
            )

            result.add((
                table, local_cols, ref_table, ref_cols,
                on_delete.group(1).upper() if on_delete else "NO ACTION",
                deferrable, initially_deferred,
            ))

    # Also parse ALTER TABLE ... ADD CONSTRAINT ... FOREIGN KEY statements.
    alter_pattern = re.compile(
        r"\bALTER\s+TABLE\s+(\w+)\s+ADD\s+CONSTRAINT\s+\w+\s+"
        r"FOREIGN\s+KEY\s*\(([^)]*)\)\s+REFERENCES\s+"
        r"(\w+)\s*\(([^)]*)\)([^;]*);",
        re.I | re.S,
    )

    for match in alter_pattern.finditer(source):
        table, local_text, ref_table, ref_text, tail = match.groups()
        on_delete = re.search(
            r"\bON\s+DELETE\s+(CASCADE|RESTRICT|SET\s+NULL|SET\s+DEFAULT|NO\s+ACTION)",
            tail,
            re.I,
        )
        result.add((
            table,
            parse_identifier_list(local_text),
            ref_table,
            parse_identifier_list(ref_text),
            on_delete.group(1).upper() if on_delete else "NO ACTION",
            bool(re.search(r"\bDEFERRABLE\b", tail, re.I)),
            bool(re.search(r"\bINITIALLY\s+DEFERRED\b", tail, re.I)),
        ))

    # Inline column REFERENCES definitions.
    for match in table_pattern.finditer(source):
        table = match.group(1)
        body, _ = extract_parenthesized(source, match.end() - 1)

        for item in split_items(body):
            column_match = re.match(r'^\s*"?(\w+)"?\s+(.+)$', item, re.S)
            if not column_match:
                continue

            local_col, definition = column_match.groups()
            ref_match = re.search(
                r"\bREFERENCES\s+(\w+)\s*\(([^)]*)\)(.*)",
                definition,
                re.I | re.S,
            )
            if not ref_match:
                continue

            ref_table, ref_text, tail = ref_match.groups()
            on_delete = re.search(
                r"\bON\s+DELETE\s+(CASCADE|RESTRICT|SET\s+NULL|SET\s+DEFAULT|NO\s+ACTION)",
                tail,
                re.I,
            )
            result.add((
                table,
                (local_col,),
                ref_table,
                parse_identifier_list(ref_text),
                on_delete.group(1).upper() if on_delete else "NO ACTION",
                bool(re.search(r"\bDEFERRABLE\b", tail, re.I)),
                bool(re.search(r"\bINITIALLY\s+DEFERRED\b", tail, re.I)),
            ))

    return result


def orm_foreign_keys():
    result = set()
    for table in Base.metadata.tables.values():
        for constraint in table.constraints:
            if not isinstance(constraint, ForeignKeyConstraint):
                continue

            elements = list(constraint.elements)
            result.add((
                table.name,
                tuple(column.name for column in constraint.columns),
                elements[0].column.table.name,
                tuple(element.column.name for element in elements),
                (elements[0].ondelete or "NO ACTION").upper(),
                bool(constraint.deferrable),
                (constraint.initially or "").upper() == "DEFERRED",
            ))
    return result


sql_fks = sql_foreign_keys(sql)
orm_fks = orm_foreign_keys()

def display(item):
    table, local, ref_table, ref_cols, on_delete, deferrable, deferred = item
    return (
        f"{table}{local} -> {ref_table}{ref_cols}; "
        f"ON DELETE {on_delete}; DEFERRABLE={deferrable}; "
        f"INITIALLY_DEFERRED={deferred}"
    )

missing = sql_fks - orm_fks
extra = orm_fks - sql_fks

if not missing and not extra:
    print(f"PASS: all {len(sql_fks)} parsed foreign-key relationships match.")
else:
    if missing:
        print("SQL foreign keys missing or different in ORM:")
        for item in sorted(missing, key=display):
            print(" -", display(item))
    if extra:
        print("ORM foreign keys absent or different in SQL:")
        for item in sorted(extra, key=display):
            print(" -", display(item))
    print(f"\nSQL FK entries: {len(sql_fks)}; ORM FK entries: {len(orm_fks)}")
    raise SystemExit(1)
