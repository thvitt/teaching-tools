from sqlalchemy.exc import SQLAlchemyError
from numpy import False_
from sqlalchemy import create_engine, MetaData, URL
import sys
from pathlib import Path

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


def main():
    arg = sys.argv[1]
    if Path(arg).exists():
        engine = create_engine(URL.create("sqlite", database=arg))
    else:
        engine = create_engine(arg)
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

    print("@startuml")
    print(HEADER)
    print("\n".join(lines))
    print()
    print("\n".join(relations))
    print("@enduml")


if __name__ == "__main__":
    main()
