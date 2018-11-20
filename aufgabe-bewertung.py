#!/usr/bin/env python3
from operator import attrgetter
from tempfile import mkstemp
from subprocess import run
from blessings import Terminal
from readchar import key, readkey
import os
import sys
import re
import csv

filename = sys.argv[1] if len(sys.argv) > 1 else "Bewertung.md"
t = Terminal()

GRADE = re.compile('^([0-9,.]+(/[0-9]+)?|b|nb)\s*$')
NAME = re.compile('^## ([^_\n]+)(_.*)?')

class Bewertung:

    def __init__(self, head, lines=None):
        self.head = head
        self.lines = [] if lines is None else lines
        self.filename = None
        self.name = NAME.match(head).group(1)

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
        return "".join(self.lines)

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

    def close(self):
        if self.filename is not None:
            os.remove(self.filename)
            self.filename = None

    def __str__(self):
        return (self.head
                + "="*len(self.head)
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
    with open(filename) as file:
        bewertung = None
        for line in file:
            if NAME.match(line):
                if bewertung: bewertungen.append(bewertung)
                bewertung = Bewertung(line)
            else:
                if bewertung: bewertung.append(line)
        bewertungen.append(bewertung)
    return bewertungen

def prepare_input_file(filename):
    names = {fn.split('_')[0] for fn in os.listdir()}
    lines = sorted(["## {}\n\n".format(name) for name in names])
    with open(filename, "wt", encoding="utf-8") as file:
        file.writelines(lines)
    print("Bewertungstemplate nach {} geschrieben.".format(filename))
    sys.exit(0)



def main(argv):
    infile = argv[1] if len(argv) > 1 else "Bewertung.md"
    try:
        bewertungen = sorted(read(infile), key=attrgetter('lastname'))
    except FileNotFoundError:
        prepare_input_file(infile)

    index = 0

    basename, _ = os.path.splitext(infile)
    with open(basename + ".csv", "wt", encoding="utf-8") as csvout:
        writer = csv.writer(csvout)
        writer.writerow(["Name", "Bewertung"])
        for bewertung in bewertungen:
            writer.writerow([bewertung.name, bewertung.grade])

    try:
        grades = [float(bewertung.grade) for bewertung in bewertungen]
        print("Durchschnittsbewertung: ", t.red(str(sum(grades) / len(grades))))
    except ValueError:
        pass # b/nb -> kein Durchschnitt

    while 0 <= index < len(bewertungen):
        bewertung = bewertungen[index]
        try:
            bewertung.copy()
            print(t.bold(bewertung.name), "\t", "Bewertung:", t.red(str(bewertung.grade)))
            print(bewertung.text, '\n')

            prompt = True
            while prompt:
                print(t.green("#{}/{}:".format(index+1, len(bewertungen))),
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



if __name__ == '__main__':
    main(sys.argv)
