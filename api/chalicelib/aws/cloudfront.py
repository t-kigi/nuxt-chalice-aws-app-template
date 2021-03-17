#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
CloudFront を操作するためのモジュールです。
"""


import re
import json
import base64
from datetime import datetime, timedelta

from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes

from chalicelib import clock

from typing import Union, Optional


class Policy:
    """ CloudFront用のポリシーを表現します """

    def __init__(self,
                 url: str,
                 expire: timedelta = None,
                 datefrom: datetime = None,
                 ipaddrs: list = None,
                 cookie_path: Optional[str] = None,
                 now: datetime = None):
        self.url = url
        self.expire = expire
        self.datefrom = datefrom
        self.ipaddrs = ipaddrs
        self.cookie_path = cookie_path or '/'
        self.now = now

    def _fix(self) -> "Policy":
        """ クラス内の動的要素を固定します """
        if self.now is None:
            self.now = clock.utcnow()
        if self.expire is None:
            self.expire = timedelta(days=1)
        return self

    def available_range(self) -> (int, int):
        """
        閲覧可能な時刻の範囲を返します。
        :return (int, int): (開始、終了) の組。
            値はUnixTime。 指定がない場合は None
        """
        self._fix()
        tdt = int((self.now + self.expire).timestamp())
        fdt = None
        if self.datefrom is not None:
            fdt = int(self.datefrom.timestamp())
        return (fdt, tdt)

    def expire_datetime(self) -> datetime:
        """ Policyの期限切れ時刻を返します """
        self._fix()
        return self.now + self.expire

    def generate(self, dumps: bool = True) -> Union[str, dict]:
        ''' CloudFront用のアクセス制限ポリシーを生成します '''
        self._fix()
        dateto = self.now + self.expire
        tsto = int(dateto.timestamp())
        conditions = {"DateLessThan": {"AWS:EpochTime": tsto}}
        if self.datefrom is not None:
            tsfrom = int(self.datefrom.timestamp())
            conditions["DateGreaterThan"] = {"AWS:EpochTime": tsfrom}
        if self.ipaddrs is not None:
            ips = [ip for ip in self.ipaddrs]
            conditions["IpAddress"] = {"AWS:SourceIp": ips}
        statement = {
            "Statement": [{
                "Resource": self.url,
                "Condition": conditions
            }]
        }
        return json.dumps(statement) if dumps else statement


class Publisher:
    """
    CloudFront で Private Access に利用する Cookie を発行するためのクラスです。
    long-url: https://docs.aws.amazon.com/ja_jp/AmazonCloudFront/latest/DeveloperGuide/private-content-setting-signed-cookie-custom-policy.html  # noqa
    """

    def __init__(self, keypair_id, keyfile):
        self.keypair_id = keypair_id
        self.keyfile = keyfile
        with open(keyfile, 'rb') as fh:
            self.privkey = serialization.load_pem_private_key(
                fh.read(), password=None, backend=default_backend())

    def _sign(self, message) -> bytes:
        """ SHA-1 ハッシュ関数と RSA を使用してハッシュ化し、署名します。 """
        return self.privkey.sign(
            message.encode(), padding.PKCS1v15(), hashes.SHA1())

    def _b64encode(self, msg: bytes) -> str:
        """ Amazon用のBase64エンコードを行います。 """
        b64msg = base64.b64encode(msg).decode('utf-8')
        for (f, t) in [('+', '-'), ('=', '_'), ('/', '~')]:
            b64msg = b64msg.replace(f, t)
        return b64msg

    def publish(self, policy: Policy) -> dict:
        """
        指定Policyによる閲覧を可能とする署名付きCookieを発行します。
        """
        json_policy = re.sub('\\s+', '', policy.generate())
        encoded_policy = self._b64encode(json_policy.encode('utf-8'))
        signature = self._b64encode(self._sign(json_policy))
        return {
            "CloudFront-Policy": encoded_policy,
            "CloudFront-Signature": signature,
            "CloudFront-Key-Pair-Id": self.keypair_id,
        }


def cookie_keys() -> list:
    """ 署名付きCookieのために利用されるCookieのキー一覧を返します """
    return [
        "CloudFront-Policy",
        "CloudFront-Signature",
        "CloudFront-Key-Pair-Id"
    ]
