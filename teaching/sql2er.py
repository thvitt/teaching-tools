from subprocess import run
from tempfile import TemporaryDirectory
from questionary import form
from typing import Annotated, Literal
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import create_engine, MetaData, URL
from pathlib import Path
from cyclopts import App, Parameter

app = App()
app.register_install_completion_command(add_to_startup=False)

HEADER = """
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
    format: Annotated[
        Literal["puml", "pdf", "html", "latex", "png", "svg", "txt", "utxt"] | None,
        Parameter(alias="-t"),
    ] = None,
):
    db_path = Path(db_url)
    if db_path.exists():
        if db_path.suffix == ".sql":
            engine = create_engine("sqlite:///:memory:")
            with engine.begin() as connection:
                connection.exec_driver_sql(db_path.read_text())
        else:
            engine = create_engine(URL.create(db_url))
    else:
        engine = create_engine(db_url)

    if format is None:
        format = output.suffix[1:] if output is not None else "puml"  # ty:ignore[invalid-assignment]  # pyright: ignore[reportAssignmentType]
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
            tmpdir / output.with_suffix(".puml").name
