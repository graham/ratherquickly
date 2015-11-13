#! /usr/bin/env python

# standard python libs
import sys
import os
import json
import urllib
import zipfile
import stat

# libs needed to work.
import boto3

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

## lambda functions
def command_push(options):
    path = options[0]
    create_if_missing=True
    check_and_set_permissions=False
    
    lam = boto3.client('lambda')
    function_name = path.replace('.', '_')
    function_path = path.replace('.', '/')
    
    try:
        thefunc = lam.get_function(FunctionName=function_name)
    except:
        #function does not exist.
        thefunc = None

    ensure_dirs('build', '.')
    filename = 'build/%s.zip' % function_name
    print 'zipping %s into %s' % (function_path, filename)
    zipdir(function_path, zipfile.ZipFile(filename, 'w', allowZip64=True))
    
    lam = boto3.client('lambda')
    push = {
        'FunctionName':function_name,
        'Code':{'ZipFile':open(filename).read()}
    }

    if thefunc == None and create_if_missing:
        print 'creating %s' % function_name
        local_config = load_config_path(function_path + "/config.json")
        push['Runtime'] = local_config['Runtime']
        push['Role'] = local_config['Role']
        push['Handler'] = local_config['Handler']
        # Lets ask AWS Lambda to create the function (with no API endpoints).
        lam.create_function(**push)
    else:
        print 'updating code for %s' % function_name
        push['ZipFile'] = push['Code']['ZipFile']
        del push['Code']
        lam.update_function_code(**push)

def command_init(options):
    path = options[0]
    master_config = load_config()
    function_name = path.replace('.', '_')
    
    config = {
        'Runtime':'nodejs',
        'Role':master_config.get('LambdaRole', 'lambda_basic_execution'),
        'Handler':'index.handler',
        'Description':'A lambda function, created Rather Quickly.'
    }

    simple_script = '''#! /usr/bin/env node\nconsole.log('Loading function');\n\nexports.handler = function(event, context) {\n    context.succeed("Push Works!");\n};\n'''

    ## lets create the local files
    print 'creating files.'
    
    dir_path = path.replace('.', '/')
    ensure_dirs(path)

    print '\t%s/config.json' % dir_path
    f = open(dir_path + '/config.json', 'w')
    f.write(json.dumps(config))
    f.close()

    print '\t%s/index.js' % dir_path
    f = open(dir_path + '/index.js', 'w')
    f.write(simple_script)
    f.close()

    print '\tadding execute permissions to index.js'
    st = os.stat(dir_path + '/index.js')
    os.chmod(dir_path + '/index.js', st.st_mode | stat.S_IEXEC)

    print 'done.'
    
def command_pull(options):
    lam = boto3.client('lambda')
    funcs = lam.list_functions().get("Functions")

    start = ''
    if len(options) > 0:
        start = options[0]
        
    ensure_dirs('functions')

    for i in funcs:
        function_name = i.get("FunctionName")
        module_path = ensure_dirs('%s' % function_name, '_')

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
        #os.remove(ziplocation)
        

def command_checkup(options):
    print 'sprinkling faiery dust...'

if __name__ == '__main__':
    main()
