from typing import Annotated, Any, Hashable, Optional
from sys import stderr
import typing
from lxml import etree
import typer
from contextlib import contextmanager
import hashlib
from struct import unpack

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


@contextmanager
def load(
    input: str,
    output: Optional[str] = None,
    inplace: bool = False,
    readonly: bool = False,
):
    doc = etree.parse(input)

    yield doc

    if readonly:
        return
    if inplace and not output:
        output = input
    if output is None:
        print(etree.tounicode(doc))
    else:
        doc.write(output)


def namespacemap(tree):
    if hasattr(tree, "getroot"):
        root = tree.getroot()
    else:
        root = tree
    namespaces = dict(root.nsmap)
    if None in namespaces:
        default_ns = namespaces[None]
        del namespaces[None]
        if default_ns not in namespaces.values():
            prefix_cand = root.tag
            if "}" in prefix_cand:
                prefix_cand = prefix_cand[prefix_cand.rfind("}") + 1 :]
            if prefix_cand in namespaces:
                prefix_cand = "root"
            namespaces[prefix_cand] = default_ns
    return namespaces


@app.command("ns")
def namespaces(input: str):
    """
    Prints the namespace prefixes that can be used with the other commands.

    The namespaces are taken from the document’s root element, a prefix for
    the default namespace is inferred, if necessary.
    """
    with load(input, readonly=True) as doc:
        print(
            "Namespace prefixes on the document’s root element:",
            format_dict(namespacemap(doc)),
            sep="\n\n",
            file=stderr,
        )


@app.command("copy")
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
):
    """
    Edits the XML file INPUT by setting the DST attribute of all elements that have a
    SRC attribute. SRC and DST may be prefixed QNames using one of the namespace
    prefixes declared in the input document’s root element.
    """
    with load(input, output, inplace) as doc:
        nsmap = namespacemap(doc)
        if None in nsmap:
            del nsmap[None]

        opcount = 0
        for el in doc.xpath(f"//*[@{src}]", namespaces=nsmap):
            value = el.get(expandns(src, nsmap))
            el.set(expandns(dst, nsmap), fmt.format(value))
            if move:
                del el.attrib[expandns(src, nsmap)]
            opcount += 1

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


@app.command("xpath")
def add_attribute(
    input: Annotated[str, typer.Argument(metavar="FILE")],
    match: Annotated[
        str,
        typer.Argument(metavar="XPATH", help="XPath selecting the elements we work on"),
    ],
    attr: Annotated[
        str,
        typer.Argument(metavar="QNAME", help="Target attribute on the matched element"),
    ],
    select: Annotated[
        str,
        typer.Option(
            "-s",
            "--select",
            metavar="XPATH",
            help="Value to select for each matched element",
        ),
    ] = "string(.)",
    fmt: Annotated[
        str,
        typer.Option("-f", "--format", help="Format string for the target attribute"),
    ] = "{value}",
    output: Annotated[
        Optional[str], typer.Option("-o", "--output", metavar="FILE", writable=True)
    ] = None,
    inplace: Annotated[bool, typer.Option("-i", "--inplace")] = False,
):
    """
    Add an attribute attr to each element matched by the XPath match in the XML file input. The attribute value will be determined by first
    evaluating the XPath select on the matched element and then formatting the result using the given format string. In the format string,
    the following variables are available between {}:

    - value: The value (or concatenated values, if multiple) of the items returned by select
    - index: The number of the match in the file
    - count: The number of items returned by the select expression
    - hash: A hash value calculated from the value
    """
    with load(input, output, inplace) as doc:
        nsmap = namespacemap(doc)
        for index, el in enumerate(doc.xpath(match, namespaces=nsmap), start=1):
            selection = el.xpath(select, namespaces=nsmap)
            value = stringify(selection)
            result = fmt.format(
                value=value, index=index, count=len(selection), hash=shortid(value)
            )
            el.set(expandns(attr, nsmap), result)


def format_dict(d: dict) -> str:

    formatted = {
        str(key) if key is not None else "": str(value) for key, value in d.items()
    }

    keylen = max((len(key) for key in formatted))
    lines = [
        key + " " * (keylen - len(key)) + "\t" + value
        for key, value in formatted.items()
    ]
    return "\n".join(sorted(lines))


def encode_int(
    number: int, alphabet: str = "0123456789abcdefghijklmnopqrstuvwxyz"
) -> str:
    base = len(alphabet)
    result: list[str] = []
    negative = number < 0
    x = abs(number)
    if x == 0:
        return "0"
    while x:
        x, rest = divmod(x, base)
        result.append(alphabet[rest])
    return ("-" if negative else "") + "".join(reversed(result))


def shortid(x: Hashable) -> str:
    digest = hashlib.shake_128(str(x).encode()).digest(4)
    cand = encode_int(unpack("!I", digest)[0])
    if not cand[0].isalpha():
        cand = "_" + cand
    return cand


def stringify(selection: Any) -> str:
    if isinstance(selection, str):
        return selection
    elif isinstance(selection, list):
        return "".join(stringify(item) for item in selection)  # type: ignore
    elif hasattr(selection, "itertext"):
        return "".join(selection.itertext())
    else:
        return str(selection)
