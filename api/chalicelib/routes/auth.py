#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
認証関連のルーティングを実装します
"""

from datetime import timedelta

from chalicelib import clock
from chalicelib.env import store
from chalicelib.aws import cloudfront
from chalicelib.webapp import responses


app = store.get('chalice.app')
cors = store.get('chalice.cors')
authorizer = store.get('chalice.authorizer')


@app.route('/api/public/auth/logout', cors=cors)
def get_logout_cookie():
    """ ログアウト時の Cookie クリア用のレスポンスを返す """
    EXPIRED = 'Thu, 01 Jan 1970 00:00:00 GMT'
    secure = '' if store.is_local() else 'Secure;'
    cookies = [
        f'{key}=;Path=/;{secure}Expires={EXPIRED}'
        for key in cloudfront.cookie_keys()
    ]
    headers = {'Set-Cookie': cookies}
    return responses.application_json(
        {'login': 'logout'}, headers=headers)


@app.route('/api/auth/signedcookie', authorizer=authorizer, cors=cors)
def get_signed_cookie():
    """
    login 領域 (/m/*) にアクセスするための
    Cookie を付与したレスポンスを返す
    """
    siteurl = store.conf('FrontUrl')
    policy = cloudfront.Policy(
        f'{siteurl}/m/*',
        expire=timedelta(days=int(store.conf('CookieExcpiredDay', 7))))
    publisher = cloudfront.Publisher(
        store.conf('CloudFrontKeyId'),
        store.conf('CloudFrontKeyFile'))
    expire = clock.http_datetime(policy.expire_datetime())
    secure = '' if store.is_local() else 'Secure;'
    cookies = [
        f'{key}={value};Path=/;{secure}Expires={expire}'
        for (key, value) in publisher.publish(policy).items()
    ]

    headers = {'Set-Cookie': cookies}
    return responses.application_json(
        {'login': 'success'}, headers=headers)
