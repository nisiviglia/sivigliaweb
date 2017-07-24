from flask import Flask, abort, render_template
from flask_restful import Resource, Api
from pymongo import MongoClient
import datetime

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True

api = Api(app)

#########################
# Database
#########################
client = MongoClient('localhost', 27017)
db = client.test

def createPost(title, text, tags):
    collection = db.posts
    post = {"date" : datetime.datetime.utcnow(),
            "title" : this.title,
            "text" : this.text,
            "tags" : this.tags}
    post_id = collection.insert_one(post).inserted_id
    print(post_it)

#########################
# Routes
#########################

@app.route("/")
def main():
    return render_template('index.html')

#########################
# Api
#########################

class TestApi(Resource):
    def get(self):
        return {'test' : 'sucessful'}

api.add_resource(TestApi, '/test')

if __name__ == "__main__":
    app.run(debug = True, port = 5000)
