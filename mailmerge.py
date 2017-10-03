#!/usr/bin/env python3

import smtplib
from email.parser import Parser
from email.utils import getaddresses
from getpass import getpass
from csv import DictReader
import pymustache
import argparse

parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                 description="Simple Mass-Mailer")
parser.add_argument('template', type=argparse.FileType(),
                    help="""
                    Template file. Header + Body for E-Mail, CSV fields will be expanded
                    using mustache (i.e., use {{Name}})
                    """)
parser.add_argument('csv', type=argparse.FileType(),
                    help="""
                    CSV file containing the data, first line must be header""")
parser.add_argument('-H', '--html', action='store_true', default=False,
                    help="ensure we send UTF-8 encoded HTML")
parser.add_argument('-n', '--dry-run', action='store_true', default=False,
                    help="Don't actually send")
parser.add_argument('-s', '--smtp-server', nargs=1, default="mailmaster.uni-wuerzburg.de",
                    help="SMTP server to use. Only SSL (port 465) supported.")
parser.add_argument('-u', '--smtp-user', nargs=1, default='thv76an',
                    help="User for the SMTP server")

options = parser.parse_args()
template = options.template.read()
reader = DictReader(options.csv)

server = smtplib.SMTP_SSL(options.smtp_server)
server.login(options.smtp_user, getpass())

for row in reader:
    formatted = pymustache.render(template, row)
    msg = Parser().parsestr(formatted) # -> message.Message
    recipients = msg.get_all('to', []) + msg.get_all('cc', [])
    addr = getaddresses(recipients)
    print("Sende an:", addr)

    if options.html:
        msg.set_type('text/html')
        msg.set_charset('utf-8')

    if not options.dry_run:
        server.send_message(msg)
