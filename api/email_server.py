#!/usr/bin/env python
# -*- coding: utf-8 -*-

# https://docs.sendgrid.com/for-developers/sending-email/v3-python-code-example
# https://developers.sendinblue.com/docs/send-a-transactional-email

import logging
logging.basicConfig(format='%(asctime)s : %(filename)s : %(levelname)s : %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

import os
SCRIPT_DIR = os.path.abspath(os.path.dirname(__file__))

import sys
import getopt
import json
import re
from urllib.parse import urlparse

import yaml

import requests
logging.getLogger('requests').setLevel(logging.INFO)

with open(f'{SCRIPT_DIR}/creds.yaml', 'r') as fp:
  config = yaml.load(fp.read(), Loader=yaml.FullLoader)
api_token = config['sendinblue_api_token']
referrer_whitelist = set(config['referrer_whitelist'])

test_message = {
    'from': 'Ron Snyder <ron@snyderjr.com>',
    'to': ['Ron Snyder <ron@snyderjr.com>'],
    'subject': 'Visual Essays Contact',
    'message': 'Testing'
}

def parse_email(s):
    match = re.search(r'<(\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b)>', s)
    return {'name': s.split('<')[0].strip(), 'email': match.group(1)} if match else {'email': s.strip()}

def sendinblue(**kwargs):
    referrer = '.'.join(urlparse(kwargs['referrer']).netloc.split('.')[-2:]) if 'referrer' in kwargs else None
    if referrer not in referrer_whitelist:
        return 'Forbidden', 403
    data = {
        'sender': parse_email(kwargs['from']),
        'to': [parse_email(to) for to in kwargs['to']] if isinstance(kwargs['to'],list) else [parse_email(kwargs['to'])],
        'subject': kwargs['subject'],
        'htmlContent': kwargs['message']
    }
    logger.debug(json.dumps(data, indent=2))
    resp = requests.post(
        'https://api.sendinblue.com/v3/smtp/email',
        headers = {
            'Content-type': 'application/json; charset=utf-8', 
            'Accept': 'application/json',
            'api-key': api_token
        },
        data = json.dumps(data))
    return resp.content, resp.status_code

def sendmail(**kwargs):
    return sendinblue(**kwargs)

def usage():
    print(f'{sys.argv[0]} [hl:f:t:s:m:]')
    print(f'   -h --help             Print help message')
    print(f'   -l --loglevel         Logging level (default=warning)')
    print(f'   -f --from             Sender email address')
    print(f'   -t --to               Recipient email addresses (comma separated)')
    print(f'   -s --subject          Email subject')
    print(f'   -m --message          Email message')


if __name__ == '__main__':
    kwargs = {}
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'hl:f:t:s:m:', ['help', 'loglevel', 'from', 'to', 'subject', 'message'])
    except getopt.GetoptError as err:
        # print help information and exit:
        print(str(err)) # will print something like "option -a not recognized"
        usage()
        sys.exit(2)

    for o, a in opts:
        if o in ('-l', '--loglevel'):
            loglevel = a.lower()
            if loglevel in ('error',): logger.setLevel(logging.ERROR)
            elif loglevel in ('warn','warning'): logger.setLevel(logging.INFO)
            elif loglevel in ('info',): logger.setLevel(logging.INFO)
            elif loglevel in ('debug',): logger.setLevel(logging.DEBUG)
        elif o in ('-f', '--from'):
            kwargs['from'] = a
        elif o in ('-t', '--to'):
            kwargs['to'] = a.split(',')
        elif o in ('-s', '--subject'):
            kwargs['subject'] = a
        elif o in ('-m', '--message'):
            kwargs['message'] = a
        elif o in ('-h', '--help'):
            usage()
            sys.exit()
        else:
            assert False, 'unhandled option'

    logger.info(sendmail(**{**test_message, **kwargs}))
