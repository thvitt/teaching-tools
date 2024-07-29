"""
Generate a tree representation from an XML file.
You can pass three kinds of parameters: 

* one XML file name (required)
* options for graphviz dot, starting with a '-' and consisting of one word, e.g. -otree.pdf -Nfont="Fira Mono"
* parameters as key=value pair, quoted if the values contain whitespace, to influence the generated graph.
"""

import sys
from collections.abc import Sequence
from importlib.resources import as_file, files
from itertools import chain
from os import fspath
from pathlib import Path
from shutil import which
from subprocess import Popen, run, PIPE
from warnings import warn


def split_args(
    args: Sequence[str] = sys.argv[1:],
) -> tuple[list[str], Path | None, list[str]]:
    params = []
    file = None
    dot_args = []
    for arg in args:
        if arg.startswith("-"):
            dot_args.append(arg)
        elif "=" in arg:
            params.append(arg)
        elif Path(arg).exists():
            file = Path(arg)
        else:
            warn(f"Param '{arg}' not recognized, skipping")
    return params, file, dot_args


def find_saxon() -> list[str]:
    exe = which("saxon")
    if exe is None:
        java = which("java")
        if java is None:
            raise ValueError("Could not find java executable.")
        for jar in chain(
            Path("/usr/local/share/java").glob("Saxon*.jar"),
            Path("/usr/share/java").glob("Saxon*.jar"),
        ):
            return [java, "-jar", fspath(jar)]
        raise ValueError("Could not find Saxon")
    else:
        return [exe]


def help():
    print(__doc__, file=sys.stderr)
    print(
        "Parameters (and their default values), must be one arg i.e. quoted:",
        file=sys.stderr,
    )
    from xml.etree import ElementTree as ET

    with files("teaching").joinpath("xml2dot.xsl").open("r") as xslt:
        tree = ET.parse(xslt)
    params = tree.findall(
        ".//xsl:param", {"xsl": "http://www.w3.org/1999/XSL/Transform"}
    )
    for param in params:
        print(f"{param.get("name"):>20}={param.text}", file=sys.stderr)


def main() -> None:
    params, xml, dot_args = split_args()
    if xml is None:
        print("No XML file given on the command line", file=sys.stderr)
        help()
        sys.exit(1)
    saxon_cmd = find_saxon()
    with as_file(files("teaching").joinpath("xml2dot.xsl")) as xsl_path:
        saxon_cmd.append("-xsl:" + fspath(xsl_path))
        saxon_cmd.append("-s:" + fspath(xml))
        saxon_cmd.extend(params)
        if dot_args:
            dot_cmd = which("dot")
            if dot_cmd is None:
                raise ValueError("Could not find dot executable.")
            saxon = Popen(saxon_cmd, stdout=PIPE)
            dot = run([dot_cmd] + dot_args, stdin=saxon.stdout)
            saxon.wait()
            sys.exit(dot.returncode)
        else:
            saxon = run(saxon_cmd)
            sys.exit(saxon.returncode)
