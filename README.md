## Thorsten’s Teaching (and System) Tools

This repository contains a few scripts that I use primarily to support teaching and maintaining my materials. There are also some other tools I didn’t find a proper place for.

This is mostly hacky and probably not suited for anybody except me.

To install, install this package using pip or poetry. Each script is a module in the package 'teaching' and a script that is installed to …/bin.

## Visualization

### encoding-tables

Generate SVG files containing encoding tables.

Optionally also generates a markdown file with a presentation of all the tables.

### xml2dot

Transforms an XML file to an illustrative GraphViz file showing the tree structure.

### sql2er

Transforms an SQL(ite) schema to a PlantUML diagram.

### aushang

Generate a (landscape) announcement using my LaTeX installation.

### xfiles-graph

Parses a project of XProc and XSLT files and generates a graph representing imports, inclusions and executions. When called as a script, writes the graph to a GraphViz .dot file.

## Preparing Materials

### htmlindex

Creates an index.html for a directory with HTML files.

It is intended for a directory with slides for a course. It will try to extract the title from the first h1 heading, it will detect and extract numbering in the filename, and it will group similar files with a common title. Date (and size) will be highlighted in a color scale, so newest files are easily visible.

### ls-md

List markdown files, optionally using their titles.

### run-with-server

Run a command while serving a directory via HTTP.

This command first starts a simple HTTP server on a free port, runs the
given command and finally shuts down the HTTP server.

The server will serve the directory given with --serve-dir (current
directory by default) and all its subdirectories. It will find a free TCP
port that is at least start_port to run the server. If --verbose, the server
will output an access log and some more details.

The remaining arguments specify the command to run and its arguments. The
special string {port} will be replaced with the port number used by the
server. If --shell is given, the system shell will be used to run the
command, in this case only one non-option argument should be given.

The exit code will be passed on from the command.

### Video stuff

#### kdenlive-guide-table

Extract labeled guides from a Kdenlive project file.

#### mltmove

Move and rename resources used within a MLT file beside the MLT file itself.

#### video-thumbnail

Extract a thumbnail from a video file.

## Encoding stuff

### fix-surrogates

There seems to be a bug in some Windows zip software that encodes filenames using the Windows codepage instead of
either old cp437 or UTF-8. When popular unzip libraries unpack such archives in a UTF-8 locale, non-ASCII
characters may end up as unicode surrogate characters. This script fixes these filenames after the fact, i.e. it
renames the unpacked files.

### diffencoding

Shows how two 8-bit encodings differ, in terms of a unicode table.

## Other

### un2up

Given a PDF file of a scanned book where two book pages make up one PDF page, this script might generate a PDF file with one book page per PDF page (to use on, e.g., a tablet)

### mix-words

Creates a file sampled from words according to a spec.

Synopsis:

    mix-words (factor | string | filename)+ [k] > output.txt 
              `---------- spec -----------´

spec - specification of the mix of the output words

k -    absolute number of words in the output file.

The specification is composed of an arbitrary sequence of numbers, strings
and filenames.

A number will set the current mix factor (the default is 1.0). A filename
argument will read and tokenize the given file. A string argument will be
tokenized. For each non-number argument, the current factor will be
distributed among the tokens resulting from that argument and used as a weight.
A final number specifies the total number of words to sample.

The script will write the generated text to stdout and a statistic to stderr.

Examples:

    mix-words foo 2 bar baz 100

generates 100 words of which approx. 20% will be 'foo', 40% 'bar' and 40%
'baz'.

    mix-words 0.8 top100.txt 0.1 New 0.05 York Orleans 5000

generates 5000 words, of which 80% will come from the file top100.txt, 10%
will be 'New', and 'York' and 'Orleans' will each make up 5% of the result.

### xml-augment-attr

```
╭─ Commands ────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ copy    Edits the XML file INPUT by setting the DST attribute of all elements that have a SRC attribute. SRC and  │
│         DST may be prefixed QNames using one of the namespace prefixes declared in the input document’s root      │
│         element.                                                                                                  │
│ ns      Prints the namespace prefixes that can be used with the other commands.                                   │
│ xpath   Add an attribute attr to each element matched by the XPath match in the XML file input. The attribute     │
│         value will be determined by first evaluating the XPath select on the matched element and then formatting  │
│         the result using the given format string. In the format string, the following variables are available     │
│         between {}:                                                                                               │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

## Grading and Feedback

### aufgabe-bewertung

When giving students feedback for programming tasks etc., I usually write a single markdown file with my comments and the grade. This script can create a template and it can fill in comments (converted from Markdown to HTML using pandoc) and grades into a CSV file exported from Moodle, so I just need to import the CSV file instead of dealing with Moodle’s web interface.

Probably highly specific to my (Uni Würzburg) needs.

### table2bewertung

Prepares a text file from a (csv or spreadsheet) table and a mustache template.

### bewertung-merge

Merges the grades from multiple CSV files to a total grade, according to some rules.

### klausur-feedback

Merges a CSV file with grades and a mustache template with feedback text into a moodle feedback table.

### similar-solutions, unify-source

Parses python files, strips comments and formatting, renames all variables to standardized names and runs a simple similarity measurement on the results, producing similarity scores and a dendrogram. This can be useful to detect the kind of group work where student A copies the solution of student B and renames some variables before manually looking at the files.

### mailmerge

Send E-Mails from a mustache template and a CSV file.
