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
import re
import traceback
from time import time as now
from urllib.parse import quote

import concurrent.futures

import requests
logging.getLogger('requests').setLevel(logging.WARNING)

import dill
from expiringdict import ExpiringDict

rights = {
  'Creative Commons: Free Reuse (CC0)': 'https://creativecommons.org/publicdomain/zero/1.0/',
  'Creative Commons: Attribution': 'https://creativecommons.org/licenses/by/4.0/',
  'Creative Commons: Attribution-ShareAlike': 'https://creativecommons.org/licenses/by-sa/4.0/',
  'Creative Commons: Attribution-NonCommercial': 'https://creativecommons.org/licenses/by-nc/4.0/',
  'Creative Commons: Attribution-NoDerivs': 'https://creativecommons.org/licenses/by-nd/4.0/',
  'Creative Commons: Attribution-NonCommercial-ShareAlike': 'https://creativecommons.org/licenses/by-nc-sa/4.0/',
  'Creative Commons: Attribution-NonCommercial-NoDerivs': 'https://creativecommons.org/licenses/by-nc-nd/4.0/'
}

class JSTORClient(object):

  def __init__(self, **kwargs):
    try:
      self._cache = dill.load(open('jstor.cache', 'rb'))
    except:
      self._cache = ExpiringDict(max_len=100, max_age_seconds=1800) # cache images for 30 minutes
    self.labs_api_token = os.environ.get("LABS_API_TOKEN")

  def _update_cache(self, key, data):
    self._cache[key] = data
    dill.dump(self._cache, open('jstor.cache', 'wb'))

  def jstor_depict_images(self, qid):
    docs = []
    # TODO
    return docs

  def get_labels(self, qids, language='en'):
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
      if 'digital_representation_of' in doc and doc['digital_representation_of']['id'] in labels:
        doc['digital_representation_of']['label'] = labels[doc['digital_representation_of']['id']]
      if 'depicts' in doc:
        recs = doc['depicts'] if isinstance(doc['depicts'],list) else [doc['depicts']]
        for rec in recs:
          if rec['id'] in labels:
            rec['label'] = labels[rec['id']]
    return docs

  def get_wd_entity(self, qid):
    resp = requests.get(f'https://www.wikidata.org/wiki/Special:EntityData/{qid}.json')
    if resp.status_code == 200:
      results = resp.json()
      return results['entities'][qid] if qid in results['entities'] else {}
  
  def get_jstor_items(self, dois):
    search_args = {
      'query': f'doi:({" OR ".join(dois)})',
      'limit': len(dois),
      'filter_queries': [],
      'tokens': ['16124', '24905214', '25794673', '24905191', '25794673', '24905216']
    }
    resp = requests.post(
      'https://www.jstor.org/api/labs-search-service/jstor/basic/',
      headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'User-Agent': 'Labs client'
      },
      json = search_args
    )
    # logger.info(f'get_jstor_items: status={resp.status_code} docs={len(resp["results"])}')
    if resp.status_code == 200:
      resp = resp.json()
      return resp['results']    

  '''
  SPARQL queries using new property P10187 (JSTOR artwork ID)

  # This query retrieves the JSTOR ID and depicts (P180) info for all items that have the property
  SELECT ?item ?depicts ?depictslabel ?jstorId WHERE {
    wd:P10187 wdt:P1630 ?formatterUrl .
    ?item wdt:P10187 ?jstorId ;
          wdt:P180 ?depicts .
    ?depicts rdfs:label ?depictslabel .
    FILTER(LANG(?depictslabel) = 'en')
    BIND(IRI(REPLACE(?jstorId, '^(.+)$', ?formatterUrl)) AS ?jstorUrl).
  }

  # This query provides counts for JSTOR items grouped by depicts (P180) ID
  SELECT ?depicts ?depictsLabel (COUNT(?item) AS ?numJstorItems)
  WHERE {
    ?item wdt:P10187 ?jstorId ;
          wdt:P180 ?depicts .
    OPTIONAL {
      ?depicts rdfs:label ?depictsLabel
      FILTER((LANG(?depictsLabel)) = 'en')
    }
  }
  GROUP BY ?depicts ?depictsLabel
  ORDER BY DESC(?numJstorItems) ?depictsLabel
  #LIMIT 50
  '''

  def get_depicts_dois_labs(self, qid):
    dois = []
    resp = requests.post(
      'https://www.jstor.org/api/labs-search-service/labs/about/',
      headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'User-Agent': 'Labs client'
      },
      json = {
        'query': {
          'query_string': {
            'query': f'statements.P180.mainsnak.datavalue.value.id.value:${qid} AND statements.P854.mainsnak.datavalue.value:(jstor or https://www.jstor.org)'
          }
        },
        'size': 100
      }
    )
    if resp.status_code == 200:
      results = resp.json()
      if 'hits' in results:
        for hit in results['hits'].get('hits',[]):
          doc = hit['_source']
          dois.append(f'10.2307/{doc["id"]}')
    logger.info(f'get_depicts_dois_labs: status={resp.status_code} dois={dois}')
    return dois

  def get_depicts_dois_wikidata(self, qid):
    dois = []
    query = f'SELECT ?jstorId WHERE {{ ?entity wdt:P10187 ?jstorId ; wdt:P180 wd:{qid} . }}'
    logger.info(query)
    resp = requests.get(
      f'https://query.wikidata.org/sparql?query={quote(query)}',
      headers = {
        'Content-Type': 'application/x-www-form-urlencoded', 
        'Accept': 'application/sparql-results+json',
        'User-Agent': 'Labs Client'
      }
    )
    if resp.status_code == 200:
      dois = ['.'.join(['10.2307/community', rec['jstorId']['value']]) for rec in resp.json()['results']['bindings']]
    logger.info(f'get_depicts_dois_wikidata: status={resp.status_code} dois={len(dois)}')
    return dois

  def get_depicts_items_labs(self, ids):
    depicts = {}
    dro = {}
    ids = '" OR "'.join([doi.replace('10.2307/','') for doi in ids])
    query =  f'id:("{ids}") AND statements.P854.mainsnak.datavalue.value:(jstor or https://www.jstor.org)'
    resp = requests.post(
      'https://www.jstor.org/api/labs-search-service/labs/about/',
      headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'User-Agent': 'Labs client',
        #'Authorization': f'Bearer {self.labs_api_token}'
      },
      json = {
        'query': {
          'query_string': {
            'query': query
          }
        },
        'size': 100
      }
    )
    if resp.status_code == 200:
      results = resp.json()

      if 'hits' in results:
        for hit in results['hits'].get('hits',[]):
          doc = hit['_source']
          statements = doc.get('statements',{})
          depicts[doc['id']] = [
            {'id': statement['mainsnak']['datavalue']['value']['id']['value'],
             'prominent': statement['rank'] == 'preferred'
            } for statement in  statements.get('P180',[])
          ]
          if 'P6243' in statements:
            dro[doc['id']] = {
              'id': statements['P6243'][0]['mainsnak']['datavalue']['value']['id']['value']
            }
    logger.info(f'get_depicts_items_labs: status={resp.status_code} items={len(depicts)}')
    return depicts, dro

  def get_depicts_items_wikidata(self, ids):
    depicts = {}
    dro = {}
    jstorid_filter = ', '.join([f'"{id}"' for id in ids])
    query = '''
      SELECT ?entity ?jstorId ?depicts WHERE {
        ?entity wdt:P10187 ?jstorId ;
                wdt:P180 ?depicts .
        FILTER(?jstorId IN (%s))
      }''' % (jstorid_filter)
    resp = requests.get(
      f'https://query.wikidata.org/sparql?query={quote(query)}',
      headers = {
        'Content-Type': 'application/x-www-form-urlencoded', 
        'Accept': 'application/sparql-results+json',
        'User-Agent': 'Labs Client'
      }
    )
    if resp.status_code == 200:
      for rec in resp.json()['results']['bindings']:
        doi = f'10.2307/community.{rec["jstorId"]["value"]}'
        if doi not in depicts:
          depicts[doi] = []
        if doi not in dro:
          dro[doi] = {'id': rec['entity']['value'].split('/')[-1]}
        depicts[doi].append({'id': rec['depicts']['value'].split('/')[-1]})
    logger.info(f'get_depicts_items_wikidata: status={resp.status_code} items={len(depicts)}')
    return depicts, dro

  def get_related_entities(self, docid, source='jstor'):
    query = f'id:"{docid}" AND statements.P854.mainsnak.datavalue.value:"{source}"'
    resp = requests.post(
      'https://www.jstor.org/api/labs-search-service/labs/about/',
      headers = {
        'User-Agent': 'Labs client',
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer {os.environ.get("JSTOR_API_KEY")}'
      },
      json = {'query': {'query_string': {'query': query}}, 'size': 100}
    )
    related = {}
    if resp.status_code == 200:
      results = resp.json()
      for doc in results.get('hits',{}).get('hits',[]):
        for prop in doc['_source']['statements']:
          if doc['_source']['statements'][prop][0]['mainsnak']['datavalue']['type'] == 'wikibase-entityid':
            related[prop] = []
            for stmt in doc['_source']['statements'][prop]:
              related[prop].append({
                'id': stmt['mainsnak']['datavalue']['value']['id']['value'],
                'prominent': stmt['mainsnak']['datavalue']['value']['id']['rank'] == 'preferred'
              })
    return related

  def jstor_image_search(self, query, limit=10, page_mark=None, filter_queries=None):
    results = {}
    search_args = {
      'query': query,
      'limit': limit,
      'tokens': ['16124', '24905214', '25794673', '24905191', '25794673', '24905216'],
      'filter_queries': ['cc_reuse_license:*'],
      'content_set_flags': ['contributed_images']
    }
    if page_mark:
      search_args['page_mark'] = page_mark
    if filter_queries:
      search_args['filter_queries'] += filter_queries
    resp = requests.post(
      'https://www.jstor.org/api/labs-search-service/jstor/basic/',
      headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'User-Agent': 'Labs client'
      },
      json = search_args
    )
    if resp.status_code == 200:
      results = resp.json()
    logger.info(f'jstor_image_search: status_code={resp.status_code} query={query} filter_queries={filter_queries} hits={len(results["results"] if resp.status_code == 200 else 0)}')
    return results
  
  def transform_results_docs(self, docs, weight=1):
    transformed = []
    for orig in docs:
      doc = {
        'id': f'jstor:{orig["doi"].replace("10.2307/","")}',
        'title': orig.get('item_title'),
        'rights': rights.get(orig['cc_reuse_license'][0]),
        'url': f'https://www.jstor.org/stable/{orig["doi"].replace("10.2307/","")}',
        'thumbnail': f'https://www.jstor.org/api/cached/thumbnails/202003101501/byitem/{orig["id"]}/0',
        'weight': weight
      }
      if len(orig['ps_desc']) > 0: doc['description'] = ' '.join(orig['ps_desc'])
      if len(orig['ps_source']) > 0: doc['owner'] = ' '.join(orig['ps_source'])
      if len(orig['ps_subject']) > 0: doc['tags'] = [re.sub(r'\.$', '', tag) for tag in orig['ps_subject']]
      transformed.append(doc)
    return transformed

  def jstor_search(self, qid, page_mark=None):
    results = {'total': 0, 'docs': [], 'page_mark': ''}

    entity = None
    depicts_dois = set()
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
      futures = {}
      futures[executor.submit(self.get_wd_entity, qid)] = 'wikidata_entity'
      futures[executor.submit(self.get_depicts_dois_labs, qid)] = 'depicts_dois_labs'
      futures[executor.submit(self.get_depicts_dois_wikidata, qid)] = 'depicts_dois_wikidata'

      for future in concurrent.futures.as_completed(futures):
        source = futures[future]
        try:
          if source == 'wikidata_entity': entity = future.result()
          elif source.startswith('depicts_dois'): depicts_dois.update(future.result())
        except Exception as exc:
          logger.warning('%r generated an exception: %s' % (source, exc))
          logger.info(traceback.format_exc())

    depicts_dois = list(depicts_dois)
    # query expression for metadata search using entity label and aliases
    label = entity['labels'].get('en',{}).get('value')
    label = f'"{label}"' if ' ' in label else label
    aliases = [f'"{alias["value"]}"' if ' ' in alias['value'] else alias['value'] for alias in entity.get('aliases',{}).get('en',[]) if alias['language'] == 'en']
    metadata_search_query = f'{label}^10'
    for alias in aliases:
      next_term = f' OR {alias}'
      if (len(metadata_search_query) + len(next_term)) < 250:
        metadata_search_query += next_term
      else:
        break
    
      # query expression for dois associated with items that depict qid
      joined_dois = '" OR "'.join(depicts_dois)
      depicts_dois_query = f'doi:("{joined_dois}")'
      depicts_dois_exclude_query = f'-doi:("{joined_dois}")'
    
    metadata_search_results = {'total':0, 'results':[]}
    depicts_dois_search_results = {'total':0, 'results':[]}
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
      futures = {}
      futures[executor.submit(self.jstor_image_search, metadata_search_query, 100, page_mark, filter_queries=[depicts_dois_exclude_query])] = 'metadata_search_query'
      if page_mark is None: futures[executor.submit(self.jstor_image_search, '*:*', 500, filter_queries=[depicts_dois_query])] = 'depicts_dois_query'

      for future in concurrent.futures.as_completed(futures):
        source = futures[future]
        try:
          if source == 'metadata_search_query': metadata_search_results = future.result()
          elif source == 'depicts_dois_query': depicts_dois_search_results = future.result()
        except Exception as exc:
          logger.warning('%r generated an exception: %s' % (source, exc))
          logger.info(traceback.format_exc())

    # logger.info(f'metadata_search_results={metadata_search_results is not None} depicts_dois_search_results={depicts_dois_search_results is not None}')
    
    docs = self.transform_results_docs(depicts_dois_search_results['results'], 1) + self.transform_results_docs(metadata_search_results['results'])
    docs = sorted(docs, key=lambda doc: doc['weight'], reverse=True)

    depicts_items_labs, dro_items_labs = self.get_depicts_items_labs([doc['id'].replace('jstor:','10.2307/') for doc in docs])
    depicts_items_wd, dro_items_wd = self.get_depicts_items_wikidata([doc['id'].replace('jstor:community.','') for doc in docs])

    depicts_items = {}
    for doi, depicts in depicts_items_wd.items():
      depicts_items[doi] = dict([(d['id'], d.get('prominent', False)) for d in depicts])
    
    for doi, depicts in depicts_items_labs.items():
      doi = f'10.2307/{doi}'
      if doi in depicts_items:
        depicts_items[doi].update(dict([(d['id'], d.get('prominent', False)) for d in depicts]))
      else:
        depicts_items[doi] = dict([(d['id'], d.get('prominent', False)) for d in depicts])
    dro_items = {**dro_items_wd, **dro_items_labs}

    logger.info(depicts_items)
    for doc in docs:
      doi = doc['id'].replace('jstor:','10.2307/')
      logger.info(f'{doi} {doi in depicts_items}')
      if doi in depicts_items:
        doc['depicts'] = [{'id': qid, 'prominent': depicts_items[doi][qid]} for qid in depicts_items[doi]]
        doc['weight'] = 3 if depicts_items[doi].get(qid) else 2
      if doi in dro_items:
        doc['digital_representation_of'] = dro_items[doi]
        doc['weight'] = 4 if dro_items[doi]['id'] == qid else 3
    self.add_labels(docs)

    results = {
      'total': metadata_search_results['total'] + depicts_dois_search_results['total'],
      'docs': docs,
      'page_mark': metadata_search_results.get('paging',{}).get('next')
    }
    # logger.info(f'jstor_search: qid={qid} limit={limit} page_mark={page_mark} total={results["total"]} dois={len(results["docs"])}')
 
    return results

  def search(self, qid, offset=0, limit=10, refresh=False, **kwargs):
    start = now()
    results = self._cache.get(qid) if (not refresh or offset > 0) else None
    from_cache = results is not None
    docs_needed = offset+limit
    docs_available = len(results['docs']) if results else 0
    # logger.info(f'fromCache={from_cache} docs_needed={docs_needed} docs_available={docs_available} total={results["total"] if results else 0}')
  
    if results is None or (docs_needed > docs_available and docs_available < results['total']):
      page_mark = results['page_mark'] if results else None
      current_results = self.jstor_search(qid, page_mark)
      current_results['docs'] = sorted(current_results['docs'], key=lambda doc: doc['weight'], reverse=True)
      self.add_labels(current_results['docs'])
      if results:
        results['docs'] += current_results['docs']
        results['page_mark'] = current_results['page_mark']
      else:
        results = current_results
      self._update_cache(qid, results)

    to_return = {
      'total': results['total'],
      'docs': results['docs'],
      'qtime': round(now()-start, 2)
    }
    logger.info(f'jstor.search: qid={qid} offset={offset} limit={limit} refresh={refresh} kwargs={kwargs} from_cache={from_cache} total={to_return["total"]} docs={len(to_return["docs"])} qtime={round(now()-start, 2)}')
    return to_return

if __name__ == '__main__':
  logger.setLevel(logging.INFO)
  parser = argparse.ArgumentParser(description='JSTOR client for image search')
  parser.add_argument('qid', help='Wikidata QID')
  parser.add_argument('--offset', help='Search results offset', type=int, default=0)
  parser.add_argument('--limit', help='Search results limit', type=int, default=10)
  parser.add_argument('--refresh', help='Refresh cache', type=bool, default=False)

  # parser.add_argument('--qid', help='Wikidata QID', default='Q42')

  client = JSTORClient()
  results = client.search(**vars(parser.parse_args()))
  print(json.dumps(results))  

  '''
  results = client.search(**vars(parser.parse_args()))
  dois = [doc['id'].replace('jstor:', '10.2307/') for doc in results['docs']]
  items = client.get_depicts_items(dois)
  print(json.dumps(items))  
  '''

  '''
  dois = client.get_depicts_dois(**vars(parser.parse_args()))
  print(json.dumps(dois))

  results = client.get_jstor_items(dois)
  print(json.dumps(results))
  '''