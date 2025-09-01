from pathlib import Path
from typing import TYPE_CHECKING, Any, Type, cast
from csv import DictReader

if TYPE_CHECKING:
    from openpyxl.cell import _CellGetValue  # pyright: ignore[reportPrivateUsage]

from attr import dataclass
from openpyxl.styles.fonts import Font
from openpyxl.styles.named_styles import NamedStyle
from openpyxl.worksheet.worksheet import Worksheet
import questionary
from openpyxl import Workbook, load_workbook
from typer import Typer
import logging

logger = logging.getLogger(__name__)

app = Typer()


class InvalidForm(ValueError): ...


def parse_his_sheet(file: Path):
    """
    Parses a single HIS sheet. Returns a dictionary mapping column heading to value for each student.
    """
    try:
        wb = load_workbook(file)
        ws = wb.active
        assert ws is not None
        rows = ws.iter_rows()
        while next(rows)[0].value != "startHISsheet":
            pass
        headings = tuple(str(cell.value) for cell in next(rows))
        raw_records: list[tuple[_CellGetValue, ...]] = []
        while record := next(rows):
            if record[0].value == "endHISsheet":
                break
            raw_records.append(tuple(cell.value for cell in record))
        return [dict(zip(headings, record)) for record in raw_records]
    except StopIteration:
        raise InvalidForm(f"{file} is not a HIS table")


@dataclass
class TaskAssessmentA:
    full_name: str
    grade: float
    max_grade: float


@dataclass
class TaskAssessmentB:
    name: str
    given_name: str
    id: int
    grade: float


def _convert[T, D](
    value: Any,  # pyright: ignore[reportExplicitAny]
    type_: type[T],
    default: D | None = None,
) -> T | D:
    try:
        return type_(value)  # pyright: ignore[reportCallIssue]
    except ValueError:
        if default is None:
            return type_()
        else:
            return default


def parse_wuecampus_sheet(file: Path):
    """
    Parses a WueCampus sheet in CSV form.

    There are actually two kinds of sheet:

    (1) a single task sheet ID with the fields
         "Vollständiger Name", E-Mail-Adresse, Status, Bewertung, Bestwertung,
         "Bewertung kann geändert werden", "Zuletzt geändert (Abgabe)",
         "Zuletzt geändert (Bewertung)", "Feedback als Kommentar"

    (2) the total sheet that can be exported from the _Bewertungen_ section of wuecampus.
        This file contains fields Vorname, Nachname, Matrikelnr., Institution, Studiengang, E-Mail-Adresse,
        then for each task a field starting with "Aufgabe: ", and then a few summary fields
    """
    with file.open(newline="") as csvfile:
        records = list(DictReader(csvfile))

    if "Bewertung" in records[0]:  # single task
        if file.stem == "Bewertung":
            task_name = file.parent.stem
        else:
            task_name = file.stem.split("-")[2]
        students = [
            TaskAssessmentA(
                full_name=record["Vollständiger Name"],
                grade=_convert(record["Bewertung"], float),
                max_grade=_convert(record["Bestwertung"], float),
            )
            for record in records
        ]
        return {task_name: students}
    else:
        result = {}
        for field in records[0]:
            if field.startswith("Aufgabe: "):
                task_name = field[8:].strip()
                students = [
                    TaskAssessmentB(
                        name=record["Nachname"],
                        given_name=record["Vorname"],
                        id=_convert(record["Matrikelnr."], int),
                        grade=_convert(record[field], float),
                    )
                    for record in records
                ]
                result[task_name] = students
    return records


def parse_his_sheets(files: list[Path]):
    result: list[dict[str, _CellGetValue]] = []
    for file in files:
        try:
            result.extend(parse_his_sheet(file))
        except InvalidForm as e:
            logger.warning(e)
    return result


def create_grade_mapping(wb: Workbook) -> Worksheet:
    ws = cast(Worksheet, wb.create_sheet("Notenverteilung"))
    note_lookup = [
        ["Untergrenze", "Note"],
        [0.0, 5.0],
        [0.50, 4.0],
        [0.55, 3.7],
        [0.60, 3.3],
        [0.65, 3.0],
        [0.70, 2.7],
        [0.75, 2.3],
        [0.80, 2.0],
        [0.85, 1.7],
        [0.90, 1.3],
        [0.95, 1.0],
    ]
    for row in note_lookup:
        ws.append(row)
    heading = NamedStyle("Heading", font=Font(name="Ubuntu", bold=True, size=12))
    for row in ws.iter_rows(1, 1, 1, 2):
        for cell in row:
            cell.style = heading
    for row in ws.iter_rows(2):
        row[0].number_format = "0%"
        row[0].font = Font(name="Ubuntu")
        row[1].number_format = "0.0"
        row[1].font = Font(name="Ubuntu", bold=True)
    return ws


@app.command()
def create(sources: list[Path], output: Path):
    n_klausur = int(
        questionary.text(
            "Wieviele Klausuraufgaben gibt es ungefähr?",
            validate=lambda text: text.isdigit() and int(text) >= 0,  # pyright: ignore[reportUnknownMemberType, reportUnknownLambdaType, reportUnknownArgumentType]
        ).ask()
    )
    klausur_text = " ".join(f"K{i}" for i in range(1, n_klausur + 1))
    klausur_text = questionary.text(
        "Aufgabenüberschriften, durch Leerzeichen getrennt?", default=klausur_text
    ).ask()
    klausur_headings = klausur_text.split()

    headings = ["Matrikelnummer", "Nachname", "Vorname", "PrüfungsNr."]
    headings.extend(klausur_headings)
    headings.extend(["Summe", "Prozent", "Note"])

    grades_wb = Workbook()
    grades_ws = grades_wb.active
    grades_ws.title = "Bewertung"  # pyright: ignore[reportOptionalMemberAccess]
    grades_mapping = create_grade_mapping(grades_wb)
    assert grades_ws is not None
    grades_ws.append(headings)
    grades_ws.append(["", "", "", "Max."] + [""] * len(klausur_headings))
    students = parse_his_sheets(sources)

    for student in students:
        record = [student.get(h) for h in headings[:4]]
        record.extend([None for _ in klausur_headings])
        grades_ws.append(record)

    total_idx = 1 + len(headings) - 3
    total_coor = grades_ws.cell(2, total_idx).coordinate
    grades_ws.cell(
        2, total_idx, f"=SUM(E2:{grades_ws.cell(2, total_idx - 1).coordinate})"
    )
    for row in range(3, 3 + len(students)):
        total = grades_ws.cell(
            row,
            total_idx,
            f"=SUM({grades_ws.cell(row, 5).coordinate}:{grades_ws.cell(row, total_idx - 1).coordinate})",
        )
        total.number_format = "0.0"
        percent = grades_ws.cell(
            row,
            total_idx + 1,
            f"={grades_ws.cell(row, total_idx).coordinate} / {total_coor}",
        )
        percent.number_format = "00.0%"
    grades_wb.save(output)


if __name__ == "__main__":
    app()
