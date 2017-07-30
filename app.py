from bson.objectid import ObjectId
from bson.json_util import dumps , loads
from datetime import datetime, timedelta
from flask import Flask, render_template, request
from flask_restful import Api, Resource
from marshmallow import fields, Schema, validate, validates, validates_schema, ValidationError
from pymongo import errors as mongoerrors, MongoClient
import jwt

#########################
# Config
#########################
app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
api = Api(app)
client = MongoClient("localhost", 27017, serverSelectionTimeoutMS=5000)
db = client.test
SECRET_KEY = "\xb3\x15[\xe9d\xe8\xd6\x1e\xf0%\x12/\xd5\xcd\x0eru\x15\xda$\xdb\xb3II]"

#########################
# Schema
#########################
class PostSchema(Schema):
    postId = fields.Str(validate=validate.Regexp(regex='[0-9a-fA-F]{24}',
            error='invalid post id'))
    date = fields.DateTime()
    title = fields.Str(error='invalid title')
    discr = fields.Str(error='invalid discription')
    text = fields.Str(error='invalid text body')
    tags = fields.List(fields.Str())
    visable = fields.Int(validate=validate.Range(min=0, max=1))
post_schema = PostSchema()

class PostAmountSchema(Schema):
    amount = fields.Int(validate=validate.Range(min=0, max=50))
postAmount_schema = PostAmountSchema()

class UserSchema(Schema):
    name = fields.Str()
    password = fields.Str()
    token = fields.Str()

    @validates_schema
    def validate_user(self, data):
        """
        Taken is generated upon successful validation of user & pass.
        If token is supplied then token is validated and user & pass is ignored.
        """
        if 'token' in data:
             result = self.__decode_auth_token(data['token'])
             if 'errors' in result:
                 raise ValidationError(result['errors'])
        else:
            try:
                user = db.users.find_one({'$and': [{'user': data['name']},
                        {'password': data['password']}]})
            except mongoerrors.PyMongoError as e:
                raise ValidationError(str(e))
            except KeyError:
                raise ValidationError('missing username or password')
            if user == None:
                raise ValidationError('invalid username or password')
            data['token'] = self.__encode_auth_token(str(user['_id']))
            return data;

    def __encode_auth_token(self, objectid):
        """
        Generates the Auth Token
        :input objectid
        :return string
        """
        payload = {
            'exp': datetime.utcnow() +
                timedelta(days=1, seconds=5),
            'iat': datetime.utcnow(),
            'sub': objectid
        }
        return jwt.encode(
                payload,
                SECRET_KEY,
                algorithm='HS256'
        )

    def __decode_auth_token(self, token):
        """
        Decodes the auth token
        :return: integerstring
        """
        try:
            payload = jwt.decode(token, SECRET_KEY)
            return {'exp': payload['exp']}
        except jwt.ExpiredSignatureError:
            return {'errors': 'token expired'}
        except jwt.InvalidTokenError:
            return {'errors': 'invalid token'}
user_schema = UserSchema()

#########################
# Api
#########################
class LoginApi(Resource):
    def post(self):
        json_data = request.get_json()
        data, errors = user_schema.load(json_data)
        if errors:
            return dumps({'errors': errors}), 400
        return dumps({'token': data['token']}), 201
api.add_resource(LoginApi, '/admin/')

class TestToken(Resource):
    def get(self, token):
        data, errors = user_schema.load({'token': token})
        if errors:
            return dumps({'errors': errors}), 400
        return dumps({'success': "good token"})
api.add_resource(TestToken, '/testToken/<token>')

class BlogApi(Resource):
    def get(self):
        try:
            curser = db.posts.find({'$query': {},
                '$orderby': {'_id': -1}}, {"text": 0}).limit(20)
        except mongoerrors.PyMongoError as e:
            post = {'errors': e}
        return dumps([post for post in curser]), 200
api.add_resource(BlogApi, '/blog/')

class BlogAmountApi(Resource):
    def get(self, amount):
        data, errors = postAmount_schema.load({'amount': amount})
        if errors:
            return dumps({'errors': errors}), 400
        try:
            curser = db.posts.find({'$query': {},
                '$orderby': {'_id': -1}}, {"text": 0}).limit(data['amount'])
        except mongoerrors.PyMongoError as e:
            post = {'errors': e}
        return dumps([post for post in curser]), 200
api.add_resource(BlogAmountApi, '/blog/<amount>')

class BlogIdApi(Resource):
    def get(self, postId):
        data, errors = post_schema.load({'postId': postId})
        if errors:
            return dumps({'errors': errors}), 400
        try:
            post = db.posts.find_one({'_id': ObjectId(data['postId'])})
        except mongoerrors.PyMongoError as e:
            post = {'errors': e}
        return dumps(post), 200

    def put(self, postId):
        json_data = request.get_json()
        json_data['postId'] = postId
        data, errors = post_schema.load(json_data)
        if errors:
            return dumps({'errors': errors}), 400
        try:
            post = db.posts.update_one({'_id': ObjectId(data['postId'])},
                {'$set': data})
            post = {'modified count': post.modified_count}
        except mongoerrors.PyMongoError as e:
            post = {'errors': e}
        return dumps(post), 201

    def delete(self, postId):
        data, errors = post_schema.load({'postId': postId})
        if errors:
            return dumps({'errors': errors}), 400
        try:
            post = db.posts.delete_one({'_id': ObjectId(data['postId'])})
            post = post.deleted_count
        except mongoerrors.PyMongoError as e:
            post = {'errors': e}
        return dumps(post), 201
api.add_resource(BlogIdApi,  '/blog/id/<postId>')

class BlogAfterIdApi(Resource):
    def get(self, afterId):
        data, errors = post_schema.load({'postId': afterId})
        if errors:
            return dumps({'errors': errors}), 400
        curser = None
        try:
            curser = db.posts.find({'$query': {'_id': {'$gt':
                ObjectId(data['postId'])}},
                '$orderby': {'_id': -1}}, {"text": 0}).limit(20)
        except mongoerrors.PyMongoError as e:
            post = {'errors': e}
        return [post for post in curser], 200
api.add_resource(BlogAfterIdApi, '/blog/id/after/<afterId>')

class BlogTitleApi(Resource):
    def get(self, title):
        data, errors = post_schema.load({'title': title})
        if errors:
            return dumps({'errors': errors}), 400
        try:
            post = db.posts.find_one({'title': data['title']})
        except mongoerrors.PyMongoError as e:
            post = {'errors': e}
        return dumps(post), 200

    def post(self, title):
        json_data = request.get_json()
        json_data['date'] = datetime.utcnow().isoformat()
        json_data['title'] = title
        json_data['visable'] = 0
        data, errors = post_schema.load(json_data)
        if errors:
            return dumps({'errors': errors}), 400
        try:
            post = db.posts.insert_one(data).inserted_id
        except mongoerrors.PyMongoError as e:
            post = {'errors': e}
        return dumps(post), 201

    def put(self, title):
        json_data = request.get_json()
        data, errors = post_schema.load(json_data)
        if errors:
            return dumps({'errors': errors}), 400
        try:
            post = db.posts.update_one({'title': data['title']},
                {'$set': data})
            post = {'modified count': post.modified_count}
        except mongoerrors.PyMongoError as e:
            post = {'errors': e}
        return dumps(post), 201

    def delete(self, title):
        data, errors = post_schema.load({'title': title})
        if errors:
            return dumps({'errors': errors}), 400
        try:
            post = db.posts.delete_one({'title': data['title']})
            post = post.deleted_count
        except mongoerrors.PyMongoError as e:
            post = {'errors': e}
        return dumps(post), 201
api.add_resource(BlogTitleApi,  '/blog/title/<title>')

#########################
# Routes
#########################
@app.route("/")
def main():
    return render_template('index.html')

#########################
# Misc
#########################
if __name__ == "__main__":
    app.run(debug = True, port = 5000)
