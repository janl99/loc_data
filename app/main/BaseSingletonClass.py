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
    lock = threading.RLock()

    def __new__(cls,*args,**kw):
        cls.lock.acquire()
        if cls._instance is None:
            cls._instance = super(Singleton,cls).__new__(cls)
        cls.lock.release()
        return cls._instance


