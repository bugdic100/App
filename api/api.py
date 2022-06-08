############### IMPORTA BIBLIOTECAS

from flask import Flask, request
from psycopg2 import connect
from datetime import date,datetime,timedelta
from flask_restx import Api,Resource,fields,marshal_with
from werkzeug.security import generate_password_hash,check_password_hash

############### CONECTA BANCO DE DADOS

conn = connect(
    host="postgres",#192.168.1.5
    database="postgres",
    port = "5432",
    user="postgres",
    password="postgres",#postgres
    options="-c search_path=dbo,desafio_python")

cur = conn.cursor()

############### CONFIGURAÇÕES INCIAIS DA API

app = Flask(__name__)
api = Api(app)

############### FUNÇÕES DE APOIO
def encontrar_usuario(nome_usuario):
    query = "SELECT * FROM usuario WHERE nome_usuario = '{}';"
    cur.execute(query.format(nome_usuario))
    result = cur.fetchall()
    if result:
        return True
    else:
        return False

def encontrar_id(id):
    query = "SELECT * FROM usuario  WHERE id_usuario = '{}';"
    cur.execute(query.format(id))
    result = cur.fetchall()
    if result:
        return True
    else:
        return False

def existe_recurso(nome_recurso):
    query = "SELECT * FROM recurso WHERE nome_recurso = '{}';"
    cur.execute(query.format(nome_recurso))
    result = cur.fetchall()
    if result:
        return True
    else:
        return False

def encontrar_recurso_disponivel(nome_recurso,qtde_recurso):
    query = "SELECT * FROM recurso WHERE nome_recurso = '{}' AND qtde_recurso >= '{}';"
    cur.execute(query.format(nome_recurso,qtde_recurso))
    result = cur.fetchall()
    if result:
        return True
    else:
        return False

def encontrar_recurso_emprestado(nome_recurso):
    query = "SELECT * FROM emprestimo WHERE nome_recurso = '{}' AND status = 'emprestado'"
    cur.execute(query.format(nome_recurso))
    result = cur.fetchall()
    if result:
        return True
    else:
        return False

def encontrar_usuario_emprestado(id_usuario):
    query = "SELECT * FROM emprestimo WHERE id_usuario = '{}' AND status = 'emprestado'"
    cur.execute(query.format(id_usuario))
    result = cur.fetchall()
    if result:
        return True
    else:
        return False
    
def encontrar_emprestimo(id,nome_recurso):
    query = "SELECT * FROM emprestimo WHERE id_usuario = '{}' AND nome_recurso = '{}' AND status = 'emprestado';"
    cur.execute(query.format(id,nome_recurso))
    result = cur.fetchall()
    if result:
        return True
    else:
        return False

############### CRUD RECURSO

@api.route('/recurso',endpoint='recurso')
@api.doc(params={'nome_recurso':'nome do recurso','qtde_recurso':'quantidade do recurso'})
class Recurso(Resource):

    def post(self):

        nome_recurso = request.args.get('nome_recurso')
        qtde_recurso = request.args.get('qtde_recurso')

        if not existe_recurso(nome_recurso) and int(qtde_recurso) >= 0:
            cur.execute('INSERT INTO recurso (nome_recurso, qtde_recurso)'
            'VALUES (%s, %s)',
            (nome_recurso,qtde_recurso)) 
            conn.commit()
            return {"Value":"recurso incluído com sucesso"}
        else:
            return {"Value":"Recurso já existe ou valor < 0"}

    def get(self):

        nome_recurso = request.args.get('nome_recurso')

        if nome_recurso is None:
            query = "SELECT * FROM recurso"
            cur.execute(query)
            result = cur.fetchall()
            return {"Value": result}
        elif existe_recurso(nome_recurso):
            query = "SELECT * FROM recurso WHERE nome_recurso = '{0}'"
            cur.execute(query.format(nome_recurso))
            result = cur.fetchall()
            return {"Value": result}
        else:
            return {"Value":"recurso não encontrado"}
        
    def put(self):

        nome_recurso = request.args.get('nome_recurso')
        qtde_recurso = int(request.args.get('qtde_recurso'))

        if existe_recurso(nome_recurso) and qtde_recurso >= 0:
            if qtde_recurso < 0:
                qtde_recurso = 0
            query = "UPDATE recurso SET qtde_recurso = qtde_recurso + '{}';"
            cur.execute(query.format(qtde_recurso))
            conn.commit()
            return {"Value":"recurso atualizado com sucesso"}
        else:
            return {"Value":"recurso não existe ou quantidade incorreta"}

    def delete(self):

        nome_recurso = request.args.get('nome_recurso')

        if existe_recurso(nome_recurso) and not encontrar_recurso_emprestado(nome_recurso):
            query = "DELETE FROM recurso WHERE nome_recurso = '{}';"
            cur.execute(query.format(nome_recurso))
            conn.commit()
            return {"Value":"recurso excluído com sucesso"}
        else:
            return {"Valor":"recurso não existe ou recurso pode estar emprestado"}


# ############### CRUD USUÁRIO
@api.route('/usuario', endpoint='usuario')
@api.doc(params={'id_usuario': 'nº identificador do usuário',
                     'nome_usuario':'nome do usuário',
                     'senha':'senha de acesso do usuário ao sistema',
                     'tipo':'perfil do usuário, poder admin, com acessos privilegiados, ou comum, para usuário operador do sistema'})

class Usuario(Resource):
    
    def post(self):

        id_usuario = request.args.get('id_usuario')
        nome_usuario = request.args.get('nome_usuario')
        senha = request.args.get('senha')
        tipo = request.args.get('tipo')

        if not encontrar_usuario(nome_usuario) and not encontrar_id(id) and tipo in ['admin','comum'] and senha is not None:
            senha_hash = generate_password_hash(senha)
            cur.execute('INSERT INTO usuario (id_usuario,nome_usuario,senha,tipo)'
            'VALUES (%s, %s, %s, %s)',
            (id_usuario,nome_usuario,senha_hash,tipo)) 
            conn.commit()
            return {"Value":"usuário incluído com sucesso"}
        else:
            return {"Value":"ID ou usuário já existe, ou perfil inexistente"}

    def get(self):

        id_usuario = request.args.get('id_usuario')
        nome_usuario = request.args.get('nome_usuario')
        tipo = request.args.get('tipo')

        if id_usuario is None or nome_usuario is None:
            query = "SELECT * FROM usuario"
            cur.execute(query)
            result = cur.fetchall()
            return {"Value":result}
        elif encontrar_usuario(nome_usuario):
            query = "SELECT id_usuario,nome_usuario,tipo FROM usuario WHERE nome_usuario = '{}';"
            cur.execute(query.format(nome_usuario))
            result = cur.fetchall()
            return {"Value":result}
        elif encontrar_usuario(id):
            query = "SELECT id_usuario,nome_usuario,tipo FROM usuario WHERE id_usuario = '{}';"
            cur.execute(query.format(id))
            result = cur.fetchall()
            return {'Value':result}
        else:
            return {"Value":"usuário não existe"}

    def put(self):

        id_usuario = request.args.get('id_usuario')
        nome_usuario = request.args.get('nome_usuario')
        senha = request.args.get('senha')
        tipo = request.args.get('tipo')

        if encontrar_id(id_usuario) and tipo in ['admin','comum']:
            senha_hash = generate_password_hash(senha)
            query = "UPDATE usuario SET nome_usuario = '{0}',senha = '{1}',tipo='{2}' WHERE id_usuario = '{3}'"
            cur.execute(query.format(nome_usuario,senha_hash,tipo,id_usuario))
            conn.commit()
            return {"values":"Atualizado com sucesso"}
        else:
            return {"Value":"usuário não existe"}

    def delete(self):
        id_usuario = request.args.get('id_usuario')
        if encontrar_id(id_usuario) and not encontrar_usuario_emprestado(id_usuario):
            query = "DELETE FROM usuario WHERE id_usuario = '{}';"
            cur.execute(query.format(id_usuario))
            conn.commit()
            return {"Value":"usuário excluído com sucesso"}
        else:
            return {"Value":"usuário não existe ou têm algum empréstimo em seu nome sem devolução"}

# ############### EMPRÉSTIMO DOS RECURSOS
@api.route('/emprestimo', endpoint='emprestimo')
@api.doc(params={'id_usuario': 'nº identificador do usuário que solicitou o empréstimo',
                     'nome_recurso':'nome do recurso que foi emprestado',
                     'qtde_recurso':'quantidade do recurso',
                     'data_inicio':'data de quando foi efetuado o empréstimo do recurso',
                     'data_fim':'data de entrega do recurso, por padrão 5 dias depois de pegar o recurso emprestado',
                     'status':'situação do empréstimo, podendo ser emprestado ou devolvido'})
class Emprestimo(Resource):

    def get(self):

            id_usuario = request.args.get('id_usuario')
            nome_recurso = request.args.get('nome_recurso')
            qtde_recurso = request.args.get('qtde_recurso')
            data_inicio = request.args.get('data_inicio')
            data_fim = request.args.get('data_fim')
            status = request.args.get('status')

            colunas_final = [id_usuario,nome_recurso,qtde_recurso,data_inicio,data_fim,status]
            filtro_final = ['id_usuario','nome_recurso','qtde_recurso','data_inicio','data_fim','status']

            colunas = []
            filtro = []
            #define colunas válidas
            for i in range(len(colunas_final)):
                if colunas_final[i] is not None:
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
            return {"Value": str(result)}
        
    def post(self):

        id_usuario = request.args.get('id_usuario')
        nome_recurso = request.args.get('nome_recurso')
        qtde_recurso = int(request.args.get('qtde_recurso'))


        if qtde_recurso < 0:
            return {"Value":"Quantidade solicitada negativa"}

        if encontrar_recurso_disponivel(nome_recurso,qtde_recurso) and encontrar_id(id_usuario):
            #empresta o recurso
            hoje = date.today()
            entrega = hoje + timedelta(days=5)
            cur.execute('INSERT INTO emprestimo (id_usuario,nome_recurso,qtde_recurso,data_inicio,data_fim,status)'
            'VALUES (%s, %s, %s, %s, %s, %s)',
            (id_usuario,nome_recurso,qtde_recurso,hoje,entrega,"emprestado")) 
            conn.commit()
            #atualiza o estoque de recurso
            atualiza_recurso = "UPDATE recurso SET qtde_recurso = qtde_recurso - '{0}' WHERE nome_recurso = '{1}'"
            cur.execute(atualiza_recurso.format(qtde_recurso,nome_recurso))
            conn.commit()
            return {"Value":"recurso emprestado com sucesso"}
        else:
            return {"Value":"Recurso indisponível na quantidade solicitada ou usuário não encontrado"}
            
    def put(self):

        id_usuario = request.args.get('id_usuario')
        nome_recurso = request.args.get('nome_recurso')

        if encontrar_emprestimo(id_usuario,nome_recurso):
            #qtde devolvida
            query_emprestimo = "SELECT qtde_recurso FROM emprestimo WHERE id_usuario = '{}' AND nome_recurso = '{}' AND status = 'emprestado';"
            cur.execute(query_emprestimo.format(id_usuario,nome_recurso))
            qtde_devolve = cur.fetchall()[0][0]
            #muda status do empréstimo
            query_status = "UPDATE emprestimo SET status = 'devolvido' WHERE id_usuario = '{}' AND nome_recurso = '{}';"
            cur.execute(query_status.format(id_usuario,nome_recurso))
            conn.commit
            #devolve recurso para o estoque
            query_atualiza_recurso = "UPDATE recurso SET qtde_recurso = qtde_recurso + '{0}' WHERE nome_recurso = '{1}';"
            cur.execute(query_atualiza_recurso.format(qtde_devolve,nome_recurso))
            conn.commit()
            return {"Value":"Recurso devolvido com sucesso"}
        else:
            return {"Value":"empréstimo não encontrado"}

api.add_resource(Recurso, '/recurso')
api.add_resource(Usuario, '/usuario')
api.add_resource(Emprestimo,'/emprestimo')

if __name__ == '__main__':
    app.run(host="0.0.0.0")
