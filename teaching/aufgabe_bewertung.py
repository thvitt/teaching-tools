#!/usr/bin/python3
from operator import attrgetter
from pathlib import Path
from tempfile import mkstemp
from subprocess import run
from typing import List, Dict

from blessings import Terminal
from more_itertools import one
try:
    from readchar import key, readkey
except ImportError as e:
    print("Failed to import readkey module. Interactions will fail.", e)
import os
import sys
import re
import csv

GRADE_FIELD = 'Bewertung'

NAME_FIELD = 'Vollständiger Name'

COMMENT_FIELD = 'Feedback als Kommentar'

filename = sys.argv[1] if len(sys.argv) > 1 else "Bewertung.md"
t = Terminal()

GRADE = re.compile('^([0-9,.]+(/[0-9]+)?|b|nb)\s*$')
NAME = re.compile('^## ([^_\n]+)(_.*)?')


class Bewertung:

    def __init__(self, name, lines=None, common_note=None):
        self.name = name
        self.lines = [] if lines is None else lines
        self.filename = None
        if common_note and isinstance(common_note, str):
            common_note = [common_note]
        self.common_note = common_note

    def append(self, *args):
        self.lines.extend(args)

    @property
    def grade(self):
        matches = [GRADE.match(line) for line in self.lines]
        grades = [match.group(1) for match in matches if match is not None]
        if len(grades) == 0:
            return ""
        elif "/" in grades[-1]:
            grade = grades[-1].split("/")[0]
            if grade.isnumeric():
                return float(grade)
            else:
                return grade
        else:
            return grades[-1]

    @property
    def text(self):
        lines = self.lines
        if self.common_note:
            lines += ['', '----', ''] + self.common_note
        return '\n'.join(lines)

    @property
    def lastname(self):
        return self.name.split()[-1]

    def mktemp(self):
        if self.filename:
            return  # already done

        fd, self.filename = mkstemp(suffix='.md', prefix='bewertung', text=True)
        with open(fd, mode="w", encoding='utf-8') as f:
            f.writelines(self.lines)

    def copy(self):
        self.mktemp()
        run("pandoc -t html -f markdown -i '{}' | xclip -i -selection clipboard -t text/html"
            .format(self.filename), shell=True)

    def to_html(self):
        pandoc = run(["pandoc", "-t", "html", "-f", "markdown"], input=self.text, text=True, capture_output=True)
        return pandoc.stdout

    def close(self):
        if self.filename is not None:
            os.remove(self.filename)
            self.filename = None

    def __str__(self):
        return (self.name
                + "=" * len(self.name)
                + "\n\n"
                + "".join(self.lines)
                + "\n\n")


def read(filename):
    """
    Liest eine Bewertungsdatei ein.

    Args:
        filename (str): Bewertungsdateiname

    Returns:
        Liste von :class:`Bewertung`en
    """
    bewertungen = []
    text = '\n' + Path(filename).read_text()
    parts = text.split('\n## ')
    preamble = parts[0].strip()
    
    for section in parts[1:]:
        lines = section.strip().split('\n')
        names = lines[0].split('; ')
        for name in names:
            bewertungen.append(Bewertung(name, lines[1:], common_note=preamble))
    
    return bewertungen


def prepare_input_file(filename, moodle_csv=None):
    with open(filename, "wt", encoding="utf-8") as file:
        if moodle_csv:
            with moodle_csv.open() as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if 'abgegeben' in row['Status']:
                        file.write(f"## {row['Vollständiger Name']}\n\n")
                    if 'spät' in row['Status']:
                        file.write(f"* {row['Status']}\n\n")
        else:
            names = {fn.split('_')[0] for fn in os.listdir()}
            lines = sorted(["## {}\n\n".format(name) for name in names])
            file.writelines(lines)

    print("Bewertungstemplate nach {} geschrieben.".format(filename))
    sys.exit(0)


def main():
    options = getargparser().parse_args()
    if options.markdown_file.exists():
        bewertungen = sorted(read(options.markdown_file), key=attrgetter('name'))
    else:
        prepare_input_file(options.markdown_file, options.moodle_csv)
        return
    try:
        grades = [float(bewertung.grade) for bewertung in bewertungen]
        print("Durchschnittsbewertung: ", t.red(str(sum(grades) / len(grades))))
    except ValueError:
        pass  # b/nb -> kein Durchschnitt

    if options.moodle_csv:
        augment_moodle_csv(bewertungen, options.moodle_csv, options.markdown_file.with_suffix('.csv'))

    if options.interactive:
        display_bewertungen(bewertungen)


def display_bewertungen(bewertungen):
    index = 0
    while 0 <= index < len(bewertungen):
        bewertung = bewertungen[index]
        try:
            bewertung.copy()
            print(t.bold(bewertung.name), "\t", "Bewertung:", t.red(str(bewertung.grade)))
            print(bewertung.text, '\n')

            prompt = True
            while prompt:
                print(t.green("#{}/{}:".format(index + 1, len(bewertungen))),
                      "{} ({})".format(bewertung.name, bewertung.grade),
                      "↑ {t.bold}p{t.normal}revious, ↓⏎ {t.bold}n{t.normal}ext, {t.bold}c{t.normal}opy again, {t.bold}q{t.normal}uit"
                      .format(t=t), end=' > ', flush=True)
                ch = readkey()
                if ch in ["p", "P", key.UP, key.BACKSPACE]:
                    print("previous")
                    index -= 1
                    prompt = False
                elif ch in ["n", "N", key.DOWN, key.ENTER]:
                    print("next")
                    index += 1
                    prompt = False
                elif ch in ["c", "C", "r", "R"]:
                    print("copy again")
                    bewertung.copy()
                    prompt = True
                elif ch in ["q", "Q", key.CTRL_C]:
                    print("quit")
                    return
        finally:
            bewertung.close()


def augment_moodle_csv(bewertungen: List[Bewertung], moodle_csv: Path, output: Path = None):
    by_name: Dict[str, Bewertung] = {bew.name: bew for bew in bewertungen}

    with moodle_csv.open() as infile:
        reader = csv.DictReader(infile)
        lines = list(reader)
        fieldnames = list(reader.fieldnames)

    if COMMENT_FIELD not in fieldnames:
        print('Unter Aufgabe / Feedback [x] Feedback als Kommentar ankreuzen und Bewertungtabelle neu exportieren')
        fieldnames.append(COMMENT_FIELD)

    if output is None:
        moodle_csv.replace(moodle_csv.with_suffix(moodle_csv.suffix + '~'))
        output = moodle_csv

    with output.open('wt') as outfile:
        writer = csv.DictWriter(outfile, fieldnames)
        writer.writeheader()
        found = set()
        not_found = set()
        for line in lines:
            name = line[NAME_FIELD]
            if name in by_name:
                line[GRADE_FIELD] = by_name[name].grade
                line[COMMENT_FIELD] = by_name[name].to_html()
                if 'Status' in fieldnames:
                    line['Status'] = 'Freigegeben'
                if 'Bewerter/in' in fieldnames:
                    line['Bewerter/in'] = 'Thorsten Vitt'
                found.add(name)
            else:
                not_found.add(name)
            writer.writerow(line)

    print(f'{len(found)} Kursteilnehmer wurden bewertet, {len(not_found)} nicht.')
    if not_found: print(' - fehlend:', ', '.join(not_found))
    missed = set(by_name) - found
    if missed:
        print(f'!!! {len(missed)} Bewertete sind nicht der Kurstabelle: {", ".join(missed)}')


def export_simple_csv(bewertungen, outfile):
    with open(outfile, "wt", encoding="utf-8") as csvout:
        writer = csv.writer(csvout)
        writer.writerow(["Name", "Bewertung"])
        for bewertung in bewertungen:
            writer.writerow([bewertung.name, bewertung.grade])


def getargparser():
    default_md = Path('Bewertung.md')
    default_csv = None
    csvs = Path().glob('*.csv')
    foreign_csvs = set(csvs) - {default_md.with_suffix('.csv')}
    if len(foreign_csvs) == 1:
        default_csv = one(foreign_csvs)

    import argparse
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter,description="""
    Tool für einen Offline-Bewertungsworkflow.
    
    Die Grundlage ist eine Markdown-Datei (Bewertung.md), in der für jede_n Student_in
    ein Abschnitt ('##'-Ebene) mit Feedback steht. Die letzte Zeile enthält ausschließlich
    die Punktzahl.
    
    Das Skript kann Bewertungen und Feedback aus dieser Datei nach HTML konvertieren und
    in eine Bewertungstabelle, wie sie aus Moodle / WueCampus kommt, eintragen oder 
    pro Teilnehmer_in in die Zwischenablage kopieren. Es kann auch eine leere Vorlage 
    erzeugen.
    """)
    parser.add_argument('markdown_file', default=default_md, type=Path, nargs='?',
                        help="Markdown-Datei fürs Feedback. Ein '##'-Abschnitt pro Student_in, "
                             "Zeile mit nur der Punktzahl für die Bewertung."
                             "Existiert die Datei nicht, wird sie erzeugt und das Skript endet.")
    parser.add_argument('-m', '--moodle-csv', type=Path, nargs='?', default=default_csv,
                        help="Bewertungsexportdatei aus Moodle")
    parser.add_argument('-i', '--interactive', action='store_true',
                        help="die Bewertungsergebnisse interaktiv präsentieren und kopieren")
    return parser


if __name__ == '__main__':
    main()
