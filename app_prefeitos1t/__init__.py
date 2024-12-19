# app_prefeitos1t/__init__.py
from flask import Blueprint

prefeitos1t = Blueprint('prefeitos1t', __name__, template_folder='templates')

from . import views  # Importa as rotas definidas em 'views.py'
