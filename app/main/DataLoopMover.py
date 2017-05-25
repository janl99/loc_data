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

class DataLoopMover(Singleton):
    """
    数据循环批量转移到日表 
    """ 
    __isinited = False
    __q = None
    __batch_size = 10000
    __movethreading = None
    __app = None
    mutex = None
    __txn = None
    def __init__(self):
        '''单根类，数据源初始化'''
        if not self.__isinited :
            self.__isinited = True
            print "dataloopmover is init..."
            self.__q = Queue.Queue()
            self.__batch_size = 10000 
            self.mutex = threading.Lock()
            self.__app = current_app._get_current_object() 

    def run(self):
        while(True):
            print "start to move his_data %s" % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            try:
                his_data_rows = self.__m_his_data_rows()
                print "his_data all rows is:%s" % str(his_data_rows)
                if his_data_rows > self.__batch_size:
                    self.__m_batch_move()
                else:
                    time.sleep(30)
            except Exception,e:
                print e

    def __start_move(self):
        if self.__movethreading == None:
           self.__start_move_thread() 
        elif self.__movethreading.is_alive:
            return
        else:
            self.__start_move_thread()

    def __start_move_thread(self):
        try:
            print "init loop move threading..."
            self.__movethreading = threading.Thread(target=DataLoopMover.run,args=(self,))
            print "set loop move threading daemon."
            self.__movethreading.setDaemon(True)
            print "start loop move threading."
            self.__movethreading.start()
        except Exception,e:
            print e

    def move(self):
        try:
            self.__start_move()
        except Exception,e:
            print e

    def __m_batch_suffixtable_exist(self,suffix):
        r = False
        tablename = "his_data" + suffix
        ret = []
        sqlstr = " show tables like '"+tablename+"';"
        try:
            with self.__app.app_context():
                t = db.session.execute(sqlstr)
                for row in t.fetchall():
                    ret.append(row[0])
            if tablename in ret:
                r = True
            else:
                t = False
        except Exception,e:
            print e
        return r

    def __m_batch_get_min_suffix(self):
        """
        get min day str '20170502' 
        """
        r = []
        try:
            sqlstr = "select min(date_format(time,'%Y%m%d')) from his_data;" 
            with self.__app.app_context():
                t = db.session.execute(sqlstr).scalar()
                r = t
        except Exception,e:
            print e
        return r

    def __m_batch_get_rows_by_suffix(self,suffix):
        """
        get rows count between  suffix 00:00:00  and suffix 23:59:59.999999' 
        """
        r = []
        st = datetime.datetime.combine(datetime.datetime.strptime(suffix,'%Y%m%d').date(), datetime.time.min)
        et = datetime.datetime.combine(datetime.datetime.strptime(suffix,'%Y%m%d').date(), datetime.time.max)
        try:
            sqlstr = "select count(*) from his_data where time between '" + st.strftime('%Y-%m-%d %H:%M:%S') +\
                "' and '" + et.strftime('%Y-%m-%d %H:%M:%S') + "' ;" 
            with self.__app.app_context():
                t = db.session.execute(sqlstr).scalar()
                r = t
        except Exception,e:
            print e
        return r

    def __m_batch_get_maxtime_for_batch(self,suffix):
        """
        get rows count between  suffix 00:00:00  and suffix 23:59:59.999999' 
        """
        r = None 
        st = datetime.datetime.combine(datetime.datetime.strptime(suffix,'%Y%m%d').date(), datetime.time.min)
        et = datetime.datetime.combine(datetime.datetime.strptime(suffix,'%Y%m%d').date(), datetime.time.max)
        print "get max time for batch ,suffix is:%s" % suffix
        try:
            sqlstr = "select time from his_data where time between '" + st.strftime('%Y-%m-%d %H:%M:%S') +\
                "' and '" + et.strftime('%Y-%m-%d %H:%M:%S') + "' order by time  limit "+ str(self.__batch_size - 1) +",1 ;" 
            with self.__app.app_context():
                t = db.session.execute(sqlstr).scalar()
                r = t
        except Exception,e:
            print e
        return r

    def __m_batch_create_suffixtable(self,suffix):
        """
        create suffix table
        """
        create_suffixtable_sqlstr = "create table his_data" + suffix + " (select * from his_data where 1 = 0 )" 
        table_exist =self.__m_batch_suffixtable_exist(suffix)
        #print "table_exist:%r" % table_exist
        if not table_exist:
            #print "create_suffixtable_sqlstr:%s" % create_suffixtable_sqlstr
            try:
                with self.__app.app_context():
                    m = db.session.execute(create_suffixtable_sqlstr)
            except Exception,e:
                print e

    def __m_batch_move_data(self,suffix,st,et):
        """
        batch move his_data rows to suffixtable by st and et.
        """
        print "__m_data_move_data for,st=%s,et=%s" % (st.strftime('%Y-%m-%d %H:%M:%S'),et.strftime('%Y-%m-%d %H:%M:%S'))
        movesqlstr = " insert into his_data" + suffix +" (id,appid,kid,time,status,errcode,loctype,locsource,data) " +\
                " select * from his_data where time between '" + st.strftime('%Y-%m-%d %H:%M:%S') +\
                "' and '" + et.strftime('%Y-%m-%d %H:%M:%S') + "' order by time;"
        delsqlstr = " delete from his_data where time between '" + st.strftime('%Y-%m-%d %H:%M:%S') +\
                "' and '" + et.strftime('%Y-%m-%d %H:%M:%S') + "' ;"

        with self.__app.app_context():
            try:
                self.__txn = db.session.begin(subtransactions=True)
                m = db.session.execute(movesqlstr)
                d = db.session.execute(delsqlstr)
                self.__txn.commit()
            except Exception,e:
                print e
                self.__txn.rollback()

    def __m_batch_move(self):
        """
        batch move data from his_data table to suffix table
        """
        try:
            suffix = self.__m_batch_get_min_suffix()
            print "Min suffix is :%s" % suffix
            self.__m_batch_create_suffixtable(suffix)
            st = datetime.datetime.combine(datetime.datetime.strptime(suffix,'%Y%m%d').date(), datetime.time.min)
            et = datetime.datetime.combine(datetime.datetime.strptime(suffix,'%Y%m%d').date(), datetime.time.max)
            print "move st,et is: %s,%s" %(st.strftime('%Y-%m-%d %H:%M:%S'),et.strftime('%Y-%m-%d %H:%M:%S'))
            rows = self.__m_batch_get_rows_by_suffix(suffix)
            print "suffix all rows is :%s" % rows
            if rows < self.__batch_size:
                self.__m_batch_move_data(suffix,st,et) 
            else:
                et = self.__m_batch_get_maxtime_for_batch(suffix)
                print "batch max time is:%s" % et.strftime('%Y-%m-%d %H:%M:%S')
                self.__m_batch_move_data(suffix,st,et)
        except Exception,e:
            print e

    def __m_his_data_rows(self):
        """
        get rows count for his_data 
        """
        r = 0
        try:
            sqlstr = "select count(*) from his_data ;"
            with self.__app.app_context():
                t = db.session.execute(sqlstr).scalar()
            r = t
        except Exception,e:
            print e
        return r


