from flask import Blueprint

# Blueprint do mapa dos vereadores
vereadores_bp = Blueprint('vereadores', __name__, template_folder='templates')

from . import views  # A importação do arquivo 'views.py' para registrar as rotas
