#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os, sys
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from flask_script import Manager, Server
from loc_data import app

manager = Manager(app)

# Turn on debugger by default and reloader
manager.add_command("runserver", Server(
    use_debugger = True,
    use_reloader = True,
    host = '0.0.0.0',
    port = 4000)
)

if __name__ == "__main__":
    manager.run()
