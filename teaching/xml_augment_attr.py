from typing import Annotated, Optional
from sys import stderr
from lxml import etree
import typer

app = typer.Typer()


def expandns(qname: str, namespaces: dict[str | None, str]) -> str:
    """
    Transforms a QName to Clark notation using the given prefix map.

    >>> expandns("path", {"svg": "http://www.w3.org/2000/svg"})
    "path"
    >>> expandns("svg:path", {"svg": "http://www.w3.org/2000/svg"})
    "{http://www.w3.org/2000/svg}path"
    >>> expandns("path", {None: "http://www.w3.org/2000/svg"})
    "{http://www.w3.org/2000/svg}path"
    """
    if ":" not in qname:
        if None in namespaces:
            prefix = None
            localname = qname
        else:
            return qname
    else:
        prefix, localname = qname.split(":", 1)

    nsurl = namespaces[prefix]
    return "{" + nsurl + "}" + localname


@app.command()
def copy_attribute(
    input: Annotated[
        str, typer.Argument(exists=True, dir_okay=False, help="Input XML file")
    ],
    src: Annotated[str, typer.Argument(help="Source attribute name")],
    dst: Annotated[str, typer.Argument(help="Target attribute name")],
    fmt: Annotated[
        str,
        typer.Option(
            "-f",
            "--format",
            help="Format for the target value. Use {} for the source attribute value.",
        ),
    ] = "{}",
    move: Annotated[
        bool, typer.Option("-m/-c", "--move/--copy", help="Remove the src attribute")
    ] = False,
    output: Annotated[
        Optional[str],
        typer.Option(
            "-o",
            "--output",
            metavar="FILE",
            help="File to save the converted document into",
            dir_okay=False,
            writable=True,
        ),
    ] = None,
    inplace: Annotated[
        bool,
        typer.Option(
            "-i", help="Modify the input file in place. Ignored if -o is given."
        ),
    ] = False,
    printns: Annotated[
        bool, typer.Option(help="Print the namespace prefix map to stderr.")
    ] = False,
):
    """
    Edits the XML file INPUT by setting the DST attribute of all elements that have a
    SRC attribute. SRC and DST may be prefixed QNames using one of the namespace
    prefixes declared in the input document’s root element.
    """
    doc = etree.parse(input)
    nsmap = dict(doc.getroot().nsmap)
    if None in nsmap:
        del nsmap[None]

    opcount = 0
    for el in doc.xpath(f"//*[@{src}]", namespaces=nsmap):
        value = el.get(expandns(src, nsmap))
        el.set(expandns(dst, nsmap), fmt.format(value))
        if move:
            del el.attrib[expandns(src, nsmap)]
        opcount += 1

    if inplace and not output:
        output = input
    if output is None:
        print(etree.tounicode(doc))
    else:
        doc.write(output)

    if printns:
        print(
            "Namespace prefixes available:", format_dict(nsmap), file=stderr, sep="\n"
        )

    if opcount:
        print(
            f"Augmented {opcount} elements that had an {src} attribute with {dst} attributes.",
            file=stderr,
        )
    else:
        print(
            f"WARNING: No elements with a {src} ({expandns(src, nsmap)}) attribute found!",
            file=stderr,
        )


def format_dict(d: dict) -> str:

    formatted = {
        str(key) if key is not None else "": str(value) for key, value in d.items()
    }

    keylen = max((len(key) for key in formatted))
    lines = [
        key + " " * (keylen - len(key)) + "\t" + value
        for key, value in formatted.items()
    ]
    return "\n".join(lines)
