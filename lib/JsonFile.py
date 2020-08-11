#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import os


class JsonFile():

    @staticmethod
    def load(path=''):
        """load json file

        Args:
            path (str, optional): json_file path. Defaults to ''.

        Returns:
            list: return list to convert from json
        """
        if not os.path.isfile(path):
            return []

        with open(path, 'r', encoding='utf_8') as f:
            tmp = f.read()
        return json.loads(tmp)

    @staticmethod
    def save(path, item):
        """save json file

        Args:
            path (str): json_file path
            item (list): file content
        """
        with open(path, 'w', encoding='utf_8') as f:
            json.dump(item, f, indent=2, ensure_ascii=False)
