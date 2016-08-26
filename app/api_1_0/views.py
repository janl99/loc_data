#!/usr/bin/env python
# -*- coding:utf-8 -*-

from urlparse import urljoin
from datetime import datetime, timedelta
from flask import request, redirect, render_template, url_for, abort, flash, g, session,json,jsonify
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

def get_result():
    return {"result":True,"msg":"OK"}

def loc_data():
    r = get_result() 
    try:
        print request.get_data()
        data = json.loads(request.get_data())
        appid = data['appid']
        kid =   data['kid']
        time =  data['time']
        content =  data['data']

        last_data = models.Last_data()
        last_data._id = appid + ":" + kid
        last_data.appid = appid
        last_data.kid = kid
        last_data.time = time
        last_data.data = content
        last_data.save()

        his_data = models.His_data()
        his_data._id = appid + ":" + kid
        his_data.appid = appid
        his_data.kid = kid
        his_data.time = time
        his_data.data = content
        his_data.save()
    except Exception, e:
        r["result"]=False
        r["msg"]=e

    return jsonify(r) 

def last_data(kids):
    r = get_result()
    try:
        print kids
        print request.args.items().__str__()
        appid = request.args.get('appid','unknow app') 
        if appid == 'unknow app':
            r["result"]=False
            r["msg"] ="unknow app" 
            return jsonify(r)
        ids = []
        for kid in kids.split(','):
            ids.append(appid+":"+kid)
        print ids 
        stime = datetime.now()
        datas = models.Last_data.objects.filter(Q(_id__in=ids)).order_by('-time')
        etime = datetime.now()
        print datas
        r["data"]=datas
        r["len"]=len(datas)
        r["time"]=(etime-stime).microseconds
    except Exception,e:
        r["result"]=False
        r["msg"] = e

    return jsonify(r) 

def his_data(kid):
    r = get_result()
    try:
        print kid
        print request.args.items().__str__()
        if kid == None or  kid == '':
            r["result"]=False
            r["msg"] ="None or empty kid" 
            return jsonify(r)

        appid = request.args.get('appid','unknow app') 
        if appid == 'unknow app':
            r["result"]=False
            r["msg"] ="unknow app" 
            return jsonify(r)

        d = datetime.now()
        init_stime = datetime.strptime(d.strftime('%Y-%m-%d') + ' 00:00:00','%Y-%m-%d %H:%M:%S')
        init_etime = init_stime + timedelta(days = 1) 
        str_stime = request.args.get('stime',init_stime.strftime('%Y-%m-%d %H:%M:%S'))
        str_etime = request.args.get('etime',init_etime.strftime('%Y-%m-%d %H:%M:%S'))
        st = datetime.strptime(str_stime,'%Y-%m-%d %H:%M:%S')
        et = datetime.strptime(str_etime,'%Y-%m-%d %H:%M:%S')
        print st
        print et
        page = int(request.args.get('page','1')) 
        print str(page)

        stime = datetime.now()
        datas = models.His_data.objects.filter(appid=appid,kid=kid,time__gte=st,time__lt=et).order_by('-time')
        print type(datas)
        data_list = []
        pdatas = datas.paginate(page,PER_PAGE)
        print type(pdatas)
        data_list = pdatas.items

        etime = datetime.now()
        r["data"]=data_list
        r["len"]=len(data_list)
        r["time"]=(etime-stime).microseconds
    except Exception,e:
        r["result"]=False
        r["msg"] = e

    return jsonify(r)

