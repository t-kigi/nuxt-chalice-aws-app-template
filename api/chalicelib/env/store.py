#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
環境全体で使えるグローバル定数を扱います。
"""

import os

import yaml

from typing import Any

__STORES = {}


def mutation(key: str, value: Any) -> Any:
    """ 値を登録します """
    __STORES[key] = value
    return value


def get(key: str, else_value: Any = None) -> Any:
    """ 登録した値を取得します """
    return __STORES.get(key, else_value)


def conf(key: str, else_value: Any = None) -> Any:
    """ コンフィグで読み込んだ値を取得します """
    return get('__config', {}).get(key, else_value)


def load_config(config_fullpath: str):
    """ コンフィグファイルを読み込みます """
    with open(config_fullpath) as fh:
        conf = yaml.safe_load(fh)
    mutation('__config', conf.get('Config', {}))


def is_local() -> bool:
    """ 環境がローカルであるかを返します """
    stage = get('chalice.stage')
    if stage is None:
        stage = mutation(
            'chalilce.stage', os.environ.get('STAGE', 'local'))
    return stage == 'local'
