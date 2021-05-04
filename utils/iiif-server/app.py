#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
logging.basicConfig(format='%(asctime)s : %(filename)s : %(levelname)s : %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

import os
import sys
import re
SCRIPT_DIR = os.path.abspath(os.path.dirname(__file__))

import json
import yaml
import hashlib
from hashlib import sha256
import traceback
import getopt
from datetime import datetime
from urllib.parse import urlparse, quote, unquote
from copy import deepcopy

import requests
from requests.auth import HTTPBasicAuth
logging.getLogger('requests').setLevel(logging.INFO)

from flask import Flask, request, make_response, Response
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

from pymongo import MongoClient

with open(f'{SCRIPT_DIR}/config.yaml', 'r') as fp:
    config = yaml.load(fp.read(), Loader=yaml.FullLoader)

iiifhosting_user, iiifhosting_token = config['iiifhosting'].split(':')
atlas_endpoint = f'mongodb+srv://{config["atlas"]}/?retryWrites=true&w=majority'
referrer_whitelist = set(config['referrer_whitelist'])
baseurl = config['baseurl']

ingest_endpoint_iiifhosting = 'https://admin.iiifhosting.com/api/v1/ingest/'

from expiringdict import ExpiringDict
_cache = ExpiringDict(max_len=100, max_age_seconds=3600)

_db_connection = None
def connect_db():
    '''MongoDB connection'''
    global _db_connection
    if _db_connection is None:
        _db_connection = MongoClient(atlas_endpoint)['iiif']
    return _db_connection

def get_image_size(url, **kwargs):
    '''Image size required for IIIF Hosting ingest'''
    size = None
    try:
        resp = requests.head(url, )
        headers = dict([(key.lower(),value) for key, value in resp.headers.items()])
        size = int(headers.get('content-length', headers.get('content_length')))
    except:
        try:
            size = 0
            with requests.get(url, stream=True) as response:
                size = sum(len(chunk) for chunk in response.iter_content(8196))
        except:
            logger.error(traceback.format_exc())
            logger.error(url)
    logger.debug(f'get_image_size: url={url} size={size}')
    return size

def queue_image_for_iiifhosting(mdb, **kwargs):
    url = kwargs['url'].replace(' ', '%20')
    name = sha256(url.encode('utf-8')).hexdigest()
    size = get_image_size(url)
    logger.info(f'queue_image_for_iiifhosting: url={url} name={name} size={size}')
    if size:
        image_data = mdb['images'].find_one({'_id': url})
        if image_data:
            image_data['source_size'] = size
        else:
            mdb['images'].insert_one({
                '_id': url,
                'status': 'submitted',
                'source_size': size,
                'submitted': datetime.utcnow().isoformat(),
                'external_id': url
            })
    data = {
        'email': iiifhosting_user,
        'secure_payload': iiifhosting_token,
        'files': [{
            'id': url, 
            'url': url, 
            # 'name': unquote(url.split('/')[-1]), 
            'name': name,
            'size': size}]
    }
    logger.debug(json.dumps(data, indent=2))
    resp = requests.post(
        ingest_endpoint_iiifhosting,
        headers = {
            'Content-type': 'application/json; charset=utf-8', 
            'Accept': 'application/json'
        },
        data = json.dumps(data))
    if resp.status_code == 200 and resp.json().get('success') == 'Task created':
        mdb['images'].update_one({'_id': kwargs['url']}, {'$set': {'status': 'pending'}})

def get_image_data(mdb, url):
    return mdb['images'].find_one({'_id': url})

def make_iiif_image(mdb, manifest=None, **kwargs):
    queue_image_for_iiifhosting(mdb, **kwargs)

def to_isodate(s):
    return s # TODO: ensure date is in proper ISO format

def add_image_data_to_manifest(manifest, image_data):
    logger.debug('add_image_data_to_manifest')
    if 'url' in image_data:
        image_data['url'] = image_data['url'].replace('http:', 'https:')
        manifest['sequences'][0]['canvases'][0]['images'][0]['resource'] = {
            '@id': image_data['external_id'],
            '@type': 'dctypes:Image',
            'format': 'image/jpeg',
            'service': {
                '@context': 'http://iiif.io/api/image/2/context.json',
                '@id': image_data['url'][:-1],
                'profile': 'https://iiif.io/api/image/2/level2.json'
            },
            'height': image_data['height'],
            'width': image_data['width']
        }
    return manifest

def update_manifests_with_image_data(mdb, image_data):
    image_data['url'] = image_data['url'].replace('http:', 'https:')
    _filter = {'sequences.canvases.images.resource.@id': {'$eq': unquote(image_data['external_id'])}}
    cursor = mdb['manifests'].find(_filter)
    for manifest in cursor:
        manifest['thumbnail'] = f'{image_data["url"]}full/150,/0/default.jpg'
        manifest = add_image_data_to_manifest(manifest, image_data)
        mdb['manifests'].replace_one({'_id': manifest['_id']}, manifest)   

def make_manifest_v2_1_1(mdb, mid, image_data, **kwargs):
    '''Create an IIIF presentation v2.1.1 manifest'''
    manifest = {
        '@context': 'http://iiif.io/api/presentation/2/context.json',
        '@id': f'{baseurl}/manifest/{mid}',
        '@type': 'sc:Manifest',
        'label': kwargs.get('label', '')  ,
        'metadata': metadata(**kwargs),
        'sequences': [{
            '@id': f'{baseurl}/sequence/{mid}',
            '@type': 'sc:Sequence',
            'canvases': [{
                '@id': f'{baseurl}/canvas/{mid}',
                '@type': 'sc:Canvas',
                'label': kwargs.get('label', ''),
                'height': 3000,
                'width': 3000,
                'images': [{
                    '@type': 'oa:Annotation',
                    'motivation': 'sc:painting',
                    'resource': {
                        '@id': kwargs['url'],
                    },
                    'on': f'{baseurl}/canvas/{mid}'
                }]
            }]
        }]
    }
    if image_data and 'url' in image_data:
        manifest = add_image_data_to_manifest(manifest, image_data)
        manifest['thumbnail'] = f'{image_data["url"]}full/150,/0/default.jpg'
    else:
        logger.info(f'No valid image data: {image_data}')

    for prop in kwargs:
        if prop.lower() in ('attribution', 'description', 'label', 'license', 'logo', 'navDate'):
            manifest[prop.lower()] = kwargs[prop]
            if prop.lower() == 'label':
                manifest['sequences'][0]['canvases'][0]['label'] = kwargs[prop]

    manifest['_id'] = mid
    logger.debug(json.dumps(manifest, indent=2))
    mdb['manifests'].insert_one(manifest)
    return mdb['manifests'].find_one({'_id': mid})

def metadata(**kwargs):
    md = []
    for prop in kwargs:
        if prop == 'navDate':
            md.append({ 'label': prop, 'value': to_isodate(kwargs['navDate']) })
        elif prop == 'url':
            md.append({ 'label': 'image-source-url', 'value': kwargs[prop] })
        else:
            md.append({ 'label': prop, 'value': kwargs[prop] })
    return md

def update_manifest(mdb, manifest, image_data, **kwargs):
    manifest['metadata'] = metadata(**kwargs)
    for prop in kwargs:
        if prop.lower() in ('attribution', 'description', 'label', 'license', 'logo', 'navDate'):
            manifest[prop.lower()] = kwargs[prop]
            if prop.lower() == 'label':
                manifest['sequences'][0]['canvases'][0]['label'] = kwargs[prop]
    if image_data:
        manifest = add_image_data_to_manifest(manifest, image_data)
    mdb['manifests'].replace_one({'_id': manifest['_id']}, manifest)        
    return mdb['manifests'].find_one({'_id': manifest['_id']})

@app.route('/manifest/<path:path>', methods=['GET'])
@app.route('/manifest/', methods=['OPTIONS', 'POST', 'PUT'])
def manifest(path=None):
    logger.info(f'manifest: method={request.method} referrer={request.referrer}')

    if request.method == 'OPTIONS':
        return ('', 204)
    elif request.method in ('HEAD', 'GET'):
        mid = path
        args = dict([(k, request.args.get(k)) for k in request.args])
        service = args.get('service')
        refresh = args.get('refresh', 'false').lower() in ('', 'true')
        mdb = connect_db()
        manifest = mdb['manifests'].find_one({'_id': mid})
        if manifest:
            etag = hashlib.md5(json.dumps(manifest.get('metadata',{}), sort_keys=True).encode()).hexdigest()
            # headers = {**cors_headers, **{'ETag': etag}}
            headers = {'ETag': etag}
            if request.method == 'GET':
                del manifest['_id']
                source_url = manifest['sequences'][0]['canvases'][0]['images'][0]['resource']['@id']
                if refresh:
                    make_iiif_image(mdb, manifest, url=source_url)
                return (manifest, 200, headers)
            else: # HEAD
                return ('', 204, headers)
        else:
            return 'Not found', 404
    elif request.method == 'POST':
        referrer = urlparse(request.referrer).netloc if request.referrer else None
        can_mutate = referrer in referrer_whitelist
        logger.info(f'referrer={referrer} can_mutate={can_mutate}')



        mdb = connect_db()
        input_data = request.json

        # make manifest id using hash of url
        mid = hashlib.sha256(input_data['url'].encode()).hexdigest()

        manifest = mdb['manifests'].find_one({'_id': mid})

        refresh = str(input_data.pop('refresh', False)).lower() in ('', 'true')

        logger.info(f'manifest: mid={mid} refresh={refresh}')

        if manifest:
            manifest_md_hash = hashlib.md5(json.dumps(manifest.get('metadata',{}), sort_keys=True).encode()).hexdigest()
            input_data_md_hash = hashlib.md5(json.dumps(metadata(**input_data), sort_keys=True).encode()).hexdigest()
            logger.info(f'manifest found: manifest_md_hash={manifest_md_hash} input_data_md_hash={input_data_md_hash}')
            if can_mutate:
                if refresh or 'service' not in manifest['sequences'][0]['canvases'][0]['images'][0]['resource']:
                    image_data = get_image_data(mdb, input_data['url'])
                    if refresh or image_data is None or image_data['status'] != 'done':
                        make_iiif_image(mdb, manifest, **input_data)
                else:
                    image_data = None
                if (image_data is not None) or (manifest_md_hash != input_data_md_hash):
                    manifest = update_manifest(mdb, manifest, image_data, **input_data)
        else:
            if not can_mutate:
                return ('Not authorized', 403)

            image_data = get_image_data(mdb, input_data['url'])
            if image_data is None and input_data['url'].endswith('/info.json'):
                resp = requests.get(input_data['url'], headers = {'Accept': 'application/json'})
                if resp.status_code == 200:
                    iiif_info = resp.json()
                    size = '1000,' if iiif_info['width'] >= iiif_info['height'] else ',1000'
                    image_data = {
                        'external_id': f'{iiif_info["@id"]}/full/{size}/0/default.jpg',
                        'url': f'{iiif_info["@id"]}/',
                        'height': iiif_info['height'],
                        'width': iiif_info['width']
                    }
            if image_data:
                make_iiif_image(mdb, manifest, **input_data)
            manifest = make_manifest_v2_1_1(mdb, mid, image_data, **input_data)
        return manifest, 200
    
    elif request.method == 'PUT':
        if not can_mutate:
            return ('Not authorized', 403)

        mdb = connect_db()
        input_data = request.json
        manifest = update_manifest(mdb, manifest, **input_data)
        return manifest, 200

@app.route('/iiifhosting-webhook', methods=['GET', 'POST'])
def iiifhosting_webhook():
    if request.method == 'GET':
        kwargs = dict([(k, request.args.get(k)) for k in request.args])
        logger.info(f'iiifhosting-webhook: qargs={kwargs}')
    if request.method == 'POST':
        image_data = request.json
        if image_data['status'] == 'done':
            mdb = connect_db()
            mdb['images'].update_one(
                {'_id': image_data['external_id']},
                {'$set': {
                    'status': 'done',
                    'created': datetime.utcnow().isoformat(),
                    'image_id': image_data['image_id'],
                    'url': image_data['url'],
                    'height': image_data['height'],
                    'width': image_data['width']
                }
            })
            update_manifests_with_image_data(mdb, image_data)
        logger.info(f'iiifhosting-webhook: image_data={json.dumps(image_data)}')
    return 'OK', 200

def usage():
    print('%s [hl:]' % sys.argv[0])
    print('   -h --help             Print help message')
    print('   -l --loglevel         Logging level (default=warning)')


if __name__ == '__main__':
    kwargs = {}
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'hl:', ['help', 'loglevel'])
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
        elif o in ('-h', '--help'):
            usage()
            sys.exit()
        else:
            assert False, 'unhandled option'

    app.run(debug=True, host='0.0.0.0')