'''
Flask app for Visual Essays site.
Dependencies: bs4 Flask Flask-Cors html5lib requests
'''

import logging
logging.basicConfig(format='%(asctime)s : %(filename)s : \
  %(levelname)s : %(message)s', level=logging.DEBUG)
logger = logging.getLogger()

import os
from time import time as now
from flask import Flask, request, send_from_directory
from flask_cors import CORS
from bs4 import BeautifulSoup

import requests
logging.getLogger('requests').setLevel(logging.WARNING)

app = Flask(__name__)
CORS(app)

def api_endpoint():
  return 'http://localhost:8000' if request.host.startswith('localhost') or request.host.startswith('192.168') else 'https://api.visual-essays.net'

# Prefix for site content
# prefix = 'visual-essays/content'
prefix = 'a3b51252'

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
  # for el in soup.find_all('link', {'rel':'icon'}): el.decompose()
  _add_link(soup, '/static/images/favicon.svg', {'rel': 'icon', 'type':'image/svg+xml'})
  _add_link(soup, '/static/images/favicon.ico', {'rel':'icon', 'type':'image/png'})

def _add_default_footer(soup):
  main = soup.find('body')
  main.append(soup.new_tag('ve-footer'))

def _customize_response(html):
  '''Perform any post-processing of API-generated HTML.'''
  # parse API-generated HTML with BeautifulSoup
  #   https://beautiful-soup-4.readthedocs.io/en/latest/
  soup = BeautifulSoup(html, 'html5lib')
  # perform custom updates to api-generated html
  _set_favicon(soup)
  if not request.host.startswith('localhost'):
    _add_script(soup, 'https://www.googletagmanager.com/gtag/js?id=G-DRHNQSMN5Y', {'type':'text/javascript', 'async':''})
  
  is_v1 = soup.find('param',ve_config='') is not None
  if is_v1: # For Juncture V1 
    for src in ['https://juncture-digital.org/images/ve-button.png', 'https://dev-visual-essays.netlify.app/images/ve-button.png']:
      btn = soup.find(src=src)
      if btn:
        btn.parent.decompose()
    html = open('static/html/juncture-v1.html', 'r').read()
    essay_text = str(soup.find('main'))
    return html.replace('<<HTML>>', essay_text)
  else:
    _add_script(soup, '//cdnjs.cloudflare.com/ajax/libs/ScrollMagic/2.0.7/ScrollMagic.min.js', {'type':'text/javascript'})
    _add_script(soup, '//cdnjs.cloudflare.com/ajax/libs/ScrollMagic/2.0.7/plugins/debug.addIndicators.min.js', {'type':'text/javascript'})
    _add_script(soup, '/static/js/main.js', {'type':'text/javascript', 'defer':''})
    _add_default_footer(soup)
    return str(soup)

def _get_html(path, base_url, ref=None, **kwargs):
  api_url = f'{api_endpoint()}/html{path}?prefix={prefix}&base={base_url}'
  if ref:
    api_url += f'&ref={ref}'
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
  qargs = dict([(k, request.args.get(k)) for k in request.args])
  base_url = f'/{"/".join(request.base_url.split("/")[3:])}'
  if base_url != '/' and not base_url.endswith('/'): base_url += '/'
  path = f'/{path}' if path else '/'
  status, html = _get_html(path, base_url, **qargs)
  if status == 200:
    html = _customize_response(html)
  logger.debug(f'render: api_endpoint={api_endpoint()} base_url={base_url} \
  prefix={prefix} path={path} status={status} elapsed={round(now()-start, 3)}')
  return html, status

if __name__ == '__main__':
  app.run(debug=True, host='0.0.0.0', port=8080)
