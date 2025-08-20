from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask import make_response
from flask import redirect
from flask import url_for
from flask_login import (current_user, LoginManager,
                             login_user, logout_user,
                             login_required)
import hashlib

app = Flask('cliqueaqui')
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://cliqueaqui_user:ket270@localhost:3306/cliqueaqui'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://ketsianechagas:shalom2016@ketsianechagas.mysql.pythonanywhere-services.com:3306/ketsianechagas$cliqueaqui'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'linuxnao'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = "Por favor, faça o login para acessar esta página."


db = SQLAlchemy(app)

@app.errorhandler(404)
def pagina_nao_encontrada(error):
    return render_template('pagnaoencontrada.html'), 404

@login_manager.user_loader
def load_user(id):
    return Usuario.query.get(id)


class Usuario(db.Model):
    __tablename__ = "usuario"
    id = db.Column('usu_id', db.Integer, primary_key=True)
    nome = db.Column('usu_nome', db.String(256))
    email = db.Column('usu_email', db.String(256))
    senha = db.Column('usu_senha', db.String(256))
    endereco = db.Column('usu_end', db.String(256))

    def __init__(self, nome, email, senha, endereco):
        self.nome = nome
        self.email = email
        self.senha = senha
        self.endereco = endereco

    def is_authenticated(self):
        return True
    def is_active(self):
        return True
    def is_anonymous(self):
        return False
    def get_id(self):
        return str(self.id)

class Categoria(db.Model):
    __tablename__ = "categoria"
    id = db.Column('cat_id', db.Integer, primary_key=True)
    nome = db.Column('cat_nome', db.String(256))
    desc = db.Column('cat_desc', db.String(256))

    def __init__(self, nome, desc):
        self.nome = nome
        self.desc = desc

class Anuncio(db.Model):
    __tablename__ = "anuncio"
    id = db.Column('anu_id', db.Integer, primary_key=True)
    nome = db.Column('anu_nome', db.String(256))
    desc = db.Column('anu_desc', db.String(256))
    qtd = db.Column('anu_qtd', db.Integer)
    preco = db.Column('anu_preco', db.Float)
    cat_id = db.Column('cat_id', db.Integer, db.ForeignKey("categoria.cat_id"))
    usu_id = db.Column('usu_id', db.Integer, db.ForeignKey("usuario.usu_id"))

    def __init__(self, nome, desc, qtd, preco, cat_id, usu_id):
        self.nome = nome
        self.desc = desc
        self.qtd = qtd
        self.preco = preco
        self.cat_id = cat_id
        self.usu_id = usu_id

class Pergunta(db.Model):
    __tablename__ = "pergunta"
    id = db.Column('per_id', db.Integer, primary_key=True)
    pergunta_texto = db.Column('pergunta_texto', db.String(256))
    resposta_texto = db.Column('resposta_texto', db.String(256))
    anu_id = db.Column('anu_id', db.Integer, db.ForeignKey("anuncio.anu_id"))
    usu_id = db.Column('usu_id', db.Integer, db.ForeignKey("usuario.usu_id"))

    def __init__(self, pergunta_texto, resposta_texto, anu_id, usu_id):
        self.pergunta_texto = pergunta_texto
        self.resposta_texto = resposta_texto
        self.anu_id = anu_id
        self.usu_id = usu_id

class Favorito(db.Model):
    __tablename__ = "favorito"
    id = db.Column('fav_id', db.Integer, primary_key=True)
    anu_id = db.Column('anu_id', db.Integer, db.ForeignKey("anuncio.anu_id"))
    usu_id = db.Column('usu_id', db.Integer, db.ForeignKey("usuario.usu_id"))

    def __init__(self, anu_id, usu_id):
        self.anu_id = anu_id
        self.usu_id = usu_id

class Compra(db.Model):
    __tablename__ = "compra"
    id = db.Column('com_id', db.Integer, primary_key=True)
    quantidade = db.Column('com_qtd', db.Integer)
    preco = db.Column('com_preco', db.Float)
    total = db.Column('com_total', db.Float)
    anu_id = db.Column('anu_id', db.Integer, db.ForeignKey("anuncio.anu_id"))
    usu_id = db.Column('usu_id', db.Integer, db.ForeignKey("usuario.usu_id"))

    def __init__(self, quantidade, preco, total, anu_id, usu_id):
        self.quantidade = quantidade
        self.preco = preco
        self.total = total
        self.anu_id = anu_id
        self.usu_id = usu_id


@app.route("/login", methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        senha_hash = hashlib.sha512(str(request.form.get('senha')).encode("utf-8")).hexdigest()
        user = Usuario.query.filter_by(email=email, senha=senha_hash).first()
        if user:
            login_user(user)
            flash("Login realizado com sucesso!", "success")
            return redirect(url_for('menu'))
        else:
            flash("E-mail ou senha incorretos.", "error")
            return redirect(url_for('login'))
    return render_template('login.html')

# Rota de logout
@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('login'))

# Rotas de Navegação
@app.route('/')
def index():
    anuncios = Anuncio.query.all()
    return render_template('index.html', anuncios=anuncios)

@app.route('/menu')
@login_required
def menu():
    return render_template('menu.html')

# -- CRUD Usuario
@app.route('/cadastro/usuario')
@login_required
def lista_usuario():
    usuarios = Usuario.query.all()
    return render_template('cadastro_usuario.html', usuarios=usuarios, titulo='Usuários')

@app.route('/cadastro/novo', methods=['GET'])
def exibir_cadastro():
    return render_template('novo_usuario.html')

@app.route('/cadastro/novousuario', methods=['POST'])
def novo_usuario():
    nome = request.form.get('nome')
    email = request.form.get('email')

    senha_do_formulario = request.form.get('senha')
    senha_hash = hashlib.sha512(senha_do_formulario.encode("utf-8")).hexdigest()

    endereco = request.form.get('endereco')
    novo_usuario = Usuario(nome, email, senha_hash, endereco)
    db.session.add(novo_usuario)
    db.session.commit()
    flash("Cadastro realizado com sucesso! Faça login para continuar.", "success")
    return redirect(url_for('login'))

@app.route('/cadastro/editarusuario/<int:id>')
@login_required
def editar_usuario(id):
    usuario = Usuario.query.get(id)
    return render_template('editar_usuario.html', usuario=usuario, titulo='Editar Usuário')

@app.route('/cadastro/salvarusuario/<int:id>', methods=['POST'])
@login_required
def salvar_usuario(id):
    usuario = Usuario.query.get(id)
    usuario.nome = request.form.get('nome')
    usuario.email = request.form.get('email')

    senha_form = request.form.get('senha')
    if senha_form:
        usuario.senha = hashlib.sha512(senha_form.encode("utf-8")).hexdigest()

    usuario.endereco = request.form.get('endereco')
    db.session.commit()
    return redirect(url_for('lista_usuario'))

@app.route('/cadastro/excluirusuario/<int:id>')
@login_required
def excluir_usuario(id):
    usuario = Usuario.query.get(id)
    db.session.delete(usuario)
    db.session.commit()
    return redirect(url_for('lista_usuario'))

# -- CRUD Categoria
@app.route('/configuracoes/categoria')
@login_required
def lista_categoria():
    categorias = Categoria.query.all()
    return render_template('config_categoria.html', categorias=categorias, titulo='Categorias')

@app.route('/configuracoes/novacategoria', methods=['POST'])
@login_required
def nova_categoria():
    nome = request.form.get('nome')
    desc = request.form.get('desc')
    nova_categoria = Categoria(nome, desc)
    db.session.add(nova_categoria)
    db.session.commit()
    return redirect(url_for('lista_categoria'))

@app.route('/configuracoes/editarcategoria/<int:id>')
@login_required
def editar_categoria(id):
    categoria = Categoria.query.get(id)
    return render_template('editar_categoria.html', categoria=categoria, titulo='Editar Categoria')

@app.route('/configuracoes/salvarcategoria/<int:id>', methods=['POST'])
@login_required
def salvar_categoria(id):
    categoria = Categoria.query.get(id)
    categoria.nome = request.form.get('nome')
    categoria.desc = request.form.get('desc')
    db.session.commit()
    return redirect(url_for('lista_categoria'))

@app.route('/configuracoes/excluircategoria/<int:id>')
@login_required
def excluir_categoria(id):
    categoria = Categoria.query.get(id)
    db.session.delete(categoria)
    db.session.commit()
    return redirect(url_for('lista_categoria'))

# -- CRUD Anuncio
@app.route('/anuncios')
def anuncios_publicos():
    anuncios = Anuncio.query.all()
    return render_template('anuncios_publicos.html', anuncios=anuncios, titulo='Anúncios')

@app.route('/anuncios/anuncio')
@login_required
def lista_anuncio():
    anuncios = Anuncio.query.all()
    categorias = Categoria.query.all()
    usuarios = Usuario.query.all()
    return render_template('cadastro_anuncio.html', anuncios=anuncios, categorias=categorias, usuarios=usuarios, titulo='Anúncios')

@app.route('/anuncios/novoanuncio', methods=['POST'])
@login_required
def novo_anuncio():
    nome = request.form.get('nome')
    desc = request.form.get('desc')
    qtd = request.form.get('qtd')
    preco = request.form.get('preco')
    cat_id = request.form.get('cat_id')
    usu_id = request.form.get('usu_id')
    novo_anuncio = Anuncio(nome, desc, qtd, preco, cat_id, usu_id)
    db.session.add(novo_anuncio)
    db.session.commit()
    return redirect(url_for('lista_anuncio'))

@app.route('/anuncios/editaranuncio/<int:id>')
@login_required
def editar_anuncio(id):
    anuncio = Anuncio.query.get(id)
    categorias = Categoria.query.all()
    usuarios = Usuario.query.all()
    return render_template('editar_anuncio.html', anuncio=anuncio, categorias=categorias, usuarios=usuarios, titulo='Editar Anúncio')

@app.route('/anuncios/salvaranuncio/<int:id>', methods=['POST'])
@login_required
def salvar_anuncio(id):
    anuncio = Anuncio.query.get(id)
    anuncio.nome = request.form.get('nome')
    anuncio.desc = request.form.get('desc')
    anuncio.qtd = request.form.get('qtd')
    anuncio.preco = request.form.get('preco')
    anuncio.cat_id = request.form.get('cat_id')
    anuncio.usu_id = request.form.get('usu_id')
    db.session.commit()
    return redirect(url_for('lista_anuncio'))

@app.route('/anuncios/excluiranuncio/<int:id>')
@login_required
def excluir_anuncio(id):
    anuncio = Anuncio.query.get(id)
    db.session.delete(anuncio)
    db.session.commit()
    return redirect(url_for('lista_anuncio'))

# -- CRUD Pergunta
@app.route('/anuncios/pergunta')
@login_required
def lista_pergunta():
    perguntas = Pergunta.query.all()
    anuncios = Anuncio.query.all()
    usuarios = Usuario.query.all()
    return render_template('anuncio_pergunta.html', perguntas=perguntas, anuncios=anuncios, usuarios=usuarios, titulo='Perguntas')

@app.route('/anuncios/novapergunta', methods=['POST'])
@login_required
def nova_pergunta():
    pergunta_texto = request.form.get('pergunta_texto')
    resposta_texto = request.form.get('resposta_texto')
    anu_id = request.form.get('anu_id')
    usu_id = request.form.get('usu_id')
    nova_pergunta = Pergunta(pergunta_texto, resposta_texto, anu_id, usu_id)
    db.session.add(nova_pergunta)
    db.session.commit()
    return redirect(url_for('lista_pergunta'))

@app.route('/anuncios/editarpergunta/<int:id>')
@login_required
def editar_pergunta(id):
    pergunta = Pergunta.query.get(id)
    anuncios = Anuncio.query.all()
    usuarios = Usuario.query.all()
    return render_template('editar_pergunta.html', pergunta=pergunta, anuncios=anuncios, usuarios=usuarios, titulo='Editar Pergunta')

@app.route('/anuncios/salvarpergunta/<int:id>', methods=['POST'])
@login_required
def salvar_pergunta(id):
    pergunta = Pergunta.query.get(id)
    pergunta.pergunta_texto = request.form.get('pergunta_texto')
    pergunta.resposta_texto = request.form.get('resposta_texto')
    pergunta.anu_id = request.form.get('anu_id')
    pergunta.usu_id = request.form.get('usu_id')
    db.session.commit()
    return redirect(url_for('lista_pergunta'))

@app.route('/anuncios/excluirpergunta/<int:id>')
@login_required
def excluir_pergunta(id):
    pergunta = Pergunta.query.get(id)
    db.session.delete(pergunta)
    db.session.commit()
    return redirect(url_for('lista_pergunta'))

# -- CRUD Favoritos
@app.route('/anuncios/favoritos')
@login_required
def lista_favoritos():
    favoritos = Favorito.query.all()
    anuncios = Anuncio.query.all()
    usuarios = Usuario.query.all()
    return render_template('anuncio_favoritos.html', favoritos=favoritos, anuncios=anuncios, usuarios=usuarios, titulo='Favoritos')

@app.route('/anuncios/novofavorito', methods=['POST'])
@login_required
def novo_favorito():
    anu_id = request.form.get('anu_id')
    usu_id = request.form.get('usu_id')
    novo_favorito = Favorito(anu_id, usu_id)
    db.session.add(novo_favorito)
    db.session.commit()
    return redirect(url_for('lista_favoritos'))

@app.route('/anuncios/excluirfavorito/<int:id>')
@login_required
def excluir_favorito(id):
    favorito = Favorito.query.get(id)
    db.session.delete(favorito)
    db.session.commit()
    return redirect(url_for('lista_favoritos'))

# -- CRUD Compra
@app.route('/anuncios/compra')
@login_required
def lista_compra():
    compras = Compra.query.all()
    anuncios = Anuncio.query.all()
    usuarios = Usuario.query.all()
    return render_template('anuncio_compra.html', compras=compras, anuncios=anuncios, usuarios=usuarios, titulo='Compras')

@app.route('/anuncios/novacompra', methods=['POST'])
@login_required
def nova_compra():
    quantidade = request.form.get('quantidade')
    preco = request.form.get('preco')
    total = float(quantidade) * float(preco)
    anu_id = request.form.get('anu_id')
    usu_id = request.form.get('usu_id')
    nova_compra = Compra(quantidade, preco, total, anu_id, usu_id)
    db.session.add(nova_compra)
    db.session.commit()
    return redirect(url_for('lista_compra'))

@app.route('/anuncios/editarcompra/<int:id>')
@login_required
def editar_compra(id):
    compra = Compra.query.get(id)
    anuncios = Anuncio.query.all()
    usuarios = Usuario.query.all()
    return render_template('editar_compra.html', compra=compra, anuncios=anuncios, usuarios=usuarios, titulo='Editar Compra')

@app.route('/anuncios/salvarcompra/<int:id>', methods=['POST'])
@login_required
def salvar_compra(id):
    compra = Compra.query.get(id)
    compra.quantidade = request.form.get('quantidade')
    compra.preco = request.form.get('preco')
    compra.total = float(compra.quantidade) * float(compra.preco)
    compra.anu_id = request.form.get('anu_id')
    compra.usu_id = request.form.get('usu_id')
    db.session.commit()
    return redirect(url_for('lista_compra'))

@app.route('/anuncios/excluircompra/<int:id>')
@login_required
def excluir_compra(id):
    compra = Compra.query.get(id)
    db.session.delete(compra)
    db.session.commit()
    return redirect(url_for('lista_compra'))

# Rotas de Relatórios
@app.route('/relatorios/vendas')
@login_required
def relatorio_vendas():
    vendas = db.session.query(Compra, Anuncio, Usuario).join(Anuncio, Compra.anu_id == Anuncio.id).join(Usuario, Compra.usu_id == Usuario.id).all()
    return render_template('relatorio_vendas.html', vendas=vendas)

@app.route('/relatorios/compras')
@login_required
def relatorio_compras():
    compras = db.session.query(Compra, Anuncio, Usuario).join(Anuncio, Compra.anu_id == Anuncio.id).join(Usuario, Compra.usu_id == Usuario.id).all()
    return render_template('relatorio_compras.html', compras=compras)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)