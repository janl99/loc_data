#!/usr/bin/env python
# -*- coding:utf-8 -*-

import threading
import datetime
import Queue
from BaseSingletonClass import Singleton
from loc_data import db,redis
from flask import current_app
from .models import his_data,last_data,his_data_schema
from .Statistics import Statistics as _statis
import time


class LocDataSaver(Singleton):
    """
    批量数据导入时，批量缓存
    """ 
    #redis last_data key profix
    LAST_LOCATION_REDIS_KEY_PREFIX = "LL"
    __isinited = False
    __q = None
    __batch_size = 100
    __savethreading = None
    __app = None
    __info_last_active_time = None
    mutex = threading.Lock()
    def __init__(self):
        '''单根类，数据源初始化'''
        self.mutex.acquire()
        if not self.__isinited :
            print "locdatasaver is init..."
            self.__q = Queue.Queue()
            self.__batch_size = 100
            self.__app = current_app._get_current_object() 
            self.__isinited = True
            self.__start_save()
        self.mutex.release()

    def run(self):
        while(True):
            print "start to save loc post data  %s" % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            self.__info_last_active_time  = datetime.datetime.now()
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
                    print "loc data queue len:%s"  % str(self.__q.qsize())
                    with self.__app.app_context():
                        r = db.session.execute(his_data.__table__.insert(),da)
                        db.session.commit()
                        print "loc data bluck insert rows:%d" % r.rowcount
                        for h in da:
                            schema = his_data_schema()
                            rediskey = self.__get_redis_Key(h['appid'],h['kid'])
                            redis_data = schema.dumps(h).data
                            redis.set(rediskey,redis_data)
                            #print "set redis data"
                            t = datetime.datetime.strptime(h['time'],'%Y-%m-%dT%H:%M:%S.%f')
                            self.__update_last_data(h['appid'],h['kid'],h['status'],h['errcode'],h['loctype'],h['locsource'],t)
                            #print "update last data."
                            self.__update_statistics(t,h['appid'],h['kid'],h['status'],h['errcode'],h['loctype'],h['locsource'])
                        print "loc data bluck save is end."
                else:
                    time.sleep(5)
            except Exception,e:
                print e

    def __get_redis_Key(self,appid,kid):
        """
        build redis key
        """
        return self.LAST_LOCATION_REDIS_KEY_PREFIX + ":" + appid.strip() + ":" + kid.strip()

    def __update_last_data(self,appid,kid,status,errcode,loctype,locsource,time):
        """
        get last_data by appid,kid
        when exist update status,errcode,loctype,locsource
        when not exit insert last_data
        """
        #print "updata last_data by:appid=%s,kid=%s,status=%s,errcode=%s,loctype=%s,locsource=%s" \
        #        % (appid,kid,status,errcode,loctype,locsource)
        try:
            with self.__app.app_context():
                l = db.session.query(last_data).filter(last_data.appid==appid,last_data.kid==kid).first()
                if l is None:
                    l = last_data()
                    l.appid = appid
                    l.kid = kid
                l.status = status
                l.errcode = errcode
                l.loctype = loctype
                l.locsource = locsource
                l.time = time
                db.session.add(l)
                db.session.commit()
        except Exception, e:
            print e

    def __update_statistics(self,time,appid,kid,status,errcode,loctype,locsource):
        """
        update loc data statictics data.
        """
        _statis().count(time,appid,kid,status,errcode,loctype,locsource) 

    def __start_save(self):
        #print "__start save...."
        if self.__savethreading is None:
           self.__start_save_thread() 
        elif self.__savethreading.is_alive:
            return
        else:
            self.__start_save_thread()

    def __start_save_thread(self):
        try:
            print "init loc saver threading..."
            self.__savethreading = threading.Thread(target=LocDataSaver.run,args=(self,))
            print "set loc saver threading daemon."
            self.__savethreading.setDaemon(True)
            print "start loc saver threading."
            self.__savethreading.start()
        except Exception,e:
            print e

    def save(self,his_data):
        try:
            self.__q.put(his_data)

        except Exception,e:
            print e

    def showinfo(self):
        r = {}
        r['id'] = id(self)
        r['last_active_time']= self.__info_last_active_time 
        r['queuelen'] = self.__q.qsize()
        return r


