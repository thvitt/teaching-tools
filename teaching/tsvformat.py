from os import environ, fspath
from typing import Annotated
from cyclopts import App, Parameter
from csv import DictReader
from pathlib import Path
from subprocess import run
from tempfile import NamedTemporaryFile
from shutil import which

app = App()


def edit(text: str, file: Path | None = None, suffix=".md") -> str:
    editor_name = environ.get("VISUAL", environ.get("EDITOR", "vi"))
    editor = which(editor_name)
    if editor is None:
        raise FileNotFoundError(editor_name)
    if file is None:
        with NamedTemporaryFile("wt", suffix=suffix, delete_on_close=False) as f:
            f.write(text)
            f.close()
            proc = run([editor, f.name])
            if proc.returncode == 0:
                return Path(f.name).read_text()
            else:
                return text
    else:
        if not file.exists() or file.stat().st_size == 0:
            file.write_text(text)
        proc = run([editor, fspath(file)])
        if proc.returncode == 0:
            return file.read_text()
        else:
            return text


@app.default
def main(
    tsv: Path,
    /,
    template: Annotated[Path | None, Parameter(["-t", "--template"])] = None,
    output: Annotated[Path | None, Parameter(["-o", "--output"])] = None,
    input_delimiter: Annotated[str, Parameter(["-d", "--delimiter"])] = "\t",
    output_delimiter: Annotated[str, Parameter(["-D", "--output-delimiter"])] = "\n",
):
    """
    Uses a TSV file and a template to fill an output file.

    Args:
        tsv: TSV input file with the data
        template: file containing the template. The template may contain each field name in {}, these are python format strings.
            If the template file is missing or empty or not specified, an editor is opened with a file pre-filled with the field names.
        input_delimiter: field separator in the input file
        output_delimiter: record separator in the output file
    """
    data = tsv.read_text().splitlines()
    reader = DictReader(data, delimiter=input_delimiter)
    assert reader.fieldnames is not None
    template_help = "\n".join(
        ["Write a template containing some of the following field names:\n\n"]
        + [f"{{{name}}}" for name in reader.fieldnames]
    )
    if template is None or not template.exists() or template.stat().st_size == 0:
        template_str = edit(template_help, template)
    else:
        template_str = template.read_text()

    result = output_delimiter.join(template_str.format_map(row) for row in reader)
    if output:
        output.write_text(result)
    else:
        print(result)
