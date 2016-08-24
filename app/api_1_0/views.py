#!/usr/bin/env python
# -*- coding:utf-8 -*-

from urlparse import urljoin
from datetime import datetime, timedelta
from flask import request, redirect, render_template, url_for, abort, flash, g, session
from flask import current_app, make_response,json
from flask.views import MethodView
#from flask_login import login_required, current_user
#from werkzeug.contrib.atom import AtomFeed
from mongoengine.queryset.visitor import Q
#from . import models, signals, forms
#from accounts.models import User
#from accounts.permissions import admin_permission, editor_permission, writer_permission, reader_permission
from loc_data.config import System_Settings
from main import models


PER_PAGE = System_Settings['pagination'].get('per_page', 10)

def loc_data():
    data = json.loads(request.get_data())
    appid = data['appid']
    kid =   data['kid']
    time =  data['time']
    content =  data['data']
    print appid
    print kid
    print time
    print content 


    return 'OK',201

def last_data(kids):
    print kids
    print request.args.items().__str__()
    return 'get_last_loc_data'

def his_data(kid):
    print kid
    print request.args.items().__str__()
    return 'get_his_loc_data'
