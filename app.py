from flask import Flask, render_template
from flask_restful import Resource, Api

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True

api = Api(app)

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
