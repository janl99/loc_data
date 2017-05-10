#!/usr/bin/env python
# -*- coding:utf-8 -*-

import threading
import datetime
import Queue
from loc_data import db
from flask import current_app
from .models import his_data
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
    __batch_size = 1000
    __savethreading = None
    __app = None
    mutex = None
    def __init__(self):
        '''单根类，数据源初始化'''
        if not self.__isinited :
            print "datacachesaver is init..."
            self.__q = Queue.Queue()
            self.__batch_size = 10000
            self.mutex = threading.Lock()
            self.__app = current_app._get_current_object() 
            self.__isinited = True

    def run(self):
        while(True):
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
                    with self.__app.app_context():
                        r = db.session.execute(his_data.__table__.insert(),da)
                        print "bluck insert rows:%d" % r.rowcount
                        db.session.commit()
                        print "savethreading is end."
                else:
                    time.sleep(5)
            except Exception,e:
                print e

    def __start_save(self):
        #print "__start save...."
        if self.__savethreading == None:
           self.__start_save_thread() 
        elif self.__savethreading.is_alive:
            return
        else:
            self.__start_save_thread()

    def __start_save_thread(self):
        try:
            print "init threading..."
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
            print "queue len:%s"  % str(self.__q.qsize())
            self.__start_save()
        except Exception,e:
            print e


