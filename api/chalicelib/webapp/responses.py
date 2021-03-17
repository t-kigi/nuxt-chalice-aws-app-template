#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
chalice.Response の簡易ヘルパです。
"""

from datetime import datetime, timedelta

from chalice import Response

from chalicelib import clock
from chalicelib.env import store

from typing import Optional


def cache_headers(cache_seconds: int, now: datetime = None):
    ''' キャッシュ用のヘッダ情報を生成します '''
    headers = {}
    if cache_seconds > 0:
        # キャッシュ指示
        now = now or clock.gmtnow()
        expire = now + timedelta(seconds=cache_seconds)
        headers['Expires'] = expire.strftime('%a, %d %b %Y %H:%M:%S GMT')
        headers['Cache-Control'] = f'public, max-age={cache_seconds}'
    else:
        # キャッシュ無効 (念の為)
        headers['Expires'] = '-1'
        headers['Cache-Control'] = 'no-cache, max-age=0'
    return headers


def application_json(body: dict, cache: bool = False,
                     headers: Optional[dict] = None) -> Response:
    """
    application/json を返すレスポンスです。
    キャッシュを明示する場合などに利用できます。
    """
    _headers = cache_headers(store.conf('TTL', 60) if cache else 0)
    _headers['Content-Type'] = 'application/json'
    if headers:
        for (k, v) in headers.items():
            _headers[k] = v
    return Response(body=body, status_code=200, headers=_headers)
