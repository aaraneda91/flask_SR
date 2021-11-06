from flask import Blueprint

operacion_bp = Blueprint('operacion', __name__, template_folder='templates')

from . import routes