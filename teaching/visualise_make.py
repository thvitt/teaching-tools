from os import chdir
import re
from subprocess import run
import shlex
import logging
from typing import Annotated, Iterable
import networkx as nx
from rich.console import Console
from rich.logging import RichHandler
from rich.syntax import Syntax
from cyclopts import App, Parameter
from pathlib import Path

app = App()

logger = logging.getLogger(__name__)


def next_uncommented_line(lines: Iterable[str]) -> str:
    for line in lines:
        if not line.startswith("#"):
            return line
    return ""


def check_for_makefile():
    if (
        not Path("GNUmakefile").exists()
        and not Path("makefile").exists()
        and not Path("Makefile").exists()
    ):
        logger.warning("No makefile found in %s", Path.cwd())


def parse_database(
    targets: list[str] | None = None, source_graph: nx.DiGraph | None = None
) -> nx.DiGraph:
    """
    Build a graph of make targets and their dependencies from the Make database


    This function runs `make -pnB` with the given targets and parses the output.
    Only sections that start with a line reading "# Files" are considered, sections
    that start with "# Variables" are ignored.

    For each rule that is not preceded by a line reading "# Not a target:", the
    target name is extracted and the dependencies are split by shlex. If the target
    name is one of the special targets like '.PHONY', the rule is skipped.

    If the rule is followed by a line that starts with a tab (a command line), the first dependency
    is considered a primary dependency and the other dependencies are secondary dependencies. Otherwise,
    all dependencies are considered primary dependencies.

    We add an edge from each dependency to the target, with a dashed line style for secondary dependencies.
    """
    graph = nx.DiGraph() if source_graph is None else source_graph.copy()
    check_for_makefile()
    cmdline = ["make", "-pnB"]
    cmdline.extend(targets or [])
    logger.info("Running `%s' in %s", shlex.join(cmdline), Path.cwd())
    proc = run(cmdline, capture_output=True, text=True)
    lines = proc.stdout.splitlines()
    logger.debug("Got %d lines, starting with:\n%s", len(lines), "\n".join(lines[:6]))
    in_files_section = False
    for lineno, line in enumerate(lines):
        if line == "# Files":
            in_files_section = True
            logger.debug("Entering files section at line %d", lineno)
            continue
        elif line == "# Variables":
            in_files_section = False
            logger.debug("Skipping variables section from line %d", lineno)
            continue
        elif line.startswith("#"):
            continue
        if (
            in_files_section
            and (match := re.match(r"^(\S.*?)::?\s+(.*)$", line))
            and lines[lineno - 1] != "# Not a target:"
        ):
            target, dep_str = match.groups()
            if "%" in target or target.startswith("."):
                logger.debug("%d: Skipping target %s", lineno, target)
                continue
            deps = shlex.split(dep_str)
            commandline = next_uncommented_line(lines[lineno + 1 :])
            if commandline.startswith("\t"):
                command = shlex.split(commandline[1:])[0]
                graph.add_edge(deps[0], target, cmdline=commandline, command=command)
                for dep in deps[1:]:
                    graph.add_edge(dep, target, style="dashed", related=deps[0])
            else:
                for dep in deps:
                    graph.add_edge(dep, target)
            logger.debug(
                "%d: Adding target %s with deps %s, next line is '%s'",
                lineno,
                target,
                deps,
                commandline,
            )
    if graph.number_of_nodes() == 0:
        logger.error("No graph generated")
        if logger.isEnabledFor(logging.DEBUG):
            Console(stderr=True).print(
                Syntax("\n".join(lines), "makefile", line_numbers=True)
            )
    return graph


def _update_graph(
    graph: nx.DiGraph,
    makefile: str | None,
    makeline: str | None,
    target: str | None,
    dep_str: str | None,
    cmds: list[str],
):
    deps = shlex.split(dep_str) if dep_str else []
    cmd = shlex.split(cmds[0])[0] if cmds else None
    if deps:
        graph.add_edge(
            target,
            deps[0],
            makefile=makefile,
            makeline=makeline,
            cmd=cmd,
            recipe="\n".join(cmds),
            weight=10,
        )
        for dep in deps[1:]:
            graph.add_edge(
                target,
                dep,
                makefile=makefile,
                makeline=makeline,
                cmd=cmd,
                secondary_to=deps[0],
                style="dashed",  # FIXME move to formatting
            )


def parse_trace(targets: list[str] | None = None):
    check_for_makefile()
    cmdline = ["make", "-n", "--trace", "-B"]
    cmdline.extend(targets or [])
    logger.info("Running `%s' in %s", shlex.join(cmdline), Path.cwd())
    proc = run(cmdline, capture_output=True, text=True)
    lines = proc.stdout.splitlines()
    logger.debug("Got %d lines, starting with:\n%s", len(lines), "\n".join(lines[:6]))
    graph = nx.DiGraph()

    makefile, makeline, target, dep_str = None, None, None, None
    recipe = []
    for line in lines:
        if re.match(r"^make: (Entering|Leaving) directory", line):
            pass
        elif match := re.match(
            r"^(.*?):(\d+): update target '([^']+)' due to: (.*)$", line
        ):
            _update_graph(graph, makefile, makeline, target, dep_str, recipe)
            makefile, makeline, target, dep_str = match.groups()
            recipe = []
        elif match := re.match(r"^(.*?):(\d+): target '([^']+)' does not exist", line):
            _update_graph(graph, makefile, makeline, target, dep_str, recipe)
            makefile, makeline, target = match.groups()
            dep_str = ""
            recipe = []
        else:
            recipe.append(line)
    _update_graph(graph, makefile, makeline, target, dep_str, recipe)
    return graph


@app.default
def main(
    targets: list[str] | None = None,
    *,
    all: Annotated[bool, Parameter(["-a", "--all"])] = False,
    cd: Annotated[Path | None, Parameter(["-C", "--directory"])] = None,
    verbose: bool = False,
    debug: bool = False,
):
    logging.basicConfig(
        level=logging.DEBUG if debug else logging.INFO if verbose else logging.WARNING,
        handlers=[
            RichHandler(show_time=False, show_path=False, console=Console(stderr=True))
        ],
        format="%(message)s",
    )
    if cd:
        chdir(cd)
    graph = parse_trace(targets)
    print(nx.nx_agraph.to_agraph(graph).to_string())
