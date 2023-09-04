from flask import Flask, request, render_template
from util import get_connection
from markupsafe import escape

app = Flask(__name__)
app.static_folder = 'static'  # Configure o diretório estático para 'static'

@app.route('/')
def pagina_principal():
    return render_template('index.html')

@app.route('/carros')
def lista_carros():
    con  = get_connection()
    cur = con.cursor(dictionary=True)
    sql = """select * from Carro"""
    cur.execute(sql)
    tuplas = cur.fetchall()
    con.close()
    cur.close()
    return render_template("lista_carros.html", dados=tuplas,  cars_busca=tuplas)

# Rota para lidar com a busca de carros
@app.route('/buscar_carros', methods=['POST'])
def buscar_carros():

    tipo = request.form.get('tipo')
    tipo += '-'+request.form.get('marca')
    tipo += '-'+request.form.get('modelo')
    tipo += '-'+request.form.get('ano')
    
    # Chama a função lista_carros_especificos com o tipo como parâmetro
    resultados = lista_carros_especificos(tipo)
    return resultados

@app.route('/carros/<tipo>')
def lista_carros_especificos(tipo):
    especificacoes = []
    especificacoes = tipo.split('-')
    con  = get_connection()
    cur = con.cursor(dictionary=True)

    verification = False

    if len(especificacoes) > 0:

        sql = "select * from Carro"
        
        for i in range(0, len(especificacoes)):
            atributo = ['tipo', 'marca', 'modelo', 'ano'][i]
            if especificacoes[i] != '':
                if verification:
                    sql += " and {} = '{}'".format(atributo, escape(especificacoes[i]))
                else:
                    sql += " where {} = '{}'".format(atributo, escape(especificacoes[i]))
                    verification = True

    print(sql)
    cur.execute(sql)
    tuplas = cur.fetchall()
    
    sql = "select * from Carro"
    

    cur.execute(sql)
    tuplas2 = cur.fetchall()

    con.close()
    cur.close()
    return render_template("lista_carros.html", dados=tuplas, cars_busca=tuplas2)

@app.route('/carros/<int:id>/editar/')
def editar_carro(id=None):
    if id != None:
        con  = get_connection()
        cur = con.cursor(dictionary=True)
        sql = """select * from Carro where id_carro={}""".format(id)
        cur.execute(sql)
        tuplas = cur.fetchall()
        con.close()
        cur.close()
        return render_template("editar_carro.html", dados=tuplas)
    else:
        return 'Formulário para editar o Carro vazio.'
    

@app.route('/carro/<int:id>/deletar/')
def deletar_contato(id=None):
    if id != None:
      con  = get_connection()
      cur = con.cursor()
      sql = """delete from Carro where id={}""".format(id)
      cur.execute(sql)
      con.commit()
      cur.close()
      con.close()
      return lista_carros()
    else:
        return 'Deleção de Carro vazio.'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug= True)
