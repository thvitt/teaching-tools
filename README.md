## Thorsten’s Teaching (and System) Tools

This repository contains a few scripts that I use primarily to support teaching and maintaining my materials. There are also some other tools I didn’t find a proper place for.

This is mostly hacky and probably not suited for anybody except me. 

### aufgabe-bewertung.py

When giving students feedback for programming tasks etc., I usually write a single markdown file with my comments and the grade. This script can create a template and it can fill in comments (converted from Markdown to HTML using pandoc) and grades into a CSV file exported from Moodle, so I just need to import the CSV file instead of dealing with Moodle’s web interface.


### mailmerge.py

Send E-Mails from a mustache template and a CSV file.

### md-images.py

Scan a markdown file for included images (using pandoc/panflute). May output simple lists (useful for copying) or Makefile snippets. The latter can be useful for automatic dependency generation, e.g., if you have a makefile that has its markdown files in a variable, this snippet:

```make
Makefile.dep : $(MARKDOWN_FILES)
    md-images -d '%.pdf' $(MARKDOWN_FILES)

include Makefile.dep
```

will automatically create rules like

```make
foo.pdf : foo.md img/pic1.png img/pic2.pdf
```


### similar-solutions.py, unify_source.py

Parses python files, strips comments and formatting, renames all variables to standardized names and runs a simple similarity measurement on the results, producing similarity scores and a dendrogram. This can be useful to detect the kind of group work where student A copies the solution of student B and renames some variables before manually looking at the files.

### diffencoding.py

Shows how two 8-bit encodings differ, in terms of a unicode table.

### encoding-tables.py

Generate SVG files containing encoding tables.

### aushang.py

Generate a (landscape) announcement using my LaTeX installation. 

### un2up.py

Given a PDF file of a scanned book where two book pages make up one PDF page, this script might generate a PDF file with one book page per PDF page (to use on, e.g., a tablet)

### xfiles-graph.py

Parses a project of XProc and XSLT files and generates a graph representing imports, inclusions and executions. When called as a script, writes the graph to a GraphViz .dot file.


### downgrade-by-origin.py

use apt to downgrade all packages to avoid a specific origin. Dangerous! May wreck your system!
