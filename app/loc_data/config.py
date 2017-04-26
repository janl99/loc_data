#!/usr/bin/env pyton
# -*- coding:utf-8 -*-

import os, sys


System_Settings = {
    'pagination':{
        'per_page': int(os.environ.get('per_page', 10)),
        'admin_per_page': int(os.environ.get('admin_per_page', 10)),
        'archive_per_page': int(os.environ.get('admin_per_page', 20)),
    },
    'query_setting':{
        'max_days_once': int(os.environ.get('max_days',31)),
        'max_days_before_today': int(os.environ.get('max_days_before_today',540))
        },
    'copyright': {
        'display_copyright': os.environ.get('allow_donate', 'true').lower() == 'true',
        'copyright_msg': os.environ.get('copyright_msg', 'The article is not allowed to repost unless author authorized').decode('utf8')
    },
}

class Config(object):
    BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

    SECRET_KEY = os.environ.get('SECRET_KEY') or 'fjdljLJDL08_80jflKzcznv*c'
    #MONGODB_SETTINGS = {'DB': 'loc_data'}

    TEMPLATE_PATH = os.path.join(BASE_DIR, 'templates').replace('\\', '/')
    STATIC_PATH = os.path.join(BASE_DIR, 'static').replace('\\', '/')

    REDIS_URL = "redis://:@192.168.2.221:6379/0"
    SQLALCHEMY_DATABASE_URI = 'mysql://root:loc_data#123456@192.168.2.221:3306/loc_data'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False



    @staticmethod
    def init_app(app):
        pass

class DevConfig(Config):
    DEBUG = True

class PrdConfig(Config):
    # DEBUG = False
    DEBUG = os.environ.get('DEBUG', 'false').lower() == 'true'
    #MONGODB_SETTINGS = {
    #        'db': 'loc_data',
    #        'host': os.environ.get('MONGO_HOST') or 'localhost',
    #        # 'port': 12345
    #    }

config = {
    'dev': DevConfig,
    'prd': PrdConfig,
    'default': DevConfig,
}
