#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
nuxt-chalice-api のテンプレート実装です。
主に、全体で利用するグローバルスコープのリソースを初期化します。
"""

import os

from chalice import (
    Chalice, CognitoUserPoolAuthorizer,
    CORSConfig
)

from chalicelib import aws
from chalicelib.env import store


stage = store.mutation(
    'chalilce.stage', os.environ.get('STAGE', 'local'))
appname = os.environ.get('APPNAME', 'wtbridge-apiv1')
app = store.mutation(
    'chalice.app', Chalice(app_name=appname))

project_dir = os.path.dirname(__file__)
conffile = os.path.join(
    project_dir, 'chalicelib', 'env', f'{stage}.yaml')
store.load_config(conffile)


authorizer = store.mutation(
    'chalice.authorizer',
    CognitoUserPoolAuthorizer(
        'MyUserPool', provider_arns=[store.conf('UserPoolARN')])
)

# local の場合のみ異なる Origin からのリクエストになるため CORS 設定が必要
if store.is_local():
    cors = CORSConfig(
        allow_origin=store.conf('FrontUrl'),
        allow_headers=['CognitoAccessToken'],
        allow_credentials=True
    )
else:
    cors = None

store.mutation('chalice.cors', cors)

# AWS boto3 client 初期化
store.mutation(
    'aws.session',
    aws.create_session(store.conf('Profile'), store.conf('Region')))
store.mutation(
    'aws.cognito-idp', store.get('aws.session').client('cognito-idp'))


# モジュール別のルーティングを追加
from chalicelib.routes import auth, example  # noqa


@app.route('/')
def ping():
    return {'hello': 'world'}
