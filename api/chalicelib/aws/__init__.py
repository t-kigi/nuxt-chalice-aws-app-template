#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
AWS リソース操作のためのモジュールです。
"""

import boto3

from typing import Optional


def create_session(profile: Optional[str] = None,
                   region: Optional[str] = None) -> boto3.session.Session:
    """ boto3 用の session を生成します """
    region = region or 'ap-northeast-1'
    if profile:
        return boto3.session.Session(
            profile_name=profile, region_name=region)
    return boto3.session.Session(region_name=region)
