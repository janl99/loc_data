#!/usr/bin/env python
# -*- coding:utf-8 -*-

from datetime import datetime,date,time
from sqlalchemy.ext.declarative import DeclarativeMeta
from flask import json

class AlchemyEncoder(json.JSONEncoder):

    def default(self, o):
        #print "obj type is: %s" % type(o)
        if isinstance(o,datetime) or isinstance(o,date):
            return o.isoformat()
        if isinstance(o.__class__, DeclarativeMeta):
            data = {}
            fields = o.__json__() if hasattr(o, '__json__') else dir(o)
            print "obj fields: %s" % fields
            for field in [f for f in fields if not f.startswith('_') and f not in ['metadata', 'query', 'query_class']]:
                #print "model class field: %r" % field
                value = o.__getattribute__(field)
                if isinstance(value,date):
                    data[field] = value.isoformat()
                elif isinstance(value,datetime):
                    data[field] = value.isoformat()
                else:
                    try:
                        json.dumps(value)
                        data[field] = value
                    except TypeError:
                        data[field] = None
            return data
        return json.JSONEncoder.default(self, o)
