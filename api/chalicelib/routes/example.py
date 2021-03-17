#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
ルーティングの実装例です。
"""

from chalice import (
    Chalice, CognitoUserPoolAuthorizer,
    CORSConfig
)

from chalicelib.env import store
from chalicelib.webapp import responses


app: Chalice = store.get('chalice.app')
cors: CORSConfig = store.get('chalice.cors')
authorizer: CognitoUserPoolAuthorizer = store.get('chalice.authorizer')


@app.route('/api/public/test', cors=cors)
def public_test():
    """ 認証なしでどこからでもアクセスできる API の実装 """
    return responses.application_json({
        'hello': 'public'
    })


@app.route('/api/private/test', authorizer=authorizer, cors=cors)
def private_test():
    """ Cognito の認証がないとアクセスできない API の実装 """
    access_token = app.current_request.headers.get('cognitoaccesstoken')
    if access_token is None:
        return responses.application_json({'user': None})

    idp = store.get('aws.cognito-idp')
    user = idp.get_user(AccessToken=access_token)
    return responses.application_json({
        'user': user
    })
