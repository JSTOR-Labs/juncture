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

def convert_urls(soup, base_url, md_source, ref=None):
  # logger.info(f'convert_urls: md_source.ref={md_source.ref} ref={ref}')
  
  # remove Github badges
  for img in soup.find_all('img'):
    if 've-button.png' in img.attrs['src']:
      img.parent.decompose()
  
  # convert absolute links
  for elem in soup.find_all(href=True):
    if elem.attrs['href'].startswith('/'):
      if md_source.source == 'github':
         elem.attrs['href'] = elem.attrs['href'][1:] + (f'?ref={ref}' if ref else '')
  
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
  
  for elem in soup.find_all('param'):
    for fld in ('url', 'banner'):
      if fld in elem.attrs and not elem.attrs[fld].startswith('http'):
        orig = elem.attrs[fld]
        gh_path = elem.attrs[fld]
        base = f'/{md_source.acct}/{md_source.repo}/{md_source.ref}'
        if gh_path.startswith('/'):
          gh_path = f'{base}{gh_path}'
        else:
          gh_path = f'{base}/' + '/'.join([elem for elem in base_url.split('/') if elem][2:-1]) + gh_path
        elem.attrs[fld] = f'https://raw.githubusercontent.com{gh_path}'
        logger.info(f'orig={orig} base_url={base_url} new={elem.attrs[fld]}')

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

def to_html(md_source, prefix, ref, base_url, web_components_source, **kwargs):
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

  set_entities(soup)
  convert_urls(soup, base_url, md_source, ref)

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

  is_v1 = soup.find('param') is not None
  if is_v1:
    template = open(f'{SCRIPT_DIR}/templates/v1.html', 'r').read()
    if prefix: template = template.replace('const PREFIX = null', f"const PREFIX = '{prefix}'")
    if ref: template = template.replace('const REF = null', f"const REF = '{ref}'")
    template = BeautifulSoup(template, 'html5lib')
    for el in template.find_all('component'):
      if 'v-bind:is' in el.attrs and el.attrs['v-bind:is'] == 'mainComponent':
        el.append(contents)
        break

    css = open(f'{SCRIPT_DIR}/templates/v1.css', 'r').read()    

  else:
    template = BeautifulSoup(open(f'{SCRIPT_DIR}/templates/v2.html', 'r').read(), 'html5lib')
    if 'localhost' in web_components_source:
      template.find('script', src='https://unpkg.com/visual-essays/dist/visual-essays/visual-essays.esm.js').attrs['src'] = 'http://localhost:3333/build/visual-essays.esm.js'
    template.body.insert(0, contents)

    css = '\n' +  open(f'{SCRIPT_DIR}/templates/main.css', 'r').read()
    style = soup.find('ve-style')
    if style and 'theme' in style.attrs:
      add_link(template, style.attrs['theme'], {'rel': 'stylesheet'})
    else:
      css += '\n' + open(f'{SCRIPT_DIR}/templates/default-theme.css', 'r').read()
    if style and 'layout' in style.attrs:
      add_link(soup, style.attrs['layout'], {'rel': 'stylesheet'})
    else:
      css += '\n' + open(f'{SCRIPT_DIR}/templates/default-layout.css', 'r').read()
    if style:
      style.decompose()

  template.find('base').attrs['href'] = base_url
  style = soup.new_tag('style')
  style.string = css
  template.head.append(style)

  meta = soup.find('ve-meta')
  if meta:
    for name in meta.attrs:
      if name == 'title':
        title = soup.new_tag('title')
        title.string = meta.attrs['title']
        template.head.append(title)
      else:
        add_meta(template, {'name': name, 'content': meta.attrs[name]})
    meta.decompose()
  else:
    add_meta(template, {'name': 'robots', 'content': 'noindex'})

  html = str(template)
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
  
  html = to_html(md_source, prefix, ref, path=_path, **kwargs) if md_source else None
  logger.info(f'get_html: path={path} url={url} source={md_source.source if md_source else None} base_url={kwargs.get("base_url")} prefix={prefix} markdown={markdown is not None} elapsed={round(now()-start,3)}')
  return html
