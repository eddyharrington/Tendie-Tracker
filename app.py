from flask import Flask
from datetime import datetime

app = Flask(__name__)


@app.route("/")
def home():
    now = datetime.now()
    return "Hello, Tendie Trackers! The day is: " + now.strftime('%A, %d %B, %Y at %X')
