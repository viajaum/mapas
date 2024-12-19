import os
from flask import Flask, render_template
from app_prefeitos1t import prefeitos1t
from app_prefeitos2t import mapa_bp
from app_vereadores import vereadores_bp  # Corrigindo a importação do Blueprint

app = Flask(__name__)

# Registrando Blueprints
app.register_blueprint(prefeitos1t, url_prefix='/prefeitos1t')
app.register_blueprint(mapa_bp, url_prefix='/prefeitos2t')
app.register_blueprint(vereadores_bp, url_prefix='/vereadores')  # Adicionando o Blueprint correto

@app.route('/')
def home():
    return render_template('index.html')  # Página principal

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # Pega a porta do ambiente
    app.run(host='0.0.0.0', port=port)  # Bind na porta correta
