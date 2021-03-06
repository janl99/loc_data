#!/usr/bin/env python
# -*- coding:utf-8 -*-

import datetime, hashlib, urllib
from flask import url_for
#import markdown2, bleach
from loc_data import db,ma,create_app
from loc_data.config import System_Settings
import Queue
import threading
import time

class Singleton(object):
    '''单例类基类'''
    def __new__(cls,*args,**kw):
        if not hasattr(cls,'_instance'):
            old = super(Singleton,cls)
            cls._instance=old.__new__(cls,*args,**kw)
        return cls._instance

class DataCacheSaver(Singleton):
    """
    批量数据导入时，批量缓存
    """ 
    __isinited = False
    __q = None
    __batch_size = 10000
    __savethreading = None
    __app = None
    mutex = None
    def __init__(self,app):
        '''单根类，数据源初始化'''
        if not self.__isinited :
            self.__q = Queue.Queue()
            self.__batch_size = 10000
            self.mutex = threading.Lock()
            self.__app = app
            self.__isinited = True

    def run(self):
        print datetime.datetime.now()
        try:
            if not self.__q.empty():
                self.mutex.acquire()
                da = []
                for i in xrange(self.__batch_size):
                    if self.__q.empty():
                        break
                    h = self.__q.get()
                    #print h
                    da.append(h)
                self.mutex.release()
                with app.app_context():
                    r = db.session.execute(his_data.__table__.insert(),da)
                    print "bluck insert rows:%d" % r.rowcount
                    db.session.commit()
                    print "savethreading is end."
            else:
                time.sleep(5)
        except Exception,e:
            print e

    def __start_save(self):
        print "__start save...."
        if self.__savethreading == None:
           self.__start_save_thread() 
        elif self.__savethreading.is_alive:
            return
        else:
            self.__start_save_thread()

    def __start_save_thread(self):
        try:
            print "init threading..."
            self.__savethreading = threading.Thread(target=DataCacheSever.run,args=(self,))
            print "set threading daemon."
            self.__savethreading.setDaemon(True)
            print "start threading."
            self.__savethreading.start()
        except Exception,e:
            print e


    def save(self,his_data):
        try:
            self.__q.put(his_data)
            print "queue len:%s"  % str(self.__q.qsize())
            self.__start_save()
        except Exception,e:
            print e

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

    def __json__(self):
        return ['id','appid','appname','token']

class last_data(db.Model):
    """
    最后状态数据，用于按条件查询数据
    """
    id =        db.Column(db.Integer,primary_key=True)
    appid =     db.Column(db.String(16))
    kid =       db.Column(db.String(16))
    time =      db.Column(db.DateTime)
    status =    db.Column(db.String(16))
    errcode =   db.Column(db.String(16))
    loctype =   db.Column(db.String(16))
    locsource = db.Column(db.String(16))

    def __unicode__(self):
        return self.appid + '-' + self.kid + '-' + self.data_time

    def __repr__(self):
        return "<his_data %d>" % self.id

    def __json__(self):
        return ['id','appid','kid','time','status','errcode','loctype','locsource']

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

    def __json__(self):
        return ['id','appid','kid','time','status','errcode','loctype','locsource','data']

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
    success_data =  db.Column(db.String(1000)) 
    # json data like:
    # {loctype:{auto:124,manual:38},
    #  locsource:{HB_MALS:{130:12,104:9,105:2},HB_Bnet_MALS:{130:12,104:9,105:2},Cli_Device:{}}}
    failed_data =  db.Column(db.String(1000))
    #def save(self,*args,**kwargs):
    #    return super(loc_statistics,self).save(*args,**kwargs)

    def __unicode__(self):
        return self._id

    def __json__(self):
        return ['id','appid','appcount','success_data','failed_data']

class his_data_schema(ma.ModelSchema):
    class Meta:
        model = his_data



