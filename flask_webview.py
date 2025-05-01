from flask import Flask
import webview

server = Flask(__name__, static_folder='.', template_folder='.')
webview.create_window('My first pywebview application', server)
webview.start()