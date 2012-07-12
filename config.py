

import os

_basedir = os.path.abspath(os.path.dirname(__file__))

DEBUG = True

ADMINS = frozenset(['hello@blibb.net'])
SECRET_KEY = 'l354SFdDFakjhlre543f2skjdlan654dSSk7jfla'  # supersecret

THREADS_PER_PAGE = 8

CSRF_ENABLED = True
CSRF_SESSION_KEY = "nRomTn23vzGcv4wecx12xv3aidoaGmoSKdfMiao"  # even more secret


ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'jpg', 'jpeg', 'gif', 'png', 'xls'])
UPLOAD_FOLDER = '/home/ivan/workspace/blibb-api/API/test/'
