#!/usr/bin/env python

# http://flask.pocoo.org/docs/config/#development-production


class Config(object):
    SECRET_KEY = '{SECRET_KEY}'
    SITE_NAME = '{SITE_NAME}'
    MEMCACHED_SERVERS = ['localhost:11211']
    SYS_ADMINS = ['foo@example.com']


class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'jpg', 'jpeg', 'gif', 'png', 'xls'])
    IMAGE_EXTENSIONS = set(['jpg', 'jpeg', 'gif', 'png'])
    ATTACHMENT_EXTENSIONS = set(['doc', 'xls', 'pdf', 'txt', 'zip'])
    UPLOAD_FOLDER = '/home/ivan/workspace/blibb-api/API/test/'
    STATIC_URL = 'http://static.blibb.net/'
    BUCKET = 'static.blibb.net'
    EXPIRE = 3600
    NUM_URL = 3


class TestConfig(Config):
    DEBUG = False
    TESTING = True
    ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'jpg', 'jpeg', 'gif', 'png', 'xls'])
    IMAGE_EXTENSIONS = set(['jpg', 'jpeg', 'gif', 'png'])
    ATTACHMENT_EXTENSIONS = set(['doc', 'xls', 'pdf', 'txt', 'zip'])
    UPLOAD_FOLDER = '/home/ivan/workspace/blibb-api/API/test/'
    STATIC_URL = 'http://static.blibb.it/'
    BUCKET = 'static.blibb.it'
    EXPIRE = 3600
    NUM_URL = 3


class DevelopmentConfig(Config):
    '''Use "if app.debug" anywhere in your code, that code will run in development code.'''
    DEBUG = True
    TESTING = True
    ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'jpg', 'jpeg', 'gif', 'png', 'xls'])
    IMAGE_EXTENSIONS = set(['jpg', 'jpeg', 'gif', 'png'])
    ATTACHMENT_EXTENSIONS = set(['doc', 'xls', 'pdf', 'txt', 'zip'])
    UPLOAD_FOLDER = '/home/ivan/workspace/blibb-api/API/test/'
    STATIC_URL = 'http://static.blibb.it/'
    BUCKET = 'static.blibb.it'
    EXPIRE = 3600
    NUM_URL = 3
