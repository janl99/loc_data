#!/usr/bin/env python
# -*- coding:utf-8 -*-

import requests 
from flask import json

url = "http://127.0.0.1:5000/api/1.0/loc_data"
data = {'ArchivesID':45571,'Lng':115.152263,'Lat':38.854287,'Accuracy':0,'GPSTime':'2016-08-23 11:51:14.597',\
        'CreateTime':'2016-08-23 11:51:14.597','Elevation':0,'IsCrossBorder':1,'Status':1,'Note':'ok',\
        'Address':'河北省保定市顺平县永平路','googleLng':115.152263,'googleLat':38.854287,\
        'googleAddress':'河北省保定市顺平县永平路','ID':40629,'LocationType':'Manual',\
        'LocationSource':'HB_MALS_BNET','LeaveStatus':0}
print '----------------------------data-------------------------------'
print data

values={'appid':'03110001','kid':'32873','time':'2016-08-23 11:51:14.597','data':json.dumps(data)}
print '----------------------------values------------------------------'
print values

headers = {'content-type':'application/json',"Accept":"application/json"}
r = requests.post(url,json.dumps(values),headers)
print '----------------------------request.result-----------------------'
print r.status_code
print r.text
