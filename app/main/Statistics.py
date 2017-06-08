#!/usr/bin/env python
# -*- coding:utf-8 -*-

import threading
import datetime
import Queue
import json
import copy
from BaseSingletonClass import Singleton
from loc_data import db
from flask import current_app
from .models import loc_statistics
import time

class Statistics(Singleton):
    """
    批量数据导入时，批量缓存
    """ 
    __isinited = False
    __savethreading = None
    __app = None
    __data = {}
    mutex = threading.Lock()
    def __init__(self):
        '''单根类，数据源初始化'''
        self.mutex.acquire()
        if not self.__isinited :
            print "loc data statistics is init..."
            self.__app = current_app._get_current_object() 
            self.__data = self.__doload()
            self.__isinited = True
        self.mutex.release()

    def run(self):
        while(True):
            try:
                #do save
                print "do statistics sava start: %s"  % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                self.__dosave()
                time.sleep(5*60)
            except Exception,e:
                print e

    def __doload(self):
        r = {}
        timestr = datetime.datetime.now().strftime('%Y-%m-%d')
        with self.__app.app_context():
            t = db.session.query(loc_statistics).filter(loc_statistics.date == timestr).all()
            if t is None or len(t) <= 0:
                return r
            for s in t:
                if not r.has_key(timestr):
                    r[timestr] = {}
                if not r[timestr].has_key(s.appid):
                    r[timestr][s.appid] = {}

                if not r[timestr][s.appid].has_key('allcount'):
                    if s.app_count > 0:
                        r[timestr][s.appid]['allcount'] = s.app_count 
                    else:
                        r[timestr][s.appid]['allcount'] = 0 

                if not r[timestr][s.appid].has_key('success'):
                    r[timestr][s.appid]['success'] = {}

                if not r[timestr][s.appid].has_key('failed'):
                    r[timestr][s.appid]['failed'] = {}

                if not s.success_data is None:
                    if len(s.success_data) > 2:
                        try:
                            r[timestr][s.appid]['success'] = json.loads(s.success_data)
                        except Exception,e:
                            print e
                            r[timestr][s.appid]['success'] = {}

                if not s.failed_data is None:
                    if len(s.failed_data) > 2:
                        try:
                            r[timestr][s.appid]['failed'] = json.loads(s.failed_data)
                        except Exception,e:
                            print e
                            r[timestr][s.appid]['failed'] = {}
        return r

    def __dosave(self):
        self.mutex.acquire()
        t = copy.deepcopy(self.__data)
        self.mutex.release()
        for kdate in t.keys():
            d = t[kdate]
            for kappid in d.keys():
                with self.__app.app_context():
                    s = db.session.query(loc_statistics).filter(loc_statistics.date == kdate,loc_statistics.appid == kappid).first()
                    if s is None:
                        s = loc_statistics()
                        s.id = None
                        s.date = kdate
                        s.appid = kappid
                    if d[kappid].has_key('allcount'):
                        s.app_count = d[kappid]['allcount']
                    if d[kappid].has_key('success'):
                        s.success_data = json.dumps(d[kappid]['success'])
                    if d[kappid].has_key('failed'):
                        s.failed_data = json.dumps(d[kappid]['failed'])
                    db.session.add(s)
                    db.session.commit()

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
            print "init statistics save threading..."
            self.__savethreading = threading.Thread(target=Statistics.run,args=(self,))
            print "set statistics save  threading daemon."
            self.__savethreading.setDaemon(True)
            print "start statistics sava threading."
            self.__savethreading.start()
        except Exception,e:
            print e

    def count(self,time,appid,kid,status,errcode,loctype,locsource):
        try:
            timestr = time.strftime('%Y-%m-%d')
            if not self.__data.has_key(timestr):
                self.__data[timestr] = {}

            if not self.__data[timestr].has_key(appid):
                self.__data[timestr][appid] = {}

            if not self.__data[timestr][appid].has_key('allcount'):
                self.__data[timestr][appid]['allcount'] = 1
            else:
                self.__data[timestr][appid]['allcount']=self.__data[timestr][appid]['allcount'] + 1

            if str(status).strip('') == '1':
                if not self.__data[timestr][appid].has_key('success'):
                    self.__data[timestr][appid]['success'] = {}

                if not self.__data[timestr][appid]['success'].has_key('locsource'):
                    self.__data[timestr][appid]['success']['locsource'] = {}

                if not self.__data[timestr][appid]['success'].has_key('loctype'):
                    self.__data[timestr][appid]['success']['loctype'] = {}

                if not self.__data[timestr][appid]['success']['loctype'].has_key(loctype):
                    self.__data[timestr][appid]['success']['loctype'][loctype] = 1
                else:
                    self.__data[timestr][appid]['success']['loctype'][loctype] = self.__data[timestr][appid]['success']['loctype'][loctype] + 1

                if not self.__data[timestr][appid]['success']['locsource'].has_key(locsource):
                    self.__data[timestr][appid]['success']['locsource'][locsource] = 1
                else:
                    self.__data[timestr][appid]['success']['locsource'][locsource] = self.__data[timestr][appid]['success']['locsource'][locsource] + 1
            else:
                if not self.__data[timestr][appid].has_key('failed'):
                    self.__data[timestr][appid]['failed'] = {}

                if not self.__data[timestr][appid]['failed'].has_key['errcode']:
                    self.__data[timestr][appid]['failed']['errcode'] = {} 

                if not self.__data[timestr][appid]['failed'].has_key['locsource']:
                    self.__data[timestr][appid]['failed']['locsource'] = {} 

                if not self.__data[timestr][appid]['failed'].has_key['loctype']:
                    self.__data[timestr][appid]['failed']['loctype'] = {}

                if not self.__data[timestr][appid]['failed']['errcode'].has_key(errcode):
                    self.__data[timestr][appid]['failed']['errcode'][errcode] = 1
                else:
                    self.__data[timestr][appid]['failed']['errcode'][errcode] = self.__data[timestr][appid]['failed']['errcode'][errcode] + 1

                if not self.__data[timestr][appid]['failed']['locsource'].has_key(locsource):
                    self.__data[timestr][appid]['failed']['locsource'][locsource] = 1
                else:
                    self.__data[timestr][appid]['failed']['locsource'][locsource] = self.__data[timestr][appid]['failed']['locsource'][locsource] + 1

                if not self.__data[timestr][appid]['failed']['loctype'].has_key(loctype):
                    self.__data[timestr][appid]['failed']['loctype'][loctype] = 1
                else:
                    self.__data[timestr][appid]['failed']['loctype'][loctype] = self.__data[timestr][appid]['failed']['loctype'][loctype] + 1

            self.__start_save()
        except Exception,e:
            print e

    def showinfo(self):
        self.__dosave()
        r = self.__data.copy() 
        return r
