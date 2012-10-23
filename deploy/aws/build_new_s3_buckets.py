# -*- coding: utf-8 -*-
#!/usr/bin/python
"""
Bootstrap a new S3 Bucket


"""
import boto
import defaults


STATIC_BUCKET_NAME = defaults.STATIC_BUCKET_NAME
MEDIA_BUCKET_NAME = defaults.MEDIA_BUCKET_NAME
LOCATION = defaults.DEFAULT_REGION

conn = boto.connect_s3()

bucket = conn.create_bucket(STATIC_BUCKET_NAME, location=LOCATION)
print 'Bucket %s successfully created.\
        Use it to store css/js/static images' % bucket.name
print 'URL: %s' % bucket.get_website_endpoint()
print 'Alternative URL: %s' % bucket.get_website_endpoint().replace('-website', '')


if MEDIA_BUCKET_NAME != STATIC_BUCKET_NAME:
    bucket = conn.create_bucket(MEDIA_BUCKET_NAME, location=LOCATION)
    print 'Bucket %s successfully created.\
            Use it to store user-uploaded media' % bucket.name
    print 'URL: %s' % bucket.get_website_endpoint()
    print 'Alternative URL: %s' % bucket.get_website_endpoint().replace('-website', '')
