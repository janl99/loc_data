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
    def __init__(self):
        '''单根类，数据源初始化'''
        if not self.__isinited :
            print "dataloopmover is init..."
            self.__q = Queue.Queue()
            self.__batch_size = 10000 
            self.mutex = threading.Lock()
            self.__app = current_app._get_current_object() 
            self.__isinited = True

    def run(self):
        while(True):
            print "start to move his_data %s,suffix queue: %s" % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),str(self.__q.qsize()))
            try:
                if self.__q.qsize() > 0:
                    while self.__q.qsize() > 0:
                        #self.mutex.acquire()
                        suffix = self.__q.get()
                        #self.mutex.release()
                        print "move data:%s" % suffix
                        self.__m_data_move_data(suffix) 
                else:
                    time.sleep(5)
                #print "thread move complated."
            except Exception,e:
                print e

    def __start_move(self):
        #print "__start save...."
        if self.__movethreading == None:
           self.__start_move_thread() 
        elif self.__movethreading.is_alive:
            return
        else:
            self.__start_move_thread()

    def __start_move_thread(self):
        try:
            print "init threading..."
            self.__movethreading = threading.Thread(target=DataLoopMover.run,args=(self,))
            print "set threading daemon."
            self.__movethreading.setDaemon(True)
            print "start threading."
            self.__movethreading.start()
        except Exception,e:
            print e

    def move(self):
        try:
            dl = self.__m_data_get_datelist()
            print dl
            for suffix in dl:
                self.__q.put(suffix)

            self.__start_move()
        except Exception,e:
            print e

    def __m_data_get_datelist(self):
        """
        get distinct day str like ['20170502','20170503'] before today
        """
        r = []
        try:
            st = datetime.datetime.combine(datetime.datetime.now().date(),datetime.time.min)
            sqlstr = "select distinct(date_format(time,'%Y%m%d')) from his_data where time < '"+ st.strftime('%Y-%m-%d %H:%M:%S') + "';" 
            with self.__app.app_context():
                t = db.session.execute(sqlstr)
                for row in t.fetchall():
                    r.append(row[0])
        except Exception,e:
            print e
        return r

    def __m_data_suffixtable_exist(self,suffix):
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

    def __m_data_move_data(self,suffix):
        print "__m_data_move_data for:%s" % suffix
        st = datetime.datetime.combine(datetime.datetime.strptime(suffix,'%Y%m%d').date(), datetime.time.min)
        et = datetime.datetime.combine(datetime.datetime.strptime(suffix,'%Y%m%d').date(), datetime.time.max)
        create_suffixtable_sqlstr = "create table his_data" + suffix +\
                " (select * from his_data where 1 = 0 )" 
        movesqlstr_tablexist = " insert into his_data" + suffix +" (id,appid,kid,time,status,errcode,loctype,locsource,data) " +\
                " select * from his_data where time between '" + st.strftime('%Y-%m-%d %H:%M:%S') +\
                "' and '" + et.strftime('%Y-%m-%d %H:%M:%S') + "';"
        #movesqlstr_tablenotexist = " create table his_data" + suffix +\
        #        " (select * from his_data where time between '" + st.strftime('%Y-%m-%d %H:%M:%S') +\
        #        "' and '" + et.strftime('%Y-%m-%d %H:%M:%S') + "');"
        delsqlstr = " delete from his_data where time between '" + st.strftime('%Y-%m-%d %H:%M:%S') +\
                "' and '" + et.strftime('%Y-%m-%d %H:%M:%S') + "' ;"
        try:
            table_exist =self.__m_data_suffixtable_exist(suffix)
            #print "table_exist:%r" % table_exist
            if not table_exist:
                #print "create_suffixtable_sqlstr:%s" % create_suffixtable_sqlstr
                with self.__app.app_context():
                    m = db.session.execute(create_suffixtable_sqlstr)
                    db.session.commit()
            #print "movesqlstr_tablexist:%s" % movesqlstr_tablexist
            with self.__app.app_context():
                m = db.session.execute(movesqlstr_tablexist)
                db.session.commit()
                print m.rowcount
            #print "delsqlstr:%s" % delsqlstr
            with self.__app.app_context():
                d = db.session.execute(delsqlstr)
                db.session.commit()
            #print d.rowcount
        except Exception,e:
            print e

