import sys
import os
import json
import urllib
import zipfile
import stat
import uuid
import pprint

sys.path.append('boto3')
sys.path.append('botocore')

# libs needed to work.
import boto3
from rather_util import *

def command_flist(args):
    lam = boto3.client('lambda')
    funcs = lam.list_functions().get("Functions")

    print 'Registered Functions:'

    for i in funcs:
        fname = i.get("FunctionName")
        handler = i.get("Handler")
        print '  ', fname.rjust(30), '->', handler

    print ''

def command_fpull(args):
    lam = boto3.client('lambda')
    funcs = lam.list_functions().get("Functions")
    config = load_config_path('.')

    name_filter = None
    if args:
        name_filter = args[0]
        print "Downloading functions that start: %s" % name_filter
    else:
        print 'Downloading Functions:'

    module_path = ensure_dirs(config.get('function_directory', 'functions'))

    for i in funcs:
        fname = i.get("FunctionName")
        handler = i.get("Handler")

        if name_filter and not fname.startswith(name_filter):
            continue

        module_path.append(fname)
        module_path = ensure_dirs('/'.join(module_path), '_')
        
        print 'creating config file for %s' % '/'.join(module_path)
        config_file = open('/'.join(module_path + ['config.json']), 'w')
        config_file.write(json.dumps(i))
        config_file.close()

        code = lam.get_function(FunctionName=i.get("FunctionName"))
        code_url = code.get('Code').get('Location')

        print 'Downloading code for %s...' % i.get("FunctionName"),
        sys.stdout.flush()
        urllib.urlretrieve(code_url, filename='/'.join(module_path + ['code.zip']))

        ziplocation = '/'.join(module_path + ['code.zip'])
        print ' unzipping...',
        sys.stdout.flush()
        unzip(ziplocation, '/'.join(module_path))

        print ' cleaning up.'
        os.remove(ziplocation)

    print ''
    
## lambda functions
def command_fpush(options):
    create_if_missing=True
    check_and_set_permissions=False
    lam = boto3.client('lambda')

    def fpush_directory(path):
        config = load_config_path(path)
        function_name = config.get('FunctionName')
        filename = 'build/%s.zip' % (uuid.uuid4())

        zipdir(path, zipfile.ZipFile(filename, 'w', allowZip64=True))

        push = {
            'FunctionName':function_name,
            'Code':{'ZipFile':open(filename).read()}
        }

        thefunc = lam.get_function(FunctionName=function_name)

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

    for i in options:
        fpush_directory(i)

def command_finvoke(args):
    lam = boto3.client('lambda')

    for fname in args:
        thefunc = lam.get_function(FunctionName=fname)

        if thefunc:
            result = lam.invoke(FunctionName=fname,
                                InvocationType='RequestResponse')
            print 'Invoked %s => %s' % (fname, result['Payload'].read())
        else:
            print 'No Function: %s' % fname

    print ''
