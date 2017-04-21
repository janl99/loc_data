#!/usr/bin/env python
# -*- coding:utf-8 -*-

import datetime, hashlib, urllib
from flask import url_for
#import markdown2, bleach
from loc_data import db
from loc_data.config import System_Settings


class app(db.Model):
    """
    标识应用平台的账户
    ---------------------------
    没有账户的应用平台，不能保存数据。
    暂没有实现鉴权，只做内部应用。token 留做以后扩展鉴权使用
    """
    id =        db.Column(db.Integer,primary_key=True)
    appid =     db.Column(db.String(16),unique=True)
    appname =   db.Column(db.String(32))
    token =     db.Column(db.String(64))

    #def save(self,*args,**kwargs):
    #    return super(app,self).save(*args,**kwargs)

    def __unicode__(self):
        return self.appid + '-' + self.appname


#class Last_data(db.Document):
#'''
#每个kid的最后位置数据
#--------------------------------------------
#准备放到redis数据库中，取消了类型实体定义。
#原则，接口收到的json串，直截取出标识，然后存入redis，返回时取出数据原封
#不动的返回,存什么，取的时候得什么。
#'''
#    _id = db.StringField(max_length=24,required=True,unique=True)
#    appid = db.StringField(max_length=10,default='unknow app',required=True)
#    kid = db.StringField(max_length=16,required=True)
#    time = db.DateTimeField()
#    status = db.StringField(max_length=10,required=True)
#    errcode = db.StringField(max_length=16,required=True)
#    loctype = db.StringField(max_length=16,required=True)
#    locsource = db.StringField(max_length=16,required=True)
#    data = db.StringField(required=True)
#
#    def save(self,*args,**kwargs):
#        return super(Last_data,self).save(*args,**kwargs)
#
#    def __unicode__(self):
#        return self.appid + '-' + self.kid

class his_data(db.Model):
    """ 
    历史位置数据
    ------------------------------------------------
    接收要保存的位置数据，从收到的json中提取了部分关键字段是检索条件用，如：
    appid,kid,time,status,errcode,loctype,locsource
    data中保存原封不动的字符串，将来返回也返回这个，以此来克服将来数据字段有
    变化时对表结构的引响。
    但是用做检索条件的字段，数据中一定要求有，否则不能存储并返回错误。
    """
    id =        db.Column(db.Integer,primary_key=True)
    appid =     db.Column(db.String(16))
    kid =       db.Column(db.String(16))
    time =      db.Column(db.DateTime)
    status =    db.Column(db.String(16))
    errcode =   db.Column(db.String(16))
    loctype =   db.Column(db.String(16))
    locsource = db.Column(db.String(16))
    data =      db.Column(db.Text)

    #def save(self,*args,**kwargs):
    #    return super(his_data,self).save(*args,**kwargs)

    def __unicode__(self):
        return self.appid + '-' + self.kid + '-' + self.data_time

    def __repr__(self):
        return "<his_data %d>" % self.id

    _mapper = {}

    @staticmethod
    def model(datesuffix=None):
        class_name = query_tablename = "his_data"
        if datesuffix is not None:
            class_name = query_tablename = "his_data%s" % datesuffix

        #print class_name
        #print query_tablename

        ModelClass = his_data._mapper.get(class_name,None)
        #print ModelClass

        if ModelClass is None:
            #print "ModelClass is None"
            ModelClass = type(class_name,(db.Model,),{
                '__module__':__name__,
                '__name__':class_name,
                '__tablename':query_tablename,
                'id': db.Column(db.Integer,primary_key=True),
                'appid':db.Column(db.String(16)),
                'kid':db.Column(db.String(16)),
                'time':db.Column(db.DateTime),
                'status':db.Column(db.String(16)),
                'errcode':db.Column(db.String(16)),
                'loctype':db.Column(db.String(16)),
                'locsource':db.Column(db.String(16)),
                'data':db.Column(db.Text),
            })
            his_data._mapper[class_name] = ModelClass

        cls = ModelClass
        return cls




class loc_statistics(db.Model):
    """
    接收到的历史位置数据统计
    ---------------------------------
    对接收到的历史位置数据进行统计
    app_count:appid 级别的统计，只要请求存储提合法的数据，app_count + 1
    sucess_data,failed_data: 定位成功,失败的数据统计,采用json格式保存,例如：
    success_data:{loctype:{auto:12834,manual:328},locsource:{HB_MALS:28123,HB_Bnet_MALS:39489,Cli_Device:3043904}}
    failed_data:{loctype:{auto:124,manual:38},
                 locsource:{HB_MALS:{130:12,104:9,105:2},
                            HB_Bnet_MALS:{130:12,104:9,105:2},
                            Cli_Device:{}
                           }
                }
    """
    id =            db.Column(db.Integer,primary_key=True)
    appid =         db.Column(db.String(16))
    date =          db.Column(db.String(20))
    app_count =     db.Column(db.Integer) 
    # json data like:
    # {loctype:{auto:12834,manual:328},locsource:{HB_MALS:28123,HB_Bnet_MALS:39489,Cli_Device:3043904}}
    success_data =  db.Column(db.String(200)) 
    # json data like:
    # {loctype:{auto:124,manual:38},
    #  locsource:{HB_MALS:{130:12,104:9,105:2},HB_Bnet_MALS:{130:12,104:9,105:2},Cli_Device:{}}}
    failed_data =  db.Column(db.String(200))

    #def save(self,*args,**kwargs):
    #    return super(loc_statistics,self).save(*args,**kwargs)

    def __unicode__(self):
        return self._id






