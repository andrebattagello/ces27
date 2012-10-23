#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Walks through a given folder (and his children), searching for files
to upload to some BUCKET in AWS S3.

The folder to search for is passed into as an argument.
    E.g.: python upload_static_s3.py '../../public/static'
The above cmd should walk (recursively) over '../../public/static'
and upload any file found to the S3 account configured.


Dependencies: S3.py (just put in the same folder as this module)
              defaults.py w/ AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY


Todo: Change to depend on Boto API and not S3.py

"""

import S3
import os
import sys
import hashlib
import mimetypes
import json
import time
from gzip import GzipFile
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

from defaults import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY
from defaults import STATIC_BUCKET_NAME as BUCKET_NAME

#IGNORE_DIRS = ['admin']
IGNORE_DIRS = []
IGNORE_EXTENSIONS = ['swp', 'bak', 'pyc', 'old']
TEXT_TYPES = ('text/css', 'text/javascript',
              'application/javascript', 'application/css')
EXTRA_FILES = {}
CACHE_FOLDER_NAME = ''  # should be the same as settings.COMPRESS_OUTPUT_DIR
                        # empty string is a lot easir to handle
GZIP_ENABLED = True
REMOTE_METADATA_FILE = 'META.json'
LOCAL_METADATA_FILE = 'META.local.json'


def _get_connection():
    conn = S3.AWSAuthConnection(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
    if conn.check_bucket_exists(BUCKET_NAME).status != 200:
        print 'Failed to establish connect. Check you auth keys.'
        sys.exit(1)
    return conn


def _get(conn, remote_file, bucket_name=BUCKET_NAME):
    """ Gets a remote file of a bucket using a connection """
    contents = None
    try:
        reply = conn.get(bucket_name, remote_file)
        contents = reply.body
        if reply.http_response.status != 200:
            print 'Failed to fetch current_remote metadata'
            contents = None
    except:
        contents = None
    return contents


def _put(conn, remote_file, contents, bucket_name=BUCKET_NAME, headers=None):
    """
    Put some contents into a remote_file of a bucket usign connection conn.
    Optionally the headers can be specified.
    """
    error_msg = 'Failed to upload to %s' % remote_file
    try:
        reply = conn.put(bucket_name, remote_file,
                         S3.S3Object(contents), headers)
        if reply.http_response.status != 200:
            print error_msg
    except:
        print error_msg


def _get_headers(content_type):
    """
    Get headers for this type of file.
    Also, put the correct content encoding.

    """
    headers = {'x-amz-acl':  'public-read',
               'Content-Type': content_type,
               'Cache-Control': 'public,max-age=31536000'}
    return headers


def _get_content_type(file_descriptor):
    """ Guess the content_type, by using its file descriptor """
    content_type = mimetypes.guess_type(file_descriptor.name)[0]
    if not content_type:
        content_type = 'text/plain'
    return content_type


def _file_can_be_compressed(filename):
    """
    Asserts if a given file (w/ name filename) can be compressed.
    content_type is optional and can speed up assertion.

    Should return True if it is a Text Type (CSS/JS)
    """
    content_type = ''
    with open(filename, 'rb') as f:
        content_type = _get_content_type(f)
    return content_type in TEXT_TYPES


def _compress_string(content):
    """
    Compress the content string passed.
    Should be called when gzip is enabled to compress text types.
    There is no real advantage in using this with images, since most are
    already nicely compressed by some image processing algorithm.

    """
    zbuf = StringIO()
    zfile = GzipFile(mode='wb', compresslevel=6, fileobj=zbuf)
    zfile.write(content)
    zfile.close()
    return zbuf.getvalue()


def _get_sha_metadata(filename):
    """ Returns the sha metada of a local file """
    with open(filename) as f:
        return hashlib.sha1(f.read()).hexdigest()


def _build_local_metadata_file(files, home=''):
    """
    Build the metadata local file with
    all sha information about files.

    File location is computed based on home kw-argument.

    """
    filepaths = [os.path.join(home, f) for f in files]
    shas = [_get_sha_metadata(f) for f in filepaths]
    metadata = dict(zip(files, shas))

    with open(LOCAL_METADATA_FILE, 'w') as f:
        f.write(json.dumps(metadata))


def upload_file(conn, filename_local, filename_s3, gzip=False):
    """
    Uploads a file to S3 bucket.

    If gzip=True, compress and upload the gzipped version of the file
    instead of the original one.

    If gzip=True and it is not possible to compress,
    then quit the upload process (don't upload at all).

    So you should always pass the correct gzip info into this function,
    in order to get a upload.

    """

    filename_s3 = filename_s3.lstrip('./')

    file_descriptor = open(filename_local, 'rb')
    content = file_descriptor.read()

    content_type = _get_content_type(file_descriptor)
    headers = _get_headers(content_type)

    #should compress if the file is compressable and gzip is enabled
    can_be_gzipped = _file_can_be_compressed(filename_local)
    if gzip and can_be_gzipped:
        content = _compress_string(content)
        headers['Content-Length'] = str(len(content))
        headers['Content-Encoding'] = 'gzip'
        extension = mimetypes.guess_extension(content_type)
        #we should not overwrite the original file in the server.
        #We change extensions: style.css --> style.gz.css, for instance
        filename_s3 = filename_s3.rstrip(extension) + '.gz' + extension

    #if gzip is enabled and it is not compressable, don't upload nothing at all
    elif gzip and not can_be_gzipped:
        return

    #upload
    print 'Uploading %s to %s' % (filename_local, filename_s3)
    _put(conn, filename_s3, content, headers=headers)
    file_descriptor.close()


def _get_file_list(folder):
    """
    Returns a recursive list of all files inside folder.
    The list element is a string w/ file path relative to folder.

    If any file is found with the same name as LOCAL_METADATA_FILE,
    then do not append it to the list.

    """
    tree = [x for x in os.walk(folder)]
    files = [os.path.join(t[0], y) for t in tree for y in t[2]]
    return [os.path.relpath(x, start=folder)
                for x in files if x != LOCAL_METADATA_FILE]


def _fetch_current_remote_metadata(conn):
    """
    Fetches the metadata remote file REMOTE_METADATA_FILE
    and returns the metadata dict equivalent.

    """
    content = _get(conn, REMOTE_METADATA_FILE)
    metadata = json.loads(content) if content else {}
    return metadata


def _fetch_current_local_metadata():
    """
    Fetches the metadata local file LOCAL_METADATA_FILE
    and returns the metadata dict equivalent.

    """
    if not os.path.exists(LOCAL_METADATA_FILE):
        return {}

    with open(LOCAL_METADATA_FILE) as f:
        return json.loads(f.read())


def _filter_file_list(files, local_metadata, remote_metadata):
    """
    Based on comparison of local and remote metada dictionaries,
    filter files to retain only the
    files which doesn't exist on remote metadata dict
    or have different content and same filename.

    Also, based on IGNORE_DIRS and IGNORE_EXTENSIONS,
    filter the net file list.

    """
    def _is_tracked(filename, metadata):
        """
        Is the filename tracked in the remote metadata dict.
        The file may be not even locally tracked yet
        """
        current_local_sha = local_metadata.get(filename, None)
        current_remote_sha = metadata.get(filename, None)
        return current_local_sha is not None \
                and current_remote_sha is not None \
                and current_local_sha == current_remote_sha

    def _is_inside_ignored_dir(filename):
        """ Is the filename inside any of the IGNORE_DIRS list """
        ignore_dirs = ['./' + x for x in IGNORE_DIRS]
        return any([filename.startswith(x) for x in ignore_dirs])

    def _has_ignored_extension(filename):
        return any([ext in IGNORE_EXTENSIONS
                        for ext in filename.split('.')[1:]])

    files = [f for f in files
                if not _is_inside_ignored_dir(f)
                and not _has_ignored_extension(f)
                and not _is_tracked(f, remote_metadata)]
    return files


def upload_all_to_s3(static_root):
    """
    Walks through all the subfolders in static_root,
    and uploads everything valid found to S3.

    If Gzip is enabled, also tries to compress and upload
    the compressed version of the static asset.

    """
    conn = _get_connection()

    files = _get_file_list(static_root)
    _build_local_metadata_file(files, home=static_root)

    local_metadata = _fetch_current_local_metadata()
    remote_metadata = _fetch_current_remote_metadata(conn)
    files_to_upload = _filter_file_list(files, local_metadata, remote_metadata)

    start_time = time.time()
    print 'Upload start: Landing in BUCKET_NAME: %s' % BUCKET_NAME

    for f in files_to_upload:
        #Upload to Bucket
        upload_file(conn, os.path.join(static_root, f), f)

        #Upload Gzip css/js version if gzip is enabled
        can_be_gzipped = _file_can_be_compressed(os.path.join(static_root, f))
        if GZIP_ENABLED and can_be_gzipped:
            upload_file(conn, os.path.join(static_root, f), f, gzip=True)

    #Extra files
    if EXTRA_FILES:
        print 'Now, uploading extra files outside public/static'
        for filename_local, filename_s3 in EXTRA_FILES.items():
            upload_file(conn, filename_local, filename_s3)

    end_time = time.time()
    print 'Upload finished: \
            Time elapsed: %s s' % round(end_time - start_time, 3)

    # refresh metadata file on the server
    print 'Uploading local metadata file'
    upload_file(conn, LOCAL_METADATA_FILE, REMOTE_METADATA_FILE)
    print 'Uploading process DONE'


if __name__ == '__main__':
    static_root = sys.argv[1]
    LOCAL_METADATA_FILE = os.path.join(static_root, LOCAL_METADATA_FILE)
    upload_all_to_s3(static_root)
