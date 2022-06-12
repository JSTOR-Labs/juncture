#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
logging.basicConfig(format='%(asctime)s : %(filename)s : %(levelname)s : %(message)s', level=logging.INFO)
logger = logging.getLogger()

import os
SCRIPT_DIR = os.path.abspath(os.path.dirname(__file__))
BASEDIR = os.path.dirname(SCRIPT_DIR)

import sys
import getopt
import traceback
import json
from datetime import datetime, timedelta
from dateutil.parser import parse

DEFAULT_PROJECT_NAME = 'visual-essays'
DEFAULT_BUCKET_NAME = 'visual-essays'
DEFAULT_CREDS_PATH = os.path.join(BASEDIR, 'gcreds.json')

from google.oauth2 import service_account
from google.cloud import storage

class Bucket(object):

    def __init__(self, **kwargs):
        self.project_name = kwargs.get('project', DEFAULT_PROJECT_NAME)
        self.bucket_name = kwargs.get('bucket', DEFAULT_BUCKET_NAME)
        self.creds_path = kwargs.get('creds_path', DEFAULT_CREDS_PATH)
        logger.debug(f'gcr-cache.init: project={self.project_name} bucket={self.bucket_name} creds={self.creds_path} creds_exists={os.path.exists(self.creds_path)}')
        credentials = service_account.Credentials.from_service_account_file(self.creds_path)
        self.client = storage.Client(self.project_name, credentials)
        self.bucket = self.client.get_bucket(self.bucket_name)
        logger.debug(f'gcr-cache: project={self.project_name} bucket={self.bucket_name}')

    def __contains__(self, key):
        logger.debug(f'{key} local={key in self.local} gc={self.bucket.blob(key).exists()}')
        return self.bucket.blob(key).exists()

    def __setitem__(self, key, value):
        blob = self.bucket.blob(key)
        blob.upload_from_string(value)

    def set(self, key, value):
        return self.__setitem__(key, value)

    def __getitem__(self, key, maxage=None, after=None):
        logger.info(f'bucket.__getitem__: key={key} maxage={maxage} after={after}')
        item = None
        blob = self.bucket.blob(key)
        try:
            if maxage is None and after is None:
                item = blob.download_as_string().decode('utf-8')
            else:
                blob.reload()
                created = blob.time_created.replace(tzinfo=None)
                age = (datetime.utcnow() - created).seconds
                if after is not None:
                    after = parse(after) + timedelta(days=1)
                logger.debug(f'{age} {created}')
                if (after is None or created > after) and (maxage is None or age < maxage): 
                    item = blob.download_as_string().decode('utf-8')
        except Exception as ex:
            if ex.response.status_code == 404:
                raise KeyError
            # logger.error(traceback.format_exc())
        logger.info(f'get: key={key} local=False gc={item is not None}')
        return item

    def get(self, key, default=None, maxage=None, after=None):
        try:
            return self.__getitem__(key, maxage, after)
        except KeyError:
            return default

    def __iter__(self, prefix=None):
        return self.client.list_blobs(self.bucket, prefix=prefix)._items_iter()

    def iteritems(self):
        for blob in self.__iter__():
            yield blob.name, self[blob.name]

    def iterkeys(self):
        for blob in self.__iter__():
            yield blob.name
    
    def itervalues(self):
        for blob in self.__iter__():
            yield self[blob.name]

    def items(self, prefix=None):
        for blob in self.__iter__(prefix):
            yield blob.name, self[blob.name]

    def keys(self, prefix=None):
        for blob in self.__iter__(prefix):
            yield blob.name

    def __len__(self):
        pass # TODO

    def __delitem__(self, key):
        blob = self.bucket.blob(key)
        if blob:
            blob.delete()

def usage():
    print('%s [hl:n:k:sxm:a:] [keys]' % sys.argv[0])
    print('   -h --help            Print help message')
    print('   -l --loglevel        Logging level (default=warning)')
    print('   -b --bucket          Bucket name (%s)' % DEFAULT_BUCKET_NAME)
    print('   -k --list            Number of keys to list (-1 = all)')
    print('   -s --size            Database size')
    print('   -x --delete          Delete item from database')
    print('   -m --maxage          Return if item age is less than max allowable age (in seconds) for retrieved object')
    print('   -a --after           Return if item created after specified date')

if __name__ == '__main__':
    kwargs = {}
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'hl:b:k:sxm:a:', ['help', 'loglevel', 'bucket', 'list', 'size', 'delete', 'maxage', 'after'])
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
        elif o in ('-n', '--name'):
            kwargs['name'] = a
        elif o in ('-f', '--key'):
            kwargs['key'] = a
        elif o in ('-k', '--list'):
            kwargs['list'] = int(a)
        elif o in ('-s', '--size'):
            kwargs['size'] = True
        elif o in ('-x', '--delete'):
            kwargs['delete'] = True
        elif o in ('-m', '--maxage'):
            kwargs['maxage'] = int(a)
        elif o in ('-a', '--after'):
            kwargs['after'] = a
        elif o in ('-h', '--help'):
            usage()
            sys.exit()
        else:
            assert False, 'unhandled option'

    bucket = Bucket(**kwargs)
        
    if kwargs.get('size', False):
        print(len(bucket))
    elif 'list' in kwargs:
        limit = kwargs.get('list')
        ctr = 0
        for key in bucket.iterkeys():
            try:
                print(key)
                ctr += 1
                if ctr == limit:
                    break
            except KeyboardInterrupt:
                break
            except:
                logger.error(traceback.format_exc())
    elif args:
        for key in args:
            if kwargs.get('delete', False):
                del bucket[key]
            else:
                print(bucket.get(key, maxage=kwargs.get('maxage'), after=kwargs.get('after')))
    else:
        ctr = 0
        for line in sys.stdin:
            rec = json.loads(line)
            bucket[rec['id']] = rec
            ctr += 1
            logger.info('%s %s', ctr, rec['id'])
