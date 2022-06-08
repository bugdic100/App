############## IMPORTA BIBLIOTECAS ##############
from flask_login import current_user, login_required,LoginManager, login_user,UserMixin, logout_user
from flask import Flask,render_template, session, url_for, redirect, request,flash,abort,sessions
from datetime import date,datetime,timedelta
from psycopg2 import connect
import jinja2
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash,check_password_hash

############## CONEXÃO DO BANCO DE DADOS ##############
conn = connect(
    host="postgres",#192.168.1.5
    database="postgres",
    port = "5432",
    user="postgres",
    password="postgres",
    options="-c search_path=dbo,desafio_python")
    
cur = conn.cursor()

############## CONFIGURAÇÕES APP ##############

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:postgres@postgres:5432/postgres"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["SESSION_PERMANENT"] = False
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

db = SQLAlchemy(app)

class User(db.Model,UserMixin):

    __tablename__ = "usuario"

    id_usuario = db.Column(db.String(64),primary_key = True)
    nome_usuario = db.Column(db.String(64),unique = True)
    tipo = db.Column(db.String(5))
    senha = db.Column(db.String(64))

    def __init__(self,id_usuario,nome_usuario,tipo,senha):
        self.id_usuario = id_usuario
        self.nome_usuario = nome_usuario
        self.tipo = tipo
        self.senha = senha

    def is_authenticated(self):
        return True

    def is_active(self):   
        return True           

    def is_anonymous(self):
        return False          

    def get_id(self):         
        return str(self.id_usuario)

############## FUNÇÕES DE APOIO ##############
#retorna objeto usuário
def check_userobj(id_usuario):
    query = "SELECT * FROM usuario WHERE id_usuario = '{}'"
    cur.execute(query.format(id_usuario))
    user = cur.fetchone()
    user = User(id_usuario=user[0],nome_usuario = user[1],senha= user[2],tipo = user[3])
    return user

#id
def check_userid(id_usuario):
    query = "SELECT * FROM usuario WHERE id_usuario = '{}'"
    cur.execute(query.format(id_usuario))
    user = cur.fetchone()
    if user:
        return True
    else:
        return False

#nome_usuario
def check_username(nome_usuario):
    query = "SELECT * FROM usuario WHERE nome_usuario = '{}'"
    cur.execute(query.format(nome_usuario))
    user = cur.fetchone()
    if user:
        return True
    else:
        return False

#recurso
def check_recurso(nome_recurso):
    query = "SELECT * FROM recurso WHERE nome_recurso = '{}'"
    cur.execute(query.format(nome_recurso))
    recurso = cur.fetchone()
    if recurso:
        return True
    else:
        return False

#emprestimo_usuario
def check_usuario_recurso(id_usuario):
    query = "SELECT * FROM emprestimo WHERE id_usuario = '{}'"
    cur.execute(query.format(id_usuario))
    recurso = cur.fetchone()
    return recurso

#emprestimo_recurso
def check_recurso(nome_recurso):
    query = "SELECT * FROM recurso WHERE nome_recurso = '{}'"
    cur.execute(query.format(nome_recurso))
    recurso = cur.fetchone()
    return recurso

############## INSERE USUÁRIO ADMINISTRADOR ##############
id_usuario = '01'
nome_usuario = 'root'
if not check_userid(id_usuario) and not check_username(nome_usuario):
    senha = 'senha'
    tipo = 'admin'
    senha_hash = generate_password_hash(senha)

    cur.execute('INSERT INTO usuario (id_usuario,nome_usuario,senha,tipo)'
    'VALUES (%s, %s, %s, %s)',
    (id_usuario,nome_usuario,senha_hash,tipo))
    conn.commit()  

del id_usuario,nome_usuario

############## ROTAS DO SISTEMA ##############

@login_manager.user_loader
def load_user(id_usuario):
    return check_userobj(id_usuario=id_usuario)

############## AUTENTICAÇÃO

@app.route('/', methods=['GET'])
def home():
    return render_template("home.html")

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        nome_usuario = request.form['nome_usuario']
        senha = request.form['senha']
        query = "SELECT * FROM usuario WHERE nome_usuario = '{}';"
        cur.execute(query.format(nome_usuario))
        user = cur.fetchone()
        if user and check_password_hash(user[2],senha):
            user = User(id_usuario=user[0],nome_usuario = user[1],senha= user[2],tipo = user[3])
            login_user(user)
            if user.tipo == "admin":
                next = "admin_page"
            else:
                next = "user_page"
            return redirect(next)
        else:
            return """<h3 style="color:Red;">Usuário ou senha incorretos</h3>"""
    return render_template('login.html')

@app.route('/logout',methods=['GET','POST'])
@login_required
def logout():
    session.clear()
    logout_user()
    return render_template('home.html')

@app.route('/admin_page', methods=['GET','POST'])
@login_required
def admin():
    if current_user.tipo == "admin":
        return render_template('admin_page.html')
    else:
        return redirect(url_for('login'))

@app.route('/user_page', methods=['GET','POST'])
@login_required
def user():
    if current_user.tipo == "comum":
        return render_template('user_page.html')
    else:
        return redirect(url_for('login'))

############## CRUD USUÁRIO

@app.route('/criar_usuario', methods=['GET','POST'])
@login_required
def criar_usuario():
    if current_user.tipo == "admin":
        if request.method == 'POST':
            id_usuario = request.form['id_usuario']
            nome_usuario = request.form['nome_usuario']
            senha = request.form['senha']
            tipo = request.form['tipo']
            if check_userid(id_usuario) or check_username(nome_usuario):
                return """<h3 style="color:Red;">ID ou nome de usuário já existe</h3>"""
            else:
                senha_hash = generate_password_hash(senha)
                cur.execute('INSERT INTO usuario (id_usuario,nome_usuario,senha,tipo)'
                'VALUES (%s, %s, %s, %s)',
                (id_usuario,nome_usuario,senha_hash,tipo))
                conn.commit()  
                return """<h3 style="color:Green;">Usuário criado com sucesso!</h3>"""
        return render_template('create_user.html')
    else:
        return redirect(url_for('login'))

@app.route('/listar_usuario', methods=['GET','POST'])
@login_required
def listar_usuario():
    if request.method == "POST":
        nome_usuario = request.form['user_name']
        query = 'SELECT * FROM usuario'
        if nome_usuario:
            query = query + " WHERE nome_usuario = '"+nome_usuario+"';"
        cur.execute(query)
        result = cur.fetchall()
        return render_template('read_user.html',result = result)
    return render_template('read_user.html')

@app.route('/atualizar_usuario', methods=['GET','POST'])
@login_required
def atualizar_usuario():
    if current_user.tipo == 'admin':
        if request.method == "POST":
            id_usuario = request.form['id_usuario']
            column = request.form['campo']
            new_value = request.form['new_value']
            usuario = check_userid(id_usuario)
            if usuario:
                if column == "Tipo":
                    column = "tipo"
                elif column == "Senha":
                    column = "senha"
                elif column == "Nome":
                    column = "nome_usuario"
                query = "UPDATE usuario SET {} = '{}' WHERE id_usuario = '{}';"
                cur.execute(query.format(column,new_value,id_usuario))
                conn.commit()
                return """<h3 style="color:Green;">Dado atualizado com sucesso.</3>"""
            else:
                return """<h3 style="color:Red;">Usuário não existe ou dado não inserido</3>"""
        return render_template('update_user.html')
    else:
        return redirect(url_for('login'))

@app.route('/excluir_usuario', methods=['GET','POST'])
@login_required
def excluir_usuario():
    if current_user.tipo == 'admin':
        if request.method == "POST":
            id_usuario = request.form['id_usuario']
            if check_userid(id_usuario):
                query = "DELETE FROM usuario WHERE id_usuario = '{}';"
                cur.execute(query.format(id_usuario))
                conn.commit()
                return """<h3 style="color:Green;">Usuário deletado com sucesso.</3>"""
            else:
                return """<h3 style="color:Red;">Usuário não existe ou dado não inserido</3>"""
        return render_template('delete_user.html')
    else:
        return redirect(url_for('login'))

############## CRUD RECURSO

@app.route('/criar_recurso', methods=['GET','POST'])
@login_required
def criar_recurso():
    if current_user.tipo == "admin":
        if request.method == "POST":
            nome_recurso = request.form['nome_recurso']
            qtde_recurso = request.form['qtde_recurso']
            if check_recurso(nome_recurso) or nome_recurso == "" or qtde_recurso == "" or int(qtde_recurso) < 0:
                return """<h3 style="color:Red;">O recurso já existe ou dados incorretos</h3>"""
            else:
                cur.execute('INSERT INTO recurso (nome_recurso, qtde_recurso)'
                'VALUES (%s, %s)',
                (nome_recurso,qtde_recurso))
                conn.commit()
                return """<h3 style="color:Green;">Recurso incluído com sucesso</h3>"""
        return render_template('create_rec.html')
    else:
        return redirect(url_for('login'))

@app.route('/listar_recurso', methods=['GET','POST'])
@login_required
def listar_recurso():
    if request.method == "POST":
        nome_recurso = request.form['nome_recurso']
        query = "SELECT * FROM recurso"
        if nome_recurso:
            query = query + " WHERE nome_recurso = '" + nome_recurso + "';"
        cur.execute(query)
        result = cur.fetchall()
        return render_template('read_rec.html',result = result)
    return render_template('read_rec.html')

@app.route('/atualizar_recurso', methods=['GET','POST'])
@login_required
def atualizar_recurso():
    if current_user.tipo == 'admin':
        if request.method == "POST":
            nome_recurso = request.form['nome_recurso']
            query = "SELECT * FROM recurso WHERE nome_recurso = '{}';"
            cur.execute(query.format(nome_recurso))
            result = cur.fetchall()
            qtde = result[0][1]
            if result and qtde > 0:
                qtde_recurso = int(request.form['qtde_recurso'])
                valor = qtde + qtde_recurso
                query = 'UPDATE recurso SET qtde_recurso = ' + str(valor) + " WHERE nome_recurso = '" + nome_recurso + "';"
                cur.execute(query)
                conn.commit()
                return """<h3 style="color:Green;">Recurso atualizado com sucesso.</h3>"""
            else:
                return """<h3 style="color:Red;">Recurso não existe, dado não inserido ou quantidade negativa</3>"""
        return render_template('update_rec.html')
    else:
        return redirect(url_for('login'))

@app.route('/excluir_recurso', methods=["GET","POST"])
@login_required
def excluir_recurso():
    if current_user.tipo == 'admin':
        if request.method == "POST":
            nome_recurso = request.form['nome_recurso']
            if check_recurso(nome_recurso):
                query = "DELETE FROM recurso WHERE nome_recurso = '{}';"
                cur.execute(query.format(nome_recurso))
                conn.commit()
                return """<h3 style="color:Green;">Recurso excluído com sucesso.</h3>"""
            else:
                return """<h3 style="color:Red;">Recurso não existe ou dado não inserido</h3>"""
        return render_template('delete_rec.html')
    else:
        return redirect(url_for('login'))

############## GESTÃO RECURSOS

@app.route('/alugar_recurso', methods=['GET','POST'])
@login_required
def alugar_recurso():
    if current_user.tipo == 'comum':
        if request.method == "POST":
            id_usuario = current_user.id_usuario
            nome_recurso = request.form['nome_recurso']
            qtde_recurso = request.form['qtde_recurso']
            query_recurso = "SELECT * FROM recurso WHERE nome_recurso = '{}';"
            cur.execute(query_recurso.format(nome_recurso))
            result = cur.fetchall()
            if result:
                if result[0][1] >= int(qtde_recurso):
                    remain = result[0][1]-int(qtde_recurso)
                    hoje = date.today()
                    entrega = hoje + timedelta(days=5)
                    hoje = hoje.strftime("%d/%m/%Y")
                    entrega = entrega.strftime("%d/%m/%Y")
                    query_emprestimo = "INSERT INTO emprestimo VALUES ('"+str(id_usuario)+"','"+nome_recurso+"','"+str(qtde_recurso)+"','"+str(hoje)+"','"+str(entrega)+"','emprestado');"
                    cur.execute(query_emprestimo)
                    conn.commit()
                    query_atualiza_recurso = "UPDATE recurso SET qtde_recurso = " + str(remain) + " WHERE nome_recurso = '"+nome_recurso+"';"                
                    cur.execute(query_atualiza_recurso)
                    conn.commit()
                    return """<h3 style="color:Green;">Recurso alugado com sucesso.</3>"""
                else:
                    return """<h3 style="color:Red;">Recurso não está disponível no momento.</3>"""
            else:
                return """<h3 style="color:Red;">Recurso não existe ou não está disponível no momento.</3>"""
        return render_template('rent_rec.html')
    else:
        return redirect(url_for('login'))

@app.route('/devolver_recurso', methods=['GET','POST'])
@login_required
def devolver_recurso():
    if current_user.tipo == 'comum':
        if request.method == "POST":
            id_usuario = current_user.id_usuario
            nome_recurso = request.form['nome_recurso']
            query_emprestimo = "SELECT * FROM emprestimo WHERE id_usuario = '{}' AND nome_recurso = '{}' AND status = 'emprestado';"
            cur.execute(query_emprestimo.format(id_usuario,nome_recurso))
            result = cur.fetchall()
            if result:
                qtde_recurso = result[0][2]
                query_devolucao = "UPDATE emprestimo SET status = 'devolvido' WHERE id_usuario = '"+id_usuario+"' AND nome_recurso = '"+nome_recurso+"';"
                cur.execute(query_devolucao)
                conn.commit()
                query_atualiza_recurso = "UPDATE recurso SET qtde_recurso = qtde_recurso + '"+str(qtde_recurso)+"' WHERE nome_recurso = '"+nome_recurso+"';"
                cur.execute(query_atualiza_recurso)
                conn.commit()
                return """<h3 style="color:Green;">Recurso devolvido com sucesso.</3>"""
            else:
                return """<h3 style="color:Red;">Não existe empréstimo para este usuário neste recurso.</3>"""
        return render_template('devolver_rec.html')
    else:
        return redirect(url_for('login'))

@app.route('/listar_aluguel', methods=['GET','POST'])
@login_required
def listar_aluguel():
    if current_user.tipo ==  "admin":
        if request.method == "POST":
            id_usuario = request.form['id_usuario']
            nome_recurso = request.form['nome_recurso']
            qtde_recurso = request.form['qtde_recurso']
            data_inicio = request.form['data_inicio']
            data_fim = request.form['data_fim']
            status = request.form['status']

            colunas_final = [id_usuario,nome_recurso,qtde_recurso,data_inicio,data_fim,status]
            filtro_final = ['id_usuario','nome_recurso','qtde_recurso','data_inicio','data_fim','status']

            colunas = []
            filtro = []
            #define colunas válidas
            for i in range(len(colunas_final)):
                if colunas_final[i]:
                    colunas.append(colunas_final[i])
                    filtro.append(filtro_final[i])

            #query data
            query_data = ""

            cont = 0

            if 'data_inicio' in filtro and 'data_fim' in filtro:
                for i in range(len(filtro)):
                    if filtro[i] == "data_inicio" or filtro[i] == "data_fim":
                        if cont == 0:
                            query_data += filtro[i] + " = '"+colunas[i]
                            cont+=1
                        else:
                            query_data += " AND "+filtro[i] + " <= " + "'"+colunas[i]+"'"
                else:
                    filtro.remove("data_inicio")
                    filtro.remove("data_fim")
                    colunas.remove(data_inicio)
                    colunas.remove(data_fim)

            #query others column
            query_others = ""

            j = 0

            if len(colunas) == 0:
                query_others = ""
            elif len(colunas) == 1:
                query_others += filtro[0] + " = '" + colunas[0] + "'"
            else:
                for col in range(len(colunas)):
                    if j == 0:
                        query_others += filtro[col] + " = '" + colunas[col] + "'"
                        j+=1
                    else:
                        query_others += " AND " + filtro[col] + " = '" + colunas[col] + "' "

            #monta query final
            queries = []

            query_final = "SELECT * FROM emprestimo "

            if query_data:
                queries.append(query_data)
            if query_others:
                queries.append(query_others)
            length = 0
            if len(queries) > 0:
                for i in queries:
                    if length == 0:
                        if i:
                            query_final += "WHERE "
                            query_final += i
                            length+=1
                    else:
                        if i:
                            query_final += " AND " + i
                            length+=1
            cur.execute(query_final)
            result = cur.fetchall()
            return render_template('listar_aluguel.html',result=result)
        return render_template('listar_aluguel.html')
    if current_user.tipo == "comum":
        if request.method == "POST":
            id_usuario = current_user.id_usuario
            nome_recurso = request.form['nome_recurso']
            qtde_recurso = request.form['qtde_recurso']
            data_inicio = request.form['data_inicio']
            data_fim = request.form['data_fim']
            status = request.form['status']

            colunas_final = [id_usuario,nome_recurso,qtde_recurso,data_inicio,data_fim,status]
            filtro_final = ['id_usuario','nome_recurso','qtde_recurso','data_inicio','data_fim','status']

            colunas = []
            filtro = []
            #define colunas válidas
            for i in range(len(colunas_final)):
                if colunas_final[i]:
                    colunas.append(colunas_final[i])
                    filtro.append(filtro_final[i])

            #query data
            query_data = ""

            cont = 0

            if 'data_inicio' in filtro and 'data_fim' in filtro:
                for i in range(len(filtro)):
                    if filtro[i] == "data_inicio" or filtro[i] == "data_fim":
                        if cont == 0:
                            query_data += filtro[i] + " = '"+colunas[i]
                            cont+=1
                        else:
                            query_data += " AND "+filtro[i] + " <= " + "'"+colunas[i]+"'"
                else:
                    filtro.remove("data_inicio")
                    filtro.remove("data_fim")
                    colunas.remove(data_inicio)
                    colunas.remove(data_fim)

            #query others column
            query_others = ""

            j = 0

            if len(colunas) == 0:
                query_others = ""
            elif len(colunas) == 1:
                query_others += filtro[0] + " = '" + colunas[0] + "'"
            else:
                for col in range(len(colunas)):
                    if j == 0:
                        query_others += filtro[col] + " = '" + colunas[col] + "'"
                        j+=1
                    else:
                        query_others += " AND " + filtro[col] + " = '" + colunas[col] + "' "

            #monta query final
            queries = []

            query_final = "SELECT * FROM emprestimo "

            if query_data:
                queries.append(query_data)
            if query_others:
                queries.append(query_others)
            length = 0
            if len(queries) > 0:
                for i in queries:
                    if length == 0:
                        if i:
                            query_final += "WHERE "
                            query_final += i
                            length+=1
                    else:
                        if i:
                            query_final += " AND " + i
                            length+=1
            cur.execute(query_final)
            result = cur.fetchall()
            return render_template('listar_aluguel.html',result=result)
        return render_template('listar_aluguel.html')
    
if __name__ == '__main__':
    app.config['SECRET_KEY'] = 'gerenciador_de_recursos'
    app.run(host="0.0.0.0",port=4000)
    app.run()
