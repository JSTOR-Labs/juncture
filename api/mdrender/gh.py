#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
logging.basicConfig(format='%(asctime)s : %(filename)s : %(levelname)s : %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

import os
import base64
import json
import yaml
from time import time as now
from collections import namedtuple

import requests
logging.getLogger('requests').setLevel(logging.INFO)

SCRIPT_DIR = os.path.abspath(os.path.dirname(__file__))
CONFIG = yaml.load(open(f'{SCRIPT_DIR}/creds.yaml', 'r').read(), Loader=yaml.FullLoader)

GH_ACCESS_TOKEN = CONFIG['GH_ACCESS_TOKEN']
GH_JSTOR_LABS_TOKEN = CONFIG['GH_JSTOR_LABS_TOKEN']

def get_gh_file_by_url(url):
    logger.debug(f'get_gh_file_by_url {url} {GH_ACCESS_TOKEN}')
    content = sha = None
    resp = requests.get(url, headers={
        'Authorization': f'Token {GH_ACCESS_TOKEN}',
        'Accept': 'application/vnd.github.v3+json',
        'User-agent': 'JSTOR Labs visual essays client'
    })
    logger.debug(f'get_gh_file_by_url {url} {resp.status_code}')
    if resp.status_code == 200:
        resp = resp.json()
        content = base64.b64decode(resp['content']).decode('utf-8')
        sha = resp['sha']
    return content, url, sha

def get_gh_file(acct, repo, path, ref=None):
    logger.info(f'get_gh_file: acct={acct} repo={repo} path={path} ref={ref}')
    ref = ref if ref else get_default_branch(acct, repo)
    url = f'https://api.github.com/repos/{acct}/{repo}/contents{path}?ref={ref}'
    return get_gh_file_by_url(url)

def put_gh_file(acct, repo, target, contents, sha, token, ref=None):
    ref = ref if ref else get_default_branch(acct, repo)
    gh_content_url = f'https://api.github.com/repos/{acct}/{repo}/contents/{target}.json?ref={ref}'
    # logger.info(f'gh_content_url={gh_content_url}')
    if acct.lower() == 'jstor-labs':
        token = GH_JSTOR_LABS_TOKEN
    payload = {
        'message': 'File update',
        'content': str(base64.b64encode(bytes(json.dumps(contents, indent=2), 'utf-8')), 'utf-8'),
        'branch': ref
    }
    if sha:
        payload['sha'] = sha
    resp = requests.put(
        gh_content_url,
        headers={'Authorization': f'Token {token}'},
        json=payload
    )
    if resp.status_code >= 200 and resp.status_code < 300:
        return 'success'
    else:
        logger.warning(f'put_gh_file: {resp.status_code} {resp.content} {gh_content_url} {token}')
        logger.info(json.dumps(contents, indent=2))
        return 'failed'

def gh_repo_info(acct, repo):
    start = now()
    logger.debug(f'gh_repo_info: acct={acct} repo={repo} GH_ACCESS_TOKEN={GH_ACCESS_TOKEN}')
    url = f'https://api.github.com/repos/{acct}/{repo}'
    resp = requests.get(url, headers={
        'Authorization': f'Token {GH_ACCESS_TOKEN}',
        'Accept': 'application/vnd.github.v3+json',
        'User-agent': 'JSTOR Labs visual essays client'
    })
    logger.debug(f'gh_repo_info: {url} {resp.status_code} {round(now()-start,3)}')
    return resp.json() if resp.status_code == 200 else None

_checked_prefixes = {}
def has_gh_repo_prefix(path):
    start = now()
    elems = path.split('/')
    prefix = '/'.join(elems[:2]) if len(elems) >= 2 else None
    if prefix is not None and prefix not in _checked_prefixes:
        repo_info = gh_repo_info(elems[0], elems[1])
        _checked_prefixes[prefix] = repo_info['default_branch'] if repo_info else None
    _is_repo_prefix = _checked_prefixes.get(prefix) is not None
    logger.debug(f'has_gh_repo_prefix: prefix={prefix} _is_repo_prefix={_is_repo_prefix} elapsed={round(now()-start,3)}')
    return _is_repo_prefix

def get_gh_markdown(path, ref=None):
    start = now()
    if has_gh_repo_prefix(path):
        elems = path.split('/')
        prefix = '/'.join(elems[:2]) if len(elems) >= 2 else None
        ref = ref or _checked_prefixes[prefix]
        acct, repo = elems[:2]
        path = f'/{"/".join(path.split("/")[2:])}'    
    markdown = url = sha = None
    if path.endswith('.md'):
        paths = [path]
    else:
        if path == '/':
            paths = ['/README.md', '/index.md']
        else:
            if path[-1] == '/':
                paths = [f'{path}{file}' for file in ('README.md', 'index.md')]
            else:
                paths = [f'{path}.md'] + [f'{path}/{file}' for file in ('README.md', 'index.md')]
    for _path in paths:
        markdown, url, sha = get_gh_file(acct, repo, _path, ref)
        if markdown:
            break
    if markdown:
        source = {'markdown': markdown, 'source': 'github', 'acct': acct, 'repo': repo, 'ref': ref, 'path': path, 'url': url, 'sha': sha}
        logger.debug(f'get_gh_markdown: acct={acct} repo={repo} ref={ref} path={path} elapsed={round(now()-start,3)}')
        return namedtuple('ObjectName', source.keys())(*source.values())

def get_default_branch(acct, repo):
    repo_info = gh_repo_info(acct, repo)
    return repo_info['default_branch'] if repo_info else None
