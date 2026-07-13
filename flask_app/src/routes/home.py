from . import routes
from flask import render_template

@routes.route('/')
def home():
    return render_template('index.html')