# -*- coding: utf-8 -*-
from ldap3 import Connection, SUBTREE, ServerPool
from config.conf import settings

__all__ = [
    "LDAPTool"
]


class LDAPTool(object):
    """
    域控验证登陆的用户名和密码
    使用管理权限的用户获取出域用户的信息，通过bind方法可以校验用户
    """

    def __init__(self):
        self.ldap_server_pool = ServerPool(settings.LDAP_SERVER_POOL)
        self.conn = None

    def get_conn(self):
        """建立连接"""
        try:
            self.conn = Connection(self.ldap_server_pool, user=settings.ADMIN_DN, password=settings.ADMIN_PASSWORD,
                                   check_names=True, lazy=False, raise_exceptions=False, auto_bind=True)
        except Exception as e:
            print('##Ldap连接失败：{}'.format(e))
        return self.conn

    def change_pw(self, new_pw, user_name=None, user_dn=None):
        """修改密码"""
        conn = self.get_conn()
        if user_dn:
            dn = user_dn
        else:
            dn = self.get_dn_by_username(user_name)
        if dn:
            self.unlock(user_dn=dn)
            res = conn.extend.microsoft.modify_password(dn, new_password=new_pw)
            return [res, conn.response]
        else:
            return [False, "user not found"]

    def get_dn_by_username(self, username):
        """获取用户名对应的dn号"""
        conn = self.get_conn()
        res = conn.search(
            search_base=settings.SEARCH_BASE,
            search_filter='(sAMAccountName={})'.format(username),
            search_scope=SUBTREE,
            attributes='*',
            paged_size=100
        )
        if res and "dn" in conn.response[0]:
            return conn.response[0]['dn']
        else:
            return [False, "user not found"]

    def get_dn_by_usercname(self, user_cname):
        """获取用户名对应的dn号"""
        conn = self.get_conn()
        res = conn.search(
            search_base=settings.SEARCH_BASE,
            search_filter='(cn={})'.format(user_cname),
            search_scope=SUBTREE,
            attributes=[],
            paged_size=100
        )
        if res and "dn" in conn.response[0]:
            return conn.response[0]['dn']

    def get_detail_by_email(self, email):
        """获取用户名对应的dn号"""
        conn = self.get_conn()
        attributes = ['cn', 'mail', 'displayName', 'sAMAccountName']
        conn.search(
            search_base=settings.SEARCH_BASE,
            search_filter='(mail={})'.format(email),
            search_scope=SUBTREE,
            attributes=attributes,
            paged_size=100
        )
        if conn.entries:
            user = conn.entries[0]
            return user.entry_attributes_as_dict
        else:
            print(f'未找到该邮箱对应的用户: {email}')

    def get_user_info(self, user_cname=None, user_name=None):
        """获取用户相信信息"""
        conn = self.get_conn()
        attributes = [
            "distinguishedName",
            "name",
            "objectGUID",
            "mail",
            "title",
            "userAccountControl"
        ]
        search_filter = None
        if user_cname:
            search_filter = '(cn={})'.format(user_cname)
        if user_name:
            search_filter = '(sAMAccountName={})'.format(user_name)
        res = conn.search(settings.SEARCH_BASE, search_filter, attributes=attributes)
        result = []
        if res:
            for entry in conn.entries:
                attrs = dict()
                for key, value in entry.entry_attributes_as_dict.items():
                    attrs[key] = value[0] if value else ''
                result.append(attrs)
        return result

    def ldap_auth(self, username="", password=""):
        """认证用户"""
        result = False
        dn = self.get_dn_by_username(username)
        if dn and isinstance(dn, list) and not dn[0]:
            return result
        conn2 = Connection(self.ldap_server_pool, user=dn, password=password, check_names=True, lazy=False,
                           raise_exceptions=False)
        conn2.bind()
        if conn2.result["description"] == "success":
            result = True
        return result

    def unlock(self, user_name=None, user_dn=None):
        """解锁用户"""
        conn = self.get_conn()
        if not user_dn:
            user_dn = self.get_dn_by_username(user_name)
        if user_dn:
            res = conn.modify(user_dn, {'lockoutTime': [('MODIFY_REPLACE', "0")]})
            return [res, conn.response]
        else:
            return [False, "账户不存在"]

    def modify_dn(self, dn, rename, new_superior=None):
        """修改AD用户DN"""
        conn = self.get_conn()
        res = conn.modify_dn(dn, 'CN={}'.format(rename), new_superior=new_superior)
        if res:
            print('AD更新DN完成：[DN: {}, NewName: {}]'.format(dn, rename))
        else:
            print('AD更新DN失败：[DN: {}, NewName: {}]'.format(dn, rename))
        return res


if __name__ == "__main__":
    ld = LDAPTool()
    print(ld.ldap_auth("charlie.zhang2", "baiqiu123!@#"))
    # print(ld.get_detail_by_email("charlie.zhang2@ibaiqiu.com"))
    # print(ld.get_dn_by_username(username="charlie.zhang2"))
