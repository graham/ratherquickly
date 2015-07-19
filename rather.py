#! /usr/bin/env python

# standard python libs
import sys
import os
import json
import urllib

# libs needed to work.
import boto3

import zipfile,os.path
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

def load_config():
    return json.loads(open('config.json').read())

def load_config_path(path):
    path = './' + path.strip('/')
    hits = []
    last_config = {}
    
    while (not last_config.get('is_root', False)) and (not (path in ('/', ''))):
        filename = "%s/config.json" % path
        print filename
        if os.path.exists(filename):
            last_config = json.loads(open(filename).read())
            hits.append(last_config)
        path = '/'.join(path.split('/')[:-1])
        
    final_config = {}
    for i in reversed(hits):
        print i
        final_config.update(i)
    return final_config

def save_config(config):
    f = open('config.json', 'w')
    f.write(json.dumps(config))
    f.close()

def ensure_dirs(path, sep='.'):
    fpath = path.split(sep)
    
    full_path = ['functions']
    for node in fpath:
        dir_path = '/'.join(full_path + [node])
        if not os.path.isdir(dir_path):
            print 'creating dir %s' % dir_path
            os.mkdir(dir_path)
        full_path.append(node)
        
    return full_path

def main():
    if len(sys.argv) <= 1:
        print 'Usage: rather.py <command> <options>'
        return

    command = sys.argv[1]
    if globals().get('command_%s' % command, None):
        fn = globals().get('command_%s' % command)
        fn(sys.argv[2:])
    else:
        print 'Command: %s not found.' % command

def command_pull(options):
    if options == []:
        print 'No args, try lambda'
        return

    for module in options:
        if module == 'lambda':
            lam = boto3.client('lambda')
            funcs = lam.list_functions().get("Functions")
            for i in funcs:
                function_name = i.get("FunctionName")
                module_path = ensure_dirs(function_name, '_')

                print 'creating config file for %s' % '/'.join(module_path)
                config_file = open('/'.join(module_path + ['config.json']), 'w')
                config_file.write(json.dumps(i))
                config_file.close()

                code = lam.get_function(FunctionName=i.get("FunctionName"))
                code_url = code.get('Code').get('Location')
                
                print 'Downloading code for %s...' % i.get("FunctionName"),
                sys.stdout.flush()
                urllib.urlretrieve(code_url, filename='/'.join(module_path + ['code.zip']))
                print ''

                ziplocation = '/'.join(module_path + ['code.zip'])
                print 'unzipping...'
                unzip(ziplocation, '/'.join(module_path))
                os.remove(ziplocation)

def command_push(options):
    module = options[0]

    for function in options[1:]:
        print function
                
def command_init(options):
    # First lets see if we already have config.json
    if os.path.exists('config.json'):
        print 'You already have a `config.json` in this directory.'
    else:
        project_name = raw_input('Project Name: ')
        print 'creating config.json...'
        f = open('config.json', 'w')
        f.write(json.dumps({'project_name':project_name, 'is_root':True}))
        f.close()
        print 'done.'
        
def command_create(options):
    if options == []:
        print 'Usage: rather.py create <module_type>'
        print '\tlambda: a lambda route behind a API Gateway resource.'
        return

    config = load_config()

    for module in options:
        if module == 'lambda':
            if not os.path.isdir('functions'):
                print 'directory `functions` being created to store lambdas.'
                os.mkdir('functions')

            print "Please provide a name for your function (can be changed later)"
            path = raw_input("Enter path (sep .): ")

            full_path = ensure_dirs(path, '.')
            
            source_file_name = 'handler.js'

            config_path = '/'.join(full_path + ['config.json'])
            source_path = '/'.join(full_path + [source_file_name])

            source_file = open(source_path, 'w')
            source_file.write('''console.log('Loading function');
exports.handler = function(event, context) {
    context.succeed('hello world.');
};''')
            source_file.close()

            config_file = open(config_path, 'w')
            config = {}
            config['type'] = 'lambda'
            config['lambda_function_name'] = '.'.join(full_path)
            config['source_file'] = source_file_name
            config['runtime'] = 'NodeJS'
            config['handler'] = 'index.handler'
            config_file.write(json.dumps(config))
            config_file.close()
        else:
            print "I don't know how to create modules of type %s" % module

if __name__ == '__main__':
    main()
