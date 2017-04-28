#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys,os

curr_dir = os.path.dirname(os.path.realpath(__file__))
mod_path = os.path.abspath(curr_dir + '/..')
print mod_path

sys.path.append(mod_path)
