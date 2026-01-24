from collections.abc import Iterable
from os import fspath
from pathlib import Path
from typing import Annotated

from cyclopts import App, Group, Parameter
from cyclopts.types import ExistingFile, PositiveInt
from cyclopts.validators import LimitedChoice
from lxml import etree
from lxml.etree import _Element, _ElementTree
from more_itertools import first
from rich import get_console
from rich.table import Column, Table  # pyright: ignore[reportPrivateUsage]

app = App()
app.register_install_completion_command(add_to_startup=False)  # pyright: ignore[reportUnknownMemberType]


class XMLNamespace(dict[str, str]):
    def __call__(self, prefix: str, localname: str = "", /):
        if not localname:
            prefix, localname = None, prefix  # ty:ignore[invalid-assignment]  # pyright: ignore[reportAssignmentType]
        namespace_url = self[prefix]
        return f"{{{namespace_url}}}{localname}"


NS = XMLNamespace(
    svg="http://www.w3.org/2000/svg",
    inkscape="http://www.inkscape.org/namespaces/inkscape",
)


class SteppedSVG:
    svgfile: Path
    svg: _ElementTree
    layers: list[_Element]
    steps: dict[str, _Element]
    stepids: list[str]
    stepnos: dict[str, int]

    def __init__(self, svgfile: Path) -> None:
        svg = etree.parse(svgfile)
        layers = svg.xpath('*[@inkscape:groupmode="layer"]', namespaces=NS)
        assert isinstance(layers, list)
        steps: dict[str, _Element] = {}
        for layer in layers:  # pyright: ignore[reportUnknownVariableType]  -- checked in the next line ...
            if not isinstance(layer, _Element):
                continue
            label = str(layer.get(NS("inkscape", "label")))
            if not label.startswith("step-"):
                continue
            stepid = label[5:]  # step-…
            steps[stepid] = layer

        self.svgfile = svgfile
        self.svg = svg
        self.layers = layers  # pyright: ignore[reportAttributeAccessIssue]  # ty:ignore[invalid-assignment]
        self.steps = steps
        self.stepids = sorted(steps)
        self.stepnos = {
            step: stepno for stepno, step in enumerate(self.stepids, start=1)
        }

    def resolve_stepid(self, step: int | str | None) -> tuple[str, int]:
        try:
            if isinstance(step, int):
                return self.stepids[step - 1], step
            elif step is not None:
                return step, self.stepnos[step]
            else:
                raise TypeError("Must give a step name or number")
        except ValueError as e:
            raise ValueError(f"{step} is not a step in {self.svgfile}") from e

    def resolve_pattern(
        self, pattern: str, infile: Path, step: int | str | None
    ) -> Path:
        stepid, stepno = self.resolve_stepid(step)
        return infile.parent / pattern.format(
            stem=infile.stem,
            name=infile.name,
            dir=fspath(infile.absolute().parent),
            step=stepid,
            stepno=stepno,
        )

    def writestep(self, step: int | str | None, target: Path):
        stepid, _ = self.resolve_stepid(step)
        layer = self.steps[stepid]
        style = layer.get("style", "")
        if "display:none" in style:
            layer.set("style", style.replace("display:none", "display:inline"))
        else:
            layer.set("style", "display:inline;" + style)
        target.parent.mkdir(parents=True, exist_ok=True)
        self.svg.write(target)
        layer.set("style", style)  # restore previous style


steparg = Group(show=False, validator=LimitedChoice(allow_none=True))


@app.default()
def svgsteps(
    infile: ExistingFile,
    /,
    step: Annotated[str | None, Parameter(alias="-s", group=steparg)] = None,
    *,
    stepno: Annotated[PositiveInt | None, Parameter(alias="-n", group=steparg)] = None,
    pattern: Annotated[str, Parameter(alias="-O")] = "{stem}-{step}.svg",
    output: Annotated[Path | None, Parameter(alias="-o")] = None,
):
    """
    Generates a series of step images from a series of layers in an Inkscape SVG.

    The input file should be an existing SVG created with Inkscape that has invisible
    layers labeled `step-…`. The script will iterate through all these labels. For each
    of the layers, a copy of the input file will be written to disk with the specific
    layer set visible. Everything else is left unchanged.

    Args:
        infile: Input SVG file.
        step: label (without `step-`) of a single step to extract. Default: all steps.
        stepno: number (starting with 1) of a single step to extract. Default: all steps.
        pattern: Pattern for generating the output file name. The name will be resolved
            relative to the input file's directory. The following substitution patterns
            are available (python format strings, actually):
            * `{stem}` - Stem (filename w/o directory and extension) of the input file
            * `{name}` - full name of the input file (w/o directory)
            * `{dir}`  - full path to the input file’s directory
            * `{step}` – step label, i.e. the layer label without the leading `step-`
            * `{stepno}` – consecutive step number. For this,
                the step labels are sorted lexicographically and enumerated, starting
                with 1.
        output: If `step` or `stepno` are given (and thus only one step extracted),
            this is the filename we are writing to. Otherwise, `pattern` will be
            resolved against this file instead of the input file.
    """
    svg = SteppedSVG(infile)
    if step or stepno:
        svg.writestep(
            step or stepno,
            output or svg.resolve_pattern(pattern, infile, step or stepno),
        )

    output = output or infile

    for step in svg.steps:
        outfile = svg.resolve_pattern(pattern, output, step)
        svg.writestep(step, outfile)
        )
