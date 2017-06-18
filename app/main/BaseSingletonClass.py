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


