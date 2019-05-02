# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from datetime import datetime
from unittest import main

# dateutil
from dateutil.parser import parse as dt_parse

# ipaddress
from ipaddress import ip_address

# Zato
from base import BaseTest, Config
from zato.common.ipaddress_ import ip_network
from zato.sso import const, status_code

# ################################################################################################################################
# ################################################################################################################################

class UserAttrTestCase(BaseTest):

# ################################################################################################################################

    def test_create(self):

        name = self._get_random_data()
        value = self._get_random_data()
        expiration = 900

        response = self.post('/zato/sso/user/attr', {
            'ust': self.ctx.super_user_ust,
            'user_id': self.ctx.super_user_id,
            'name': name,
            'value': value,
            'expiration': expiration
        })

        self.assertEqual(response.status, status_code.ok)

# ################################################################################################################################

    def test_create_already_exists(self):

        name = self._get_random_data()
        value = self._get_random_data()

        response1 = self.post('/zato/sso/user/attr', {
            'ust': self.ctx.super_user_ust,
            'user_id': self.ctx.super_user_id,
            'name': name,
            'value': value,
        })

        response2 = self.post('/zato/sso/user/attr', {
            'ust': self.ctx.super_user_ust,
            'user_id': self.ctx.super_user_id,
            'name': name,
            'value': value,
        }, False)

        self.assertEqual(response1.status, status_code.ok)
        self.assertEqual(response2.status, status_code.error)
        self.assertListEqual(response2.sub_status, [status_code.attr.already_exists])

# ################################################################################################################################

    def test_create_another_user_super_user(self):

        username = self._get_random_username()
        password = self._get_random_data()

        response = self.post('/zato/sso/user', {
            'ust': self.ctx.super_user_ust,
            'username': username,
            'password': password,
        })

        user_id = response.user_id
        self._approve(user_id)

        name = self._get_random_data()
        value = self._get_random_data()
        expiration = 900

        response = self.post('/zato/sso/user/attr', {
            'ust': self.ctx.super_user_ust,
            'user_id': user_id,
            'name': name,
            'value': value,
            'expiration': expiration
        })

        self.assertEqual(response.status, status_code.ok)

# ################################################################################################################################

    def test_create_another_user_regular_user(self):

        username1 = self._get_random_username()
        password1 = self._get_random_data()

        username2 = self._get_random_username()
        password2 = self._get_random_data()

        response1 = self.post('/zato/sso/user', {
            'ust': self.ctx.super_user_ust,
            'username': username1,
            'password': password1,
        })

        response2 = self.post('/zato/sso/user', {
            'ust': self.ctx.super_user_ust,
            'username': username2,
            'password': password2,
        })

        user_id1 = response1.user_id
        self._approve(user_id1)

        user_id2 = response2.user_id
        self._approve(user_id2)

        response = self.post('/zato/sso/user/login', {
            'username': username1,
            'password': password1,
        })

        ust = response.ust

        name = self._get_random_data()
        value = self._get_random_data()
        expiration = 900

        response = self.post('/zato/sso/user/attr', {
            'ust': ust,
            'user_id': user_id2,
            'name': name,
            'value': value,
            'expiration': expiration
        }, False)

        self.assertEqual(response.status, status_code.error)
        self.assertEqual(response.sub_status, [status_code.auth.not_allowed])

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################