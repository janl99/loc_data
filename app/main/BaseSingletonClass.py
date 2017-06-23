#!/usr/bin/env python
# -*- coding:utf-8 -*-

import threading
import redis

class Singleton(object):
    '''process singleton base class'''
    _instance = None
    lock = threading.Lock()

    def __new__(cls,*args,**kwargs):
        if not cls._instance:
            try:
                cls.lock.acquire()
                if not cls._instance:
                    cls._instance = super(Singleton,cls).__new__(cls,*args,**kwargs)
            finally:
                cls.lock.release()
        return cls._instance

class Global_Singleton(object):
    '''global singleton base class'''
    _instance = None
    lock = threading.Lock()

    def __new__(cls,*args,**kwargs):
        if not cls._instance:
            try:
                cls.lock.acquire()
                if not cls._instance:
                    cls._instance = super(Global_Singleton,cls).__new__(cls,*args,**kwargs)
            finally:
                cls.lock.release()
        return cls._instance 

    @staticmethod
    def gl_getredis(self):
        conn = None
        try:
            conn = redis.StrictRedis(host='redis',port=6379,db=0)
        except Exception,e:
            print e
        return conn

    @staticmethod
    def gl_acquire(self):
        r = 0 
        try:
            redis_conn = self.gl_getredis(self)
            r = redis_conn.setnx('FLAG:statistics',1) 
            print "global_singleton get redis global lock:%s" % str(r) 
        except Exception,e:
            print e
        return r

    @staticmethod
    def gl_release(self):
        r = 0 
        try:
            redis_conn = self.gl_getredis(self)
            r = redis_conn.delete('FLAG:statistics') 
            print "global_singleton release redis global lock:%s" % str(r)
            return r
        except Exception,e:
            print e
            r = 0
        return r 

