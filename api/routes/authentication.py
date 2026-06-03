#!/usr/bin/python3
# -*- coding:utf-8 -*-
# @Author         : Charlie Zhang
# @Email          : charlie.zhang2@ibaiqiu.com
# @Time           : 2026/6/3 20:22
# @Version        : 1.0
# @File           : user.py
# @Software       : PyCharm
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from config.conf import settings
from core.ldap import LDAPTool
from core.sign import get_signer

router = APIRouter()


class LoginRequest(BaseModel):
    username: str
    password: str


@router.post("/login")
def login(req: LoginRequest):
    ldap = LDAPTool()
    if not ldap.ldap_auth(req.username, req.password):
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    token = get_signer().sign_t({"sub": req.username}, expires_in=settings.TOKEN_EXPIRE_DAYS * 86400)
    return {"access_token": token, "token_type": "bearer"}
