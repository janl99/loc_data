#!/usr/bin/env python
# -*- coding:utf-8 -*-

from flask import Blueprint
from . import views 

api = Blueprint('api', __name__)

api.add_url_rule('/loc_data', 'loc_data', views.loc_data,methods=['GET','POST'])
api.add_url_rule('/last_data/<string:kids>','last_data',views.last_data,methods=['GET'])
api.add_url_rule('/his_data/<string:kid>','his_data',views.his_data,methods=['GET'])
api.add_url_rule('/statistics/<string:kids>','statistics',views.statistics,methods=['GET'])
#api.add_url_rule('/import_hisdata','import_hisdata',views.import_hisdata,methods=['GET','POST'])
#api.add_url_rule('/get_his_datecount/<string:date>','get_his_datecount',views.get_his_datecount,methods=['GET'])
#api.add_url_rule('/get_all_last_data/<string:appid>','get_all_last_data',views.get_all_last_data,methods=['GET'])
