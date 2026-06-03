#!/usr/bin/python3
# -*- coding:utf-8 -*-
# @Author         : Charlie Zhang
# @Email          : charlie.zhang2@ibaiqiu.com
# @Time           : 2026/6/3 20:13
# @Version        : 1.0
# @File           : sign.py
# @Software       : PyCharm
import jwt
from datetime import datetime, timedelta, timezone

from config.conf import settings


class Singleton(type):
    def __init__(cls, *args, **kwargs):
        cls.__instance = None
        super().__init__(*args, **kwargs)

    def __call__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__call__(*args, **kwargs)
        return cls.__instance


class Signer(metaclass=Singleton):

    def __init__(self, secret_key=None):
        self.secret_key = secret_key
        self.algorithm = "HS256"

    def sign(self, payload: dict):
        """
        永不过期Token
        """
        return jwt.encode(
            payload,
            self.secret_key,
            algorithm=self.algorithm
        )

    def unsign(self, token: str):
        """
        验证永不过期Token
        """
        try:
            return jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm]
            )
        except jwt.InvalidTokenError:
            return {}

    def sign_t(self, payload: dict, expires_in=3600):
        """
        生成带过期时间Token
        """
        data = payload.copy()

        data["exp"] = datetime.now(timezone.utc) + timedelta(seconds=expires_in)

        return jwt.encode(
            data,
            self.secret_key,
            algorithm=self.algorithm
        )

    def unsign_t(self, token: str):
        """
        验证带过期时间Token
        """
        try:
            return jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm]
            )

        except jwt.ExpiredSignatureError:
            return {}

        except jwt.InvalidTokenError:
            return {}


def get_signer():
    return Signer(settings.SECRET_KEY)
