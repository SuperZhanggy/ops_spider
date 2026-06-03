#!/usr/bin/python3
# -*- coding:utf-8 -*-
# @Author         : Charlie Zhang
# @Email          : charlie.zhang2@ibaiqiu.com
# @Time           : 2026/6/3 21:33
# @Version        : 1.0
# @File           : deps.py
# @Software       : PyCharm

from core.sign import get_signer
import jwt
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
    token = authorization.replace("Bearer ", "")

    try:
        payload = get_signer().unsign_t(token)
        return payload
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=401,
            detail="Token无效"
        )
