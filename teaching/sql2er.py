from os import fspath
from pathlib import Path
from shutil import copy2
from subprocess import run
from sys import exception
import sys
from tempfile import TemporaryDirectory
from typing import Annotated, Literal

from cyclopts import App, Parameter
from sqlalchemy import URL, Engine, MetaData, create_engine
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


def db2plantuml(engine: Engine) -> str:
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


@app.default
def main(
    db_url: str,
    /,
    output: Annotated[Path | None, Parameter(alias="-o")] = None,
    *,
    format: Annotated[  # noqa: A002
        Literal["puml", "pdf", "html", "latex", "png", "svg", "txt", "utxt"] | None,
        Parameter(alias="-t"),
    ] = None,
):
    """
    Generate a diagram from a database schema.

    The diagram will either be in PlantUML format, or we will call PlantUML to convert it to
    the output format explicitely given or inferred from the output file name

    Args:
        db_url: Either a database URL, or a SQLite database file, or a SQLite SQL ddl / dump file.
        output: Output file. If missing, inferred.
        format: Format of the output file.
    """
    try:
        db_path = Path(db_url)
        if db_path.exists():
            if db_path.suffix == ".sql":
                engine = create_engine("sqlite:///:memory:")
                raw_con = engine.raw_connection()
                raw_cur = raw_con.cursor()
                raw_cur.executescript(db_path.read_text())
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
        output = db_path.with_suffix("." + format)

    puml = db2plantuml(engine)
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
                    copy2(file, output.parent)
