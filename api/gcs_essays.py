#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
logging.basicConfig(format='%(asctime)s : %(filename)s : %(levelname)s : %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

import sys
import getopt
import json
import jwt
import time
import datetime
from hashlib import sha256

from mdrender.google_cloud_storage import Bucket

class GCSEssays(object):

  def __init__(self, **kwargs):
    self.essays_store = Bucket(bucket='visual-essays')
  
  def _decode_token(self, token):
    decoded = jwt.decode(token, options={'verify_signature': False})
    if 'exp' in decoded:
      decoded['expires_at'] = datetime.datetime.fromtimestamp(decoded['exp']).strftime('%Y-%m-%dT%H:%M:%SZ')
    if 'email' in decoded:
      decoded['emailhash'] = sha256(decoded['email'].lower().encode('utf-8')).hexdigest()[:7]
    return decoded
    
  def _token_is_valid(self, claims):
    if 'exp' in claims:
      current = round(time.time())
      remaining = claims['exp']-current
      logger.info(f'_token_is_valid: current={current} expires={claims["exp"]} remaining={remaining}')
      return remaining > 0
    return False

  def get(self, path):
    logger.info(f'get: path={path}')
    path_elems = [elem for elem in path.split('/') if elem]
    if len(path_elems) == 1: # get files list
      return 200, [key for key in self.essays_store.keys(prefix=path_elems[0])]
    else: # get file
      content = self.essays_store.get('/'.join(path_elems))
      return 200 if content else 404, content

  def put(self, path, content, token):
    logger.info(f'put: path={path}')
    if not self._token_is_valid(self._decode_token(token)):
      return 403, {}
    path_elems = [elem for elem in path.split('/') if elem]
    self.essays_store['/'.join(path_elems)] = content
    return 200, content

  def delete(self, path, token):
    logger.info(f'delete: path={path}')
    if not self._token_is_valid(self._decode_token(token)):
      return 403
    path_elems = [elem for elem in path.split('/') if elem]
    del self.essays_store['/'.join(path_elems)]
    return 204

def usage():
    print('%s [hl:d] path' % sys.argv[0])
    print('   -h --help            Print help message')
    print('   -l --loglevel        Logging level (default=warning)')
    print('   -d --delete          Delete object')

if __name__ == '__main__':
  kwargs = {}
  try:
    opts, args = getopt.getopt(sys.argv[1:], 'hl:d', ['help', 'loglevel', 'delete'])
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
    elif o in ('-d', '--delete'):
      kwargs['delete'] = True
    elif o in ('-h', '--help'):
      usage()
      sys.exit()
    else:
      assert False, 'unhandled option'

  client = GCSEssays()

  if sys.stdin.isatty():
    for key in args:
      if kwargs.get('delete', False):
        client.delete(key)
      else:
        print(client.get(key))
  elif len(args) == 1:
    key = args[0]
    for content in sys.stdin:
      logger.info(f'key={key} content={content}')
      client.put(key, content)
      break
