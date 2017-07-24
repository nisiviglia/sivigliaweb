from pymongo import errors as mongoerrors, MongoClient
from bson.objectid import ObjectId
import datetime

client = MongoClient("localhost", 27017, serverSelectionTimeoutMS=5000)
db = client.test

def newPost(title, discr, text, tags):
    try:
        post = {"date" : datetime.datetime.utcnow(),
                "title" : title,
                "discr" : discr,
                "text" : text,
                "tags" : tags,
                "visable" : 0}
        post_id = db.posts.insert_one(post).inserted_id
        return(post_id)

    except mongoerrors.PyMongoError as e:
        return("Database insert failed: " + str(e))

def updatePostById(postId, nti, ndi, nte, nta, nv):
    post = {"title": nti,
            "discr": ndi,
            "text": nte,
            "tags": nta,
            "visable": nv}
    post = dict(filter(lambda x: x[1] is not None, post.items()))
    try:
        db.posts.update_one({'_id' : ObjectId(postId)}, {'$set': post})
        return "success"

    except mongoerrors.PyMongoError as e:
        return("Database update failed: " + str(e))

def deletePostById(postId):
    try:
        db.posts.remove({'_id' : ObjectId(postId)})
        return ("Post '{}' removed".format(title))

    except mongoerrors.PyMongoError as e:
        return("Database remove failed: " + str(e))

def getPostPreviews(n):
    try:
        curser = db.posts.find({'$query': {},
            '$orderby': {'_id': -1}}, {"text": 0}).limit(n)
        return [post for post in curser]

    except mongoerrors.PyMongoError as e:
        return("Database get post previews failed: " + str(e))

def getPostPreviews(n, afterId):
    try:
        curser = db.posts.find({'$query': {'_id': {'$gt': ObjectId(afterId)}},
            '$orderby': {'_id': -1}}, {"text": 0}).limit(n)
        return [post for post in curser]

    except mongoerrors.PyMongoError as e:
        return("Database get post previews after failed: " + str(e))

def getPostById(postId):
    try:
        return  db.posts.find_one({'_id': ObjectId(postId)})

    except mongoerrors.PyMongoError as e:
        return("Database get post failed: " + str(e))

def getPostByTitle(title):
    try:
        return  db.posts.find_one({'title': title})

    except mongoerrors.PyMongoError as e:
        return("Database get post failed: " + str(e))
