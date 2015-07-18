#! /usr/bin/env python

# standard python libs
import sys
import os
import json

# libs needed to work.
import boto3

def main():
    if len(sys.argv) <= 1:
        print 'Usage: rather.py <command> <options>'
        return

    command = sys.argv[1]
    if globals().get('command_%s' % command, None):
        fn = globals().get('command_%s' % command)
        fn(sys.argv[1:])
    else:
        print 'Command: %s not found.' % command

def command_init(options):
    # First lets see if we already have config.json
    if os.path.exists('config.json'):
        print 'You already have a `config.json` in this directory.'
    else:
        project_name = raw_input('Project Name: ')
        print 'creating config.json...'
        f = open('config.json', 'w')
        f.write(json.dumps({'project_name':project_name}))
        f.close()
        print 'done.'
        
def command_create(options):
    print 'calling create.'

if __name__ == '__main__':
    main()
