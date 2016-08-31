#!/usr/bin/env python
# -*- coding:utf-8 -*-

from flask import Blueprint
from . import views 

api = Blueprint('api', __name__)

api.add_url_rule('/loc_data', 'loc_data', views.loc_data,methods=['GET','POST'])
api.add_url_rule('/last_data/<string:kids>','last_data',views.last_data,methods=['GET'])
api.add_url_rule('/his_data/<string:kid>','his_data',views.his_data,methods=['GET'])
api.add_url_rule('/statistics/<string:kids>','statistics',views.statistics,methods=['GET'])

