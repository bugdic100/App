from flask import Flask, request
from psycopg2 import connect
from datetime import date,datetime,timedelta
from flask_restx import Api,Resource
from werkzeug.security import generate_password_hash,check_password_hash

conn = connect(
    host="192.168.1.5",#postgres
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

@api.route('/recurso',endpoint='recurso')
@api.doc(params={'nome_recurso': 'Nome do recurso','qtde_recurso':'quantidade do recurso'})
class Recurso(Resource):

    def post(self,nome_recurso=None,qtde_recurso=None):
        if not encontrar_recurso(nome_recurso) and qtde_recurso >= 1:
            cur.execute('INSERT INTO recurso (nome_recurso, qtde_recurso)'
            'VALUES (%s, %s)',
            (nome_recurso,qtde_recurso)) 
            conn.commit()
            return 'sucess',200
        else:
            return {"Value":"Recurso já existe ou valor < 0"}

    def get(self,nome_recurso=None,qtde_recurso=None):
        if nome_recurso != None and qtde_recurso != None:
            query = "SELECT * FROM recurso WHERE nome_recurso = '{0}' AND qtde_recurso = '{1}'"
            cur.execute(query.format(nome_recurso,qtde_recurso))
            result = cur.fetchall()
            if result:
                return {"Value": result}
            else:
                return {"Value":"recurso não encontrado"}
        
        if nome_recurso != None and qtde_recurso == None:
            query = "SELECT * FROM recurso WHERE nome_recurso = '{0}'"
            cur.execute(query.format(nome_recurso))
            result = cur.fetchall()
            if result:
                return {"Value":result}
            else:
                return {"Value":"recurso não encontrado"}

        if nome_recurso == None and qtde_recurso != None:
            query = "SELECT * FROM recurso WHERE qtde_recurso = '{0}'"
            cur.execute(query.format(qtde_recurso))
            result = cur.fetchall()
            if result:
                return {"Value":result}
            else:
                return {"Value":"recurso na quantidade especificada não encontrado"}

        if nome_recurso == None and qtde_recurso == None:
            query = "SELECT * FROM recurso"
            cur.execute(query)
            result = cur.fetchall()
            return {"Value":result} 

    def put(self,nome_recurso,qtde_recurso):
        if encontrar_recurso(nome_recurso) and qtde_recurso >= 0:
            query = "UPDATE recurso SET qtde_recurso = qtde_recurso + "+str(qtde_recurso)+";"
            cur.execute(query)
            conn.commit()
            return 'sucess',200
        else:
            return {"Value":"recurso não existe ou quantidade incorreta"}
    
    def delete(self,nome_recurso,qtde_recurso):
        if encontrar_recurso(nome_recurso) and qtde_recurso >= 0:
            query = "DELETE FROM recurso WHERE nome_recurso = '"+nome_recurso+"' AND qtde_recurso = '"+str(qtde_recurso)+"';"
            cur.execute(query)
            conn.commit()
            return 'sucess',200
        else:
            return "recurso não existe"

@api.route('/usuario/<string:id>&<string:nome>&<string:senha>&<string:tipo>', endpoint='usuario')
@api.doc(params={'id': 'nº identificador do usuário','nome_usuario':'nome do usuário',
'senha':'senha de acesso do usuário ao sistema','tipo':'perfil do usuário, poder admin, com acessos privilegiados, ou comum, para usuário operador do sistema'})
class Usuario(Resource):
    def post(self,id=None,nome=None,senha=None,tipo=None):
        if not encontrar_usuario(nome) or not encontrar_id(id) and tipo not in ['admin','comum'] and senha != None:
            senha_hash = generate_password_hash(senha)
            query = cur.execute('INSERT INTO usuario (id,nome,senha,tipo)'
            'VALUES (%s, %s, %s, %s)',
            (id,nome,senha_hash,tipo)) 
            cur.execute(query)
            conn.commit()
            return 'sucess',200
        else:
            return "ID ou usuário já existe, ou perfil inexistente"
        
    def get(self,id,nome,tipo=None):
        if encontrar_usuario(nome):
            query = "SELECT * FROM usuario WHERE nome_usuario = '{}';"
            cur.execute(query.format(nome))
            result = cur.fetchall()
            return {'Value':result},200
        elif encontrar_usuario(id):
            query = "SELECT * FROM usuario WHERE id_usuario = '{}';"
            cur.execute(query.format(id))
            result = cur.fetchall()
            return {'Value':result},200
        elif tipo != None:
            query = "SELECT * FROM usuario WHERE tipo = '{}';"
            cur.execute(query.format(tipo))
            result = cur.fetchall()
            return {'Value':result},200
        else:
            return {"Value":"usuário não existe"}

    def put(self,id=None,nome=None,tipo=None,senha=None):
        if encontrar_usuario(id) and nome != None and tipo != None and senha != None:
            senha_hash = generate_password_hash(senha)
            query = "UPDATE usuario SET nome_usuario = '{}' tipo = '{}' and senha = '{}' WHERE id_usuario = '{}';"
            cur.execute(query.format(nome,tipo,senha_hash))
            conn.commit()
            return {"values":"sucess"},200
        else:
            return "usuário não existe"

    def delete(self,id):
        if encontrar_usuario(id):
            query = "DELETE FROM usuario WHERE id_usuario = '{}';"
            cur.execute(query.format(id))
            conn.commit()
            return {"Value":"usuário excluído com sucesso"}
        else:
            return {"Value":"usuário não existe"}

@api.route('/emprestimo', endpoint='emprestimo')
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

    def post(self,id=None,nome_recurso=None,qtde_recurso=None):
        if encontrar_recurso(nome_recurso) and encontrar_id(id) and qtde_recurso > 0:
            query = "SELECT * FROM recurso WHERE nome_recurso = '{}';"
            cur.execute(query.format(nome_recurso))
            result = cur.fetchall()
            if result[0][1] >= int(qtde_recurso):
                hoje = date.today()
                entrega = hoje + timedelta(days=5)
                query = query = cur.execute('INSERT INTO emprestimo (id,nome_recurso,qtde_recurso,data_inicio,data_fim,status)'
                'VALUES (%s, %s, %s, %s, %s, %s)',
                (id,nome_recurso,qtde_recurso,hoje,entrega,"emprestado")) 
                cur.execute(query)
                conn.commit()
            else:
                return 'Quantidade do recurso indisponível'
        else:
            return {"value":"recurso, usuário ou quantidade não encontrado"}

    def put(self,id,nome_recurso,qtde_recurso,data_inicio,data_fim,status):
        if encontrar_emprestimo(id,nome_recurso,qtde_recurso,data_inicio,data_fim,status):
            query = "UPDATE emprestimo SET status = 'devolvido' WHERE id_usuario = '{}' AND nome_recurso = '{}';"
            cur.execute(query.format(id,nome_recurso))
            conn.commit

            query_emprestimo = "SELECT * FROM emprestimo WHERE id_usuario = '{}' AND nome_recurso = '{}' AND status = 'emprestado';"
            cur.execute(query_emprestimo.format(id,nome_recurso))
            result = cur.fetchall()    
            
            query_atualiza_recurso = "UPDATE recurso SET qtde_recurso = qtde_recurso + '"+str(result[0][2])+"' WHERE nome_recurso = '"+nome_recurso+"';"
            cur.execute(query_atualiza_recurso)
            conn.commit()
            return {"Value":"Recurso devolvido com sucesso"}
        else:
            return "empréstimo não encontrado"

api.add_resource(Recurso, '/recurso')
api.add_resource(Usuario, '/usuario/<string:id>&<string:nome>&<string:senha>&<string:tipo>')
api.add_resource(Emprestimo,'/emprestimo')

if __name__ == '__main__':
    app.run(host="0.0.0.0")