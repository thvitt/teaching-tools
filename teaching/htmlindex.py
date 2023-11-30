from collections import defaultdict
from datetime import datetime
from typing import Annotated, Optional
import html5lib
import typer
from pathlib import Path
import xml.etree.ElementTree as ET
from tqdm import tqdm as track
import humanize
import re


app = typer.Typer()

template = """
<!doctype html>
<html>
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=yes" />
<style>
  a:link {
    text-decoration: none;
    color: inherit;
  }

  a:link:hover {
    text-decoration: underline;
  }
  tr:hover {
      background-color: hsl(90, 30%, 80%); 
  }

  tr.ol {
      opacity: 0.5;
  }

  /* filename column */
  td.path {
    text-align: right;
    color: gray;
  }

  td.n { font-weight: bold; font-size: 16pt; text-align: right; }

  td.title {
    font-weight: bold;
    font-size: 16pt;
  }

  td.size { text-align: right; }
  td.variants { color: gray; font-variant: italic; }

  a.anchor-link {
    display: none;
  }

  table {
    margin-inline: auto;
  }
</style>
<title>{title}</title>
</head>
<body>
</body>


</html>
"""


def get_heading(path: Path):
    doc = html5lib.parse(path.read_bytes(), namespaceHTMLElements=False)
    el = None
    for pattern in [".//h1", ".//h2", ".//h3", ".//p", ".//title"]:
        el = doc.find(pattern)
        if el is not None:
            break
    return el


def h(tag: str, *args, parent: Optional[ET.Element] = None, **attrib):
    if "class_" in attrib:
        attrib["class"] = attrib["class_"]
        del attrib["class_"]
    if parent:
        el = ET.SubElement(parent, tag, attrib)
    else:
        el = ET.Element(tag, attrib)
    if len(args) == 1 and isinstance(args[0], str):
        el.text = args[0]
    elif args:
        el.extend(args)
    return el


@app.command()
def prepare_index(
    files: list[Path],
    output: Annotated[Optional[Path], typer.Option("-o", "--output")] = None,
    print_title: Annotated[
        bool,
        typer.Option("-1", "--print-title", help="print only the first file’s title"),
    ] = False,
):
    if print_title:
        heading = get_heading(files[0])
        if heading:
            print(heading.text)
            return 0
        else:
            return 1

    titles_ = []
    for path in track(files, desc="Building index"):
        titles_.append((path, get_heading(path)))

    # group by equal title
    titles = defaultdict(list)
    title_els = {}
    for path, h1 in titles_:
        titles[h1.text].append(path)
        title_els[h1.text] = h1

    index = html5lib.parse(template, namespaceHTMLElements=False)
    body = index.find("body")
    table = ET.SubElement(body, "table")

    for title, paths in titles.items():
        by_len = sorted(paths, key=lambda p: len(p.stem))
        path = by_len[0]
        variants = {p.stem.replace(path.stem, ""): p for p in by_len[1:]}

        tr = ET.SubElement(table, "tr")
        tr.append(h("td", h("a", path.stem, href=path.as_posix()), class_="path"))

        n_match = re.match(r"(\d+[A-Za-z]*)[-_].*", path.stem)
        n = "" if n_match is None else (re.sub(r"^0*", "", n_match.group(1)) + ".")
        tr.append(h("td", n, class_="n"))

        h1 = title_els[title]
        h1.tag = "a"
        h1.set("href", path.as_posix())
        tr.append(h("td", h1, class_="title"))

        mtime = datetime.fromtimestamp(path.stat().st_mtime)
        tr.append(h("td", mtime.strftime("%Y-%m-%d %H:%M"), class_="time"))
        tr.append(h("td", humanize.naturalsize(path.stat().st_size), class_="size"))

        if variants:
            var_td = h("td", parent=tr, class_="variants")
            for label, var_path in variants.items():
                var_td.append(h("span", " · "))
                var_td.append(h("a", label, href=var_path.as_posix()))

    result = ET.tostring(index, method="html", xml_declaration=False, encoding="utf-8")

    if output:
        if isinstance(result, bytes):
            output.write_bytes(result)
        else:
            output.write_text(result, encoding="utf-8")
    else:
        print(result)
