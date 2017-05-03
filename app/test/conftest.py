#!/usr/bin/env python
# -*- coding:utf-8 -*-

import pytest
from loc_data import create_app,db as _db,redis as _redis
from main.models import app,last_data,his_data

@pytest.fixture(scope='session')
def app():
    app = create_app('dev')
    return app


@pytest.fixture(scope='session')
def db(app,request):
    _db.drop_all()
    _db.create_all()
    return _db

@pytest.yield_fixture(scope='function',autouse=True)
def session(db,request):
    conn = _db.engine.connect()
    #txn = conn.begin()

    options = dict(bind=conn,binds={})
    session = _db.create_scoped_session(options=options)

    _db.session = session

    yield session

    session.remove()
    #txn.rollback()
    conn.close()
