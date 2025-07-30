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
    sample_by: Annotated[str | None, Parameter(["-s", "--sample-by"])] = None,
    sample_size: Annotated[int, Parameter(["-n", "--sample-size"])] = 1,
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
        sample_by: group by this column and randomly select sample-size items from each group
        sample_size: number of items to sample from each group
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
    if sample_by is not None:
        md = (
            md.groupby(sample_by)
            .apply(pd.DataFrame.sample, n=sample_size)
            .reset_index(drop=True)
        )
        logger.info(
            "Grouped by %s and sampled %d files from each group, selecting a total of %d files",
            sample_by,
            sample_size,
            md.index.size,
        )

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
