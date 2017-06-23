#!/usr/bin/env python
# -*- coding:utf-8 -*-

from flask import Blueprint
from . import views #,admin_views, errors

main = Blueprint('main', __name__)

main.add_url_rule('/', 'index', views.index)
main.add_url_rule('/status','status',views.status)
main.add_url_rule('/reloadapp','reloadapp',views.reload_app)
