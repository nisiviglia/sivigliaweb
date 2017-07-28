from bson.objectid import ObjectId
from bson.json_util import dumps , loads
from datetime import datetime
from flask import Flask, render_template, request
from flask_restful import Api, Resource
from marshmallow import fields, Schema, validate
from pymongo import errors as mongoerrors, MongoClient

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
api = Api(app)
client = MongoClient("localhost", 27017, serverSelectionTimeoutMS=5000)
db = client.test

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

#########################
# Api
#########################
class BlogApi(Resource):
    def get(self):
        curser = None
        try:
            curser = db.posts.find({'$query': {},
                '$orderby': {'_id': -1}}, {"text": 0}).limit(50)
        except mongoerrors.PyMongoError as e:
            return("Database get post previews after failed: " + str(e))
        return dumps([post for post in curser])
api.add_resource(BlogApi, '/blog/')

class BlogIdApi(Resource):
    def get(self, postId):
        data, errors = post_schema.load({'postId': postId})
        if errors:
            return dumps({'errors': errors}), 400
        try:
            post = db.posts.find_one({'_id': ObjectId(data['postId'])})
        except mongoerrors.PyMongoError as e:
            post = {'errors': e}
        return dumps(post)
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
                '$orderby': {'_id': -1}}, {"text": 0}).limit(50)
        except mongoerrors.PyMongoError as e:
            post = {'errors': e}
        return [post for post in curser]
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
        return dumps(post)

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
        return dumps(post)

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
