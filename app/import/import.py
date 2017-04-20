#!/usr/bin/evn python
# -*- coding:utf-8 -*-

import requests 
from datetime import datetime,timedelta
from flask import json
import pymssql

import_post_url = "http://127.0.0.1:4000/api/1.0/import_hisdata"
date_count_url = "http://127.0.0.1:4000/api/1.0/get_his_datecount"
headers = {'content-type':'application/json',"Accept":"application/json"}
appid = '03110001'
db_host = '192.168.2.23'
db_user = 'hb'
db_pass = 'hb123456'
db_name = 'hb.sftong.net'

def save(appid,baid,lng,lat,acc,gt,ct,elev,iscross,status,errcode,addr,glng,glat,gaddr,ID,loctype,loc_source,leave):
    r = False
    data = {'ArchivesID':str(baid),'Lng':str(lng),'Lat':str(lat),'Accuracy':str(acc),'GPSTime':\
            gt.strftime('%Y-%m-%d %H:%M:%S'),\
            'CreateTime':ct.strftime('%Y-%m-%d %H:%M:%S'),'Elevation':str(elev),'IsCrossBorder':str(iscross),'Status':str(status),'Note':str(errcode),\
            'Address':addr,'googleLng':str(glng),'googleLat':str(glat),\
            'googleAddress':gaddr,'ID':str(ID),'LocationType':loctype,\
            'LocationSource':loc_source,'LeaveStatus':str(leave)}

    values={'appid':'03110001','kid':str(baid),'status':str(status),'errcode':errcode,'loctype':loctype,\
            'locsource':loc_source,'time':ct.strftime('%Y-%m-%d %H:%M:%S'),'data':json.dumps(data)}
    #print 'url:' + url
    #print 'data:' + json.dumps(values)
    #print 'headers:' + json.dumps(headers)
    r = requests.post(import_post_url,json.dumps(values),headers)
    #print r.url
    #print r.text
    try:
        result = json.loads(r.text)
        if result["result"] == True:
            r = True 
        else:
            r = False 
    except Exception,e:
        print e
        r = False 
    return r

def read_source_data(tablename):
    _r = [] 
    try:
        conn = pymssql.connect(db_host,db_user,db_pass,db_name)
        cur = conn.cursor()
        sql = "select * from " + tablename
        cur.execute(sql)
        _r = cur.fetchall()
        #print _r
        conn.close()
    except Exception,e:
        print e
        _r =[] 
    return _r 

def read_source_table_rows(tablename):
    _r = 0
    try:
        conn = pymssql.connect(db_host,db_user,db_pass,db_name)
        cur = conn.cursor()
        sql = "select count(*) from " + tablename
        cur.execute(sql)
        resList = cur.fetchall()
        #print resList
        _r = resList[0][0]
        conn.close()
    except Exception,e:
        print e
        _r = 0
    return _r 

def read_Destion_date_rows(date):
    _r = 0
    _url = date_count_url + "/" + date.strftime("%Y-%m-%d")
    param = {"appid":appid}
    #print _url
    ret = requests.get(_url,params=param)
    #print ret.url
    #print ret.text
    try:
        result = json.loads(ret.text)
        if result["result"] == True:
            _r = int(result["data"]) 
        else:
            _r = 0 
    except Exception,e:
        print e
        _r = 0 
    return _r

def import_data(tablename,date):
    print "import table:%s date:%s. please wait..." % (t[0],t[1])
    source_rows = read_source_table_rows(tablename)
    print "  --Source table:%s data rows:%d" % (tablename,source_rows)
    dest_date_rows = read_Destion_date_rows(date)
    print "  --Destion Date: %s data rows:%d" % (date.strftime("%Y-%m-%d"),dest_date_rows)
    if source_rows == 0:
        print "  --Source table: %s data rows is 0 jump it." % (tablename)
    else:
        if dest_date_rows <= 0 :
            print "import data..." 
            data = read_source_data(tablename)
            for it in data:
                save(appid,it[1],it[2],it[3],it[4],it[5],it[6],it[7],it[8],it[9],it[10],\
                        it[11],it[12],it[13],it[14],it[0],it[15],it[16],it[17])
        else:
            while True:
                print "  --Some data is at Date,please choose Append or Jump?"
                c = raw_input("  --[A]ppend,[J]ump?:")
                if c == "j" or c == "J" or c == "":
                    print "  --User do jump"
                    break
                elif c == "a" or c == "A":
                    print "  --Append import"
                    data = read_source_data(tablename)
                    for it in data:
                        save(appid,it[1],it[2],it[3],it[4],it[5],it[6],it[7],it[8],it[9],it[10],\
                                it[11],it[12],it[13],it[14],it[0],it[15],it[16],it[17])
                    break

if __name__ == "__main__":
    print "-------------------welcome to import GPS_HistoryPosition--------------------"
    print "Option:"
    print "1. if you wang to import day table,like  GPS_HistoryPosition20161001."
    print "2. if you wnag to import current table,like GPS_HistoryPosition"
    tables = []
    start_str_date = ""
    end_str_date = ""
    cnum = raw_input("please Enter the Num 1 or 2:")
    if cnum == "1":
        while True:
            start_str_date = raw_input("please Enter Start date like 2016-10-01:")
            str_sdate = start_str_date + ' 00:00:00'
            date_ok = False 
            try:
                st = datetime.strptime(str_sdate,'%Y-%m-%d %H:%M:%S')
                date_ok = True
            except Exception,e:
                print e
                date_ok = False

            if date_ok == False:
                print "Start Date Invalid. Please retry agin."
                continue


            end_str_date = raw_input("please Enter End date like 2016-10-31:")
            str_edate = end_str_date + ' 00:00:00'
            date_ok = False 
            try:
                et = datetime.strptime(str_edate,'%Y-%m-%d %H:%M:%S')
                date_ok = True
            except Exception,e:
                print e
                date_ok = False

            if date_ok == False:
                print "End date Invalid. Please retry agin."
                continue

            if et < st:
                print "End date  >= Start date."
                continue

            td = st
            while td <= et:
                tn = ("GPS_HistoryPosition" + td.strftime('%Y%m%d'),td)
                tables.append(tn)
                td = td + timedelta(days = 1)

            print "all talbes:%d" % (len(tables))
            break

    elif cnum == "2":
        tn = ("GPS_HistoryPosition",datetime.now)
        tables.append(tn)

    print "---------begin to import data,all tables:%d---------------" % (len(tables))
    for t in tables:
        # code...
        #print " import table:%s date:%s. please wait..." % (t[0],t[1])
        import_data(t[0],t[1])


    print "all tables data is processed."


