from . import routes
from flask import render_template

@routes.route('/library')
def library_landing():
    return render_template('library.html')