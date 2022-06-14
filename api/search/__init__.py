#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
logging.basicConfig(format='%(asctime)s : %(filename)s : %(levelname)s : %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

import argparse
import json
import traceback
from time import time as now

import concurrent.futures

try:
  from .commons import CommonsClient
  from .jstor import JSTORClient
except:
  from commons import CommonsClient
  from jstor import JSTORClient

class SearchClient(object):

  def __init__(self, **kwargs):
    self._commons = CommonsClient()
    self._jstor = JSTORClient()
  
  def merge(self, by_source, offset=0, limit=10, page_mark=None):
    
    cursors = dict([(source, 0) for source in by_source])
    for source,source_data in by_source.items():
      logger.info(f'{source}={len(source_data["docs"])}')
     
    docs = [] 
    try:   
      for weight in range(5, 0, -1):
        weight_done = False
        while not weight_done:
          matched = False
          for source in sorted(by_source):
            source_docs = by_source[source]['docs']
            if len(source_docs) > cursors[source] and source_docs[cursors[source]]['weight'] == weight:
              to_add = source_docs[cursors[source]]
              to_add['seq'] = offset + len(docs)
              docs.append(to_add)
              cursors[source] += 1
              matched = True
              if len(docs) == offset + limit:
                raise StopIteration
          weight_done = not matched
    except StopIteration:
      pass

    return docs[offset:offset+limit]

  def search(self, qid, source='all', offset=0, limit=10, **kwargs):
  
    start = now()
    by_source = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
      futures = {}
      if 'commons' in source or 'all' in source:
        futures[executor.submit(self._commons.search, qid, offset, limit, **kwargs)] = 'commons'
      if 'jstor' in source or 'all' in source:      
        futures[executor.submit(self._jstor.search, qid, offset, limit, **kwargs)] = 'jstor'

      for future in concurrent.futures.as_completed(futures):
        source = futures[future]
        try:
          by_source[source] = future.result()
        except Exception as exc:
          logger.warning('%r generated an exception: %s' % (source, exc))
          logger.info(traceback.format_exc())
    
    resp = {
      **{
        'total': sum(rec['total'] for rec in by_source.values()),
        'qtime': round(now()-start, 2)
      },
      **{'docs': self.merge(by_source, offset, limit)}
    }
    logger.info(f'search: qid={qid} source={source} offset={offset} limit={limit} kwargs={kwargs} total={resp["total"]} docs={len(resp["docs"])} qtime={round(now()-start, 2)}')
    return resp

if __name__ == '__main__':
  logger.setLevel(logging.INFO)
  parser = argparse.ArgumentParser(description='IIIF Image Search')
  parser.add_argument('qid', help='Wikidata QID')
  parser.add_argument('--offset', help='Search results offset', type=int, default=0)
  parser.add_argument('--limit', help='Search results limit', type=int, default=10)

  client = SearchClient()
  results = client.search(**vars(parser.parse_args()))
  print(json.dumps(results))