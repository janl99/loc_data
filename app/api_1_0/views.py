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

def save_statistics(appid,status,errcode,loctype,locsource):
    st = models.Loc_statistics()
    tk = datetime.now().strftime('%Y-%m-%d')
    try:
        st = models.Loc_statistics.objects(_id=tk).first()
    except Exception,e:
        print e
        st = None

    if st == None:
        st = models.Loc_statistics()
        st._id = tk 
        st.data = '{}'

    d = json.loads(st.data)
    if not d.has_key('date'):
        d['date']= tk 

    if d.has_key('recv'):
        c = int(d['recv'])
        d['recv'] = c + 1
    else:
        d['recv']= 1

    d_app = {}
    if d.has_key('app'):
        d_app = d['app']
    else:
        d['app']=d_app

    d_app_curr = {}
    if d_app.has_key(appid):
        d_app_curr = d_app[appid]
    else:
        d_app[appid]=d_app_curr

    d_app_curr_source = {}
    if d_app_curr.has_key('source'):
        d_app_curr_source = d_app_curr['source']
    else:
        d_app_curr_source = {}

    d_app_curr_source_curr = {}
    if d_app_curr_source.has_key(locsource):
        d_app_curr_source_curr = d_app_curr_source[locsource] 
    else:
        d_app_curr_source_curr = {}

    if d_app_curr_source_curr.has_key('recv'):
        c_source = int(d_app_curr_source_curr['recv'])
        d_app_curr_source_curr['recv'] = c_source + 1
    else:
        d_app_curr_source_curr['recv'] = 1


    d_app_curr_source_curr_status = {}
    if d_app_curr_source_curr.has_key("status"):
        d_app_curr_source_curr_status = d_app_curr_source_curr['status']
    else:
        d_app_curr_source_curr_status = {}

    if status =='1':
        if d_app_curr_source_curr_status.has_key('OK'):
            c_ok = int(d_app_curr_source_curr_status['OK'])
            d_app_curr_source_curr_status['OK'] = c_ok + 1
        else:
            d_app_curr_source_curr_status['OK'] = 1
    else:
        if d_app_curr_source_curr_status.has_key(errcode):
            c_err = int(d_app_curr_source_curr_status[errcode])
            d_app_curr_source_curr_status[errcode]=c_err + 1
        else:
            d_app_curr_source_curr_status[errcode] = 1

    d_app_curr_source_curr['status']=d_app_curr_source_curr_status
    d_app_curr_source[locsource] = d_app_curr_source_curr
    d_app_curr['source'] = d_app_curr_source


    d_app_curr_type = {}
    if d_app_curr.has_key('type'):
        d_app_curr_type = d_app_curr['type']
    else:
        d_app_curr_type = {}

    if d_app_curr_type.has_key(loctype):
        c_type = int(d_app_curr_type[loctype])
        d_app_curr_type[loctype] = c_type + 1
    else:
        d_app_curr_type[loctype] = 1
    d_app_curr['type'] = d_app_curr_type

    st.data = json.dumps(d)
    st.save()

def loc_data():
    stime = datetime.now()
    r = get_result() 
    try:
        print request.get_data()
        data = json.loads(request.get_data())
        appid = data['appid']
        kid =   data['kid']
        time =  data['time']
        status = data['status']
        errcode = data['errcode']
        loctype = data['loctype']
        locsource = data['locsource']
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

        save_statistics(appid,status,errcode,loctype,locsource)

        etime = datetime.now()
        r["time"]=(etime-stime).microseconds

    except Exception, e:
        print e
        r["time"]=(datetime.now()-stime).microseconds
        r["result"]=False
        r["msg"]=e

    return jsonify(r) 

def last_data(kids):
    stime = datetime.now()
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

        datas = models.Last_data.objects.filter(Q(_id__in=ids)).order_by('-time')
        etime = datetime.now()
        print datas
        r["data"]=datas
        r["len"]=len(datas)
        r["time"]=(etime-stime).microseconds
    except Exception,e:
        print e
        r["data"]=[]
        r["len"]=0
        r["time"]=(datetime.now()-stime).microseconds
        r["result"]=False
        r["msg"] = e

    return jsonify(r) 

def his_data(kid):
    stime = datetime.now()
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


        datas = models.His_data.objects.filter(appid=appid,kid=kid,time__gte=st,time__lt=et).order_by('-time')
        print type(datas)
        data_list = []
        pdatas = datas.paginate(page,PER_PAGE,False)
        print type(pdatas)
        print '--------------------------------------------------------'
        if type(pdatas).__str__() == "404: Not Found":
            print "get 404 not found data."
            data_list = []
        else:
            data_list = pdatas.items

        etime = datetime.now()
        r["data"]=data_list
        r["len"]=len(data_list)
        r["time"]=(etime-stime).microseconds
    except Exception,e:
        print e
        r["data"]=[]
        r["len"]= 0
        r["time"]=(datetime.now()-stime).microseconds
        r["result"]=False
        r["msg"] = e

    return jsonify(r)

def statistics(kids):
    stime = datetime.now()
    r = get_result()
    try:
        #print kids
        #print request.args.items().__str__()
        ids = kids.split(',')
        #print ids 

        datas = models.Loc_statistics.objects.filter(Q(_id__in=ids)).order_by('-_id')
        etime = datetime.now()
        #print datas
        r["data"]=datas
        r["len"]=len(datas)
        r["time"]=(etime-stime).microseconds
    except Exception,e:
        print e
        r["data"]=[]
        r["len"]=0
        r["time"]=(datetime.now()-stime).microseconds
        r["result"]=False
        r["msg"] = e

    return jsonify(r) 


