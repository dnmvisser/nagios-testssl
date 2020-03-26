#!/usr/bin/env python3
import argparse
import os
import sys
import tempfile
import subprocess
import json
import jmespath
from pprint import pprint
from urllib.parse import urlparse

def nagios_exit(message, code):
    print(message)
    sys.exit(code)

severities = {
        'OK': 1,
        'INFO': 2,
        'LOW': 3,
        'MEDIUM': 4,
        'HIGH': 5,
        'CRITICAL': 6
        }
try:
    parser = argparse.ArgumentParser(description='Check output of testssl.sh')
    parser.add_argument('--uri', help='host|host:port|URL|URL:port.'
            'Port 443 is default, URL can only contain HTTPS protocol', required=True)
    parser.add_argument('--testssl', help='Path to the testssl.sh script', required=True)
    parser.add_argument('--critical', help='Findings of this severity level trigger a CRITICAL',
            choices=severities.keys(), default='CRITICAL')
    parser.add_argument('--warning', help='Findings of this severity level trigger a WARNING', 
            choices=severities.keys(), default='HIGH')
    # FIXME this is unreliable
    parser.add_argument('trailing_args', nargs=argparse.REMAINDER)
    args = parser.parse_args()

    if severities[args.critical] < severities[args.warning]:
        parser.error('The severity level to raise a WARNING must be less that the level to raise a CRITICAL')

    if urlparse(args.uri).scheme != 'https':
        parser.error('The scheme of the URI must be \'https\'')

    uri = args.uri
    testssl = args.testssl
    critical = args.critical
    warning = args.warning
    trailing_args = args.trailing_args
    # pprint(args)

    # start with clean slate
    ok_msg = []
    warn_msg = []
    crit_msg = []

    msg = {
            'ok': [],
            'warning': [],
            'critical': []
            }

    # Create temp file
    fd, temp_path = tempfile.mkstemp()

    # Set command and arguments
    subproc_args = [
        testssl,
        '--jsonfile-pretty',
        temp_path,
        uri
        ]

    # Inject this script's trailing command line arguments before the 'uri' part of
    # the testssl.sh command.
    for extra in trailing_args:
        subproc_args.insert(3, extra)

    # Run it
    proc = subprocess.run(subproc_args, stdout=subprocess.PIPE)

    with open(temp_path) as f:
        json = json.load(f)
    os.close(fd)
    os.remove(temp_path)

    r = jmespath.search('scanResult[].[*][*]|[0][0][][]|[?severity]', json)

    # Add integer severity level
    for item in r:
        item['severity_int'] = severities[item['severity']]

    def get_severity_count_aggregated(severity_int):
        return len([f for f in r if f['severity_int'] >= severity_int])

    def get_severity_items_aggregated(severity_int):
        _results = sorted([f for f in r if f['severity_int'] >= severity_int], key = lambda i: i['severity_int'], reverse=True)
        return list(map(lambda x: x['severity'] +  ": " + x['id'] + " (" + x['finding'] + ")", _results))

    if get_severity_count_aggregated(severities[critical]) > 0:
        msg['critical'].append("{0} issues found for {1} with severity {2} or higher.\n{3}".format(
            get_severity_count_aggregated(severities[critical]),
            uri,
            critical,
            '\n'.join(get_severity_items_aggregated(severities[critical])),
            ))
    if get_severity_count_aggregated(severities[warning]) > 0:
        msg['warning'].append("{0} issues found for {1} with severity {2} or higher.\n{3}".format(
            get_severity_count_aggregated(severities[warning]),
            uri,
            warning,
            '\n'.join(get_severity_items_aggregated(severities[warning])),
            ))
    else:
        msg['ok'].append("No issues found for {0} with severity {1} or higher.".format(
            uri,
            warning,
            ))

except Exception as e:
    nagios_exit("UNKNOWN: Unknown error: {0}.".format(e), 3)

# Exit with accumulated message(s)
if len(msg['critical']) > 0:
    nagios_exit("CRITICAL: " + ' '.join(msg['critical']), 2)
elif len(msg['warning']) > 0:
    nagios_exit("WARNING: " + ' '.join(msg['warning']), 1)
else:
    nagios_exit("OK: " + ' '.join(msg['ok']), 0)
