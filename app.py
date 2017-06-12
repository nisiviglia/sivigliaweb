from flask import Flask, render_template
app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True

#########################
# Routes
#########################

@app.route("/")
def main():
    return render_template('index.html')


#########################
# End Routes
#########################
if __name__ == "__main__":
    app.run(debug = True, port = 5000)
