'''
Flask app for Visual Essays site.
Dependencies: bs4 Flask Flask-Cors html5lib PyYAML requests
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
from bs4 import BeautifulSoup

import yaml

import requests
logging.getLogger('requests').setLevel(logging.WARNING)

app = Flask(__name__)
CORS(app)

config = yaml.load(open(f'{SCRIPT_DIR}/config.yaml', 'r').read(), Loader=yaml.FullLoader) if os.path.exists(f'{SCRIPT_DIR}/config.yaml') else {}
logger.info(config)

def api_endpoint():
  '''Selects API endpoint to use'''
  if request.host.startswith('localhost'):
    endpoint = 'http://localhost:8000'
  else:
    domain = '.'.join(request.host.split('.')[-2:])
    if domain in ('visual-essays.net',):
      endpoint = f'https://api.{domain}'
    else:
      endpoint = 'https://api.juncture-digital.org'
  return endpoint

# Prefix for site content
prefix = config.get('prefix','a3b51252')
default_ref = config.get('ref')

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

def _get_html(path, base_url, ref=default_ref, **kwargs):
  api_url = f'{api_endpoint()}/html{path}?prefix={prefix}&base={base_url}'
  if ref: api_url += f'&ref={ref}'
  resp = requests.get(api_url)
  return resp.status_code, resp.text if resp.status_code == 200 else ''

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
@app.route('/')
def render_html(path=None):
  start = now()
  base_url = f'/{"/".join(request.base_url.split("/")[3:])}'
  if base_url != '/' and not base_url.endswith('/'): base_url += '/'
  path = f'/{path}' if path else '/'
  status, html = _get_html(path, base_url, **dict(request.args))
  logger.info(f'render: api_endpoint={api_endpoint()} base_url={base_url} prefix={prefix} path={path} status={status} elapsed={round(now()-start, 3)}')
  return html, status

if __name__ == '__main__':
  app.run(debug=True, host='0.0.0.0', port=8080)
