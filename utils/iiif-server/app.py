#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
logging.basicConfig(format='%(asctime)s : %(filename)s : %(levelname)s : %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

import os
import sys
import math
SCRIPT_DIR = os.path.abspath(os.path.dirname(__file__))

import json
import yaml
import hashlib
from hashlib import sha256
import traceback
import getopt
from datetime import datetime
from urllib.parse import urlparse

import requests
logging.getLogger('requests').setLevel(logging.INFO)

from flask import Flask, request, Response, redirect
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
placeholder_image = 'https://upload.wikimedia.org/wikipedia/commons/e/e0/PlaceholderLC.png'

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
    logger.info(f'get_image_size: url={url} size={size}')
    return size

def queue_image_for_iiifhosting(mdb, **kwargs):
    name = sha256(kwargs['url'].encode('utf-8')).hexdigest()
    size = get_image_size(kwargs['url'])
    logger.info(f'queue_image_for_iiifhosting: url={kwargs["url"]} name={name} size={size}')
    if size:
        image_data = mdb['images'].find_one({'_id': kwargs['url']})
        if image_data:
            image_data['source_size'] = size
        else:
            mdb['images'].insert_one({
                '_id': kwargs['url'],
                'status': 'submitted',
                'source_size': size,
                'submitted': datetime.utcnow().isoformat(),
                'external_id': kwargs['url']
            })
    data = {
        'email': iiifhosting_user,
        'secure_payload': iiifhosting_token,
        'files': [{
            'id': kwargs['url'], 
            'url': kwargs['url'], 
            'name': name,
            'size': size}]
    }
    logger.info(json.dumps(data, indent=2))
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
    logger.debug(f'add_image_data_to_manifest: image_data={image_data}')
    if 'url' in image_data:
        image_data['url'] = image_data['url'].replace('http:', 'https:')
        manifest['sequences'][0]['canvases'][0]['images'][0]['resource'] = {
            '@id': image_data['external_id'],
            '@type': 'dctypes:Image',
            'format': 'image/jpeg',
            'height': image_data['height'],
            'width': image_data['width']
        }
        if image_data['status'] == 'done':
            manifest['sequences'][0]['canvases'][0]['images'][0]['resource']['service'] = {
                '@context': 'http://iiif.io/api/image/2/context.json',
                '@id': image_data['url'][:-1],
                'profile': 'https://iiif.io/api/image/2/level2.json'
            }
            manifest['thumbnail'] = f'{image_data["url"]}full/150,/0/default.jpg'
        else:
            if 'thumbnail' in manifest:
                del manifest['thumbnail']
    logger.debug(json.dumps(manifest, indent=2))
    return manifest

def update_manifests_with_image_data(mdb, image_data):
    image_data['url'] = image_data['url'].replace('http:', 'https:')
    _filter = {'sequences.canvases.images.resource.@id': {'$eq': image_data['external_id']}}
    logger.info(f'update_manifests_with_image_data: image_data={image_data}')
    logger.info(image_data['external_id'])
    cursor = mdb['manifests'].find(_filter)
    for manifest in cursor:
        logger.info(f'manifest={manifest}')
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

def _source(url):
    _url = urlparse(url)
    if _url.hostname == 'raw.githubusercontent.com':
        path_elems = [elem for elem in _url.path.split('/') if elem]
        acct, repo, ref = path_elems[:3]
        path = f'/{"/".join(path_elems[3:])}'
        logger.info(f'GitHub image: hostname={_url.hostname} acct={acct} repo={repo} ref={ref} path={path}')
        return f'https://{_url.hostname}/{acct}/{repo}/main{path}'
    else:
        return url

@app.route('/gp-proxy/<path:path>', methods=['GET', 'HEAD'])
def gp_proxy(path):
    gp_url = f'https://plants.jstor.org/seqapp/adore-djatoka/resolver?url_ver=Z39.88-2004&svc_id=info:lanl-repo/svc/getRegion&svc_val_fmt=info:ofi/fmt:kev:mtx:jpeg2000&svc.format=image/jpeg&rft_id=/{path}'
    if request.method in ('HEAD'):
        resp = requests.get(gp_url, headers = {'User-Agent': 'JSTOR Labs'})
        _cache[gp_url] = resp.content
        if resp.status_code == 200:
            res = Response('', 204, content_type='image/jpeg')
            res.headers.add('Content-Length', str(len(resp.content)))
            res.headers.add('Content_Length', str(len(resp.content)))
            return res
    else:
        content = _cache.get(gp_url)
        if content is None:
            resp = requests.get(gp_url, headers = {'User-Agent': 'JSTOR Labs'})
            if resp.status_code == 200:
                content = resp.content
        if content:
            return (content, 200, {'Content-Type': 'image/jpeg', 'Content-Length': len(content)})

@app.route('/manifest/<path:path>', methods=['GET'])
@app.route('/manifest/', methods=['OPTIONS', 'POST', 'PUT'])
def manifest(path=None):
    referrer = '.'.join(urlparse(request.referrer).netloc.split('.')[-2:]) if request.referrer else None
    can_mutate = referrer in referrer_whitelist
    if request.method == 'OPTIONS':
        return ('', 204)
    elif request.method in ('HEAD', 'GET'):
        mid = path
        args = dict([(k, request.args.get(k)) for k in request.args])
        if 'url' in args:
            args['url'] = args['url'].replace(' ', '%20')
        refresh = args.get('refresh', 'false').lower() in ('', 'true')
        mdb = connect_db()
        manifest = mdb['manifests'].find_one({'_id': mid})
        logger.info(f'manifest: method={request.method} mid={mid} found={manifest is not None} refresh={refresh} referrer={referrer} can_mutate={can_mutate}')
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

        mdb = connect_db()
        input_data = request.json
        if 'url' in input_data:
            input_data['url'] = input_data['url'].replace(' ', '%20')
        source = _source(input_data['url'])

        # make manifest id using hash of url
        mid = hashlib.sha256(source.encode()).hexdigest()

        manifest = mdb['manifests'].find_one({'_id': mid})

        refresh = str(input_data.pop('refresh', False)).lower() in ('', 'true')

        logger.info(f'manifest: method={request.method} source={source} mid={mid} found={manifest is not None} refresh={refresh} referrer={referrer} can_mutate={can_mutate}')

        if manifest:
            logger.info(f'manifest={manifest}')
            if can_mutate:
                if refresh or 'service' not in manifest['sequences'][0]['canvases'][0]['images'][0]['resource']:
                    image_data = get_image_data(mdb, source)
                    logger.info(f'image_data={image_data}')
                    if refresh or image_data is None or image_data['status'] != 'done':
                        make_iiif_image(mdb, manifest, **input_data)
                else:
                    image_data = None
                manifest_md_hash = hashlib.md5(json.dumps(manifest.get('metadata',{}), sort_keys=True).encode()).hexdigest()
                input_data_md_hash = hashlib.md5(json.dumps(metadata(**input_data), sort_keys=True).encode()).hexdigest()
                if (image_data is not None) or (manifest_md_hash != input_data_md_hash):
                    manifest = update_manifest(mdb, manifest, image_data, **input_data)
        else:
            if not can_mutate:
                return ('Not authorized', 403)

            image_data = get_image_data(mdb, source)
            if image_data is None and source.endswith('/info.json'):
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
            if not image_data:
                make_iiif_image(mdb, manifest, **input_data)
            manifest = make_manifest_v2_1_1(mdb, mid, image_data, **input_data)
        return manifest, 200
    
    elif request.method == 'PUT':
        if not can_mutate:
            return ('Not authorized', 403)

        mdb = connect_db()
        input_data = request.json
        source = _source(input_data['url'])
        mid = hashlib.sha256(source.encode()).hexdigest()
        manifest = mdb['manifests'].find_one({'_id': mid})
        return update_manifest(mdb, manifest, **input_data), 200

@app.route('/iiifhosting-webhook', methods=['GET', 'POST'])
def iiifhosting_webhook():
    if request.method == 'GET':
        kwargs = dict([(k, request.args.get(k)) for k in request.args])
        logger.info(f'iiifhosting-webhook: qargs={kwargs}')
    if request.method == 'POST':
        image_data = request.json
        logger.info(f'iiifhosting-webhook: image_data={json.dumps(image_data)}')
        # if image_data['status'] == 'done':
        mdb = connect_db()
        found = mdb['images'].find_one({'_id': image_data['external_id']})
        logger.info(f'found={found}')
        if found:
            mdb['images'].update_one(
                {'_id': image_data['external_id']},
                {'$set': {
                    'status': image_data['status'],
                    'created': datetime.utcnow().isoformat(),
                    'image_id': image_data['image_id'] if 'image_id' in image_data else image_data['external_id'],
                    'url': image_data['url'],
                    'height': image_data['height'],
                    'width': image_data['width']
                }
            })
        update_manifests_with_image_data(mdb, image_data)
    return 'OK', 200

def _calc_region_and_size(image_data, args, type='thumbnail'):
        
    im_width = int(image_data['width'])
    im_height = int(image_data['height'])

    width = height = None

    if 'size' in args:
        size = args.get('size', 'full').replace('x',',').replace('X',',')
        if ',' not in size:
            size = f'{size},'
        width, height = [int(arg) if arg.isdecimal() else None for arg in size.split(',')]
    else:
        if 'width' in args: width = int(args['width'])
        if 'height' in args: height = int(args['height'])

    if width == None and height == None:
        width = 400 if type == 'thumbnail' else 1000
        height = 260 if type == 'thumbnail' else 400
    else:
        if not width: width = round(im_height/height * im_width)
        if not height: height = round(width/im_width * im_height)
    aspect = width / height

    if aspect > 1:
        x = 0
        w = im_width
        h = math.ceil(im_width / aspect)
        y = math.ceil((im_height-h) / 2)
    else:
        y = 0
        h = im_height
        w = math.ceil(im_height * aspect)
        x = math.ceil((im_width-w) / 2)

    region = f'{x},{y},{w},{h}'
    size = f'{width},{height}'

    logger.info(f'_calc_region_and_size: width={width} height={height} aspect={aspect} im_width={im_width} im_height={im_height} region={region} size={size}')
    return region, size

@app.route('/thumbnail/', methods=['GET'])
@app.route('/thumbnail/', methods=['OPTIONS', 'POST', 'PUT'])
@app.route('/banner/', methods=['GET'])
@app.route('/banner/', methods=['OPTIONS', 'POST', 'PUT'])
def thumbnail():
    action = request.path.split('/')[1]
    referrer = '.'.join(urlparse(request.referrer).netloc.split('.')[-2:]) if request.referrer else None
    can_mutate = referrer is None or referrer in referrer_whitelist
    if request.method == 'OPTIONS':
        return ('', 204)
    elif request.method in ('HEAD', 'GET'):
        args = dict([(k, request.args.get(k)) for k in request.args])
        refresh = args.get('refresh', 'false').lower() in ('', 'true')
        region = args.get('region', 'full')
        size = args.get('size', 'full')
        rotation = args.get('rotation', '0')
        quality = args.get('quality', 'default')
        format = args.get('format', 'jpg')

        logger.info(f'thumbnail: method={request.method} action={action} region={region} size={size} referrer={referrer} can_mutate={can_mutate} args={args}')
        if 'url' in args:
            source = _source(args['url'])
            mdb = connect_db()
            image_data = get_image_data(mdb, source)
            if image_data and not refresh:
                if region == 'full':
                    region, size = _calc_region_and_size(image_data, args, action)
                # logger.info(json.dumps(image_data, indent=2))
                thumbnail_url = f'{image_data["url"].replace("http:","https:")}{region}/{size}/{rotation}/{quality}.{format}'
                logger.info(thumbnail_url)
                return redirect(thumbnail_url)
                '''
                resp = requests.get(thumbnail_url)
                if resp.status_code == 200:
                    content = resp.content
                    if content:
                        return (content, 200, {'Content-Type': 'image/jpeg', 'Content-Length': len(content)})
                '''
            else:
                if can_mutate:
                    queue_image_for_iiifhosting(mdb, url=source)
                    placeholder = get_image_data(mdb, placeholder_image)
                    if region == 'full':
                        region, size = _calc_region_and_size(placeholder, args, action)
                    thumbnail_url = f'{placeholder["url"].replace("http:","https:")}{region}/{size}/{rotation}/{quality}.{format}'
                    logger.info(thumbnail_url)
                    return redirect(thumbnail_url)
                    '''
                    resp = requests.get(thumbnail_url)
                    if resp.status_code == 200:
                        content = resp.content
                        if content:
                            return (content, 200, {'Content-Type': 'image/jpeg', 'Content-Length': len(content)})
                    '''
                else:
                    return 'Not found', 404
    return 'Bad Request', 400

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