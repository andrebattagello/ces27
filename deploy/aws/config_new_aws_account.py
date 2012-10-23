# -*- coding: utf-8 -*-
#!/usr/bin/python
"""
Setup the most common one-time configs in AWS
when registering a new AWS account.

You're gonna need one keypair to ssh access.
You're gonna need a security group w/ HTTP and SSH access rules

You probably don't need more than 1 key pair
or more than 1 security group right now.

You probably don't need to run this file multiple times. Just one time is fine.

"""

from boto import ec2
import defaults
import os

KEY_NAME = defaults.KEY_NAME
DEFAULT_REGION = defaults.DEFAULT_REGION


def create_key_pair(conn):
    """
    Asks if it should create a new key pair on ~/.ssh/
    Cancel creation if key pair file already exists on ~/.ssh/

    """
    print 'This script is gonna create a key pair under ~/.ssh/%s.pem.\
            Should proceed?' % KEY_NAME
    answer = raw_input()
    if answer.lower() not in ('y', 'yes'):
        print 'Key pair operation is gonna cancel right now.'
        return

    if os.path.exists('~/.ssh/%s.pem' % KEY_NAME):
        print 'Error: Current key ~/.ssh/%s.pem already exists.' % KEY_NAME
        print 'Key pair operation is gonna cancel right now.'
        return

    key_pair = conn.create_key_pair(KEY_NAME)
    key_pair.save('~/.ssh')

    print 'keypair generate at ~/.ssh/%s.pem' % KEY_NAME
    print 'Run  chmod 600 ~/.ssh/%s.pem  on the shell' % KEY_NAME


def create_security_group(conn):
    """
    Asks if it should create a new security group with http and ssh port rules

    """
    print 'This script is gonna create a security group with following rules:\
            tcp:80:0.0.0.0/0 and tcp:22:0.0.0.0/0. Should proceed?'
    answer = raw_input()
    if answer.lower() not in ('y', 'yes'):
        print 'Security group operation is gonna cancel right now.'
        return

    security_group = conn.get_all_security_groups()[0]  # default sec group
    security_group.authorize('tcp', 80, 80, '0.0.0.0/0')
    security_group.authorize('tcp', 22, 22, '0.0.0.0/0')
    print 'Security group created'


def main():
    conn = ec2.connect_to_region(DEFAULT_REGION)
    create_key_pair(conn)
    create_security_group(conn)


if __name__ == '__main__':
    main()
