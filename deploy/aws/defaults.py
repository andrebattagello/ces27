# -*- coding: utf-8 -*-
"""
Global defaults (used in several other aws config scripts).


Important constants defined in this file
which are used in other scripts under this package:

    #Auth constants:
    AWS_ACCESS_KEY_ID
    AWS_SECRET_ACCESS_KEY

    #Global constants
    DEFAULT_REGION
    REGION_NAME (by default, the same as DEFAULT_REGION)

    #EC2 constants:
    DEFAULT_AMI_IMAGE_ID
    DEFAULT_INSTANCE_TYPE
    KEY_NAME

    #S3 constants:
    STATIC_BUCKET_NAME
    MEDIA_BUCKET_NAME



Dependencies: AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY on os.environ

"""
import os
try:
    AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
    AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']
except:
        print """
        Please, define the following parameters as OS environment variables.
            AWS_ACCESS_KEY_ID
            AWS_SECRET_ACCESS_KEY

        """
        import sys
        sys.exit(1)


#Account access defaults
KEY_NAME = 'ces27-key'

#S3 defaults
STATIC_BUCKET_NAME = 'ces27'
PHOTOS_BUCKET_NAME = 'ces27'

#EC2 defaults
DEFAULT_AMI_IMAGE_ID = 'ami-aa855bb7'  # Default Linux Amazon AMI
DEFAULT_INSTANCE_TYPE = 't1.micro'  # Free tier is just for micro instances

#Locale defaults
DEFAULT_REGION = 'sa-east-1'  # Sao Paulo, Brazil
REGION_NAME = DEFAULT_REGION
