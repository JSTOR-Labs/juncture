'''
Flask app for Visual Essays site.
Dependencies: bs4 Flask Flask-Cors html5lib requests serverless_wsgi
'''

import logging
logging.basicConfig(format='%(asctime)s : %(filename)s : \
  %(levelname)s : %(message)s', level=logging.DEBUG)
logger = logging.getLogger()

import os
SCRIPT_DIR = os.path.abspath(os.path.dirname(__file__))

from time import time as now
from flask import Flask, request, send_from_directory
from flask_cors import CORS
from serverless_wsgi import handle_request
import argparse

from bs4 import BeautifulSoup

import requests
logging.getLogger('requests').setLevel(logging.WARNING)

app = Flask(__name__)
CORS(app)

def handler(event, context):
  return handle_request(app, event, context)

API_ENDPOINT = 'https://api.juncture-digital.org'
PREFIX = 'kent-map/dofe' # Prefix for site content
CONTENT_ROOT = None

def _add_link(soup, href, attrs=None):
  link = soup.new_tag('link')
  link.attrs = {**{'href':href}, **(attrs if attrs else {})}
  soup.head.append(link)

def _add_script(soup, src, attrs=None):
  script = soup.new_tag('script')
  script.attrs = {**{'src':src}, **(attrs if attrs else {})}
  soup.body.append(script)

def _set_favicon(soup):
  # Remove default favicon
  for el in soup.find_all('link', {'rel':'icon'}): el.decompose()
  # Add custom favicon
  # _add_link(soup, '/static/images/favicon.svg', {'rel': 'icon', 'type':'image/svg+xml'})
  # _add_link(soup, '/static/images/favicon.ico', {'rel':'icon', 'type':'image/png'})

def _set_style(soup):
  # Remove default favicon
  for el in soup.find_all('link', {'rel':'stylesheet'}): el.decompose()
  # Add custom stylesheet
  # _add_link(soup, '/static/css/custom.css', {'rel': 'stylesheet'})

def _customize_response(html):
  '''Perform any post-processing of API-generated HTML.'''
  # parse API-generated HTML with BeautifulSoup
  #   https://beautiful-soup-4.readthedocs.io/en/latest/
  soup = BeautifulSoup(html, 'html5lib')
  # perform custom updates to api-generated html
  # _set_favicon(soup)
  # _set_style(soup)
  return str(soup)

def _get_local_content(path):
  if path.endswith('/'): path = path[:-1]
  _paths = [f'{CONTENT_ROOT}{path}.md', f'{CONTENT_ROOT}{path}/README.md']
  for _path in _paths:
    if os.path.exists(_path):
      return open(_path, 'r').read()

def _get_html(path, base_url, ref=None, **kwargs):
  if CONTENT_ROOT:
    logger.info(f'_get_html: path={path} prefix={PREFIX} base={base_url}')
    md = _get_local_content(path)
    api_url = f'{API_ENDPOINT}/html/?prefix={PREFIX}&base={base_url}'
    resp = requests.post(api_url, json={'markdown':md, 'prefix':PREFIX})
    status_code, html =  resp.status_code, resp.text if resp.status_code == 200 else ''
  else:
    api_url = f'{API_ENDPOINT}/html{path}?prefix={PREFIX}&base={base_url}'
    if ref: api_url += f'&ref={ref}'
    resp = requests.get(api_url)
    status_code, html =  resp.status_code, resp.text if resp.status_code == 200 else ''
  if status_code == 200 and API_ENDPOINT == 'http://localhost:8000':
    html = html.replace('https://unpkg.com/visual-essays/dist/visual-essays','http://localhost:3333/build')
  return status_code, html

@app.route('/favicon.ico')
def favicon():
  return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/robots.txt')
def robots_txt():
  return send_from_directory(os.path.join(app.root_path, 'static'), 'robots.txt', mimetype='text/plain')

@app.route('/sitemap.txt')
def sitemap_txt():
  return send_from_directory(os.path.join(app.root_path, 'static'), 'sitemap.txt', mimetype='text/plain')

@app.route('/<path:path>')
@app.route('/<path:path>/')
@app.route('/')
def render_html(path=None):
  start = now()
  qargs = dict([(k, request.args.get(k)) for k in request.args])
  base_url = f'/{"/".join(request.base_url.split("/")[3:])}'
  if base_url != '/' and not base_url.endswith('/'): base_url += '/'
  path = f'/{path}' if path else '/'
  status, html = _get_html(path, base_url, **qargs)
  if status == 200:
    html = _customize_response(html)
  logger.debug(f'render: api_endpoint={API_ENDPOINT} base_url={base_url} \
  prefix={PREFIX} path={path} status={status} elapsed={round(now()-start, 3)}')
  return html, status

if __name__ == '__main__':
  logger.setLevel(logging.INFO)
  parser = argparse.ArgumentParser(description='Image Info')
  parser.add_argument('--port', help='Port', type=int, default=9000)
  parser.add_argument('--api', help='API Endpoint', default=API_ENDPOINT)
  parser.add_argument('--prefix', help='Content URL prefix', default=PREFIX)
  parser.add_argument('--root', help='Local content root', default=None)
  args = parser.parse_args()
  API_ENDPOINT = args.api
  PREFIX = args.prefix
  CONTENT_ROOT = os.path.abspath(args.root) if args.root else None
  logger.info(f'CONTENT_ROOT={CONTENT_ROOT}')
  app.run(debug=True, host='0.0.0.0', port=args.port)
