# -*- coding: utf-8 -*-
#!/usr/bin/python
"""
Clean up old backup files
inside of backup_root
to retain a max of max_backup_files

"""
import sys
import os
from datetime import datetime


def extract_creation_date(filename):
    try:
        date_string = filename.split('db_')[1].split('.gz')[0]
    except:
        print 'Failed to match filename with "db_<datetime_string>.gz"'
        sys.exit(1)

    return datetime.strptime(date_string, '%b-%d-%Y_%H-%M')


def cleanup(backup_root, max_backup_files):
    files = [os.path.join(backup_root, f) for f in os.listdir(backup_root)]

    #Just have at most max_backup_files files on this folder -> nothing to do
    if len(files) <= max_backup_files:
        print 'There are %s files on %s. Nothing to do.' % (len(files),
                                                            backup_root)
        return

    creation_dates = [extract_creation_date(f) for f in files]

    #sort
    files_creation_dates = zip(files, creation_dates)
    files_creation_dates = sorted(files_creation_dates,
                                  key=lambda e: e[1], reverse=True)

    #delete
    files_to_delete = [f[0] for f in files_creation_dates[max_backup_files:]]
    for f in files_to_delete:
        print 'Deleting %s' % f
        os.remove(f)


if __name__ == '__main__':
    backup_root = sys.argv[1]
    max_backup_files = int(sys.argv[2])
    cleanup(backup_root, max_backup_files)
