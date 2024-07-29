#!/usr/bin/env python3

from collections import UserDict
from itertools import chain
from pathlib import Path
from typing import Annotated, Optional

import pandas as pd
import pymustache
from typer import Argument, Typer
import logging

logger = logging.getLogger(__name__)

app = Typer()


class LoggingDict(UserDict):

    def __contains__(self, key: object) -> bool:
        contained = super().__contains__(key)
        if not contained:
            logger.error("Template variable %s not found in data", key)
        return contained


def glob_completer(*patterns):
    def completer():
        return list(map(str, chain.from_iterable(Path().glob(p) for p in patterns)))

    return completer


@app.command()
def convert(
    table: Annotated[
        Path,
        Argument(
            help="Table with source data",
            autocompletion=glob_completer("*.csv", "*.tsv", "*.xlsx", "*.ods"),
            exists=True,
        ),
    ],
    template_file: Annotated[
        Path,
        Argument(
            help="Mustache template file for each row",
            exists=True,
            autocompletion=glob_completer("*.md", "*.tmpl"),
        ),
    ],
    output: Annotated[Optional[Path], Argument(help="Output file")] = None,
):
    logging.basicConfig(level=logging.INFO)
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
    data = data.dropna(subset=data.columns[0])
    logger.info("Data table:\n%s", data)
    template = template_file.read_text()
    result = []
    for _, row in data.iterrows():
        result.append(pymustache.render(template, LoggingDict(row.to_dict())))
    result_text = "\n".join(result)
    if output is None:
        print(result_text)
    else:
        output.write_text(result_text)


if __name__ == "__main__":
    app()
