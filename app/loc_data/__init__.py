#!/usr/bin/env python
#  -*- coding:utf-8 -*-

import os

from flask import Flask
# from flask.ext.mongoengine import MongoEngine
# from flask.ext.login import LoginManager
# from flask.ext.principal import Principal 
#from flask_mongoengine import MongoEngine
#from flask_login import LoginManager
#from flask_principal import Principal     
from flask_sqlalchemy import SQLAlchemy
from flask_redis import FlaskRedis
from flask_marshmallow import Marshmallow

from config import config

db = SQLAlchemy()
redis = FlaskRedis() 
ma = Marshmallow()

#login_manager = LoginManager()
#login_manager.session_protection = 'strong'
#login_manager.login_view = 'accounts.login'

#principals = Principal()

def create_app(config_name):
    app = Flask(__name__, 
        template_folder=config[config_name].TEMPLATE_PATH, static_folder=config[config_name].STATIC_PATH)
    app.config.from_object(config[config_name])

    config[config_name].init_app(app)

    db.init_app(app)
    ma.init_app(app)
    redis.init_app(app)
#   login_manager.init_app(app)
#   principals.init_app(app)

    from main.sqlalchemy_json_encoder import AlchemyEncoder
    app.json_encoder = AlchemyEncoder

    from main.urls import main as main_blueprint
#   from accounts.urls import accounts as accounts_blueprint
    from api_1_0.urls import api as api_1_0_blueprint
    app.register_blueprint(main_blueprint)
    app.register_blueprint(api_1_0_blueprint,url_prefix='/api/1.0')
#   app.register_blueprint(blog_admin_blueprint, url_prefix='/admin')
#   app.register_blueprint(accounts_blueprint, url_prefix='/accounts')

    return app

app = create_app(os.getenv('config') or 'default')

