#!/usr/bin/env python
# -*- coding:utf-8 -*-

from datetime import datetime
import json
import pytest
from loc_data import db 
from main.models import app as modelapp,last_data,his_data
from main.CJsonEncoder import CJsonEncoder

@pytest.mark.usefixtures('client_class')
class TestApp(object):

    counter = 1
    accid = "0311000001"
    aids = [84971,84972] 
    kid = 84971
    lng = 115.152263
    lat = 38.854287
    addr = '顺平县永平路'
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
            "locsource":'HB_MALS_BNET'},\
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
        d = datetime.now()
        val = {'ArchivesID':str(self.kid),'Lng':self.lng,'Lat':self.lat,'Accuracy':0,\
                'GPSTime':d,'CreateTime':d,'Elevation':0,\
                'IsCrossBorder':0,'Status':self.status,'Note':self.errcode,\
                'Address':'河北省保定市顺平县永平路',\
                'googleLng':self.lng,'googleLat':self.lat,\
                'googleAddress':'河北省保定市顺平县永平路',\
                'ID':self.counter,'LocationType':self.loctype,\
                'LocationSource':self.locsource,'LeaveStatus':0}

        pd = {'appid':self.accid,'kid':str(self.kid),'status':str(self.status),\
                'errcode':self.errcode,'loctype':self.loctype,\
                'locsource':self.locsource,'time':d,'data':json.dumps(val,cls=CJsonEncoder)}
        resp = self.client.post('/api/1.0/loc_data',\
                data = json.dumps(pd,cls=CJsonEncoder),
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
        assert resp.json['len'] == 2
        assert t[0]['kid'] == resp.json['data'][0]['kid'] or t[0]['kid'] == resp.json['data'][1]['kid']
        assert t[1]['kid'] == resp.json['data'][0]['kid'] or t[1]['kid'] == resp.json['data'][1]['kid']



