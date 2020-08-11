#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" 環境変数読み込みライブラリ

    参考：https://qiita.com/harukikaneko/items/b004048f8d1eca44cba9
"""


import os
from os.path import join, dirname
from dotenv import load_dotenv

load_dotenv(verbose=True)

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

USER = os.environ.get("USER")
PASS = os.environ.get("PASS")
