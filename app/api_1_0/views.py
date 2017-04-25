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
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

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
                    filter(appid==appid,kid==kid,his_data.time.between(st,et)).\
                    order_by("time")
            print q
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
        print "query with status and without errcode"
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
        #val = request.get_data()
        #print type(val)
        #print val
        data = json.loads(request.get_data())
        #print type(data)
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
        #todo3: build redis key  
        rediskey = __get_redis_Key(appid,kid)
        #todo4: build his_data entity 
        hdata = his_data()
        hdata.appid = appid
        hdata.kid = kid
        hdata.time = time
        hdata.status = status
        hdata.errcode = errcode
        hdata.loctype = loctype
        hdata.locsource = locsource
        hdata.data = content
        #todo5: save his_data entity to redis
        print "----------hdata serialize ...------------"
        redis_data = json.dumps(hdata)
        print redis_data
        th = json.loads(redis_data)
        print th
        print "-----------------------------------------"
        redis.set(rediskey,redis_data)
        #todo6: save hist_data to mysql database.
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
        print "---------last data param----------------"
        print kids
        print request.args.items().__str__()
        print "----------------------------------------"
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
            print "--------------redis get data----------"
            print type(d)
            print d
            print "---------------json.locads------------"
            i = json.loads(d)
            print type(i)
            print i
            print "---------------build his_data----------"
            td = his_data() 
            print type(td)
            print td.appid
            print i["appid"]
            print type(i["time"])
            print i["time"]

            td.id = 0
            td.appid = i["appid"]
            td.kid = i["kid"]
            td.time = i["time"] 
            td.status =i["status"] 
            td.errcode = i["errcode"]
            td.loctype = i["loctype"]
            td.locsource = i["locsource"]
            td.data = i["data"] 
            print type(td)
            print td
            print "-------------------------------------------"
            data.append(td)
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
        data_list = pdatas.items
        print "---show query datas.---"
        print data_list 
        datalen = len(data_list)
        print type(data_list[0])
        print dir(data_list[0])
        print "---------------------------"
        print data_list[0].id
        print data_list[0].appid
        print data_list[0].kid
        print data_list[0].time
        print data_list[0].status
        print data_list[0].errcode
        print data_list[0].loctype
        print data_list[0].locsource
        print data_list[0].data
        print "---------------------------"
        print type(data_list[0].appid)
        print type(data_list[0].data)
        print type(data_list[0].time)
        etime = datetime.now()
        r["data"]= data_list
        r["len"]= datalen
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



