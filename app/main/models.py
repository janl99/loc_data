#!/usr/bin/env python
# -*- coding:utf-8 -*-

import datetime, hashlib, urllib
from flask import url_for
#import markdown2, bleach
from loc_data import db
from loc_data.config import System_Settings

class App(db.Document):
    _id = db.StringField(max_length=8,required=True,unique=True)
    appname = db.StringField(max_length=32,required=True)

    def save(self,*args,**kwargs):
        return super(App,self).save(*args,**kwargs)

    def __unicode__(self):
        return self.appid + '-' + self.appname


class Last_data(db.Document):
    _id = db.StringField(max_length=24,required=True,unique=True)
    appid = db.StringField(max_length=8,default='unknow app',required=True)
    kid = db.StringField(max_length=16,required=True)
    time = db.DateTimeField()
    data = db.StringField(required=True)

    def save(self,*args,**kwargs):
        return super(Last_data,self).save(*args,**kwargs)

    def __unicode__(self):
        return self.appid + '-' + self.kid

class His_data(db.Document):
    _id = db.StringField(max_length=24,required=True,unique=True)
    appid = db.StringField(max_length=8,default='unknow app',required=True)
    kid = db.StringField(max_length=16,required=True)
    time = db.DateTimeField()
    data = db.StringField(required=True)

    def save(self,*args,**kwargs):
        return super(Last_data,self).save(*args,**kwargs)

    def __unicode__(self):
        return self.appid + '-' + self.kid + '-' + self.data_time








