from typing import Annotated
from lxml import etree
import typer

app = typer.Typer()


@app.command()
def svg_label_to_id(
    input: Annotated[str, typer.Argument(exists=True, dir_okay=False)],
    output: Annotated[str, typer.Argument(writable=True)],
):
    doc = etree.parse(input)
    attr = "{http://inkscape.org/namespace/inkscape}label"
    for element in doc.findall(f"//*[{attr}]"):
        element.set("id", element.get(attr))
    doc.write(output)
