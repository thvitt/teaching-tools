from pathlib import Path
import pandas as pd
from cyclopts import App
from htbuilder import HtmlElement, div, ul, li, a, strong, br, small

app = App(help_format="markdown", help_on_error=True)


def format_group(
    df: pd.DataFrame,
    module: str = "Module",
    course: str = "Course",
    details: str = "Details",
) -> HtmlElement:
    return div(
        strong(a(df.loc[:, module].iat[0], href=df.loc[:, module + "_link"].iat[0])),
        ul(
            li(a(row[course], href=row[course + "_link"]), br(), small(row[details]))
            for _, row in df.iterrows()
        ),
    )


@app.default()
def main(csv: Path, html: Path | None = None, /):
    """
    Write a HTML course overview from a table exported from WueStudy.

    To prepare,

     1. Go to the Vorlesungsverzeichnis and switch to the language to export
     2. fully expand the courses to export
     3. save the resulting page as html, `source.html`
     4. open source.html in Visidata, open the correct table
     5. save as `source.csv`
     6. `sd "#err" "" source.csv`
     7. `vd --null_value="" source.csv`
     8. now fill missing values, remove unused columns, remove exams
     9. Deduplicate rows using the Details column: Mark the details column as index (`!`), ` select-duplicate-rows`, `gd`, `!` again to unmark the column
    10. adjust the column names such that you have columns `Section`, `Module`, `Module_link`, `Course`, `Course_link`, `Details`

    """
    if csv.suffix == ".tsv":
        table = pd.read_table(csv)
    else:
        table = pd.read_csv(csv)

    if html is None:
        html = csv.with_suffix(".html")

    converted = table.groupby("Module").apply(format_group)
    dom = div(converted)
    html.write_text(str(dom))
