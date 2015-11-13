#! /usr/bin/env python

# standard python libs
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

from ratherquickly.rather_function import *
from ratherquickly.rather_util import *

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

def command_config(args):
    gateway = boto3.client('apigateway')
    config = load_config_path('.')

    api_id = config.get('target_api', None) 
    if api_id:
        api = gateway.get_rest_api(restApiId=api_id)
        pprint.pprint(api)
    else:
        print 'You need to set your target_api.'

def command_rlist(args):
    gateway = boto3.client('apigateway')
    config = load_config_path('.')
    api_id = config.get('target_api', None)

    resources = gateway.get_resources(restApiId=api_id)
    for i in resources.get('items',[]):
        print i

def command_dlist(args):
    gateway = boto3.client('apigateway')
    config = load_config_path('.')
    api_id = config.get('target_api', None)
    
    deployments = gateway.get_deployments(restApiId=api_id)
    for i in deployments.get('items', []):
        print i
    
def command_slist(args):
    gateway = boto3.client('apigateway')
    config = load_config_path('.')
    api_id = config.get('target_api', None)

    stages = gateway.get_stages(restApiId=api_id)
    for i in stages.get('item'):
        print i.get('stageName').rjust(10), ' -> ', i.get('deploymentId')

if __name__ == '__main__':
    main()
