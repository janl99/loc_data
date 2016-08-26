#!/usr/bin/env python
# -*- coding:utf-8 -*-

import requests 
from datetime import datetime,timedelta
from flask import json

url = "http://127.0.0.1:5000/api/1.0/loc_data"
headers = {'content-type':'application/json',"Accept":"application/json"}
c_count = 0
f_count = 0
stime = datetime.now()
td = datetime.now()
d = td
for kid in range(1,101):
    # code...
    d = td + timedelta(minutes=30) 
    data = {'ArchivesID':str(2314),'Lng':115.152263,'Lat':38.854287,'Accuracy':0,'GPSTime':\
             d.strftime('%Y-%m-%d %H:%M:%S'),\
            'CreateTime':d.strftime('%Y-%m-%d %H:%M:%S'),'Elevation':0,'IsCrossBorder':1,'Status':1,'Note':'ok',\
            'Address':'河北省保定市顺平县永平路','googleLng':115.152263,'googleLat':38.854287,\
            'googleAddress':'河北省保定市顺平县永平路','ID':40629,'LocationType':'Manual',\
            'LocationSource':'HB_MALS_BNET','LeaveStatus':0}

    values={'appid':'03110001','kid':str(2314),'time':d.strftime('%Y-%m-%d %H:%M:%S'),'data':json.dumps(data)}
    r = requests.post(url,json.dumps(values),headers)
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
