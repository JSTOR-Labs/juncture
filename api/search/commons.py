#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
logging.basicConfig(format='%(asctime)s : %(filename)s : %(levelname)s : %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

import os
SCRIPT_DIR = os.path.abspath(os.path.dirname(__file__))
BASEDIR = SCRIPT_DIR

import argparse
import json
import traceback
import hashlib
from time import time as now
from urllib.parse import quote, unquote

from typing import List

import concurrent.futures

from bs4 import BeautifulSoup

import requests
logging.getLogger('requests').setLevel(logging.WARNING)

import dill
from expiringdict import ExpiringDict

class CommonsClient(object):

  def __init__(self, **kwargs):
    try:
      self._cache = dill.load(open('commons.cache', 'rb'))
    except:
      self._cache = ExpiringDict(max_len=100, max_age_seconds=1800) # cache images for 30 minutes
  
  def _update_cache(self, key, data):
    self._cache[key] = data
    dill.dump(self._cache, open('commons.cache', 'wb'))

  def wikidata_depict_images(self, qid):
    start = now()
    docs = []
    query = '''
      SELECT DISTINCT ?image ?depicts WHERE { 
      ?entity wdt:P180 wd:%s ; wdt:P180 ?depicts ; wdt:P18 ?image . }''' % qid
    resp = requests.get(
      f'https://query.wikidata.org/sparql?query={quote(query)}',
      headers = {
        'Content-Type': 'application/x-www-form-urlencoded', 
        'Accept': 'application/sparql-results+json',
        'User-Agent': 'Labs Client'
      }
    )
    if resp.status_code == 200:
      images = {}
      for rec in resp.json()['results']['bindings']:
        title = unquote(rec['image']['value'].split('/')[-1])
        url = f'https://commons.wikimedia.org/wiki/File:{title.replace(" ", "_")}'
        id = f'wc:{quote(title.replace(" ","_"))}'
        if id not in images:
          images[id] = {
            'id': id,
            'title': title,
            'depicts': [],
            'url': url,
            'thumbnail': self.image_url(title, 240),
            'weight': 2
          }
        images[id]['depicts'].append({'id': rec['depicts']['value'].split('/')[-1]})
      docs = images.values()
    logger.info(f'wikidata_depict_images: status={resp.status_code} docs={len(docs)} qtime={round(now()-start, 2)}')
    return docs

  def commons_depict_images_sparql(self, qid: str):
    start = now()
    docs = None
    query = '''
      SELECT DISTINCT ?entity ?image ?depicts ?rank ?dro WHERE { 
        ?entity wdt:P180 wd:%s ; schema:url ?image .   
        ?entity p:P180 [ ps:P180 ?depicts ; wikibase:rank ?rank ] .
        OPTIONAL { ?entity wdt:P6243 ?dro . }
      }''' % qid
    resp = requests.get(
      f'https://wcqs-beta.wmflabs.org/sparql?query={quote(query)}',
      headers = {
        'Content-Type': 'application/x-www-form-urlencoded', 
        'Accept': 'application/sparql-results+json',
        'User-Agent': 'Labs Client'
      }
    )
    logger.info(f'wcqs-beta.wmflabs.org.response_code={resp.status_code}')
    if resp.status_code == 200:
      docs = []
      images = {}
      for rec in resp.json()['results']['bindings']:
        title = unquote(rec['image']['value'].split('/')[-1])
        url = f'https://commons.wikimedia.org/wiki/File:{title.replace(" ", "_")}'
        id = f'wc:{quote(title.replace(" ","_"))}'
        if id not in images:
          images[id] = {
            'id': id,
            'title': title,
            'depicts': [],
            'url': url,
            'thumbnail': self.image_url(title, 240),
            'weight': 2
          }
        depicts_id = rec['depicts']['value'].split('/')[-1]
        depicts = {'id': depicts_id}
        if rec['rank']['value'].split('#')[-1] == 'PreferredRank':
          depicts['prominent'] = True
          if depicts_id == qid:
            images[id]['weight'] = 3
        if 'dro' in rec:
          dro_id = rec['dro']['value'].split('/')[-1]
          images[id]['digital_representation_of'] = {'id': dro_id}
          depicts['prominent'] = True
          if dro_id == qid:
            images[id]['weight'] = 4
        images[id]['depicts'].append(depicts)
      docs = images.values()
      for doc in docs:
        doc['depicts'].sort(key=lambda doc: doc.get('prominent',False), reverse=True)
    logger.info(f'commons_depict_images_sparql: status={resp.status_code} docs={len(docs) if docs else None} qtime={round(now()-start, 2)}')
    return docs

  def commons_depict_images_wikimedia(self, qid: str):
    start = now()
    def get_depicts():
      url = f'https://commons.wikimedia.org/w/api.php?action=query&list=search&srsearch=haswbstatement:P180={qid}&srnamespace=6&srlimit=500&format=json'
      return requests.get(url).json().get('query',{}).get('search',[])

    def get_dro():
      url = f'https://commons.wikimedia.org/w/api.php?action=query&list=search&srsearch=haswbstatement:P6243={qid}&srnamespace=6&srlimit=500&format=json'
      return requests.get(url).json().get('query',{}).get('search',[])

    def parse_results(recs):
      images = {}
      for rec in recs:
        title = rec['title'][5:]
        url = f'https://commons.wikimedia.org/wiki/File:{title.replace(" ", "_")}'
        id = f'wc:{quote(title.replace(" ","_"))}'
        if id not in images:
          images[id] = {
            'id': id,
            'title': title,
            'depicts': [{'id': qid}],
            'url': url,
            'thumbnail': self.image_url(title, 240),
            'weight': 2
          }
      return images

    by_source = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
      futures = {}
      futures[executor.submit(get_depicts)] = 'depicts'
      futures[executor.submit(get_dro)] = 'dro'

      for future in concurrent.futures.as_completed(futures):
        source = futures[future]
        try:
          by_source[source] = parse_results(future.result())
        except Exception as exc:
          logger.warning('%r generated an exception: %s' % (source, exc))
          logger.info(traceback.format_exc())

    if 'depicts' in by_source and 'dro' in by_source:
      for id, doc in by_source['dro'].items():
        if id not in by_source['depicts']:
          by_source['depicts'][id] = by_source['dro'][id]
        by_source['depicts'][id]['digital_representation_of'] = {'id': qid, 'prominent': True}
        by_source['depicts'][id]['depicts'][0]['prominent'] = True
        by_source['depicts'][id]['weight'] = 3

    docs = by_source.get('depicts',{}).values()
    for doc in docs:
        doc['depicts'].sort(key=lambda doc: doc.get('prominent',False), reverse=True)
    logger.info(f'commons_depict_images_wikimedia: docs={len(docs)} qtime={round(now()-start, 2)}')
    return docs

  def commons_depict_images(self, qid: str):
    docs = self.commons_depict_images_sparql(qid)
    if docs == None:
      docs = self.commons_depict_images_wikimedia(qid)
    return docs

  def get_image_metadata(self, titles: List[str]):
    start = now()
    metadata = {}
    titles = [f'File:{title}' for title in titles]
    url = f'https://commons.wikimedia.org/w/api.php?origin=*&format=json&action=query&prop=imageinfo&iiprop=extmetadata|size|mime&titles={"|".join(titles)}'
    resp = requests.get(url)
    if resp.status_code == 200:
      resp = resp.json()
      pages = resp.get('query',{}).get('pages',{})
      for pageid, page in pages.items():
        if 'imageinfo' in page:
          md = {**page['imageinfo'][0], **page['imageinfo'][0]['extmetadata']}
          del md['extmetadata']
          md['pageid'] = pageid
          metadata[page['title']] = md
    logger.info(f'get_image_metadata: items={len(metadata)} qtime={round(now()-start, 2)}')
    return metadata

  def extract_text(self, val, lang='en'):
    soup = BeautifulSoup(val, 'html5lib')
    _elem = soup.select_one(f'[lang="{lang}"]')
    return (_elem.text if _elem else soup.text).strip()

  def get_labels(self, qids, language='en'):
    start = now()
    labels = {}
    values = ' '.join([f'(<http://www.wikidata.org/entity/{qid}>)' for qid in qids])
    query = f'SELECT ?item ?label WHERE {{ VALUES (?item) {{ {values} }} ?item rdfs:label ?label . FILTER (LANG(?label) = "{language}" || LANG(?label) = "en") .}}'
    resp = requests.post(
      'https://query.wikidata.org/sparql',
      headers = {
        'Content-Type': 'application/x-www-form-urlencoded', 
        'Accept': 'application/sparql-results+json',
        'User-Agent': 'Labs Client'
      },
      data={'query': query}
    )
    if resp.status_code == 200:
      labels = dict([(rec['item']['value'].split('/')[-1],rec['label']['value']) for rec in resp.json()['results']['bindings']])
      for qid in qids:
        if qid not in labels:
          labels[qid] = ''
    logger.info(f'get_labels: items={len(labels)} qtime={round(now()-start, 2)}')
    return labels

  def add_labels(self, docs, language='en'):
    labels = self._cache.get(f'{language}-labels', {})
    
    qids = set([])
    for doc in docs:
      for fld in ('depicts', 'digital_representation_of'):
        if fld in doc:
          recs = doc[fld] if isinstance(doc[fld],list) else [doc[fld]]
          for rec in recs:
            if rec['id'] not in labels:
              qids.add(rec['id'])
    if len(qids) > 0:
      labels = {**labels, **self.get_labels(qids, language)}
      self._update_cache(f'{language}-labels', labels)

    for doc in docs:
      for fld in ('depicts', 'digital_representation_of'):
        if fld in doc:
          recs = doc[fld] if isinstance(doc[fld],list) else [doc[fld]]
          for rec in recs:
            if rec['id'] in labels:
              rec['label'] = labels[rec['id']]
    return docs

  def image_url(self, title, width=None):
    title = title.replace(' ','_')
    md5 = hashlib.md5(title.encode('utf-8')).hexdigest()
    extension = title.split('.')[-1]
    img_url = f'https://upload.wikimedia.org/wikipedia/commons/{"thumb/" if width else ""}'
    img_url += f'{md5[:1]}/{md5[:2]}/{quote(title)}'
    if width:
      img_url = f'{img_url}/{width}px-{title}'
      if extension == 'svg': img_url += '.png'
      elif extension == 'tif' or extension == 'tiff': img_url += '.jpg'
    return img_url

  def search(self, qid, offset=0, limit=10, language='en', refresh=False, **kwargs):
    start = now()
    docs = self._cache.get(qid) if (not refresh or offset > 0) else None
    from_cache = docs is not None
    if docs is None:
      by_source = {}
      with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        futures = {}
        futures[executor.submit(self.wikidata_depict_images, qid)] = 'wikidata'
        futures[executor.submit(self.commons_depict_images, qid)] = 'commons'

        for future in concurrent.futures.as_completed(futures):
          source = futures[future]
          try:
            by_source[source] = future.result()
          except Exception as exc:
            logger.warning('%r generated an exception: %s' % (source, exc))
            logger.info(traceback.format_exc())
      docs = list({
        **dict([(doc['id'],doc) for doc in by_source.get('wikidata',{})]),
        **dict([(doc['id'],doc) for doc in by_source.get('commons', {})]),
      }.values())
      
      docs = self.add_labels(docs, language)
      docs = sorted(docs, key=lambda doc: doc['weight'], reverse=True)
      self._update_cache(qid, docs)
    
    metadata_needed = [doc['title'] for doc in docs[:offset+(limit*(3 if offset == 0 else 1))] if 'pageid' not in doc]
    # logger.info(f'offset={offset} limit={limit} metadata_needed={len(metadata_needed)}')
    if len(metadata_needed) > 0:
      metadata = self.get_image_metadata(metadata_needed)
      for doc in docs:
        md = metadata.get(f'File:{doc["title"]}')
        if md is None: continue
        doc['pageid'] = md['pageid']
        # logger.info(json.dumps(md,indent=2))
        if md is None: continue
        if 'LicenseUrl' in md:
            doc['rights'] = md['LicenseUrl']['value']
        elif md.get('License',{}).get('value') in ('pd', 'pdm'):
          doc['rights'] = 'https://creativecommons.org/publicdomain/mark/1.0/'
        if 'ObjectName' in md:
          doc['title'] = self.extract_text(md['ObjectName']['value'])
        else:
          doc['title'] = unquote(doc['id'][3:])
        if 'ImageDescription' in md:
          # doc['description'] = md['ImageDescription']['value']
          doc['description'] = self.extract_text(md['ImageDescription']['value'])
        for fld in ['Attribution', 'Artist']:
          if fld in md:
            # doc['owner'] = md[fld]['value'].replace('<big>','').replace('</big>','')
            doc['owner'] = self.extract_text(md[fld]['value'].replace('<big>','').replace('</big>',''))
            break
      self._update_cache(qid, docs)
    
    results = {
      'total': len(docs),
      'docs': docs,
      'qtime': round(now()-start, 2)
    }
    logger.info(f'commons.search: qid={qid} offset={offset} limit={limit} kwargs={kwargs} fromCache={from_cache} total={results["total"]} docs={len(results["docs"])} qtime={round(now()-start, 2)}')
    return results

if __name__ == '__main__':
  logger.setLevel(logging.INFO)
  parser = argparse.ArgumentParser(description='Commons client for image search')
  parser.add_argument('qid', help='Wikidata QID')
  parser.add_argument('--offset', help='Search results offset', type=int, default=0)
  parser.add_argument('--limit', help='Search results limit', type=int, default=10)
  parser.add_argument('--refresh', help='Refresh cache', type=bool, default=False)

  # parser.add_argument('--qid', help='Wikidata QID', default='Q42')

  client = CommonsClient()
  results = client.search(**vars(parser.parse_args()))
  print(json.dumps(results))