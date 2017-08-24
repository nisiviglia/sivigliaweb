from bson.objectid import ObjectId
from bson.json_util import dumps , loads
from datetime import datetime, timedelta
from flask import abort, Flask, render_template, request, Response
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth
from flask_restful import Api, Resource
from marshmallow import fields, Schema, validate
from pymongo import errors as mongoerrors, MongoClient
import jwt

#########################
# Config
#########################
app = Flask(__name__)
app.config.from_object('config.DevelopmentConfig')
app.config.from_envvar('SIVIGLIAWEB_CONFIG', silent=True)
SECRET_KEY = app.config['SECRET_KEY']
api = Api(app)
basic_auth = HTTPBasicAuth()
token_auth = HTTPTokenAuth('Bearer')
client = MongoClient(app.config['DATABASE_URL'])
db = client.get_default_database()
MAX_GET_POSTS = 20;

#########################
# Auth
#########################
@token_auth.verify_token
def decode_auth_token(token):
    """
    Decodes the auth token
    :input string
    :return: bool
    """
    try:
        payload = jwt.decode(token, SECRET_KEY)
        return True
    except jwt.ExpiredSignatureError:
        return False
    except jwt.InvalidTokenError:
        return False

def encode_auth_token(user):
    """
    Generates the Auth Token
    :input string
    :return string
    """
    payload = {
        'exp': datetime.utcnow() +
            timedelta(days=1, seconds=1),
        'iat': datetime.utcnow(),
        'sub': user
    }
    return jwt.encode(
            payload,
            SECRET_KEY,
            algorithm='HS512'
    )

@basic_auth.get_password
def get_password(user):
    '''
    Grabs password from database for HTTPBasicAuth.
    :input string
    :returns string
    '''
    try:
        result = db.users.find_one({'$query': {'user': user}}, {'password': 1})
        if result:
            return result['password']
        else:
            return None
    except mongoerrors.PyMongoError as e:
        return None

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

#########################
# Api
#########################
class LoginApi(Resource):
    @basic_auth.login_required
    def get(self):
        return Response(dumps({'token': encode_auth_token(basic_auth.username())}),
                mimetype='application/json', status_code='200')
api.add_resource(LoginApi, '/api/v1/login/')

class BlogApi(Resource):
    def get(self):
        try:
            curser = db.posts.find({'$query': {},
                '$orderby': {'_id': -1}}, {"text": 0}).limit(MAX_GET_POSTS)
        except mongoerrors.PyMongoError as e:
            post = {'errors': e}
        return Response(dumps([post for post in curser]),
                mimetype='application/json', status_code='200')
api.add_resource(BlogApi, '/api/v1/blog/')

class BlogAmountApi(Resource):
    def get(self, amount):
        data, errors = postAmount_schema.load({'amount': amount})
        if errors:
            return Response(dumps({'errors': errors}),
                    mimetype='application/json', status_code='400')
        try:
            curser = db.posts.find({'$query': {},
                '$orderby': {'_id': -1}}, {"text": 0}).limit(data['amount'])
        except mongoerrors.PyMongoError as e:
            post = {'errors': e}
        return Response(dumps([post for post in curser]),
                mimetype='application/json', status_code='200')
api.add_resource(BlogAmountApi, '/api/v1/blog/<amount>')

class BlogIdApi(Resource):
    def get(self, postId):
        data, errors = post_schema.load({'postId': postId})
        if errors:
            return Response(dumps({'errors': errors}),
                    mimetype='application/json', status_code='400')
        try:
            post = db.posts.find_one({'_id': ObjectId(data['postId'])})
        except mongoerrors.PyMongoError as e:
            post = {'errors': e}
        return Response(dumps(post),
                mimetype='application/json', status_code='201')

    @token_auth.login_required
    def put(self, postId):
        json_data = request.get_json()
        json_data['postId'] = postId
        data, errors = post_schema.load(json_data)
        if errors:
            return Response(dumps({'errors': errors}),
                    mimetype='application/json', status_code='400')
        try:
            post = db.posts.update_one({'_id': ObjectId(data['postId'])},
                {'$set': data})
            post = {'modified count': post.modified_count}
        except mongoerrors.PyMongoError as e:
            post = {'errors': e}
        return Response(dumps(post),
                mimetype='application/json', status_code='201')

    @token_auth.login_required
    def delete(self, postId):
        data, errors = post_schema.load({'postId': postId})
        if errors:
            return Response(dumps({'errors': errors}),
                    mimetype='application/json', status_code='400')
        try:
            post = db.posts.delete_one({'_id': ObjectId(data['postId'])})
            post = post.deleted_count
        except mongoerrors.PyMongoError as e:
            post = {'errors': e}
        return Response(dumps(post),
                mimetype='application/json', status_code='201')
api.add_resource(BlogIdApi,  '/api/v1/blog/id/<postId>')

class BlogAfterIdApi(Resource):
    def get(self, afterId):
        data, errors = post_schema.load({'postId': afterId})
        if errors:
            return Response(dumps({'errors': errors}),
                    mimetype='application/json', status_code='400')
        curser = None
        try:
            curser = db.posts.find({'$query': {'_id': {'$gt':
                ObjectId(data['postId'])}},
                '$orderby': {'_id': -1}}, {"text": 0}).limit(20)
        except mongoerrors.PyMongoError as e:
            post = {'errors': e}
        return [post for post in curser], 200
api.add_resource(BlogAfterIdApi, '/api/v1/blog/id/after/<afterId>')

class BlogTitleApi(Resource):
    def get(self, title):
        data, errors = post_schema.load({'title': title})
        if errors:
            return Response(dumps({'errors': errors}),
                    mimetype='application/json', status_code='400')
        try:
            post = db.posts.find_one({'title': data['title']})
            if post == None:
                return 404

        except mongoerrors.PyMongoError as e:
            post = {'errors': e}
        return Response(dumps(post),
                mimetype='application/json', status_code='200')

    @token_auth.login_required
    def post(self, title):
        json_data = request.get_json()
        if(json_data == None):
            return Response(dumps({'errors': 'POST data not found'}),
                    mimetype='application/json', status_code='400')
        json_data['date'] = datetime.utcnow().isoformat()
        json_data['title'] = title
        json_data['visable'] = 0
        data, errors = post_schema.load(json_data)
        if errors:
            return Response(dumps({'errors': errors}),
                    mimetype='application/json', status_code='400')
        try:
            post = db.posts.insert_one(data).inserted_id
        except mongoerrors.PyMongoError as e:
            post = {'errors': e}
        return Response(dumps(post),
                mimetype='application/json', status_code='201')

    @token_auth.login_required
    def put(self, title):
        json_data = request.get_json()
        data, errors = post_schema.load(json_data)
        if errors:
            return Response(dumps({'errors': errors}),
                    mimetype='application/json', status_code='400')
        try:
            post = db.posts.update_one({'title': data['title']},
                {'$set': data})
            post = {'modified count': post.modified_count}
        except mongoerrors.PyMongoError as e:
            post = {'errors': e}
        return Response(dumps(post),
                mimetype='application/json', status_code='201')

    @token_auth.login_required
    def delete(self, title):
        data, errors = post_schema.load({'title': title})
        if errors:
            return Response(dumps({'errors': errors}),
                    mimetype='application/json', status_code='400')
        try:
            post = db.posts.delete_one({'title': data['title']})
            post = post.deleted_count
        except mongoerrors.PyMongoError as e:
            post = {'errors': e}
        return Response(dumps(post),
                mimetype='application/json', status_code='201')
api.add_resource(BlogTitleApi,  '/api/v1/blog/title/<title>')

#########################
# Routes
#########################
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def main(path):
    return render_template('index.html', url_path=path)

#########################
# Misc
#########################
if __name__ == "__main__":
    app.run()
