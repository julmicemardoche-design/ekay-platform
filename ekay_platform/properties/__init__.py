from flask import Blueprint

properties = Blueprint('properties', __name__)

from . import routes, forms, errors
