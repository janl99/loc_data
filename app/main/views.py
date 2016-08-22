#!/usr/bin/env python
# -*- coding:utf-8 -*-

from urlparse import urljoin
from datetime import datetime, timedelta
from flask import request, redirect, render_template, url_for, abort, flash, g, session
from flask import current_app, make_response
from flask.views import MethodView
#from flask_login import login_required, current_user
#from werkzeug.contrib.atom import AtomFeed
from mongoengine.queryset.visitor import Q
#from . import models, signals, forms
#from accounts.models import User
#from accounts.permissions import admin_permission, editor_permission, writer_permission, reader_permission
from loc_data.config import System_Settings


PER_PAGE = System_Settings['pagination'].get('per_page', 10)


#def get_base_data():
#    pages = models.Post.objects.filter(post_type='page', is_draft=False)
#    blog_meta = OctBlogSettings['blog_meta']
#    data = {'blog_meta':blog_meta, 'pages':pages}
#    return data

def index():
    return 'Hello'

