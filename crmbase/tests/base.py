# -*- coding: utf-8 -*-
# * File Name : base.py
#
# * Copyright (C) 2010 Gaston TJEBBES <g.t@majerti.fr>
# * Company : Majerti ( http://www.majerti.fr )
#
#   This software is distributed under GPLV3
#   License: http://www.gnu.org/licenses/gpl-3.0.txt
#
# * Creation Date : 13-03-2012
# * Last Modified :
#
# * Project :
#
import os
import unittest

from pyramid import testing
from mock import Mock

from paste.deploy.loadwsgi import appconfig
from sqlalchemy import engine_from_config
from sqlalchemy.orm import sessionmaker

from crmbase.models import DBSESSION
from crmbase.models import DBBASE  # base declarative object

here = os.path.dirname(__file__)
settings = appconfig('config:' + os.path.join(here, '../../', 'test.ini'),
                                                          "crmbase")

class BaseTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = engine_from_config(settings, prefix='sqlalchemy.')
        cls.DBSession = sessionmaker()
        cls.connection = cls.engine.connect()
        DBSESSION.configure(bind=cls.connection)

    def setUp(self):
        # begin a non-ORM transaction
        self.trans = self.connection.begin()

        # bind an individual DBSESSION to the connection
        self.session = self.DBSession(bind=self.connection)
        DBBASE.session = self.session

    def tearDown(self):
        # rollback - everything that happened with the
        # DBSESSION above (including calls to commit())
        # is rolled back.
        testing.tearDown()
        self.trans.rollback()
        self.session.close()

class BaseViewTest(BaseTestCase):
    """
        Base class for testing views
    """
    def setUp(self):
        super(BaseViewTest, self).setUp()
        self.config = testing.setUp(request=testing.DummyRequest())

    def get_csrf_request(self, post=None):
        """
            Insert a dummy csrf token in the posted datas
        """
        def_csrf = 'default_csrf'
        if not u'csrf_token' in post.keys():
            post.update({'csrf_token': def_csrf})
        request = testing.DummyRequest(post)
        request.session = Mock()
        csrf_token = Mock()
        csrf_token.return_value = def_csrf
        request.session.get_csrf_token = csrf_token
        return request
