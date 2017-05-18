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


