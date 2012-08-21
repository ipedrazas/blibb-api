

import os

_basedir = os.path.abspath(os.path.dirname(__file__))

DEBUG = True

ADMINS = frozenset(['hello@blibb.net'])
SECRET_KEY = 'l354SFdDFakjhlre543f2skjdla23423qewsd$sdfsn654dSSk7jfla'  # supersecret

THREADS_PER_PAGE = 8

CSRF_ENABLED = True
CSRF_SESSION_KEY = "nRomTn23vzGcv4wecDfffRrrx12xv3aidoaGmoSKdfMiao"  # even more secret

IMAGE_EXTENSIONS = set(['jpg', 'jpeg', 'gif', 'png'])
ATTACHMENT_EXTENSIONS = set(['doc', 'xls', 'pdf', 'txt', 'zip'])
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'jpg', 'jpeg', 'gif', 'png', 'xls', 'zip'])


UPLOAD_FOLDER = '/home/ivan/workspace/blibb-api/API/test/'
