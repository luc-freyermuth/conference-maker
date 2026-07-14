from flask import Blueprint
routes = Blueprint('routes', __name__)

from .home import *
from .maker import *
from .library import *
from .details import *