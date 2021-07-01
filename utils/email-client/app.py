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

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from flask import Flask, request, Response, redirect
from flask_cors import CORS

with open(f'{SCRIPT_DIR}/config.yaml', 'r') as fp:
    config = yaml.load(fp.read(), Loader=yaml.FullLoader)
logger.info(json.dumps(config, indent=2))

referrer_whitelist = set(config['referrer_whitelist'])

test_message = {
    'from': 'JSTOR Labs <labs@ithaka.org>',
    'to': ['Ron Snyder <ron.snyder@ithaka.org>'],
    'subject': 'Contact Us',
    'message': 'Testing'
}

app = Flask(__name__)
CORS(app)

def sendgrid(**kwargs):
    fields = {'to': 'to_emails', 'from': 'from_email', 'message': 'html_content'}
    message = Mail(**dict([(fields.get(fld,fld),val) for fld, val in kwargs.items()]))
    try:
        sg = SendGridAPIClient(config['providers']['sendgrid']['api_token'])
        response = sg.send(message)
        logger.debug(response.status_code)
        logger.debug(response.body)
        logger.debug(response.headers)
        return response.body, 200
    except Exception as e:
        logger.error(json.loads(e.body))
        return json.loads(e.body), 500

def parse_email(s):
    match = re.search(r'<(\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b)>', s)
    return {'name': s.split('<')[0].strip(), 'email': match.group(1)} if match else {'name': '', 'email': s.strip()}

def sendinblue(**kwargs):
    data = {
        'sender': parse_email(kwargs['from']),
        'to': [parse_email(to) for to in kwargs['to']] if isinstance(kwargs['to'],list) else [parse_email(kwargs['to'])],
        'subject': kwargs['subject'],
        'htmlContent': kwargs['message']
    }
    resp = requests.post(
        'https://api.sendinblue.com/v3/smtp/email',
        headers = {
            'Content-type': 'application/json; charset=utf-8', 
            'Accept': 'application/json',
            'api-key': config['providers']['sendinblue']['api_token']
        },
        data = json.dumps(data))
    return resp

def sendmail(**kwargs):
    return globals()[kwargs.pop('provider', config['default_provider'])](**kwargs)

@app.route('/', methods=['OPTIONS', 'POST'])
def _sendmail():
    referrer = '.'.join(urlparse(request.referrer).netloc.split('.')[-2:]) if request.referrer else None
    logger.info(f'sendmail: referrer={referrer} provider={request.json.get("provider", config["default_provider"])} payload={request.json}')
    if referrer in referrer_whitelist:
        return sendmail(**request.json)
    else:
        return 'Forbidden', 403

def usage():
    print(f'{sys.argv[0]} [hl:p:f:t:s:m:]')
    print(f'   -h --help             Print help message')
    print(f'   -l --loglevel         Logging level (default=warning)')
    print(f'   -p --provider         Provider (default={config["default_provider"]}')
    print(f'   -f --from             Sender email address')
    print(f'   -t --to               Recipient email addresses (comma separated)')
    print(f'   -s --subject          Email subject')
    print(f'   -m --message          Email message')


if __name__ == '__main__':
    kwargs = {}
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'hl:p:f:t:s:m:', ['help', 'loglevel', 'provider', 'from', 'to', 'subject', 'message'])
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
        elif o in ('-p', '--provider'):
            kwargs['provider'] = a
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

    # logger.info(sendmail(**{**test_message, **kwargs}))
    app.run(debug=True, host='0.0.0.0')