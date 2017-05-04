#!/usr/bin/env python
# -*- coding:utf-8 -*-

from datetime import datetime,timedelta
import json
import pytest
from loc_data import db 
from main.models import app as modelapp,last_data,his_data
from main.CJsonEncoder import CJsonEncoder

@pytest.mark.usefixtures('client_class')
class TestApp(object):

    counter = 1
    accid = "0311000001"
    aids = [84971,84972,84973,84974,84975,84976,84977,84978,84979,84980,84981,84982] 
    kid = 84971
    lng = 115.152263
    lat = 38.854287
    addr = '顺平县永平路'
    d = datetime.now()
    status = 1
    errcode = 'ok'
    loctype = 'Auto'
    locsource = 'HB_MALS_BNET'
    params =[{"lng":115.152263,"lat":38.854287,"addr":'顺平县永平路',\
            "status":1,"errcode":'ok',"loctype":'Manual',\
            "locsource":'HB_MALS_BNET'},\
            {"lng":0,"lat":0,"addr":'',"status":0,"errcode":'130',\
            "loctype":'Manual',"locsource":'HB_MALS_BNET'},\
            {"lng":0,"lat":0,"addr":'',"status":0,"errcode":'147',\
            "loctype":'Manual',"locsource":'HB_MALS_BNET'},\
            {"lng":115.152263,"lat":38.854287,"addr":'顺平县永平路',\
            "status":1,"errcode":'ok',"loctype":'Auto',\
            "locsource":'HB_MALS_BNET'},\
            {"lng":0,"lat":0,"addr":'',"status":0,"errcode":'130',\
            "loctype":'Auto',"locsource":'HB_MALS_BNET'},\
            {"lng":0,"lat":0,"addr":'',"status":0,"errcode":'147',\
            "loctype":'Auto',"locsource":'HB_MALS_BNET'},\
            {"lng":115.152263,"lat":38.854287,"addr":'顺平县永平路',\
            "status":1,"errcode":'ok',"loctype":'Manual',\
            "locsource":'HB_MALS'},\
            {"lng":0,"lat":0,"addr":'',"status":0,"errcode":'130',\
            "loctype":'Manual',"locsource":'HB_MALS'},\
            {"lng":0,"lat":0,"addr":'',"status":0,"errcode":'147',\
            "loctype":'Manual',"locsource":'HB_MALS'},\
            {"lng":115.152263,"lat":38.854287,"addr":'顺平县永平路',\
            "status":1,"errcode":'ok',"loctype":'Auto',\
            "locsource":'HB_MALS'},\
            {"lng":0,"lat":0,"addr":'',"status":0,"errcode":'130',\
            "loctype":'Auto',"locsource":'HB_MALS'},\
            {"lng":0,"lat":0,"addr":'',"status":0,"errcode":'147',\
            "loctype":'Auto',"locsource":'HB_MALS'},]

    def test_api_v1_applist(self):
        a = modelapp(appid='0311000001',appname='testapp')
        db.session.add(a)
        db.session.commit()
        resp = self.client.get('/api/1.0/apps',\
                content_type='application/json')
        a1 = db.session.query(modelapp).get(1)
        assert resp.status_code == 200
        assert resp.json['len'] == 1
        assert resp.json['data'][0]['appid'] == a1.appid
        return resp.json['data'][0]['appname'] == a1.appname
        return a

    def test_api_v1_loc_data(self):
        val = {'ArchivesID':str(self.kid),'Lng':self.lng,'Lat':self.lat,'Accuracy':0,\
                'GPSTime':self.d,'CreateTime':self.d,'Elevation':0,\
                'IsCrossBorder':0,'Status':self.status,'Note':self.errcode,\
                'Address':'河北省保定市顺平县永平路',\
                'googleLng':self.lng,'googleLat':self.lat,\
                'googleAddress':'河北省保定市顺平县永平路',\
                'ID':self.counter,'LocationType':self.loctype,\
                'LocationSource':self.locsource,'LeaveStatus':0}

        pd = {'appid':self.accid,'kid':str(self.kid),'status':str(self.status),\
                'errcode':self.errcode,'loctype':self.loctype,\
                'locsource':self.locsource,'time':self.d,'data':json.dumps(val,cls=CJsonEncoder)}
        t = json.dumps(pd,cls=CJsonEncoder)
        #print t
        resp = self.client.post('/api/1.0/loc_data',\
                data = t,
                content_type='application/json')
        self.counter += 1
        assert resp.status_code == 200       
        return pd 

    def test_api_v1_l_data(self):
        t = []
        kids = ','.join(map(str,self.aids)) 
        for k in self.aids:
            self.kid = k
            l = self.test_api_v1_loc_data()
            t.append(l)
        resp = self.client.get('/api/1.0/l_data/'+kids+"?appid="+self.accid,\
                content_type='application/json') 
        assert resp.status_code == 200
        assert resp.json['len'] == len(self.aids) 

    def test_api_v1_q_data(self):
        t = []
        c = 0
        for k in self.aids:
            self.kid = k
            self.lng =  self.params[c]['lng']
            self.lat = self.params[c]['lat']
            self.addr = self.params[c]['addr']
            self.status = self.params[c]['status']
            self.errcode = self.params[c]['errcode']
            self.loctype = self.params[c]['loctype']
            self.locsource = self.params[c]['locsource']
            l = self.test_api_v1_loc_data()
            t.append(l)
            c+= 1
        # query by kid ,it's same by l_data
        resp = self.client.get('/api/1.0/q_data/'+self.accid + '?kid=' + str(self.kid))
        assert resp.status_code == 200
        assert resp.json['len'] == 1
        # query by status == 1 ,all location complated data 
        resp = self.client.get('/api/1.0/q_data/'+self.accid + '?status=1')
        assert resp.status_code == 200
        assert resp.json['len'] == 4 
        # query by status == 0 ,all loccation filed data
        resp = self.client.get('/api/1.0/q_data/'+self.accid + '?status=0')
        assert resp.status_code == 200
        assert resp.json['len'] == 8 
        # query by status == 0 and errcode = 130 
        resp = self.client.get('/api/1.0/q_data/'+self.accid + '?status=0&errcode=130')
        assert resp.status_code == 200
        assert resp.json['len'] ==4 
        # query by status == 1 and errcode = 147 ,will no result, all status == 1 then errcode will be ok  
        resp = self.client.get('/api/1.0/q_data/'+self.accid + '?status=1&errcode=147')
        assert resp.status_code == 200
        assert resp.json['len'] ==0
        #query  status==0 and errcode==147 and loctype == Auto
        resp = self.client.get('/api/1.0/q_data/'+self.accid + '?status=0&errcode=147&loctype=Auto')
        assert resp.status_code == 200
        assert resp.json['len'] ==2 
        #query status == 0 and errcode == 147 and loctype == Auto and locsource==HB_MALS_BNET
        resp = self.client.get('/api/1.0/q_data/'+self.accid + '?status=0&errcode=147&loctype=Auto&locsource=HB_MALS_BNET')
        assert resp.status_code == 200
        assert resp.json['len'] ==1

    def test_api_v1_h_data(self):
        t = []
        for k in self.params:
            self.lng =  k['lng']
            self.lat = k['lat']
            self.addr = k['addr']
            self.status = k['status']
            self.errcode = k['errcode']
            self.loctype = k['loctype']
            self.locsource = k['locsource']
            l = self.test_api_v1_loc_data()
            t.append(l)
        # query by kid ,
        # it's default time between today+min and today+max and page ==1 
        # page size = 10 
        # like: 2017-05-03 00:00:00 to 2017-05-03 23:59:59.999999 
        resp = self.client.get('/api/1.0/h_data/'+str(self.kid) + '?appid=' + self.accid)
        assert resp.status_code == 200
        print resp.json
        assert resp.json['len'] == 10 #page size is 10 default is page = 1

    def test_api_v1_m_data(self):
        t = []
        c = 0
        for k in self.params:
            self.d = datetime.now() + timedelta(days = -1 * c)
            self.lng =  k['lng']
            self.lat = k['lat']
            self.addr = k['addr']
            self.status = k['status']
            self.errcode = k['errcode']
            self.loctype = k['loctype']
            self.locsource = k['locsource']
            l = self.test_api_v1_loc_data()
            t.append(l)
            c += 1
        resp = self.client.get('/api/1.0/m_data')
        assert resp.status_code == 200
        print resp.json


