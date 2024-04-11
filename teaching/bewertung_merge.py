#!/usr/bin/env python3

from dataclasses import dataclass
from os import fspath
from pathlib import Path
from typing import Iterable, Union

import numpy as np
import pandas as pd
import argparse

import sys

from pandas.core.common import inspect


def first_index_above(value: float, limits: list[float]):
    assert list(limits)
    for idx, limit in enumerate(limits):
        if value < limit:
            return idx - 1
    return idx


def autoload_df(file: str | Path):
    path = Path(file)
    try:
        if path.suffix == ".tsv":
            df = pd.read_csv(fspath(path), sep="\t", header=0)
        elif path.suffix == ".xlsx":
            df = pd.read_excel(fspath(path), 0, header=0)
        elif path.suffix == ".csv":
            df = pd.read_csv(fspath(path), sep=",")
            if len(df.columns) < 2:
                df = pd.read_csv(fspath(path), sep=";")
        else:
            raise ValueError(f"Did not recognize {file}’s type")
        cols = [col for col in df.columns if "mail" in str(col).lower()]
        if cols:
            return df.set_index(cols[0])
        else:
            return df
    except Exception as e:
        raise OSError(f"{type(e)} reading {file}: {e}") from e


@dataclass
class LinearGradeConverter:
    min_worst_grade: float = 16.0
    min_best_grade: float = 39
    grade_steps: tuple[float] = (4.0, 3.7, 3.3, 3.0, 2.7, 2.3, 2.0, 1.7, 1.3, 1.0)
    fail_grade = 5.0

    def __post_init__(self):
        self.lower_limits = np.linspace(
            self.min_worst_grade, self.min_best_grade, len(self.grade_steps)
        )
        print(list(zip(self.lower_limits, self.grade_steps)))

    def grade_for(self, points: float) -> float:
        idx = first_index_above(points, self.lower_limits)
        if idx < 0:
            return self.fail_grade
        else:
            return self.grade_steps[idx]

    def __call__(self, points: Iterable[float], details=False) -> Union[float, dict]:
        total = sum(points)
        result = self.grade_for(total)
        aspects = {"points": points, "total": total, "grade": result}
        print(aspects)
        if details:
            return aspects
        else:
            return result


@dataclass
class InfosysGradeConverter(LinearGradeConverter):
    min_success_tasks: int = 2
    min_success_points: float = 50
    very_good_points: float = 80
    very_good_tasks: int = 2
    good_points: float = 70
    good_tasks_for_13: int = 3
    very_good_tasks_for_13: int = 2
    good_tasks_for_23: int = 2
    max_tasks_used: int = 4

    def __call__(self, points: Iterable[float], details=False) -> Union[dict, float]:
        top_points = sorted(points, reverse=True)
        used_points = top_points[: self.max_tasks_used]
        grade = super().__call__(used_points)

        # mindestens zwei Aufgaben à >= 5.0 zum bestehen:
        if (
            len(top_points) < self.min_success_tasks
            or top_points[self.min_success_tasks - 1] < self.min_success_points
        ):
            grade = self.fail_grade

        # drei sehr gute oder vier gute => min. 1.3
        if (
            top_points[self.very_good_tasks_for_13] >= self.very_good_points
            or top_points[self.good_tasks_for_13] >= self.good_points
        ):
            grade = min(1.3, grade)
        if top_points[self.good_tasks_for_23] >= self.good_points:
            grade = min(2.3, grade)

        if details:
            return {
                "used_points": used_points,
                "eff_sum": sum(used_points),
                "grade": grade,
            }
        else:
            return grade


GRADER_CLASSES = {"linear": LinearGradeConverter, "infosys": InfosysGradeConverter}


def _getargparser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    p.add_argument("csv", nargs="*", help="Bewertung.csv-Dateien", type=Path)
    p.add_argument(
        "-m",
        "--metadata-file",
        type=Path,
        help="CSV-Datei mit Studierendenmetadaten",
    )
    p.add_argument(
        "-M",
        "--metadata-columns",
        nargs="+",
        default=["Matrikel"],
        help="Metadatenfelder aus der Metadatendatei",
    )
    p.add_argument(
        "-t",
        "--column-title",
        choices=["parent", "stem", "path"],
        default="parent",
        help="Spaltentitel für Aufgabe",
    )
    p.add_argument("-o", "--output-file", type=argparse.FileType("wt"), default=None)
    p.add_argument("-g", "--grader", default=None, choices=GRADER_CLASSES.keys())
    p.add_argument(
        "-G",
        "--grader-config",
        help="Configuration options as comma-separated key=value pairs",
    )
    p.add_argument(
        "--help-grader",
        help="Help on selected grader and config",
        action="store_true",
    )
    return p


class GradeTable:
    def __init__(
        self,
        options=None,
        /,
        *,
        csv: list[Path] = [],
        metadata_file=None,
        metadata_columns=["Matrikel"],
        column_title="parent",
        grade_converter=None,
        **kwargs,
    ) -> None:
        if options is not None:
            self.__init__(**options.__dict__)
            return

        if not csv:
            csv = sorted(Path().glob("**/Bewertung.csv"))
        if not csv:
            raise ValueError(
                "Keine Bewertungsdateien angegeben und auch keine in **/Bewertung.csv gefunden."
            )

        self.csv = csv
        self.metadata_file = metadata_file
        self.metadata_columns = list(metadata_columns)
        self.column_title = column_title
        self.grade_converter = grade_converter
        self._load_data()

    def _load_data(self):
        # collect columns and names
        names = {}
        score_tables = {}
        for csv in self.csv:
            df = autoload_df(csv)
            names.update(df["Vollständiger Name"])
            if self.column_title == "parent":
                title = csv.parent.stem
            elif self.column_title == "stem":
                title = csv.stem
            else:
                title = str(csv)
            score_tables[title] = df["Bewertung"]

        result_table = {"Name": names}

        if self.metadata_file:
            md = autoload_df(self.metadata_file)
            md = md[self.metadata_columns]
            result_table.update(md.to_dict())

        result_table.update(score_tables)
        self.results = pd.DataFrame(result_table)
        self.grade_columns = list(score_tables.keys())

    @property
    def grades(self):
        return self.results[self.grade_columns]

    def __str__(self) -> str:
        return self.results.to_markdown()

    def dropna(self, required_submissions=1):
        self.results = self.results.loc[
            self.grades.dropna(thresh=required_submissions).index
        ]

    def add_sum(self, title="Summe"):
        self.results[title] = self.grades.sum(axis=1)

    def add_final_grade(self, title="Note", converter=None, details=False):
        if converter is None:
            converter = self.grade_converter
        if not converter:
            raise ValueError("No grade converter configured")
        final_grades = {}
        for key, grades in self.grades.fillna(0).iterrows():
            top_grades = sorted(grades)
            final_grades[key] = converter(top_grades, details=details)
        if details:
            self.results = self.results.join(pd.DataFrame(final_grades).T)
        else:
            self.results[title] = pd.Series(final_grades)


def main():
    options = _getargparser().parse_args()
    if options.grader:
        Grader = GRADER_CLASSES[options.grader]
        grader_config = {}
        if options.grader_config:
            member_type = {
                name: type(value) for name, value in inspect.getmembers(Grader)
            }
            for opt_str in options.grader_config.split(","):
                key, value = opt_str.split("=")
                grader_config[key] = member_type[key](value)
        options.grade_converter = Grader(**grader_config)
        if options.help_grader:
            grader_help(options.grade_converter)

    table = GradeTable(options)
    table.add_sum()
    table.dropna(2)
    if options.grader:
        table.add_final_grade(details=True)

    if options.output_file:
        table.results.to_csv(options.output_file)
    print(table)


def grader_help(grader):
    import inspect

    doc = inspect.getdoc(grader)
    members = inspect.getmembers(grader)
    print(type(grader).__name__)
    print(doc)
    for name, value in members:
        if not name.startswith("_"):
            print("-", name, "\t", value)
    sys.exit(0)


if __name__ == "__main__":
    main()
