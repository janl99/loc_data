#!/usr/bin/env python
# -*- coding:utf-8 -*-

from urlparse import urljoin
from datetime import datetime,timedelta,time,date
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
from main.models import his_data,his_data_schema 
from loc_data import db,redis,ma
from sqlalchemy import text

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

#page size
PER_PAGE = System_Settings['pagination'].get('per_page', 10)
#onec query, starttime and endtime must be less then max_days_once
MAX_DAYS_ONCE = System_Settings['query_setting'].get('max_days_once',31)
#query starttime must  between  18 month nearst  30 * 18 month = 540 days
MAX_DAYS_BEFORE_TODAY = System_Settings['query_setting'].get('max_days_before_today',540)
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
    print "---build suffix list---"
    r = []
    curr = datetime.now()
    if st < curr and curr < et: #same day
        print " now is between st and et"
        r.append(datetime.now().strftime('%Y%m%d'))

    for i in range(delta.days):
        r.append((st + datetime.timedelta(i)).strftime('%Y%m%d'))
    print "--build date list end.---"
    return r

def __build_his_data_table_query(appid,kid,st,et,status,errcode,loctype,locsource,isquerytoday):
    if isquerytoday:
        q = db.session.query(his_data).filter(his_data.id == 0)
    else:
        q = db.session.query(his_data).filter(appid==appid,kid==kid,his_data.time.between(st,et))
        if not __Is_NoneOrEmpty(status):
            q.filter(status==status)
        if not __Is_NoneOrEmpty(errcode):
            q.filter(errcode==errcode)
        if not __Is_NoneOrEmpty(loctype):
            q.filter(loctype==loctype)
        if not __Is_NoneOrEmpty(locsource==locsource):
            q.filter(locsource==locsource)
    q.order_by("time")
    return q

def __build_his_data_suffixtable_query(appid,kid,st,et,status,errcode,loctype,locsource,suffix):
    te = his_data.model(suffix)
    q = db.session.query(te).filter(appid==appid,kid==kid,te.time.between(st,et))
    if not __Is_NoneOrEmpty(status):
        q.filter(status==status)
    if not __Is_NoneOrEmpty(errcode):
        q.filter(errcode==errcode)
    if not __Is_NoneOrEmpty(loctype):
        q.filter(loctype==loctype)
    if not __Is_NoneOrEmpty(locsource==locsource):
        q.filter(locsource==locsource)
    return q

def __build_hisdata_query(appid,kid,st,et,status,errcode,loctype,locsource):
    print "-----------start build query------------------------"
    is_query_his_data = False
    dl = __build_date_list(st,et)
    print dl
    todaysuffix = datetime.now().strftime('%Y%m%d')
    print todaysuffix
    if todaysuffix in dl:
        print "query include today table."
        dl.remove(todaysuffix)
    q = __build_his_data_table_query(appid,kid,st,et,status,errcode,loctype,locsource,is_query_his_data)
    print q
    for suffix in dl:
        tq = __build_his_data_suffixtable_query(appid,kid,st,et,status,errcode,loctype,locsource,suffix) 
        q.union(tq)
        print "suffix:%s" % suffix 
        print q
    return q
    print "----------------build query end-----------------------"

def __loc_data_check(his_data):
    """
    loc_data.postdata check 
    if all passed  return true else return false
    """
    r = __get_result()
    #todo1: check appid,kid
    if __Is_NoneOrEmpty(his_data.appid):
        r["result"] = False
        r["msg"] = "invalid appid."
        return r
    if __Is_NoneOrEmpty(his_data.kid):
        r["result"] = False
        r["msg"] = "invalid kid."
        return r
    #todo2: check appid is allowed.
    if not __Check_AppidAllowed(his_data.appid):
        r["result"] = False
        r["msg"] = "appid is not allowed."
        return r

    return r

def __last_data_check(kids,appid):
    """
    last_data param check
    if no kid in kids or appid invalid return false else true
    """
    r = __get_result()
    if __Is_NoneOrEmpty(appid):
        r["result"]=False
        r["msg"] ="invalid appid" 
        return jsonify(r)
    if __Is_NoneOrEmpty(appid):
        r["result"] = False
        r["msg"] = "appid is not allowed."
        return r
    ta = kids.split(',')
    if len(ta) <= 0:
        r["result"] = False
        r["msg"] = "invalid kids."
        return r

    return r

def __h_data_check(kid,appid):
    """
    h_data query param check 
    if all passed return true else false
    """
    r = __get_result()
    #todo1: check appid,kid
    if __Is_NoneOrEmpty(kid):
        r["result"] = False
        r["msg"] = "invalid kid."
        return r
    if __Is_NoneOrEmpty(appid):
        r["result"] = False
        r["msg"] = "invalid appid."
        return r
    #todo2: check appid is allowed.
    if not __Check_AppidAllowed(his_data.appid):
        r["result"] = False
        r["msg"] = "appid is not allowed."
        return r

    return r

def __h_data_check_time(stime,etime):
    """
    check stime and etime
    empty check: 
    when stime etime both empty then set to default val st = today + min,et = today + max 
    when stime or etime is empty then return invalid time param   
    when strim  and etime both not empty then convert to datetime ,
    when convert failed then return invalid time param format must like:2017-04-25 00:00:00
    value check: 
    when et <= st then return invalid time param  must etime > stime 
    when (et - st).days > 31 then return invalid time param must (etime - sttime).days > 31 
    when (now - st).months >18 then return invalid time param only can get 18 months data nearst. 
    """
    r = __get_result()
    st = et = None
    print "-------------h_date stime and etime check----------------"
    print "stime:%s,etime:%s" %(stime,etime)
    print "stime type:%s" % type(stime)
    print "etime type;%s" % type(etime)
    if __Is_NoneOrEmpty(stime) and __Is_NoneOrEmpty(etime):
        print "both not set stime and etime"
        st = datetime.combine(datetime.now().date(),time.min)
        et = datetime.combine(datetime.now().date(),time.max) 
        return r,st,et

    if not __Is_NoneOrEmpty(stime) and not  __Is_NoneOrEmpty(etime): 
        print "both set stime and etime"
        try:
            st = datetime.strptime(stime,'%Y-%m-%d %H:%M:%S')
            et = datetime.strptime(etime,'%Y-%m-%d %H:%M:%S')
        except Exception,e:   
            print e 
            r["result"] = False
            r["msg"] = "invalid time param,format must like:2017-04-25 00:00:00"
            return r,st,et
    else: 
        print "not both set stime and etime"
        r["result"] = False
        r["msg"] = "invalid time param,must both set stime and etime or both not set stime and etime."
        return r,st,et
    if st == None or et == None:
        print "st == None or et == None"
        r["result"] = False
        r["msg"] = "invalid time param.param is None"
        return r,st,et
    if not isinstance(st,date) or not isinstance(et,date):
        print "not isinstance(st,date) or not isinstance(et,date)"
        r["result"] = False
        r["msg"] = "invalid time param. parm is not datetime"
        return r,st,et
    if et <= st :
        print "et <= st"
        r["result"] = False
        r["msg"] = "invalid time param. must etime > stime"
        return r,st,et
    if (et - st).days > MAX_DAYS_ONCE:
        print "(et - st).days > 31: %d" % (et - st).days
        r["result"] = False
        r["msg"] = "invalid time param. must (etime - stime).days <= 31"
        return r,st,et
    print type(datetime.now())
    print type(st)
    if (datetime.now() - st).days > MAX_DAYS_BEFORE_TODAY :
        print "(datetime.now() - st).months > 18:%d" %  (datetime.now() - st).days
        r["result"] = False
        r["msg"] = "invalid time param. only can get 18 months data nearst"
        return r,st,et
    print "--------------h_data stime and etime check end----------------"
    return r,st,et

def loc_data():
    """
    receive post data and save. 
    1. set data val to redis for fast get. 
    2. save to mysql database for query sometime.
    """
    stime = datetime.now()
    r = __get_result() 
    try:
        print "todo1: get post data"
        val = request.get_data()
        schema = his_data_schema()
        print "todo2: deseariler his_data"
        h =  schema.loads(val).data
        print "todo3: data check"
        c = __loc_data_check(h)
        if not  c["result"]:
            return c
        print "todo4: build redis key"
        rediskey = __get_redis_Key(h.appid,h.kid)
        print "todo5: save his_data to redis"
        redis_data = schema.dumps(h).data
        redis.set(rediskey,redis_data)
        print "todo6: save hist_data to mysql database."
        h.id = None
        db.session.add(h)
        db.session.commit()
        print "todo7: update loc data statistics."
        __update_statistics(h.appid,h.status,h.errcode,h.loctype,h.locsource)
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
        print "todo 1: get query param and check" 
        appid = request.args.get('appid','') 
        c = __last_data_check(kids,appid)
        if not c["result"]:
            return c
        print "todo 2: loop get data by kids from redis"
        data = []
        for kid in kids.split(','):
            if __Is_NoneOrEmpty(kid):
                continue
            rediskey = __get_redis_Key(appid,kid)
            d = redis.get(rediskey)
            schema = his_data_schema()
            h = schema.loads(d).data
            data.append(h)
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
    """
    query his_data by kid,appid,stime,etime,status,errcode,loctype,locsoure,page 
    default page =1 
    page size configed = 10
    stime,etime must be both set or both not set,if both not set,default query today data.
    """
    stime = datetime.now()
    r = __get_result()
    try:
        print "todo 1: check kid and appid"
        appid = request.args.get('appid','') 
        c = __h_data_check(kid,appid)
        if not c["result"]:
            return jsonify(c) 
        print "todo 2: get status,errcode whith no check"
        status = request.args.get('status','')
        errcode = request.args.get('errorcode','')
        print "todo 3: get stime and etime"
        s = request.args.get('stime','')
        e = request.args.get('etime','')
        ct,st,et = __h_data_check_time(s,e)
        if not ct["result"]:
            return jsonify(ct)
        print "todo 4: get loctype,locsource"
        loctype =  request.args.get('loctype','')
        locsource = request.args.get('locsource','')
        print "todo 5 get page param"
        page = int(request.args.get('page','1')) 
        print "todo 6: build query" 
        q = __build_hisdata_query(appid,kid,st,et,status,errcode,loctype,locsource)
        data_list = []
        print "todo 7: get data by page"
        pdatas = q.paginate(page,PER_PAGE,False)
        data_list = pdatas.items
        etime = datetime.now()
        r["data"]= data_list
        r["len"]= len(data_list) 
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
    """
    loc_data statistics.
    """
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



