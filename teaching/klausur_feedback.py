from typing import Annotated, Any, Optional
from pathlib import Path
from csv import DictReader, Sniffer, DictWriter
import typer
import chevron
from subprocess import run
import sys

app = typer.Typer()


def template_keys(template: str) -> set[str]:
    result: set[str] = set()
    for kind, value in chevron.tokenizer.tokenize(template):
        if kind != "literal":
            result.add(value)
    return result


def read_csv(csv: Path, delimiters: Optional[str] = None) -> list[dict[str, Any]]:
    with csv.open(newline="") as file:
        dialect = Sniffer().sniff(file.read(1024), delimiters)
        file.seek(0)
        reader = DictReader(file, dialect=dialect)
        return list(reader)


@app.command()
def main(
    grade_csv: Annotated[
        Path, typer.Argument(exists=True, dir_okay=False, help="CSV-Datei mit Noten")
    ],
    template: Annotated[
        Path, typer.Argument(exists=True, dir_okay=False, help="Template für Feedback")
    ],
    moodle_input: Annotated[
        Path,
        typer.Argument(
            exists=True, dir_okay=False, help="Offline-Bewertungstabelle aus Moodle"
        ),
    ],
    moodle_output: Annotated[
        Optional[Path], typer.Argument(help="Ausgabe-Bewertungstabelle")
    ] = None,
    grade_key: Annotated[
        str, typer.Option("-g", "--grade-key", help="Name der Spalte mit der Bewertung")
    ] = "Note",
):

    grades = read_csv(grade_csv)
    grades_by_addr = {row["Mail"]: row for row in grades}
    template_ = template.read_text()
    feedback_table = read_csv(moodle_input, delimiters=",")
    result = {row["E-Mail-Adresse"]: row for row in feedback_table}

    tmpl_keys = template_keys(template_)
    grade_keys = set(grades[0].keys())

    if tmpl_keys - grade_keys:
        print(
            f"[ERROR] The template keys {tmpl_keys - grade_keys} are missing from the grade table!",
            file=sys.stderr,
        )
    if grade_keys - tmpl_keys:
        print(
            f"[INFO] The keys {grade_keys - tmpl_keys} will not be represented in the feedback",
            file=sys.stderr,
        )

    for mail, row in grades_by_addr.items():
        feedback = chevron.render(template_, row)
        feedback_html = run(
            ["pandoc"], input=feedback, capture_output=True, text=True
        ).stdout
        result[mail]["Feedback als Kommentar"] = feedback_html
        result[mail]["Bewertung"] = row[grade_key]

    result_rows = list(result.values())
    if moodle_output:
        with moodle_output.open("wt") as f:
            DictWriter(f, fieldnames=result_rows[0].keys()).writerows(result_rows)
    else:
        DictWriter(sys.stdout, fieldnames=result_rows[0].keys()).writerows(result_rows)
