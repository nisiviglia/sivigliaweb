import base64
from bson.json_util import dumps, loads
import os
from pymongo import errors as mongoerrors, MongoClient
import pytest
import re
import sys

sys.path.insert(0,'..')
import app as myapp

'''
Make sure to set app.py to use TestingConfig.
This can be done either by ENV_variable 'SIVIGLIAWEB_CONFIG'
or within app.py its self.
'''

class TestLoginApi:

    def setup(self):
        self.app = myapp.app.test_client()
        client = MongoClient(myapp.app.config['DATABASE_URL'])
        db = client.get_default_database()
        assert list(db.collection_names()) == []

        db.users.insert_one({'user': 'testuser', 'password': 'testpassword'})

    def teardown(self):
        client = MongoClient(myapp.app.config['DATABASE_URL'])
        client.drop_database(client.get_default_database())

    def test_not_logged_in(self):
        rv = self.app.get('/api/v1/login/')
        assert rv.status_code == 401

    def test_correct_password(self):
        valid_credentials = base64.b64encode(b'testuser:testpassword').decode('utf-8')
	rv = self.app.get('/api/v1/login/', headers={'Authorization': 'Basic ' + valid_credentials})
        assert rv.status_code == 200
        assert re.search('(([A-Za-z0-9_-]){36,}\.([A-Za-z0-9_-]){64,}\.([A-Za-z0-9_-]){64,}){1}', rv.data) != None

    def test_incorrect_password(self):
        valid_credentials = base64.b64encode(b'testuser:wrongpassword').decode('utf-8')
	rv = self.app.get('/api/v1/login/', headers={'Authorization': 'Basic ' + valid_credentials})
        assert rv.status_code == 401

    def test_POST(self):
        rv = self.app.post('/api/v1/login/')
        assert rv.status == '405 METHOD NOT ALLOWED'

    def test_PUT(self):
        rv = self.app.post('/api/v1/login/')
        assert rv.status == '405 METHOD NOT ALLOWED'

class TestBlogTitleApi:
    def setup(self):
        self.app = myapp.app.test_client()
        client = MongoClient(myapp.app.config['DATABASE_URL'])
        db = client.get_default_database()
        assert list(db.collection_names()) == [], "are you using the test config?"

    def teardown(self):
        client = MongoClient(myapp.app.config['DATABASE_URL'])
        client.drop_database(client.get_default_database())

    def test_POST_not_logged_in(self):
        rv = self.app.post('/api/v1/blog/title/testtitle')
        assert rv.status_code == 401

    def test_PUT_not_logged_in(self):
        rv = self.app.put('/api/v1/blog/title/testtitle')
        assert rv.status_code == 401

    def test_DELETE_not_logged_in(self):
        rv = self.app.delete('/api/v1/blog/title/testtitle')
        assert rv.status_code == 401

    def test_login_add_post(self):
        token = myapp.encode_auth_token('testuser')
        auth = dict(Authorization=('Bearer ' + token))
        post = dict(discr= 'test discription',
                    text= 'sometext goes here',
                    tags= ['test', 'tags'])
        rv = self.app.post('/api/v1/blog/title/testtitle',
                data=dumps(post),
                headers=auth)
        assert rv.status_code == 200






