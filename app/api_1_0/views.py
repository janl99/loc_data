#!/usr/bin/env python
# -*- coding:utf-8 -*-

from urlparse import urljoin
from datetime import datetime, timedelta
from flask import request, redirect, render_template, url_for, abort, flash, g, session,json,jsonify
from flask import current_app, make_response,json
from flask.views import MethodView
#from flask_login import login_required, current_user
#from werkzeug.contrib.atom import AtomFeed
#from mongoengine.queryset.visitor import Q
#from . import models, signals, forms
#from accounts.models import User
#from accounts.permissions import admin_permission, editor_permission, writer_permission, reader_permission
from loc_data.config import System_Settings
from main.models import his_data 
from loc_data import db,redis
from sqlalchemy import text

PER_PAGE = System_Settings['pagination'].get('per_page', 10)
LAST_LOCATION_REDIS_KEY_PREFIX = "LL"

def __get_result():
    """
    build base result. 
    """
    return {"result":True,"msg":"OK"}

def __Is_NoneOrEmpty(val):
    """
    check val is empty or None,return True else False.
    """
    if val == None:
        return True 
    if val == "": 
        return True 
    return False 

def __Check_AppidAllowed(appid):
    """
    check appid is allowed.
    """
    return True 

def __get_redis_Key(appid,kid):
    """
    build redis key
    """
    return LAST_LOCATION_REDIS_KEY_PREFIX + ":" + appid.strip() + ":" + kid.strip()

def __update_statistics(appid,status,errcode,loctype,locsource):
    """
    update loc data statictics data.
    """
    pass

def __build_date_list(st,et):
    print "---build date list---"
    r = []
    if st > datetime.now():
        st = datetime.now()
    if et > datetime.now():
        et = datetime.now()
    delta = et - st
    print "datediff days: %s" % str(delta.days)
    if delta.days <= 0: #same day
        print "st and et is same day."
        if (datetime.now() - et).days == 0: # same day and today
            print "st and et is same day and today."
            t = datetime.now().strftime('%Y%m%d')
            print t
            r.append(t)
            return r
        elif (datetime.now() - et).days > 0:  # same old day
            print "st and et is same day befor today."
            return r.append(et.strftime('%Y%m%d'))
    else:
        print "st and et is diff day."
        for i in range(delta.days):
            r.append((st + iatetime.timedelta(i)).strftime('%Y%m%d'))
    print "--build date list end.---"
    return r

def __build_hisdata_query(appid,kid,status,errcode,st,et):
    print "-----------start build query------------------------"
    dl = __build_date_list(st,et)
    print dl
    #kwargs = {'appid':appid,'kid':kid,'time':st,'time':et}
    #todo 1: check status and errcode isNoneOrEmpty
    if __Is_NoneOrEmpty(status) and __Is_NoneOrEmpty(errcode):
        #todo 2: query without status and errcode
        print "status and errcode is none or empty."
        todaysuffix = datetime.now().strftime('%Y%m%d')
        print todaysuffix
        if todaysuffix in dl:
            print "query include today table."
            q = db.session.query(his_data).\
                    filter(appid==appid,kid==kid).\
                    order_by(his_data.time)
        else:
            print "query not include today table."
            q = db.session.query(his_data).\
                    filter(his_data.id == 0)
        for suffix in dl:
            te = his_data.model(suffix)
            tq = db.session.query(te).filter(appid==appid,kid==kid)
            q.union(tq) 
            #print q.all()
        return q
    elif not __Is_NoneOrEmpty(status) and __Is_NoneOrEmpty(errcode):
       #todo 3: query with status and without errcode
        pass
    elif __Is_NoneOrEmpty(status) and not __Is_NoneOrEmpty(errcode):
        #todo 4: query without status and with errcode
        pass
    elif not __Is_NoneOrEmpty(status) and not __Is_NoneOrEmpty(errcode):
        #todo 5: query width status and errcode both.
        pass
    print "----------------build query end-----------------------"

def loc_data():
    """
    receive post data and save. 
    1. set data val to redis for fast get. 
    2. save to mysql database for query sometime.
    """
    stime = datetime.now()
    r = __get_result() 
    try:
        #print request.get_data()
        data = json.loads(request.get_data())
        #todo0: receive json data
        appid = data['appid']
        kid =   data['kid']
        time =  data['time']
        status = data['status']
        errcode = data['errcode']
        loctype = data['loctype']
        locsource = data['locsource']
        content =  data['data']
        #todo1: check appid,kid
        if __Is_NoneOrEmpty(appid):
            r["result"] = False
            r["msg"] = "invalid appid."
            return r
        if __Is_NoneOrEmpty(kid):
            r["result"] = False
            r["msg"] = "invalid kid."
            return r
        #todo2: check appid is allowed.
        if not __Check_AppidAllowed(appid):
            r["result"] = False
            r["msg"] = "appid is not allowed."
            return r
        #todo3: build redis key and set to redis
        rediskey = __get_redis_Key(appid,kid)
        redis.set(rediskey,data)
        #todo4: save data to mysql
        hdata = his_data()
        #hdata.id = appid + ":" + kid
        hdata.appid = appid
        hdata.kid = kid
        hdata.time = time
        hdata.status = status
        hdata.errcode = errcode
        hdata.loctype = loctype
        hdata.locsource = locsource
        hdata.data = content
        db.session.add(hdata)
        db.session.commit()
        __update_statistics(appid,status,errcode,loctype,locsource)
        etime = datetime.now()
        r["time"]=(etime-stime).microseconds
    except Exception, e:
        print e
        r["time"]=(datetime.now()-stime).microseconds
        r["result"]=False
        r["msg"]=e
    return jsonify(r)

def last_data(kids):
    """
    get some kid last locdata, by kids.
    kids is string split by ','. eg.  kids = "kid1,kid2,kid3"
    And request param must inclue appid.
    """
    stime = datetime.now()
    r = __get_result()
    try:
        print kids
        print request.args.items().__str__()
        #todo 1: get appid and check it allowed
        appid = request.args.get('appid','') 
        if __Is_NoneOrEmpty(appid):
            r["result"]=False
            r["msg"] ="invalid appid" 
            return jsonify(r)
        if __Is_NoneOrEmpty(appid):
            r["result"] = False
            r["msg"] = "appid is not allowed."
            return r
        #todo 2: loop get data by kids
        data = []
        for kid in kids.split(','):
            if __Is_NoneOrEmpty(kid):
                continue
            rediskey = __get_redis_Key(appid,kid)
            d = redis.get(rediskey)
            data.append(d)
        print data 
        etime = datetime.now()
        r["data"]=data
        r["len"]=len(data)
        r["time"]=(etime-stime).microseconds
    except Exception,e:
        print e
        r["data"]=[]
        r["len"]=0
        r["time"]=(datetime.now()-stime).microseconds
        r["result"]=False
        r["msg"] = e
    return jsonify(r) 

def h_data(kid):
    stime = datetime.now()
    r = __get_result()
    try:
        #print kid
        #print request.args.items().__str__()
        #todo 1: check kid
        if __Is_NoneOrEmpty(kid):
            r["result"]=False
            r["msg"] ="invalid kid" 
            return jsonify(r)
        #todo 2: check appid
        appid = request.args.get('appid','') 
        if __Is_NoneOrEmpty(appid):
            r["result"]=False
            r["msg"] ="invalid app" 
            return jsonify(r)
        #todo 3: get status,errcode whith no check
        status = request.args.get('status','')
        errcode = request.args.get('errorcode','')
        #todo 4: init starttime and endtime
        d = datetime.now()
        init_stime = datetime.strptime(d.strftime('%Y-%m-%d') + ' 00:00:00','%Y-%m-%d %H:%M:%S')
        init_etime = init_stime + timedelta(days = 1) 
        #todo 5: get starttime and endtime by init value
        str_stime = request.args.get('stime',init_stime.strftime('%Y-%m-%d %H:%M:%S'))
        str_etime = request.args.get('etime',init_etime.strftime('%Y-%m-%d %H:%M:%S'))
        st = datetime.strptime(str_stime,'%Y-%m-%d %H:%M:%S')
        et = datetime.strptime(str_etime,'%Y-%m-%d %H:%M:%S')
        page = int(request.args.get('page','1')) 
        print "--------------query his_data params--------------- "
        print "appid:%s" % appid
        print "kid:%s" % kid
        print "status:%s" % status
        print "errorcode:%s" % errcode
        print "starttime:%s" % st.strftime('%Y-%m-%d %H:%M:%S')
        print "endtime:%s" % et.strftime('%Y-%m-%d %H:%M:%S')
        print "page:%s" % str(page)
        print "----------------end-----------------------------------"
        #todo 6: get page and default value 1
        q = __build_hisdata_query(appid,kid,status,errcode,st,et)

        data_list = []
        pdatas = q.paginate(page,PER_PAGE,False)
        #print type(pdatas)
        #print '--------------------------------------------------------'
        #for p in dir(pdatas):
        #    print p
        #print pdatas.pages

        #if type(pdatas).__str__() == "404: Not Found":
        #    print "get 404 not found data."
        #    data_list = []
        #else:
        data_list = pdatas.items
        print "---show query datas.---"
        print pdatas.items 

        etime = datetime.now()
        r["data"]=data_list
        r["len"]=len(data_list)
        r["page"] = page
        r["pages"] = pdatas.pages
        r["time"]=(etime-stime).microseconds
    except Exception,e:
        print e
        r["data"]=[]
        r["len"]= 0
        r["page"]= 1
        r["pages"] = 0
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


'''
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

def import_hisdata():
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

        his_data = models.his_data()
        his_data._id = appid + ":" + kid
        his_data.appid = appid
        his_data.kid = kid
        his_data.time = time
        his_data.data = content
        his_data.save()

        etime = datetime.now()
        r["time"]=(etime-stime).microseconds

    except Exception, e:
        print e
        r["time"]=(datetime.now()-stime).microseconds
        r["result"]=False
        r["msg"]=e

    return jsonify(r)

def get_his_datecount(date):
    stime = datetime.now()
    r = get_result()
    try:
        print date 
        print request.args.items().__str__()

        appid = request.args.get('appid','unknow app') 
        if appid == 'unknow app':
            r["result"]=False
            r["msg"] ="unknow app" 
            return jsonify(r)

        #d = datetime.now()
        #st = datetime.strptime(d.strftime('%Y-%m-%d') + ' 00:00:00','%Y-%m-%d %H:%M:%S')
        #et = st + timedelta(days = 1)
        #init_date = d.strftime('%Y-%m-%d') 
        str_sdate = date + ' 00:00:00'
        print "str_sdate:%s" % (str_sdate)
        date_ok = False 
        try:
            st = datetime.strptime(str_sdate,'%Y-%m-%d %H:%M:%S')
            et = st + timedelta(days = 1)
            date_ok = True
        except Exception,e:
            print e
            date_ok = False

        if date_ok == False:
            r["result"]=False
            r["msg"] ="Invalid date " 
            return jsonify(r)

        print st
        print et
        c = models.His_data.objects.filter(appid=appid,time__gte=st,time__lt=et).count()
        print c 
        print '--------------------------------------------------------'

        etime = datetime.now()
        r["data"]=c
        r["len"]=1
        r["time"]=(etime-stime).microseconds
    except Exception,e:
        print e
        r["data"]= 0
        r["len"]= 0
        r["time"]=(datetime.now()-stime).microseconds
        r["result"]=False
        r["msg"] = e

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

def get_all_last_data(appid):
    stime = datetime.now()
    r = get_result()
    try:
        print appid 
        #datas = models.Last_data.objects.filter(appid=appid).all()
        #datas = db.getCollection(Last_data.kid,Last_data.status,Last_data.errcode).filter(appid=appid).all()
        datas = models.Last_data.objects.filter(appid=appid).only("kid","status","errcode").all()
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

        status = request.args.get('status','')
        errorcode = request.args.get('errorcode','')

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

        if status == '' and errorcode == '':
            datas = models.his_data.objects.filter(appid=appid,kid=kid,time__gte=st,time__lt=et).order_by('-time')
        elif status != '' and errorcode == '':
            datas = models.his_data.objects.filter(appid=appid,kid=kid,status=status,time__gte=st,time__lt=et).order_by('-time')
        elif status == '' and errorcode != '':
            datas = models.is_data.objects.filter(appid=appid,kid=kid,errorcode=errorcode,time__gte=st,time__lt=et).order_by('-time')
        elif status != '' and errorcode != '':
            datas = models.his_data.objects.filter(appid=appid,kid=kid,status=status,errorcode=errorcode,time__gte=st,time__lt=et).order_by('-time')

        print type(datas)
        data_list = []
        pdatas = datas.paginate(page,PER_PAGE,False)
        #print type(pdatas)
        #print '--------------------------------------------------------'
        #for p in dir(pdatas):
        #    print p
        #print pdatas.pages

        #if type(pdatas).__str__() == "404: Not Found":
        #    print "get 404 not found data."
        #    data_list = []
        #else:
        data_list = pdatas.items

        etime = datetime.now()
        r["data"]=data_list
        r["len"]=len(data_list)
        r["page"] = page
        r["pages"] = pdatas.pages
        r["time"]=(etime-stime).microseconds
    except Exception,e:
        print e
        r["data"]=[]
        r["len"]= 0
        r["page"]= 1
        r["pages"] = 0
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
'''

