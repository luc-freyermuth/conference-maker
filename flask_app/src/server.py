from flask import Flask
from routes import routes

from config import get_conference_and_modules_path, get_gui_path

server = Flask(__name__, static_url_path='/static', static_folder=get_conference_and_modules_path(), template_folder=get_gui_path())
server.config['SEND_FILE_MAX_AGE_DEFAULT'] = 1
server.config['SECRET_KEY'] = 'TODO CHANGE THIS WHEN RELEASING IN PROD'

server.register_blueprint(routes)