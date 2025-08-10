from flask import Flask, render_template, request, make_response
from flask_sqlalchemy import SQLAlchemy

app = Flask('cliqueaqui')
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:ket270@localhost/cliqueaqui'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Rota para a página inicial
@app.route('/')
def index():
    return render_template('index.html')

# Rota para o menu de navegação
@app.route('/menu')
def menu():
    return render_template('menu.html')

# Rotas da seção 'Cadastros'
@app.route('/cadastro/usuario')
def cadastro_usuario():
    return render_template('cadastro_usuario.html')

@app.route('/cadastro/anuncio')
def cadastro_anuncio():
    return render_template('cadastro_anuncio.html')

# Rotas da seção 'Anúncios' (navegação)
@app.route('/anuncios/pergunta')
def anuncio_pergunta():
    return render_template('anuncio_pergunta.html')

@app.route('/anuncios/compra')
def anuncio_compra():
    return render_template('anuncio_compra.html')

@app.route('/anuncios/favoritos')
def anuncio_favoritos():
    return render_template('anuncio_favoritos.html')

# Rotas da seção 'Configurações'
@app.route('/configuracoes/categoria')
def config_categoria():
    return render_template('config_categoria.html')

# Rotas da seção 'Relatórios'
@app.route('/relatorios/vendas')
def relatorio_vendas():
    return render_template('relatorio_vendas.html')

@app.route('/relatorios/compras')
def relatorio_compras():
    return render_template('relatorio_compras.html')

if __name__ == '__main__':
    app.run(debug=True)