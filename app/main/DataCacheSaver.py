#!/usr/bin/env python
# -*- coding:utf-8 -*-

import threading
import datetime
import Queue
from BaseSingletonClass import Singleton
from loc_data import db
from flask import current_app
from .models import his_data
import time

class DataCacheSaver(Singleton):
    """
    批量数据导入时，批量缓存
    """ 
    __isinited = False
    __q = None
    __batch_size = 500
    __savethreading = None
    __app = None
    __info_last_active_time = None
    mutex = threading.Lock()
    def __init__(self):
        '''单根类，数据源初始化'''
        self.mutex.acquire()
        if not self.__isinited :
            print "datacachesaver is init..."
            self.__q = Queue.Queue()
            self.__batch_size = 500
            self.__app = current_app._get_current_object() 
            self.__isinited = True
        self.mutex.release()

    def run(self):
        idle = 0
        while(True):
            print "start to save import data  %s" % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            self.__info_last_active_time = datetime.datetime.now()
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
                    print "queue len:%s"  % str(self.__q.qsize())
                    with self.__app.app_context():
                        r = db.session.execute(his_data.__table__.insert(),da)
                        print "bluck insert rows:%d" % r.rowcount
                        db.session.commit()
                        print "bluck save is end."
                    idle = 0
                else:
                    time.sleep(5)
                    idle = idle + 1
                    #more than 30 min empty loop break.
                    if idle > 360 :
                        print "import threading is idle,exit break."
                        break
            except Exception,e:
                print e

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
            print "init threading..."
            if not self.__savethreading is None:
                self.__savethreading = None 
            self.__savethreading = threading.Thread(target=DataCacheSaver.run,args=(self,))
            print "set threading daemon."
            self.__savethreading.setDaemon(True)
            print "start threading."
            self.__savethreading.start()
        except Exception,e:
            print e

    def save(self,his_data):
        try:
            self.__q.put(his_data)
            self.__start_save()
        except Exception,e:
            print e

    def showinfo(self):
        r = {}
        r['id'] = id(self)
        r['last_active_time'] = self.__info_last_active_time
        r['queuelen'] = self.__q.qsize()
        return r
