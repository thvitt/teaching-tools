#!/usr/bin/env python3

import smtplib
from email.parser import Parser
from email.utils import getaddresses
from email import policy
from getpass import getpass
from csv import DictReader
import pymustache
import argparse

import sys

from tabulate import tabulate

parser = argparse.ArgumentParser(
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    description="Simple Mass-Mailer",
)
parser.add_argument(
    "template",
    type=argparse.FileType(),
    help="""
                    Template file. Header + Body for E-Mail, CSV fields will be expanded
                    using mustache (i.e., use {{Name}})
                    """,
)
parser.add_argument(
    "csv",
    type=argparse.FileType(),
    help="""
                    CSV file containing the data, first line must be header""",
)
parser.add_argument(
    "-H",
    "--html",
    action="store_true",
    default=False,
    help="ensure we send UTF-8 encoded HTML",
)
parser.add_argument(
    "-n", "--dry-run", action="store_true", default=False, help="Don't actually send"
)
parser.add_argument(
    "-t",
    "--to",
    nargs="?",
    const="from",
    help="Only generate the first e-mail, and send it to the given address (default: the From: address)",
)
parser.add_argument(
    "-s",
    "--smtp-server",
    nargs=1,
    default="mailmaster.uni-wuerzburg.de",
    help="SMTP server to use. Only SSL (port 465) supported.",
)
parser.add_argument(
    "-u", "--smtp-user", nargs=1, default="thv76an", help="User for the SMTP server"
)
parser.add_argument("-d", "--csv-delimiter", nargs=1, default=",")

options = parser.parse_args()
template = options.template.read()
reader = DictReader(options.csv, delimiter=options.csv_delimiter[0])
records = list(reader)

print("Records:")
print(tabulate(records))

template_vars = {
    v.value for v in pymustache.compiled(template).children if v.type_string == "V"
}
columns = set(reader.fieldnames)

if template_vars - columns:
    print(
        "ERROR: The following template variables are not in the table:",
        ", ".join(template_vars - columns),
    )
if columns - template_vars:
    print(
        "INFO: The following table columns are not in the template:",
        ", ".join(columns - template_vars),
    )

answer = input("Continue? [y, N] ").strip().lower()
if answer != "y":
    sys.exit(1)

server = smtplib.SMTP_SSL(options.smtp_server)

if not options.dry_run:
    server.login(options.smtp_user, getpass())

if options.to:
    reader = records[0]
for row in records:
    formatted = pymustache.render(template, row)
    header, body = formatted.split("\n\n", maxsplit=1)
    msg = Parser(policy=policy.EmailPolicy(utf8=True)).parsestr(
        header, headersonly=True
    )
    if options.html:
        msg.set_content(body, subtype="html", charset="utf-8")
    else:
        msg.set_content(body, charset="utf-8")

    if options.to:
        if options.to == "from":
            recipients = msg.get_all("from", [])
        else:
            recipients = [options.to]
    else:
        recipients = (
            msg.get_all("to", []) + msg.get_all("cc", []) + msg.get_all("bcc", [])
        )
    addr = getaddresses([r for r in recipients if r])
    print("Sende an:", addr)

    if not options.dry_run:
        server.send_message(msg)
    else:
        print(msg)
