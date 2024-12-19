from flask import Blueprint

mapa_bp = Blueprint('mapa_prefeitos2t', __name__, template_folder='templates')

from . import views
