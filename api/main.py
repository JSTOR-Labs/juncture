#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

logging.basicConfig(format='%(asctime)s : %(filename)s : %(levelname)s : %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

import os, sys, json
SCRIPT_DIR = os.path.abspath(os.path.dirname(__file__))
sys.path.append(SCRIPT_DIR)

from typing import List, Optional

from pydantic import BaseModel

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import Response

from fastapi.middleware.cors import CORSMiddleware

from starlette.responses import RedirectResponse

from mdrender import get_markdown, get_html
from image_info import ImageInfo
from annotations import Annotations as AnnotationsClient
annos = AnnotationsClient()

from email_server import sendmail

from gcs_essays import GCSEssays as GCSEssaysClient
gcs_essays = GCSEssaysClient()

from prezi_upgrader import Upgrader

app = FastAPI()

web_components_source = 'https://unpkg.com/visual-essays/dist/visual-essays/visual-essays.esm.js'
local_web_components_source = 'http://localhost:3333/build/visual-essays.esm.js'

default_prefix = 'visual-essays/content'
# default_prefix = 'a3b5125'

app.add_middleware(
  CORSMiddleware,
  allow_origins=['*'],
  allow_methods=['*'],
  allow_headers=['*'],
  allow_credentials=True,
)

class Depicts(BaseModel):
  id: str
  label: Optional[str]
  prominent: Optional[bool]

class ResultsDoc(BaseModel):
  seq: int
  id: str
  title: str
  description: Optional[str] = None
  url: Optional[str] = None
  depicts: List[Depicts] = []
  tags: List[str] = []
  digital_representation_of: Optional[Depicts] = None
  thumbnail: Optional[str] = None
  owner: Optional[str] = None
  rights: Optional[str] = None
  weight: Optional[int] = 1

@app.get('/')
def main():
  return RedirectResponse(url='/docs/')

@app.get('/markdown/{path:path}/')
@app.get('/markdown/')
def markdown(
  path: Optional[str] = None,
  url: Optional[str] = None,
  prefix: Optional[str] = default_prefix
):
  logger.info(f'markdown: path={path} url={url}')
  markdown = get_markdown(path, prefix, url)
  if markdown is None:
    raise HTTPException(status_code=404, detail='Not found')
  return Response(content=markdown, media_type='text/markdown')

@app.get('/image-info/')
def image_info(url: str):
  status_code, info = ImageInfo()(url=url)
  return Response(
    status_code=status_code,
    content=json.dumps(info),
    media_type='application/json')

@app.get('/html/{path:path}/')
@app.get('/html/')
async def html(
  request: Request,
  path: Optional[str] = None,
  url: Optional[str] = None,
  base: Optional[str] = None,
  prefix: Optional[str] = default_prefix,
  ref: Optional[str] = None
):
  referrer = request.headers.get('referer')
  base_url = base if base else referrer if referrer else '/'
  logger.info(f'html: path={path} url={url} base_url={base_url} prefix={prefix} referrer={referrer}')
  html = get_html(
    path=path,
    url=url,
    base_url=base_url,
    prefix=prefix,
    ref=ref,
    web_components_source = local_web_components_source if request.client.host == '127.0.0.1' else web_components_source
  )
  if html is None:
    raise HTTPException(status_code=404, detail='Not found')
  return Response(content=html, media_type='text/html')

@app.post('/html/')
async def markdown_to_html(
  request: Request,
  base: Optional[str] = None
):
  markdown = await request.body()
  markdown = markdown.decode('utf-8')
  referrer = request.headers.get('referer')
  base_url = base if base else referrer if referrer else '/'
  logger.info(f'html: base_url={base_url} referrer={referrer} markdown_size={len(markdown)}')
  html = get_html(
    markdown=markdown,
    base_url=base_url, 
    web_components_source = local_web_components_source if request.client.host == '127.0.0.1' else web_components_source
  )
  if html is None:
    raise HTTPException(status_code=404, detail='Not found')
  return Response(content=html, media_type='text/html')

@app.post('/annotation/')
async def create_annotation(request: Request):
  payload = await request.body()
  kwargs = json.loads(payload)
  kwargs['token'] = request.headers.get('authorization','').split()[-1]
  status_code, created = annos.create_annotation(**kwargs)
  return Response(
    status_code=status_code,
    content=json.dumps(created),
    media_type='application/json')

@app.get('/annotations/{path:path}/')
async def get_annotations(request: Request, path: str):
  return annos.get_annotations(path, request.base_url)

@app.get('/annotation/{path:path}/')
async def get_annotation(request: Request, path: str):
  return annos.get_annotation(path, request.base_url)

@app.put('/annotation/{path:path}/')
async def update_annotation(request: Request, path: str):
  annotation = await request.body()
  token = request.headers.get('authorization','').split()[-1]
  status_code, updated = annos.update_annotation(path, json.loads(annotation), token)
  return Response(status_code=status_code, content=json.dumps(updated))

@app.delete('/annotation/{path:path}/')
async def delete_annotation(request: Request, path: str):
  token = request.headers.get('authorization','').split()[-1]
  return Response(status_code=annos.delete_annotation(path, token))

@app.get('/gcs/{path:path}/')
async def get_gcs(path: str):
  status_code, content = gcs_essays.get(path)
  if isinstance(content, list):
    return content
  else:
    return Response(content=content, status_code=status_code, media_type='text/plain')

@app.post('/gcs/{path:path}/')
async def put_gcs(request: Request, path: str):
  content = await request.body()
  token = request.headers.get('authorization','').split()[-1]
  status_code, content = gcs_essays.put(path, content, token)
  return Response(status_code=status_code, content=content, media_type='text/plain')

@app.delete('/gcs/{path:path}/')
async def delete_gcs(request: Request, path: str):
  token = request.headers.get('authorization','').split()[-1]
  return gcs_essays.delete(path, token)

@app.post('/sendmail/')
async def _sendmail(request: Request):
  referrer = request.headers.get('referer')
  body = await request.body()
  content, status_code = sendmail(**{**json.loads(body), **{'referrer': referrer}})
  logger.info(status_code)
  return Response(status_code=status_code, content=content) 

@app.post('/prezi2to3/')
async def prezi2to3(request: Request):
  body = await request.body()
  v2_manifest = json.loads(body)
  upgrader = Upgrader(flags={
    'crawl': False,        # NOT YET IMPLEMENTED. Crawl to linked resources, such as AnnotationLists from a Manifest
    'desc_2_md': True,     # If true, then the source's `description` properties will be put into a `metadata` pair. If false, they will be put into `summary`.
    'related_2_md': False, # If true, then the `related` resource will go into a `metadata` pair. If false, it will become the `homepage` of the resource.
    'ext_ok': False,       # If true, then extensions are allowed and will be copied across.
    'default_lang': 'en',  # The default language to use when adding values to language maps.
    'deref_links': False,  # If true, the conversion will dereference external content resources to look for format and type.
    'debug': False,        # If true, then go into a more verbose debugging mode.
    'attribution_label': '', # The label to use for requiredStatement mapping from attribution
    'license_label': ''} # The label to use for non-conforming license URIs mapped into metadata
  )
  v3_manifest = upgrader.process_resource(v2_manifest, True) 
  v3_manifest = upgrader.reorder(v3_manifest)
  return v3_manifest

if __name__ == '__main__':
  app.run(debug=True, host='0.0.0.0', port=8000)
