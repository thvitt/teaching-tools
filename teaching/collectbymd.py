from pathlib import Path
from typing import Annotated
from cyclopts import App, Parameter
import pandas as pd
import csv
from rich import progress
from rich.logging import RichHandler
import logging

logger = logging.getLogger(__name__)

app = App()


@app.default
def collect_by_md(
    metadata: Path,
    sources: str,
    targets: str,
    /,
    *,
    output: Annotated[Path, Parameter(["-o", "--output"])] = Path(),
    query: Annotated[str | None, Parameter(["-q", "--query"])] = None,
    verbose: Annotated[bool, Parameter(["-v", "--verbose"])] = False,
):
    """
    Selects specific files according to metadata.

    Args:
        metadata: CSV/TSV file with metadata
        sources: Pattern string to identify the source files. May contain metadata fields from the CSV file like {id}.
        targets: Pattern string to identify the target files. May contain metadata fields from the CSV file like {id}.
        output: root directory for the target files.
        query: pandas query, select only those files.
        verbose: Report what is done, not only errors or warnings.
    """
    logging.basicConfig(
        level=logging.INFO if verbose else logging.WARNING,
        format="%(message)s",
        handlers=[RichHandler(show_time=False)],
    )
    with metadata.open() as f:
        dialect = csv.Sniffer().sniff(f.read(4096))
    md = pd.read_csv(metadata, dialect=dialect())
    logger.info(
        "Read %d records from %s, fields: %s",
        md.index.size,
        metadata,
        md.columns,
    )
    if query:
        md.query(query, inplace=True)
        logger.info("%d remain after query %s", md.index.size, query)
    target = output

    for _, row in progress.track(md.iterrows(), total=md.index.size, transient=True):
        try:
            src = Path(sources.format_map(row))
            dst = target / targets.format_map(row)
            logger.info("%s => %s", src, dst)
            dst.parent.mkdir(exist_ok=True, parents=True)
            dst.write_bytes(src.read_bytes())
        except Exception as e:
            logger.exception(
                "%s: %s handling row %s", type(e), e, "\t".join(map(str, row.values()))
            )


if __name__ == "__main__":
    app()
