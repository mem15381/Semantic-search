from flask import Flask

app = Flask(__name__)


@app.route('/')
def home():
    return 'Hello Wonderful People!'


@app.route('/about')
def about():
    return 'This is a tutorial Flask app on serving routes'