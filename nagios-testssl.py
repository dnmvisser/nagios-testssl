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
        'LOW': 1,
        'MEDIUM': 2,
        'HIGH': 3,
        'CRITICAL': 4,
        }
try:
    parser = argparse.ArgumentParser(description='Check output of testssl.sh')
    parser.add_argument('--uri', help='host|host:port|URL|URL:port.'
            'Port 443 is default, URL can only contain HTTPS protocol', required=True)
    parser.add_argument('--testssl', help='Path to the testssl.sh script', required=True)
    parser.add_argument('--skip-ids', help='Comma separated list of IDs to skip from the result', default='')
    parser.add_argument('--critical', help='Findings of this severity level trigger a CRITICAL',
            choices=severities.keys(), default='CRITICAL')
    parser.add_argument('--warning', help='Findings of this severity level trigger a WARNING', 
            choices=severities.keys(), default='HIGH')
    # FIXME this is unreliable
    #parser.add_argument('trailing_args', nargs=argparse.REMAINDER)
    args = parser.parse_args()

    if severities[args.critical] < severities[args.warning]:
        parser.error('The severity level to raise a WARNING can not be higher than the level to raise a CRITICAL')

    if urlparse(args.uri).scheme != 'https':
        parser.error('The scheme of the URI must be \'https\'')

    uri = args.uri
    testssl = args.testssl
    critical = args.critical
    warning = args.warning
    skip_ids = args.skip_ids.split(',')
    # trailing_args = args.trailing_args
    # pprint(args)


    # Possible nagios statuses
    # start with clean slate
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
        # '--fast',
        '--jsonfile-pretty',
        temp_path,
        uri
        ]

    # FIXME this is unreliable
    # Inject this script's trailing command line arguments before the 'uri' part of
    # the testssl.sh command.
    # for extra in trailing_args:
    #     subproc_args.insert(3, extra)

    # Run it
    proc = subprocess.run(subproc_args, stdout=subprocess.PIPE)

    # temp_path = os.path.expanduser('~/work/testssl_results/reset.json')
    with open(temp_path) as f:
        json = json.load(f)
    os.close(fd)
    # pprint(temp_path)
    os.remove(temp_path)

    r = jmespath.search('scanResult[].[*][*]|[0][0][][]|[?severity]', json)

    # Filter out only supported severity levels
    r = [x for x in r if x['severity'] in severities.keys()]

    # Filter out skip_ids
    r = [x for x in r if x['id'] not in skip_ids]

    # Add integer severity level
    for item in r:
        item['severity_int'] = severities[item['severity']]

    def get_severity_count_aggregated(severity_int):
        return len([f for f in r if f['severity_int'] >= severity_int])

    def get_severity_items_aggregated(severity_int):
        _results = sorted([f for f in r if f['severity_int'] >= severity_int], key = lambda i: i['severity_int'], reverse=True)
        return list(map(lambda x: x['severity'] +  ": " + x['id'] + " (" + x['finding'] + ")", _results))

    if get_severity_count_aggregated(severities[critical]) > 0:
        msg['critical'].append("{0} issue{1} found for {2} with severity {3} or higher.\n{4}".format(
            get_severity_count_aggregated(severities[critical]),
            's' if get_severity_count_aggregated(severities[critical]) > 1 else '',
            uri,
            critical,
            '\n'.join(get_severity_items_aggregated(severities[critical])),
            ))
    if get_severity_count_aggregated(severities[warning]) > 0:
        msg['warning'].append("{0} issue{1} found for {2} with severity {3} or higher.\n{4}".format(
            get_severity_count_aggregated(severities[warning]),
            's' if get_severity_count_aggregated(severities[warning]) > 1 else '',
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
