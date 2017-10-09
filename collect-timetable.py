#!/usr/bin/env python3
import re
from itertools import chain

from bs4 import BeautifulSoup
from requests import Session
import vobject
import argparse

from vobject.base import VObjectError

url = "https://www-sbhome1.zv.uni-wuerzburg.de/qisserver/rds?state=wtree&search=1&trex=step&root120172=121564|118444|120995&P.vx=kurz"

#
# 1. the navigational tables have a first 'td' with a width attribute that denotes indent, we're only interested in the
#    maximally indented rows

session = Session()

def remove_duplicates(iterable):
    seen = set()
    for item in iterable:
        if item not in seen:
            seen.add(item)
            yield item

def collect_lecture_links(url):
    """
    Sammelt rekursiv links zu Lehrveranstaltungsseiten ausgehend von einer
    Übersichtsseite des Vorlesungsverzeichnis (url).

    Ergebnis kann Duplikate enthalten
    """
    soup = BeautifulSoup(session.get(url).content, 'lxml')
    content = soup.find('div', 'divcontent')
    # on an overview page, there are lots of tables, but mainly two kinds:
    # 1. navigational stuff – table[border='0']
    # 2. actual lecture overviews – no border attribute (but a summary), nested within nav tables
    navtables = content.find_all('table', border=0)

    # to represent indention, the navigational tables contain a first column with a predefined width
    max_indent = max(int(table.find('td').get('width', 0)) for table in navtables)
    # tables w/o width are boring, those with non-maximum width link to parent pages.
    maxlevel_tables = [table for table in navtables if table.find('td', width=max_indent)]

    for table in maxlevel_tables:
        # now these tables may either contain another table with links to lectures ...
        if table.select('table[summary]'):
            for row in table.find_all('tr'):
                if row.find('a', 'regular'):
                    link = row.find('a', 'regular')
                    print('Found lecture page for', link.text.strip())
                    yield link.get('href')
        else:
            # or they don't contain a table but rather links to other overview pages
            links = table.find_all('a')
            if links:  # there are also tables with only text labels
                link = links[-1]
                print('Following subpage', link.text.strip())
                yield from collect_lecture_links(link.get('href'))


def calendar_urls(url):
    """
    Liefert alle iCalendar-URLs zu einer Lehrveranstaltung

    :param url: URL der Lehrveranstaltungsseite
    :return: Liste der URLs mit iCalendar-Daten
    """
    soup = BeautifulSoup(session.get(url).text, 'lxml')
    links = soup.select('a[href]')
    return [a.get('href') for a in links if 'iCalendar' in a.get('href')]

def fix_ics_linebreaks(ics_text):
    lines = []
    for line in re.split('\r?\n', ics_text):
        if ":" in line:
            lines.append(line)
        else:
            lines[-1] += line
    return "\n".join(lines)


def get_events(ics_url: str):
    """
    Lädt das vCalendar-File von ics_url und zieht alle 'Event'-Objekte heraus
    :param ics_url: vCalendar-Datei
    :return: Liste von Event-Objekten
    """
    response = session.get(ics_url)
    try:
        components = vobject.readComponents(fix_ics_linebreaks(response.text), ignoreUnreadable=True)
        for component in components:
            for child in component.getChildren():
                if child.name == 'VEVENT':
                    yield child
    except VObjectError as e:
        print("ERROR parsing", ics_url, ": ", e)


def collect_calendar(root_url: str) -> vobject.icalendar.VCalendar2_0:
    """
    Collects all evens from the
    :param root_url:
    :return:
    """
    cal = vobject.iCalendar()
    lecture_pages = remove_duplicates(collect_lecture_links(root_url))
    ics_urls = chain.from_iterable(calendar_urls(lec) for lec in lecture_pages)
    events = chain.from_iterable(get_events(url) for url in ics_urls)
    for event in events:
        cal.add(event)
    return cal

def getargparser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="""
        Dieses Skript sucht ausgehend von einer SB@Home-Vorlesungsverzeichnis-Seite rekursiv alle zu den Lehrveranstaltungen
        verlinkten Events heraus und speichert sie in einer iCalendar-Datei.
    """)
    parser.add_argument("url", help="SB@Home-Ausgangs-URL")
    parser.add_argument("output", type=argparse.FileType("wt", encoding="UTF-8"), help=".ics-Datei")
    return parser

if __name__ == '__main__':
    options = getargparser().parse_args()
    cal = collect_calendar(options.url)
    cal.serialize(options.output)
