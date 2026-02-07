import sys
from os import fspath
from pathlib import Path
from shutil import copy2
from subprocess import run
from tempfile import TemporaryDirectory
from typing import Annotated, Literal

from cyclopts import App, Parameter
from cyclopts.types import StdioPath
from sqlalchemy import (
    URL,
    Engine,
    MetaData,
    create_engine,
)
from sqlalchemy.exc import SQLAlchemyError

app = App()
app.register_install_completion_command(add_to_startup=False)  # pyright: ignore[reportUnknownMemberType]

HEADER = """@startuml
skinparam shadowing true
skinparam ClassFontStyle bold
hide circle
hide empty methods
left to right direction

!define table(x) class x 
!define PK(x) <u>x</u>
!define NN(x) *x
!define UQ(x) x <color:blue>UQ</color>
!define col(name,type) name: <color:gray>type</color>
"""

HEADER_ER = """@startuml
skinparam shadowing true
skinparam ClassFontStyle bold
skinparam linetype ortho
hide circle
hide empty methods
left to right direction

!define table(x) class x 
!define PK(x) <u>x</u>
"""


def db2plantuml(engine: Engine) -> str:
    """
    Extract a PlantUML database diagram from a database.
    """
    metadata = MetaData()
    try:
        metadata.reflect(bind=engine)
    except SQLAlchemyError:
        metadata.reflect(bind=engine, resolve_fks=False)

    lines: list[str] = []
    relations: list[str] = []

    for table in metadata.tables.values():
        try:
            lines.append(f"table({table.name})  {{")

            for col in table.columns:
                colstr = f"col({col.name},{col.type})"
                if col.primary_key:
                    colstr = f"PK({colstr})"
                if not col.nullable:
                    colstr = f"NN({colstr})"
                if col.unique:
                    colstr = f"UQ({colstr})"
                lines.append("    {field} " + colstr)

                for fk in col.foreign_keys:
                    relations.append(
                        f"{table.name}::{col.name} --> {fk.target_fullname.replace('.', '::')}"
                    )
        except Exception as e:
            print(e)

        lines.append("}\n")

    return "\n".join([HEADER, *lines, "\n\n", *relations, "@enduml\n"])


def db2er(engine: Engine) -> str:
    """
    Try to extract an ER model from a database.
    """
    metadata = MetaData()
    try:
        metadata.reflect(bind=engine)
    except SQLAlchemyError:
        metadata.reflect(bind=engine, resolve_fks=False)

    relationships: list[str] = []
    ignore_tables: set[str] = set()

    # first, look n:m relationships
    for table in metadata.tables.values():
        if len(table.foreign_key_constraints) == 2:
            fk1, fk2 = table.foreign_key_constraints
            if set(fk1.column_keys) | set(fk2.column_keys) == set(table.columns.keys()):
                relationships.append(
                    f'{fk1.referred_table.name} }}o--o{{ {fk2.referred_table.name}: "{table.name}"'
                )
                ignore_tables.add(table.name)

    lines: list[str] = []

    # now, go through the remaining tables
    for table in metadata.tables.values():
        # skip coupling tables
        if table.name in ignore_tables:
            continue

        # foreign key constraints originating here are converted to relationships
        rel_columns: set[str] = set()
        for fk in table.foreign_key_constraints:
            source = table.name
            target = fk.referred_table.name
            rel_columns |= set(fk.column_keys)
            rel_name = fk.column_keys[0]
            opt_source = "o" if fk.elements[0].column.nullable else "|"
            opt_target = "o" if fk.columns[0].nullable else "|"
            relationships.append(
                f"{source} }}{opt_target}--{opt_source}| {target}: {rel_name}"
            )

        lines.append(f"table({table.name})  {{")
        for column in table.columns:
            if column.name in rel_columns:
                continue
            colstr = column.name
            if column.primary_key:
                colstr = f"PK({colstr})"
            lines.append("    {field} " + colstr)
        lines.append("}\n")

    return "\n".join([HEADER_ER, *lines, "\n\n", *relationships, "@enduml\n"])


def engine_from_ddl(ddl: str) -> Engine:
    engine = create_engine("sqlite:///:memory:")
    raw_con = engine.raw_connection()
    raw_cur = raw_con.cursor()
    raw_cur.executescript(ddl)
    return engine


@app.default
def main(
    db_url: Annotated[str, Parameter(allow_leading_hyphen=True)],
    /,
    output: Annotated[StdioPath | None, Parameter(alias="-o")] = None,
    *,
    format: Annotated[  # noqa: A002
        Literal["puml", "pdf", "html", "latex", "png", "svg", "txt", "utxt"] | None,
        Parameter(alias="-t"),
    ] = None,
    er: Annotated[bool, Parameter(alias="-e", negative=False)] = False,
):
    """
    Generate a diagram from a database schema.

    The diagram will either be in PlantUML format, or we will call PlantUML to convert it to
    the output format explicitely given or inferred from the output file name

    Args:
        db_url: Either a database URL, or a SQLite database file, or a SQLite SQL ddl / dump file, or "-" to read SQL from stdin.
        output: Output file. If missing, inferred. If "-", the output is written to stdout.
        format: File format of the output.
        er: try to reverse-engineer an ER diagram instead of the DB diagram.
    """
    try:
        db_path = StdioPath(db_url)
        if db_path.is_stdio:
            engine = engine_from_ddl(sys.stdin.read())
        elif db_path.exists():
            if db_path.suffix == ".sql":
                engine = engine_from_ddl(db_path.read_text())
            else:
                engine = create_engine(URL.create(drivername="sqlite", database=db_url))
        else:
            engine = create_engine(db_url)
    except SQLAlchemyError as e:
        print("ERROR: Could not open database %s: %s", db_url, e)
        sys.exit(1)

    if format is None:
        format = output.suffix[1:] if output is not None else "puml"  # ty:ignore[invalid-assignment]  # pyright: ignore[reportAssignmentType]  # noqa: A001
    elif output is None:
        if er:
            output = StdioPath(
                db_path.with_name(db_path.stem + "-er").with_suffix("." + format)
            )
        else:
            output = StdioPath(db_path.with_suffix("." + format))

    puml = db2er(engine) if er else db2plantuml(engine)
    if format == "puml":
        if output is None:
            print(puml)
        else:
            output.write_text(puml)
    else:
        with TemporaryDirectory() as tmpdir:
            assert output is not None
            tmp_puml = Path(tmpdir) / output.with_suffix(".puml").name
            tmp_puml.write_text(puml)
            run(["plantuml", f"-t{format}", "-o", tmpdir, fspath(tmp_puml)])
            for file in Path(tmpdir).iterdir():
                if file.is_file() and file.suffix != ".puml":
                    if output.is_stdio:
                        output.write_bytes(file.read_bytes())
                    else:
                        copy2(file, output.parent)
