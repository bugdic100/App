from flask import Flask, request
from psycopg2 import connect
from datetime import date,datetime,timedelta
from flask_restx import Api,Resource

conn = connect(
    host="localhost",#192.168.1.5
    database="postgres",#exercicio
    port = "5432",
    user="postgres",
    password="postgres",#docker
    options="-c search_path=dbo,desafio_python")

cur = conn.cursor()

app = Flask(__name__)
api = Api(app)

#Funções de apoio
def encontrar_usuario(nome_usuario):
    query = "SELECT * FROM usuario WHERE nome_usuario = '"+nome_usuario+"';"
    cur.execute(query)
    result = cur.fetchall()
    if result:
        return True
    else:
        return False

def encontrar_recurso(nome_recurso):
    query = "SELECT * FROM recurso WHERE nome_recurso = '"+nome_recurso+"';"
    cur.execute(query)
    result = cur.fetchall()
    if result:
        return True
    else:
        return False

def encontrar_id(id):
    query = "SELECT * FROM usuario  WHERE id_usuario = '"+id+"';"
    cur.execute(query)
    result = cur.fetchall()
    if result:
        return True
    else:
        return False
    
def encontrar_emprestimo(id_usu,nome_recurso,qtde_recurso,data_inicio,data_fim,status):
    query = "SELECT * FROM emprestimo WHERE id_usuario = '"+id_usu+"' OR nome_recurso = '"+nome_recurso+"' OR qtde_recurso = '"+str(qtde_recurso)+"' OR data_inicio = '"+data_inicio+"' OR data_fim = '"+data_fim+"' OR status = '"+status+"';"
    cur.execute(query)
    result = cur.fetchall()
    if result:
        return True
    else:
        return False

@api.route('/recurso/<string:nome_recurso>&<int:qtde_recurso>', endpoint='recurso')
@api.doc(params={'nome_recurso': 'Nome do recurso','qtde_recurso':'quantidade do recurso'})
class Recurso(Resource):

    def post(self,nome_recurso,qtde_recurso):
        if not encontrar_recurso(nome_recurso) and qtde_recurso >= 0:
            cur.execute('INSERT INTO recurso (nome_recurso, qtde_recurso)'
            'VALUES (%s, %s)',
            (nome_recurso,qtde_recurso)) 
            conn.commit()
            return 'sucess',200
        else:
            return {"Value":"Recurso já existe"}

    def get(self,nome_recurso,qtde_recurso):
        if encontrar_recurso(nome_recurso) and qtde_recurso >= 0:
            query = "SELECT * FROM recurso WHERE nome_recurso = '"+nome_recurso+"' AND qtde_recurso = '"+str(qtde_recurso)+"';"
            cur.execute(query)
            result = cur.fetchall()
            conn.commit()
            return {"Value":result}
        else:
            return {"Value":"recurso não existe"}

    def put(self,nome_recurso,qtde_recurso):
        if encontrar_recurso(nome_recurso) and qtde_recurso >= 0:
            query = "UPDATE recurso SET qtde_recurso = qtde_recurso + "+str(qtde_recurso)+";"
            cur.execute(query)
            conn.commit()
            return 'sucess',200
        else:
            return {"Value":"recurso não existe"}
    
    def delete(self,nome_recurso,qtde_recurso):
        if encontrar_recurso(nome_recurso) and qtde_recurso >= 0:
            query = "DELETE FROM recurso WHERE nome_recurso = '"+nome_recurso+"' AND qtde_recurso = '"+str(qtde_recurso)+"';"
            cur.execute(query)
            conn.commit()
            return 'sucess',200
        else:
            return "recurso não existe"

@api.route('/usuario/<string:id_usuario>&<string:nome_usuario>&<string:senha>&<string:tipo>', endpoint='usuario')
@api.doc(params={'id': 'nº identificador do usuário','nome_usuario':'nome do usuário',
'senha':'senha de acesso do usuário ao sistema','tipo':'perfil do usuário, poder admin, com acessos privilegiados, ou comum, para usuário operador do sistema'})
class Usuario(Resource):

    def post(self,id,nome,senha,tipo):
        if not encontrar_usuario(nome):
            query = cur.execute('INSERT INTO usuario (id,nome,senha,tipo)'
            'VALUES (%s, %s, %s, %s)',
            (id,nome,senha,tipo)) 
            cur.execute(query)
            conn.commit()
            return 'sucess',200
        else:
            return "usuário já existe"
        
    def get(self,id,nome,senha,tipo):
        if encontrar_usuario(nome):
            query = "SELECT * FROM WHERE id_usuario = '"+id+"';"
            cur.execute(query)
            result = cur.fetchall()
            return {'Value':result},200
        else:
            return "usuário não existe"

    def put(self,id,nome,senha,tipo):
        if encontrar_usuario(nome):
            query = "UPDATE usuario SET nome_usuario = '"+nome+"', senha = '"+senha+"', tipo = '"+tipo+"' WHERE id_usuario = '"+id+"';"
            cur.execute(query)
            conn.commit()
            return {"values":"sucess"},200
        else:
            return "usuário não existe"

    def delete(self,id,nome,senha,tipo):
        if encontrar_usuario(nome):
            query = "DELETE FROM usuario WHERE id_usuario = '"+id+"';"
            cur.execute(query)
            conn.commit()
        else:
            return "usuário não existe"

@api.route('/emprestimo/<string:id>&<string:nome_recurso>&<int:qtde_recurso>&<string:data_inicio>&<string:data_fim>&<string:status>', endpoint='emprestimo')
@api.doc(params={'id': 'nº identificador do usuário que solicitou o empréstimo',
'nome_recurso':'nome do recurso que foi emprestado','data_inicio':'data de quando foi efetuado o empréstimo do recurso',
'data_fim':'data de entrega do recurso, por padrão 5 dias depois de pegar o recurso emprestado','status':'situação do empréstimo, podendo ser emprestado ou devolvido'})
class Emprestimo(Resource):
    def get(self,id,nome_recurso,qtde_recurso,data_inicio,data_fim,status):
        if encontrar_emprestimo(id,nome_recurso,qtde_recurso,data_inicio,data_fim,status):
            query = "SELECT * FROM emprestimo WHERE id_usuario = '"+id+"' OR nome_recurso = '"+nome_recurso+"' OR qtde_recurso = '"+str(qtde_recurso)+"' OR data_inicio = '"+data_inicio+"' OR data_fim = '"+data_fim+"' OR status = '"+status+"';"
            cur.execute(query)
            result = cur.fetchall()
            return {"value":result}
        else:
            return "empréstimo não encontrado"

    def post(self,id,nome_recurso,qtde_recurso,data_inicio,data_fim,status):
        if encontrar_recurso(nome_recurso) and encontrar_id(id) and qtde_recurso > 0:
            query = "SELECT * FROM recurso WHERE nome_recurso = '"+nome_recurso+"';"
            cur.execute(query)
            result = cur.fetchall()
            if result[0][1] >= int(qtde_recurso):
                hoje = date.today()
                entrega = hoje + timedelta(days=5)
                query = query = cur.execute('INSERT INTO emprestimo (id,nome_recurso,qtde_recurso,data_inicio,data_fim,status)'
                'VALUES (%s, %s, %s, %s, %s, %s)',
                (id,nome_recurso,qtde_recurso,hoje,entrega,status)) 
                cur.execute(query)
                conn.commit()
            else:
                return 'Quantidade do recurso indisponível'
        else:
            return {"value":"recurso ou usuário não encontrado"}
    def put(self,id,nome_recurso,qtde_recurso,data_inicio,data_fim,status):
        if encontrar_emprestimo(id,nome_recurso,qtde_recurso,data_inicio,data_fim,status):
            query = "UPDATE emprestimo SET status = 'devolvido' WHERE id_usuario = '"+id+"' AND nome_recurso = '"+nome_recurso+"';"
            cur.execute(query)
            conn.commit
            return "sucess",200
        else:
            return "empréstimo não encontrado"

api.add_resource(Recurso, '/recurso/<string:nome_recurso>&<int:qtde_recurso>')
api.add_resource(Usuario, '/usuario/<string:id_usuario>&<string:nome_usuario>&<string:senha>&<string:tipo>')
api.add_resource(Emprestimo,'/emprestimo/<string:id>&<string:nome_recurso>&<int:qtde_recurso>&<string:data_inicio>&<string:data_fim>&<string:status>')

if __name__ == '__main__':
    app.run()


























