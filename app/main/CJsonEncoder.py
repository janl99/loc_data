#!/usr/bin/env python
# -*- coding:utf-8 -*-

from datetime import datetime,date,time
import json

class CJsonEncoder(json.JSONEncoder):
    def default(self,obj):
        if isinstance(obj,datetime) or isinstance(obj,date):
            return obj.isoformat()
        else:
            return json.JSONEncoder.default(self,obj)

