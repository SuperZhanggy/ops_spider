#!/usr/bin/python3
# -*- coding:utf-8 -*-
# @Author         : Charlie Zhang
# @Email          : charlie.zhang2@ibaiqiu.com
# @Time           : 2026/6/3 21:33
# @Version        : 1.0
# @File           : deps.py
# @Software       : PyCharm
from config.conf import settings
from core.sign import get_signer
from fastapi import Header, HTTPException

async def login_required(
    authorization: str = Header(None)
):
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="未登录"
        )
    # Bearer token
    if authorization.startswith("Bearer "):
        token = authorization.replace("Bearer ", "")
        payload = get_signer().unsign_t(token)
        is_authenticated = False if not payload else True

    elif authorization.startswith("ApiKey "):
        token = authorization.replace("ApiKey ", "")
        is_authenticated = token in settings.API_KEYS

    else:
        is_authenticated = False

    if not is_authenticated:
        raise HTTPException(
            status_code=401,
            detail="Token无效"
        )
