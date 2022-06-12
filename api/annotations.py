#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
logging.basicConfig(format='%(asctime)s : %(filename)s : %(levelname)s : %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

import argparse
import json
import jwt
import datetime
import time
from hashlib import sha256

from mdrender.gh import has_gh_repo_prefix, get_gh_file, put_gh_file
from mdrender.google_cloud_storage import Bucket

test_annos = json.load(open(f'./test_annotations.json', 'r'))

class Annotations(object):

  def __init__(self, **kwargs):
    self.annotations_store = Bucket(bucket='ve-annotations')

  def _parse_path(self, path):
    path_elems = [elem for elem in path.split('/') if elem]
    for i in range(2):
      is_gh_repo = has_gh_repo_prefix('/'.join(path_elems[i:i+2]))
      if is_gh_repo:
        user = path_elems[i]
        repo = path_elems[i+1]
        target = '/'.join(path_elems[i+2:])
        return user, repo, target
    user = path_elems[0]
    repo = None
    target = '/'.join(path_elems[1:])
    logger.debug('parse_path: path={path} user={user} repo={repo} target={target}')
    return user, repo, target

  def _get_annotations(self, user, repo, target, base_url=None):
    logger.debug(f'_get_annotations: user={user} repo={repo} target={target}')
    annotations = []
    sha = None
    if repo:
      content, _, sha = get_gh_file(user, repo, f'{target}.json')
      if content:
        content = json.loads(content)
        annotations = content['items'] if isinstance(content, dict) and 'items' in content else content
        target_uri = f'/{user}/{repo}/{target}'
        anno_base_uri = f'{base_url if base_url else "/"}annotation/{user}/{repo}{target}'
    else:
      match = None
      for key in self.annotations_store.keys(user):
        _target = key.split('/',1)[1]
        if _target.startswith(target):
          match = key
          break
      content = self.annotations_store.get(match) if match else None
      if content:
        annotations = json.loads(content)
        target_uri = f'/{user}/{target}'
        anno_base_uri = f'{base_url if base_url else "/"}annotation/{user}/{target}'

    # convert relative IDs to full URIs
    for anno in annotations:
      anno['target']['id'] = target_uri
      anno['id'] = f'{anno_base_uri}/{anno["id"]}'
    return annotations, sha
  
  def _decode_token(self, token):
    try:
      decoded = jwt.decode(token, options={'verify_signature': False})
      if 'exp' in decoded:
        decoded['expires_at'] = datetime.datetime.fromtimestamp(decoded['exp']).strftime('%Y-%m-%dT%H:%M:%SZ')
      if 'email' in decoded:
        decoded['emailhash'] = sha256(decoded['email'].lower().encode('utf-8')).hexdigest()
      return decoded
    except:
      return {}
    
  def _token_is_valid(self, claims):
    if 'exp' in claims:
      current = round(time.time())
      remaining = claims['exp']-current
      logger.info(f'_token_is_valid: current={current} expires={claims["exp"]} remaining={remaining}')
      return remaining > 0
    return False

  def _set_annotations(self, user, repo, target, annotations, sha, token):
    logger.debug(f'_set_annotations: user={user} repo={repo} target={target} sha={sha} token={token}')
    if repo:
      put_gh_file(user, repo, target, annotations, sha, token)
    else:
      self.annotations_store[f'{user}/{target}'] = json.dumps(annotations)

  def get_annotations(self, path, base_url):
    user, repo, target = self._parse_path(path)
    annotations, _ = self._get_annotations(user, repo, target, base_url)
    if len(annotations) == 0 and '/' in target:
      annotations, _ = self._get_annotations(user, repo, target.split('/')[-1], base_url)
    return {'user': user, 'repo': repo, 'target': target,
      'annotations': annotations
    }

  def create_annotation(self, path, annotation, token, **kwargs):
    claims = self._decode_token(token)
    if not self._token_is_valid(claims):
      return 403, {}
    logger.debug(f'create_annotation: path={path} creator={claims["emailhash"]}')
    annotation['creator'] = claims['emailhash']
    user, repo, target = self._parse_path(path)
    annotations, sha = self._get_annotations(user, repo, target)
    annotations.append(annotation)
    self._set_annotations(user, repo, target, annotations, sha, token)
    return 201, annotation

  def get_annotation(self, path, base_url):
    user, repo, target = self._parse_path(path)
    annoid = target.split('/')[-1]
    target = '/'.join(target.split('/')[:-1])
    logger.info(f'get_annotation: user={user} target={target} annoid={annoid}')
    annotations, _ = self._get_annotations(user, repo, target, base_url)
    if len(annotations) == 0 and '/' in target:
      annotations, _ = self._get_annotations(user, repo, target.split('/')[-1], base_url)
    for i in range(len(annotations)):
      if annotations[i]['id'].split('/')[-1] == annoid:
        return annotations[i]

  def delete_annotation(self, path, token):
    if not self._token_is_valid(self._decode_token(token)):
      return 403
    user, repo, target = self._parse_path(path)
    annoid = target.split('/')[-1]
    target = '/'.join(target.split('/')[:-1])
    logger.debug(f'delete_annotation: path={path} user={user} repo={repo} target={target} annoid={annoid}')
    annotations, sha = self._get_annotations(user, repo, target)
    annotations = [anno for anno in annotations if annoid != anno['id'].split('/')[-1]]
    self._set_annotations(user, repo, target, annotations, sha, token)
    return 204

  def update_annotation(self, path, annotation, token):
    if not self._token_is_valid(self._decode_token(token)):
      return 403, {}
    user, repo, target = self._parse_path(path)
    annoid = target.split('/')[-1]
    target = '/'.join(target.split('/')[:-1])
    logger.debug(f'update_annotation: user={user} target={target} annoid={annoid}')
    annotations, sha = self._get_annotations(user, repo, target)
    for i in range(len(annotations)):
      if annotations[i]['id'].split('/')[-1] == annoid:
        annotations[i] = annotation
        break
    self._set_annotations(user, repo, target, annotations, sha, token)
    return 202, annotation

if __name__ == '__main__':
  logger.setLevel(logging.INFO)
  parser = argparse.ArgumentParser(description='Image Info')
  parser.add_argument('url', help='Image URL')

  client = Annotations()
  results = client.__call__(**vars(parser.parse_args()))
  print(json.dumps(results))