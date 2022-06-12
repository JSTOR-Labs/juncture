#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
logging.basicConfig(format='%(asctime)s : %(filename)s : %(levelname)s : %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

import os
SCRIPT_DIR = os.path.abspath(os.path.dirname(__file__))
BASEDIR = os.path.dirname(SCRIPT_DIR)

import re
from time import time as now
from collections import namedtuple

from mdrender.generators import default

from bs4 import BeautifulSoup, Doctype

import markdown
from mdrender.gh import has_gh_repo_prefix, get_gh_markdown

import requests
logging.getLogger('requests').setLevel(logging.WARNING)

from mdrender.google_cloud_storage import Bucket

# https://shoelace.style/
shoelace_version = '2.0.0-beta.73'

def convert_urls(soup, base_url, md_source):
  # logger.info(f'convert_urls: source={md_source}')
  
  # remove Github badges
  for elem in soup.find_all(href=True):
    if 'mdrender' in elem.attrs['href']:
      elem.decompose()
  
  # convert absolute links
  for elem in soup.find_all(href=True):
    if elem.attrs['href'].startswith('/'):
      elem.attrs['href'] = f'/{elem.attrs["href"][1:]}'
  
  # convert image URLs
  for elem in soup.find_all(src=True):
    if elem.attrs['src'].startswith('http') or elem.name.startswith('ve-'): continue
    if md_source.source == 'github': # create github content url 
      base_url_path_elems = base_url.split('/')[6:-1]
      src_elems = re.sub(r'^\.\/', '', elem.attrs['src']).split('/')
      up = src_elems.count('..')
      gh_path = '/'.join(base_url_path_elems[:-up] + src_elems[up:])
      elem.attrs['src'] = f'https://raw.githubusercontent.com/{md_source.acct}/{md_source.repo}/{md_source.ref}/{gh_path}'
    elif elem.attrs['src'].startswith('/'):
      elem.attrs['src'] = f'{base_url}{elem.attrs["src"][1:]}'
  return soup

def get_gcs_markdown(path):
  essays = Bucket(bucket='visual-essays')
  _user, _essay_path = path.split('/',1)
  match = None
  for key in essays.keys(_user):
    if key.split('/',1)[1] == _essay_path:
      match = key
      break
  if match:
    source = {'markdown': essays.get(match), 'source': 'google-cloud-storage'}
    return namedtuple('ObjectName', source.keys())(*source.values())

def source_path(path, prefix):
  source = None
  if path:
    path = path[:-1] if path[-1] == '/' else path
    if re.match(r'^[0-9a-f]{7,64}$', path):
      path = f'{path}/default'
      source = 'gcs'
    else:
      if '/' not in path: path = f'{prefix}/{path}'
      if re.match(r'^[0-9a-f]{7,64}\/', path):
        source = 'gcs'
      else:
        if has_gh_repo_prefix(path):
          source = 'gh'
        else:
          path = f'{prefix}/{path}'
          source = 'gcs' if re.match(r'^[0-9a-f]{7,64}\/', prefix) else 'gh'
  elif prefix:
    path = prefix
    if re.match(r'^[0-9a-f]{7,64}$', prefix):
      source = 'gcs'
      path = f'{path}/default'
    elif re.match(r'^[0-9a-f]{7,64}\/.+', prefix):
      source = 'gcs'
    else:
      source = 'gh'
  logger.info(f'source={source} prefix={prefix} path={path}')
  return source, path

def load_remote(url):
  markdown = ''
  resp = requests.get(url)
  if resp.status_code == 200:
    markdown = resp.text
  logger.info(f'load_remote: url={url} status={resp.status_code} markdown_size={len(markdown)}')
  source = {'markdown': markdown, 'source': 'url', 'url': url}
  return namedtuple('ObjectName', source.keys())(*source.values())

def add_link(soup, href, attrs=None):
  link = soup.new_tag('link')
  link.attrs = {**{'href':href}, **(attrs if attrs else {})}
  soup.head.append(link)

def add_script(soup, src, attrs=None):
  script = soup.new_tag('script')
  script.attrs = {**{'src':src}, **(attrs if attrs else {})}
  soup.body.append(script)

def add_meta(soup, attrs=None):
  meta = soup.new_tag('meta')
  meta.attrs = attrs
  soup.head.append(meta)

def add_shoelace(soup):
  add_link(soup, f'https://cdn.jsdelivr.net/npm/@shoelace-style/shoelace@{shoelace_version}/dist/themes/light.css', {'rel': 'stylesheet'})
  add_script(soup, f'https://cdn.jsdelivr.net/npm/@shoelace-style/shoelace@{shoelace_version}/dist/shoelace.js', {'type': 'module'})

def merge_entities(tag, qids=None):
  qids = qids or []
  qids = qids + [qid for qid in tag.attrs.get('entities',[]) if qid not in qids]
  return merge_entities(tag.parent, qids) if tag.parent else qids

def find_qids(text):
  return re.findall(r'\b(Q[0-9]+)\b', text) if text else []

def set_entities(soup):
  for p in soup.find_all('p'):
    qids = find_qids(p.string)
    if qids:
      prior = p.find_previous_sibling()
      if not prior:
        soup.body.attrs['entities'] = qids
      else:
        p.parent.attrs['entities'] = qids
      p.decompose()

  for el in soup.find_all('section'):
    qids = merge_entities(el)
    if qids:
      el.attrs['entities'] = qids
      for child in el.find_all(recursive=False):
        if child.name.startswith('ve-'):
          child.attrs['entities'] = qids

  for el in soup.find_all('section'):
    if 'entities' in el.attrs:
      del el.attrs['entities']
  if 'entities' in soup.body.attrs:
    del soup.body.attrs['entities']

def to_html(md_source, path, base_url, **kwargs):
  start = now()
  html = markdown.markdown(
    md_source.markdown,
    extensions=[
      'customblocks',
      'extra',
      'pymdownx.mark',
      'mdx_outline',
      'codehilite',
      'fenced_code'
      # 'mdx_urlize'
    ],
    extension_configs = {
      'customblocks': {
        'fallback': default,
        'generators': {
          'default': 'md.generators:default'
        }
      }
    }
  )
  #html = re.sub(r'(\S)<em>', r'\1_', html)
  #html = re.sub(r'<\/em>(\S)', r'_\1', html)
  
  soup = BeautifulSoup(html, 'html5lib')
  soup.insert(0, Doctype('html'))
  soup.html.attrs['lang'] = 'en'

  set_entities(soup)
  convert_urls(soup, base_url, md_source)

  # for Juncture compatibility
  # if path: convert_tags (soup, path)

    

  # insert a 'main' wrapper element around the essay content
  main = soup.html.body
  main.attrs = soup.html.body.attrs
  main.name = 'main'
  body = soup.new_tag('body')
  contents = main.replace_with(body)
  body.append(contents)

  footnotes = soup.find('div', class_='footnote')
  if footnotes:
    footnotes.name = 'section'
    contents.append(footnotes)

  base = soup.new_tag('base')
  base.attrs['href'] = base_url
  soup.head.insert(0, base)

  add_meta(soup, {'name': 'viewport', 'content': 'width=device-width, initial-scale=1.0, minimum-scale=1.0, maximum-scale=5.0'})
  meta = soup.find('ve-meta')
  if meta:
    for name in meta.attrs:
      if name == 'title':
        title = soup.new_tag('title')
        title.string = meta.attrs['title']
        soup.head.append(title)
      else:
        add_meta(soup, {'name': name, 'content': meta.attrs[name]})
    meta.decompose()
  else:
    add_meta(soup, {'name': 'robots', 'content': 'noindex'})

  add_shoelace(soup)
  add_link(soup, '/static/css/main.css', {'rel': 'stylesheet'})
  style = soup.find('ve-style')
  if style:
    add_link(soup, style.attrs['layout'] if 'layout' in style.attrs else '/static/css/default-layout.css', {'rel': 'stylesheet'})
    add_link(soup, style.attrs['theme'] if 'theme' in style.attrs else '/static/css/default-theme.css', {'rel': 'stylesheet'})
    style.decompose()
  else:
    add_link(soup, '/static/css/default-layout.css', {'rel': 'stylesheet'})
    add_link(soup, '/static/css/default-theme.css', {'rel': 'stylesheet'})

  add_script(soup, kwargs['web_components_source'], {'type': 'module'})

  html = str(soup)
  html = re.sub(r'\s+<p>\s+<\/p>', '', html) # removes empty paragraphs
  return html

def get_markdown(path=None, prefix=None, url=None, ref=None, **kwargs):
  if url:
    md_source = load_remote(url)
  else:
    _source, _path = source_path(path, prefix)
    md_source = get_gh_markdown(_path, ref) if _source == 'gh' else get_gcs_markdown(_path)
  return md_source.markdown

def get_html(path=None, url=None, markdown=None, prefix=None, ref=None, **kwargs):
  start = now()
  _source, _path = source_path(path, prefix)
  if markdown:
    source = {'markdown': markdown, 'source': 'input'}
    md_source = namedtuple('ObjectName', source.keys())(*source.values())
  else:
    if url:
      md_source = load_remote(url)
    else:
      md_source = get_gh_markdown(_path, ref) if _source == 'gh' else get_gcs_markdown(_path)
  
  html = to_html(md_source, path=_path, **kwargs) if md_source else None
  logger.info(f'get_html: path={path} url={url} base_url={kwargs.get("base_url")} prefix={prefix} markdown={markdown is not None} elapsed={round(now()-start,3)}')
  return html
