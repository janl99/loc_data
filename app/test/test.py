#!/usr/bin/env python
# -*- coding:utf-8 -*-

import requests 
from datetime import datetime,timedelta
from flask import json

url = "http://127.0.0.1:4000/api/1.0/loc_data"
headers = {'content-type':'application/json',"Accept":"application/json"}
c_count = 0
f_count = 0
stime = datetime.now()
td = datetime.now()
d = td
lng = 115.152263
lat = 38.854287
aid = 84971 
id = 1
appid = "0311000001"
for kid in range(1,2):
    # code...
    d = td + timedelta(minutes=30) 
    data = {'ArchivesID':str(aid),'Lng':lng,'Lat':lat,'Accuracy':0,'GPSTime':\
             d.strftime('%Y-%m-%d %H:%M:%S'),\
            'CreateTime':d.strftime('%Y-%m-%d %H:%M:%S'),'Elevation':0,'IsCrossBorder':0,'Status':1,'Note':'ok',\
            'Address':'河北省保定市顺平县永平路','googleLng':lng,'googleLat':lat,\
            'googleAddress':'河北省保定市顺平县永平路','ID':id + kid,'LocationType':'Manual',\
            'LocationSource':'HB_MALS_BNET','LeaveStatus':0}

    values={'appid':appid,'kid':str(aid),'status':str(1),'errcode':'','loctype':'Manual',\
            'locsource':'HB_MALS_BNET','time':d.strftime('%Y-%m-%d %H:%M:%S'),'data':json.dumps(data)}
    print 'url:' + url
    print 'data:' + json.dumps(values)
    print 'headers:' + json.dumps(headers)
    r = requests.post(url,json.dumps(values),headers)
    print r.text
    try:
        result = json.loads(r.text)
        if result["result"] == True:
            c_count =  c_count + 1
        else:
            f_count =  f_count + 1
    except:
        f_count = f_count + 1

etime = datetime.now()
ts = (etime - stime).seconds
print "Test Result:  post complated,%d ; post failed, %d ; estime,%d seconds." % (c_count,f_count,ts)  
