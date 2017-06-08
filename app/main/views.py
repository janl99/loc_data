#!/usr/bin/env python
# -*- coding:utf-8 -*-

from urlparse import urljoin
from datetime import datetime, timedelta
from flask import request, redirect, render_template, url_for, abort, flash, g, session,jsonify
from flask import current_app, make_response
from flask.views import MethodView
#from flask_login import login_required, current_user
#from werkzeug.contrib.atom import AtomFeed
#from mongoengine.queryset.visitor import Q
#from . import models, signals, forms
#from accounts.models import User
#from accounts.permissions import admin_permission, editor_permission, writer_permission, reader_permission
from .DataCacheSaver import DataCacheSaver as _saver
from .DataLoopMover import DataLoopMover as _mover
from .LocDataSaver import LocDataSaver as _locsaver
from .Authenticate import Authenticate as _auth
from .Statistics import Statistics  as _statis
from loc_data.config import System_Settings
from . import models
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


PER_PAGE = System_Settings['pagination'].get('per_page', 10)


#def get_base_data():
#    pages = models.Post.objects.filter(post_type='page', is_draft=False)
#    blog_meta = OctBlogSettings['blog_meta']
#    data = {'blog_meta':blog_meta, 'pages':pages}
#    return data

def __get_locdatasaver():
    '''
    get loc data saver
    '''
    r = _locsaver()
    return r

def __get_dataimportsaver():
    '''获取import缓存保存器实例'''
    r = _saver()
    return r

def __get_datamover():
    '''
    获取数据转移器
    '''
    r = _mover()
    return r

def __get_requestauthenticate():
    '''get Authenticate'''
    r = _auth()
    return r

def __get_statistics():
    '''get statistics'''
    r = _statis() 
    return r


def index():
    #app = models.App()
    #app._id = "03110001"
    #app.appname = "test app"
    #app.save()
    return 'Hello'

def status():
    data = {}
    data['Authenticate'] = __get_requestauthenticate().showinfo() 
    data['LocDataSaver'] = __get_locdatasaver().showinfo()
    data['ImportSaver'] = __get_dataimportsaver().showinfo()
    data['DataLoopMover'] = __get_datamover().showinfo()
    data['Statistics'] = __get_statistics().showinfo()
    return jsonify(data) 
