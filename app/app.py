from flask import Flask,render_template, url_for, redirect, request
from datetime import date,datetime,timedelta
from psycopg2 import connect
import jinja2

conn = connect(
    host="postgres",#192.168.1.5
    database="postgres",#exercicio
    port = "5432",
    user="postgres",
    password="postgres",#docker
    options="-c search_path=dbo,desafio_python")

cur = conn.cursor()

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return render_template("home.html")

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        pwd = request.form['password']
        query = "SELECT * FROM usuario WHERE nome_usuario = '"+username+"' and senha = '"+pwd+"';"
        cur.execute(query)
        result = cur.fetchall()
        if result[0][3] == "admin":
            return redirect('/admin_page')
        elif result[0][3] == "comum":
            return redirect('/user_page')
        else:
            return """<h3>Dados incorretos ou Usuário não existe</h3>"""
    return render_template('login.html')

@app.route('/logout',methods=['GET','POST'])
def logout():
    pass

@app.route('/admin_page', methods=['GET','POST'])
def admin():
    return render_template('admin_page.html')

@app.route('/user_page', methods=['GET','POST'])
def user():
    return render_template('user_page.html')
    
@app.route('/criar_recurso', methods=['GET','POST'])
def criar_recurso():
    if request.method == "POST":
        nome_recurso = request.form['nome_recurso']
        qtde_recurso = request.form['qtde_recurso']
        query_existe_recurso = "SELECT * FROM recurso WHERE nome_recurso = '"+nome_recurso+"';"
        cur.execute(query_existe_recurso)
        existe_recurso = cur.fetchall()
        if existe_recurso or nome_recurso == "" or qtde_recurso == "" or int(qtde_recurso) < 0:
            return """<h3 style="color:Red;">O recurso já existe ou dados incorretos</h3>"""
        else:
            cur.execute('INSERT INTO recurso (nome_recurso, qtde_recurso)'
            'VALUES (%s, %s)',
            (nome_recurso,qtde_recurso))
            conn.commit()
            return """<h3 style="color:Green;>Recurso incluído com sucesso</h3>"""
    return render_template('create_rec.html')

@app.route('/criar_usuario', methods=['GET','POST'])
def criar_usuario():
    if request.method == "POST":
        user_id = request.form['user_id']
        query_existe_usuario = "SELECT * FROM usuario WHERE id_usuario = '"+user_id+"';"
        cur.execute(query_existe_usuario)
        existe_usuario = cur.fetchall()
        user_name = request.form['user_name']
        user_pwd = request.form['user_pwd']
        user_type = request.form['user_type']
        if existe_usuario or user_name == "" or user_pwd == "" or user_type == "":
            return """<h3 style="color:Red;">Usuário já existe ou dado não inserido</h3>"""
        else:
            cur.execute('INSERT INTO usuario (id_usuario,nome_usuario,senha,tipo)'
            'VALUES (%s, %s, %s, %s)',
            (user_id,user_name,user_pwd,user_type))
            conn.commit()
            return """<h3 style="color:Green;">Usuário inserido com sucesso</h3>"""
    return render_template('create_user.html')

@app.route('/listar_recurso', methods=['GET','POST'])
def listar_recurso():
    if request.method == "POST":
        nome_recurso = request.form['resource_name']
        query = 'SELECT * FROM recurso'
        if nome_recurso:
             query = query + " WHERE nome_recurso = '" + nome_recurso + "';"
        cur.execute(query)
        result = cur.fetchall()
        return render_template('read_rec.html',result = result)
    return render_template('read_rec.html')

@app.route('/listar_usuario', methods=['GET','POST'])
def listar_usuario():
    if request.method == "POST":
        user_name = request.form['user_name']
        query = 'SELECT * FROM usuario'
        if user_name:
            query = query + " WHERE nome_usuario = '" + user_name + "';"
        cur.execute(query)
        result = cur.fetchall()
        return render_template('read_user.html',result = result)
    return render_template('read_user.html')

@app.route('/atualizar_recurso', methods=['GET','POST'])
def atualizar_recurso():
    if request.method == "POST":
        nome_recurso = request.form['nome_recurso']
        query = "SELECT * FROM recurso WHERE nome_recurso = '"+nome_recurso+"';"
        cur.execute(query)
        result = cur.fetchall()
        qtde = result[0][1]
        if result and qtde > 0:
            qtde_recurso = int(request.form['qtde_recurso'])
            valor = qtde + qtde_recurso
            query = 'UPDATE recurso SET qtde_recurso = ' + str(valor) + " WHERE nome_recurso = '" + nome_recurso + "';"
            cur.execute(query)
            conn.commit()
            return """<h3 style="color:Green;">Recurso atualizado com sucesso.</3>"""
        else:
            return """<h3 style="color:Red;">Recurso não existe, dado não inserido ou quantidade negativa</3>"""
    return render_template('update_rec.html')

@app.route('/atualizar_usuario', methods=['GET','POST'])
def atualizar_usuario():
    if request.method == "POST":
        id_user = request.form['id_user']
        column = request.form['campo']
        new_value = request.form['new_value']
        query = "SELECT * FROM usuario WHERE id_usuario = '"+id_user+"';"
        cur.execute(query)
        result = cur.fetchall()
        if result:
            if column == "Tipo":
                column = "tipo"
            elif column == "Senha":
                column = "senha"
            elif column == "Nome":
                column = "nome_usuario"
            query = "UPDATE usuario SET "+column+" = '" + new_value + "' WHERE id_usuario = '"+id_user+"';"
            cur.execute(query)
            conn.commit()
            return """<h3 style="color:Green;">Dado atualizado com sucesso.</3>"""
        else:
            return """<h3 style="color:Red;">Usuário não existe ou dado não inserido</3>"""
    return render_template('update_user.html')

@app.route('/excluir_recurso', methods=["GET","POST"])
def excluir_recurso():
    if request.method == "POST":
        nome_recurso = request.form['nome_recurso']
        query = "SELECT * FROM recurso WHERE nome_recurso = '"+nome_recurso+"';"
        cur.execute(query)
        result = cur.fetchall()
        if result:
            query = "DELETE FROM recurso WHERE nome_recurso = '"+nome_recurso+"';"
            cur.execute(query)
            conn.commit()
            return """<h3 style="color:Green;">Recurso excluído com sucesso.</3>"""
        else:
            return """<h3 style="color:Red;">Recurso não existe ou dado não inserido</3>"""
    return render_template('delete_rec.html')

@app.route('/excluir_usuario', methods=['GET','POST'])
def excluir_usuario():
    if request.method == "POST":
        nome_usuario = request.form['user_name']
        query = "SELECT * FROM usuario WHERE nome_usuario = '"+nome_usuario+"' AND tipo = 'comum';"
        cur.execute(query)
        result = cur.fetchall()
        if result:
            query = "DELETE FROM usuario WHERE nome_usuario = '"+nome_usuario+"';"
            cur.execute(query)
            conn.commit()
            return """<h3 style="color:Green;">Usuário deletado com sucesso.</3>"""
        else:
            return """<h3 style="color:Red;">Usuário não existe ou dado não inserido</3>"""
    return render_template('delete_user.html')

@app.route('/alugar_recurso', methods=['GET','POST'])
def alugar_recurso():
    if request.method == "POST":
        id_usuario = request.form['id_usuario']
        nome_recurso = request.form['nome_recurso']
        qtde_recurso = request.form['qtde_recurso']
        query_recurso = "SELECT * FROM recurso WHERE nome_recurso = '"+nome_recurso+"';"
        cur.execute(query_recurso)
        result = cur.fetchall()
        if result:
            if result[0][1] >= int(qtde_recurso):
                remain = result[0][1]-int(qtde_recurso)
                hoje = date.today()
                entrega = hoje + timedelta(days=5)
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

@app.route('/devolver_recurso', methods=['GET','POST'])
def devolver_recurso():
    if request.method == "POST":
        id_usuario = request.form['id_usuario']
        nome_recurso = request.form['nome_recurso']
        query_emprestimo = "SELECT * FROM emprestimo WHERE id_usuario = '"+id_usuario+"' AND nome_recurso = '"+nome_recurso+"' AND status = 'emprestado';"
        cur.execute(query_emprestimo)
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

@app.route('/listar_aluguel', methods=['GET','POST'])
def listar_aluguel():
    if request.method == "POST":
        id_usuario = request.form['id_usuario']
        query = "SELECT * FROM emprestimo WHERE id_usuario = '"+id_usuario+"';"
        cur.execute(query)
        result = cur.fetchall()
        return render_template('listar_aluguel.html',result=result)
    return render_template('listar_aluguel.html')

if __name__ == '__main__':
    app.run()
