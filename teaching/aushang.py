#!/usr/bin/env python3
import io
import shutil
import subprocess
import sys
from argparse import ArgumentParser, FileType
from os import fspath
from pathlib import Path
from string import Template
from tempfile import TemporaryDirectory
from time import sleep

template = Template(r"""
\documentclass[paper=a4,paper=landscape,headheight=2.5cm,headinclude,fontsize=12pt,DIV16]{scrartcl}
\usepackage{polyglossia}
\usepackage{fontspec}
\usepackage{scrlayer-scrpage}
\usepackage{graphicx}
\usepackage{adjustbox}
\usepackage{layout}

\setdefaultlanguage[spelling=new]{german}

\setmainfont{MetaNormal-Roman}[BoldFont={MetaBold-Roman}]
\setsansfont{MetaNormal-Roman}[BoldFont={MetaBold-Roman}]

\pagestyle{plain.scrheadings}

\newcommand{\wuehead}{\noindent%
\adjustimage{%
	viewport={0 0 {\textwidth} {\height}},
	height=2.5cm,
	clip=true,
	rlap}{unilogo4c.jpg}%
	\hfill
	\begin{minipage}[b][2.5cm][c]{\linewidth}%
	    \raggedleft\bfseries
	    Lehrstuhl für Computerphilologie\\
	    und Neuere deutsche Literaturgeschichte\par
	    Institut f\"ur Deutsche Philologie\\
	    Philosophische Fakultät
	\end{minipage}%
}


\rohead[\wuehead]{\wuehead}
\cofoot[]{}


\begin{document}

{\raggedleft ${date}\par}

\fontsize{36pt}{48pt}\selectfont


\centering
\vspace{\fill}

{\bfseries\fontsize{48pt}{72pt}\selectfont
$title
}

$content

\vspace*{\fill}

\end{document}
""")
spacer = '\n\n\\vspace{\\fill}\n\n'


def _main():
    parser = ArgumentParser()
    parser.add_argument('message', nargs='+')
    parser.add_argument('-o', '--output', type=Path, metavar='PDF', help='save pdf here')
    parser.add_argument('-t', '--tex', type=Path, help='save intermediate tex file')
    parser.add_argument('-p', '--print', nargs='?', const='', metavar='PRINTER')
    parser.add_argument('-d', '--date', default=r'\today', help='Message for the date line')
    options = parser.parse_args()

    tex_string = template.substitute(dict(date=options.date,
                                          title=options.message[0],
                                          content=(spacer + spacer.join(options.message[1:]))
                                                    if len(options.message) > 1 else ''))

    try:
        with TemporaryDirectory(prefix='aushang-') as _tmpdir:
            tmpdir = Path(_tmpdir)
            texfile = tmpdir / 'aushang.tex'
            texfile.write_text(tex_string)
            process = subprocess.run(['lualatex', '--interaction=nonstopmode', texfile], input='', capture_output=True,
                                     cwd=tmpdir, encoding='utf-8', check=True)
            pdffile = texfile.with_suffix('.pdf')
            if options.print is not None:
                lp_args= ['lp']
                if options.print:
                    lp_args.extend('-d', options.print)
                lp_args.append(fspath(pdffile))
                print("Printing: ", *lp_args)
                subprocess.run(lp_args, cwd=tmpdir)
            if options.tex:
                shutil.move(texfile, options.tex)
            if options.output:
                shutil.move(pdffile, options.output)
            elif options.print is None:
                subprocess.run(['xdg-open', fspath(pdffile)])
                sleep(1)
    except subprocess.CalledProcessError as e:
        print('{} failed with error {}.'.format(e.cmd, e.returncode), e.stdout, e.stderr, sep='\n\n', file=sys.stderr)
        sys.exit(e.returncode)



if __name__ == '__main__':
    _main()
