Dependencies
============

Boto
S3.py (bundled together in this package)
    S3.py is Amazon S3 Python API

TODO: Replace S3.py dependency with Boto S3 API


Building new instances and buckets
==================================

0) put the following variables in the OS environment variables
    AWS_ACCESS_KEY_ID
    AWS_SECRET_ACCESS_KEY

    defaults.py expects to find this keys under os.environ keys

1) python config_new_aws_account.py
    Config a new keypair and security group

2) python build_new_ec2_instance.py
    Launch a new EC2 Instance

3) python build_new_s3_buckets.py
    Create new S3 Buckets



S3 utils
========

4) python upload_to_static_s3.py '<my_static_folder>'
    Uploads everything under <my_static_folder> to S3.
    Warning: Files uploaded are gonna be all public.
