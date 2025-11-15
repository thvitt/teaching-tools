from collections.abc import Iterable
from os import fspath
from typing import Annotated

from cyclopts import App, Parameter
from cyclopts.types import ExistingFile
from lxml import etree
from lxml.etree import _Element

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


@app.default()
def svgsteps(
    infile: ExistingFile,
    output: Annotated[str, Parameter(alias="-o")] = "{stem}-{step}.svg",
):
    """
    Generates a series of step images from a series of layers in an Inkscape SVG.

    The input file should be an existing SVG created with Inkscape that has invisible
    layers labeled `step-…`. The script will iterate through all these labels. For each
    of the layers, a copy of the input file will be written to disk with the specific
    layer set visible. Everything else is left unchanged.

    Args:
        infile: Input SVG file.
        output: Pattern for generating the output file name. The name will be resolved
            relative to the input file's directory. The following substitution patterns
            are available (python format strings, actually):
            * `{stem}` - Stem (filename w/o directory and extension) of the input file
            * `{name}` - full name of the input file (w/o directory)
            * `{dir}`  - full path to the input file’s directory
            * `{step}` – step label, i.e. the layer label without the leading `step-`
            * `{stepno}` – consecutive step number. For this,
                the step labels are sorted lexicographically and enumerated, starting
                with 1.

    """
    svg = etree.parse(infile)
    layers = svg.xpath('*[@inkscape:groupmode="layer"]', namespaces=NS)
    assert isinstance(layers, Iterable)
    steps: dict[str, _Element] = {}
    for layer in layers:
        if not isinstance(layer, _Element):
            continue
        label = str(layer.get(NS("inkscape", "label")))
        if not label.startswith("step-"):
            continue
        stepid = label[5:]  # step-…
        steps[stepid] = layer

    for stepno, step in enumerate(sorted(steps), start=1):
        layer = steps[step]
        style = layer.get("style", "")
        if "display:none" in style:
            layer.set("style", style.replace("display:none", "display:inline"))
        else:
            layer.set("style", "display:inline;" + style)
        outfile = infile.parent / output.format(
            stem=infile.stem,
            name=infile.name,
            dir=fspath(infile.absolute().parent),
            step=step,
            stepno=stepno,
        )
        svg.write(outfile)
        layer.set("style", style)  # restore previous style
