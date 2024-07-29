#!/usr/bin/env python3

from itertools import chain
from pathlib import Path
from typing import Annotated, Literal, Optional, Union

import pandas as pd
import pymustache
from typer import Argument, Typer

app = Typer()


def complete_table():
    return [
        str(p)
        for p in chain(
            Path().glob("*.csv"),
            Path().glob("*.tsv"),
            Path().glob("*.xlsx"),
            Path().glob("*.ods"),
        )
    ]


@app.command()
def convert(
    table: Annotated[
        Path,
        Argument(
            help="Table with source data",
            autocompletion=complete_table,
            exists=True,
        ),
    ],
    template_file: Annotated[
        Path, Argument(help="Mustache template file for each row", exists=True)
    ],
    output: Annotated[Optional[Path], Argument(help="Output file")] = None,
):
    if table.suffix == ".csv":
        data = pd.read_csv(table)
    elif table.suffix == ".tsv":
        data = pd.read_csv(table, sep="\t")
    elif table.suffix == ".xlsx":
        data = pd.read_excel(table)
    elif table.suffix == ".ods":
        data = pd.read_excel(table, engine="odf")
    else:
        raise ValueError(
            f"Unknown input file format: {table.suffix}. Please provide a CSV, TSV, XLSX, or ODS file.",
        )

    template = template_file.read_text()
    result = []
    for _, row in data.iterrows():
        result.append(pymustache.render(template, row))
    result_text = "\n".join(result)
    if output is None:
        print(result_text)
    else:
        output.write_text(result_text)


if __name__ == "__main__":
    app()
