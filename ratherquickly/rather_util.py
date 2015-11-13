import sys
import os
import json
import urllib
import zipfile
import stat
import uuid
import pprint

def unzip(source_filename, dest_dir):
    with zipfile.ZipFile(source_filename) as zf:
        for member in zf.infolist():
            # Path traversal defense copied from
            # http://hg.python.org/cpython/file/tip/Lib/http/server.py#l789
            words = member.filename.split('/')
            path = dest_dir
            for word in words[:-1]:
                drive, word = os.path.splitdrive(word)
                head, word = os.path.split(word)
                if word in (os.curdir, os.pardir, ''): continue
                path = os.path.join(path, word)
            zf.extract(member, path)

def zipdir(path, ziph):
    curdir = os.path.abspath(os.curdir)
    os.chdir(path)
    for root, dirs, files in os.walk('.'):
        for file in files:
            filepath = os.path.join(root, file)
            if file == 'config.json' or file.startswith('.'):
                pass
            else:
                info = zipfile.ZipInfo(file)
                ziph.write(filename=filepath)
    os.chdir(curdir)
    
def load_config():
    return json.loads(open('config.json').read())

def load_config_path(path):
    path = './' + path.strip('/')
    hits = []
    last_config = {}
    
    while (not last_config.get('is_root', False)) and (not (path in ('/', ''))):
        filename = "%s/config.json" % path
        if os.path.exists(filename):
            last_config = json.loads(open(filename).read())
            hits.append(last_config)
        path = '/'.join(path.split('/')[:-1])
        
    final_config = {}
    for i in reversed(hits):
        final_config.update(i)
    return final_config

def save_config(config):
    f = open('config.json', 'w')
    f.write(json.dumps(config))
    f.close()

def ensure_dirs(path, sep='.'):
    fpath = path.split(sep)
    full_path = []
    
    for node in fpath:
        dir_path = '/'.join(full_path + [node])
        if not os.path.isdir(dir_path):
            print 'creating dir %s' % dir_path
            os.mkdir(dir_path)
        full_path.append(node)
        
    return full_path
