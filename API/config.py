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
    UPLOAD_FOLDER = '/home/ivan/workspace/blibb-api/API/test/'


class TestConfig(Config):
    DEBUG = False
    TESTING = True
    ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'jpg', 'jpeg', 'gif', 'png', 'xls'])
    UPLOAD_FOLDER = '/home/ivan/workspace/blibb-api/API/test/'


class DevelopmentConfig(Config):
    '''Use "if app.debug" anywhere in your code, that code will run in development code.'''
    DEBUG = True
    TESTING = True
    ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'jpg', 'jpeg', 'gif', 'png', 'xls'])
    UPLOAD_FOLDER = '/home/ivan/workspace/blibb-api/API/test/'
