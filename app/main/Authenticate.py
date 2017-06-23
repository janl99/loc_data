#!/usr/bin/env python
# -*- coding:utf-8 -*-

import threading
import datetime
import Queue
from BaseSingletonClass import Singleton
from loc_data import db
from flask import current_app
from .models import app 
import time

class Authenticate(Singleton):
    """
    check appid request is allowed 
    """ 
    __isinited = False
    __app = None
    __data = {} 
    mutex = threading.Lock()
    __info_last_active_time = None
    def __init__(self):
        '''单根类，数据源初始化'''
        self.mutex.acquire()
        if not self.__isinited :
            print "autheenticate is init..."
            self.__data = {}
            self.__app = current_app._get_current_object() 
            with self.__app.app_context():
                t = db.session.query(app).all()
                self.__data.clear()
                for a in t:
                    self.__data[a.appid] = a.token.split(',')
            self.__info_last_active_time = datetime.datetime.now()
            self.__isinited = True
        self.mutex.release()

    def loadconfig(self):
        try:
            with self.__app.app_context():
                t = db.session.query(app).all()
                print t 
                self.mutex.acquire()
                self.__data.clear()
                for a in t:
                    self.__data[a.appid] = a.token.split(',')
                self.mutex.release()
        except Exception,e:
            print e


    def check(self,appid,ip):
        r = False
        try:
            self.__info_last_active_time = datetime.datetime.now()
            if not self.__data.has_key(appid):
                return r
            if ip in self.__data[appid]:
                r = True 
                return r
        except Exception,e:
            print e
            r = False
        return r


    def showinfo(self):
        r = {}
        r['id'] = id(self)
        r['last_active_time'] = self.__info_last_active_time
        r['data'] = self.__data
        return r



