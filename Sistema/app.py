from flask import Flask, render_template, request, flash, redirect, url_for
import mysql.connector
from util import get_connection
from modulos.clientes import *
from modulos.carros import *
from modulos.aluguel import *

app = Flask(__name__)
app.static_folder = 'static'  # Configure o diretório estático para 'static'
app.config['SECRET_KEY'] = 'LOCACAR'  # Substitua 'sua_chave_secreta_aqui' por uma chave secreta real

per_page = 10  # Número de resultados por página

@app.route('/')
def pagina_principal():
    return render_template('index.html')

# -----------CARROS--------

@app.route('/carros')
def lista_carros():
    con  = get_connection()
    cur = con.cursor(dictionary=True)

    # Passe apenas os resultados da página atual para o template
    page = int(request.args.get('page', 1))
    start_index = (page - 1) * per_page
    end_index = start_index + per_page

    sql = """select * from Carro LIMIT %s, %s"""

    cur.execute(sql, (start_index, end_index))
    tuplas = cur.fetchall()

    sql = """ select nome_tipo from Tipo"""

    cur.execute(sql)
    tipos = cur.fetchall()

    sql = """ select tipo from Carro"""

    cur.execute(sql)
    tipos2 = cur.fetchall()

    con.close()
    cur.close()



    return render_template("lista_carros.html", dados=tuplas, tipos=tipos, tipos_busca=tipos2, page=page)

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

    page = int(request.args.get('page', 1))
    start_index = (page - 1) * per_page
    end_index = start_index + per_page

    try:
        con  = get_connection()
        cur = con.cursor(dictionary=True)
    except mysql.connector.Error as err:
        flash(f'Erro ao conectar ao banco: {err}', 'error')  # Mensagem de erro
        return redirect(url_for('pagina_principal'))

    sql = trata_busca_carros(especificacoes)

    print(sql)
    cur.execute(sql)
    tuplas = cur.fetchall()
    
    sql = "select * from Carro LIMIT %s, %s;"
    

    cur.execute(sql, (start_index, end_index))
    tuplas = cur.fetchall()

    sql = """ select nome_tipo from Tipo"""

    cur.execute(sql)
    tipos = cur.fetchall()

    

    sql = """ select tipo from Carro"""

    cur.execute(sql)
    tipos2 = cur.fetchall()

    con.close()
    cur.close()

    return render_template("lista_carros.html", dados=tuplas, tipos=tipos, tipos_busca=tipos2, page=page)

@app.route('/carros/editar/')
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
    

@app.route('/cadastro_carro', methods=['POST'])
def cadastrar_carro():
    if request.method == 'POST':

        tipo = request.form.get('tipo_cadastro')
        marca = request.form.get('marca_carro')
        modelo = request.form.get('modelo_carro')
        ano = request.form.get('ano_carro')
        
        print(f"\nTipo: {tipo} Marca: {marca} Modelo: {modelo} Ano: {ano}")

        try:
            con = get_connection()
            cur = con.cursor()
            sql = """insert into Carro(tipo, marca, modelo, ano) values(%s, %s, %s, %s)"""
            cur.execute(sql, (tipo, marca, modelo, ano))
            con.commit()
            cur.close()
            con.close()
            flash('Carro cadastrado com sucesso!', 'success')  # Mensagem de sucesso
            return redirect(url_for('lista_carros'))

        except mysql.connector.Error as err:
            flash(f'Erro ao cadastrar o carro: {err}', 'error')  # Mensagem de erro
            return redirect(url_for('pagina_principal'))
        except Exception as err:
            flash(f'Erro ao cadastrar o carro: {err}', 'error')  # Mensagem de erro
            return redirect(url_for('lista_carros'))
    else:
        flash('Método inválido para o cadastro de carro.', 'error')  # Mensagem de erro
        return redirect(url_for('lista_carros'))
    

# ---------- CLIENTES ------------------------

@app.route('/clientes')
def lista_clientes():

    page = int(request.args.get('page', 1))
    start_index = (page - 1) * per_page
    end_index = start_index + per_page

    con  = get_connection()
    cur = con.cursor(dictionary=True)

    sql = """select * from Cliente LIMIT %s,%s """

    cur.execute(sql, (start_index, end_index))
    print(start_index)
    tuplas = cur.fetchall()

    con.close()
    cur.close()

    return render_template("listar_clientes.html", busca=tuplas, page=page)


@app.route('/cadastrar_cliente', methods=['POST'])
def cadastrar_cliente():
    if request.method == 'POST':

        nome = request.form.get('nome')
        nome = nome.upper()
        ddd = request.form.get('ddd')
        numero = request.form.get('telefone')
        # Inserir um hífen na posição desejada (no exemplo, após o quinto dígito)
        telefone = "("+ddd+") "+ numero[:5] + "-" + numero[5:]
        
        print(f"\nCliente: {nome} Telefone: {telefone}")

        try:
            con = get_connection()
            cur = con.cursor()
            sql = """insert into Cliente(nome_cliente, telefone_cliente) values(%s, %s)"""
            cur.execute(sql, (nome, telefone))
            con.commit()
            cur.close()
            con.close()
            flash('Cliente cadastrado com sucesso!', 'success')  # Mensagem de sucesso
            return redirect(url_for('listar_clientes'))

        except mysql.connector.Error as err:
            flash(f'Erro ao cadastrar o Cliente: {err}', 'error')  # Mensagem de erro
            return redirect(url_for('lista_clientes'))

    else:
        flash('Método inválido para o cadastro de Clientes.', 'error')  # Mensagem de erro
        return redirect(url_for('lista_clientes'))

# Rota para lidar com a busca de clientes
@app.route('/buscar_cliente', methods=['POST'])
def buscar_cliente():
    nome_cliente = request.form.get('nome_cliente')
    ddd_cliente = request.form.get('ddd_cliente')
    telefone_cliente = request.form.get('telefone_cliente')

    # Verifique se os campos existem antes de concatená-los
    tipo = ''
    if nome_cliente is not None:
        tipo += nome_cliente
    if ddd_cliente is not None:
        tipo += '-' + ddd_cliente
    else:
        tipo += '-'
    if telefone_cliente is not None:
        tipo += '-' + telefone_cliente
    else:
        tipo += '-'


    # Chama a função lista_clietes com o tipo como parâmetro
    resultados = lista_clientes_especificos(tipo)
    return resultados

@app.route('/buscar_clientes/especificos')
def lista_clientes_especificos(tipo):
    especificacoes = []
    especificacoes = tipo.split('-')

    page = int(request.args.get('page', 1))
    start_index = (page - 1) * per_page
    end_index = start_index + per_page

    print("Especificacoes: [")
    print(especificacoes)
    print("]\n")

    try:
        con  = get_connection()
        cur = con.cursor(dictionary=True)
    except mysql.connector.Error as err:
        flash(f'Erro ao conectar ao banco: {err}', 'error')  # Mensagem de erro
        return redirect(url_for('pagina_principal'))

    sql = trata_busca_clientes(especificacoes)



    if sql == -1:
        flash(f'Erro de busca busca Inválida', 'error')  # Mensagem de erro
        return redirect(url_for('lista_clientes'))        

    sql += " LIMIT %s, %s"

    print(sql)

    try:
        cur.execute(sql, (start_index, end_index))
        tuplas = cur.fetchall()

    except Exception as err:
        flash(f'Erro na busca do cliente: {err}', 'error')  # Mensagem de erro
        return redirect(url_for('lista_clientes'))
    
    con.close()
    cur.close()

    return render_template("listar_clientes.html", busca=tuplas, page=page)

@app.route('/cliente/aluguel', methods=['POST'])
def aluguel_cliente():
    if request.method == 'POST':
        id = request.form.get('id_cliente')
        nome = request.form.get('nome_cliente')
        page = int(request.args.get('page', 1))
        start_index = (page - 1) * per_page
        end_index = start_index + per_page

        nome_cli = {}

        print(nome)

        try:
            con = get_connection()
            cur = con.cursor()

            # Chame a stored procedure para atualizar alugueis
            cur.callproc('atualizar_estado_alugueis')

            # Certifique-se de fazer o commit das alterações
            con.commit()

            cur.close()
            con.close()

            print('Alugueis atualizados com sucesso!')
        except Exception as e:
            flash(f'Erro ao chamar a procedure: {str(e)}', 'error')

        if id is not None:
            try:
                con = get_connection()
                cur = con.cursor(dictionary=True)

                # Consulta para recuperar os aluguéis do cliente com contagem de carros
                sql = """
                        SELECT A.*, (SELECT COUNT(*) FROM RefereCarros WHERE data_inicial = A.data_inicial AND id_cliente = A.id_cliente) AS num_carros
                        FROM Aluguel AS A
                        WHERE id_cliente = %s
                        LIMIT %s, %s
                    """

                cur.execute(sql, (id, start_index, end_index))
                
                tuplas = cur.fetchall()

                sql = """
                        SELECT C.id_carro, C.tipo, C.marca, C.modelo, C.ano
                        FROM Carro AS C
                        LEFT JOIN RefereCarros AS RC ON C.id_carro = RC.id_carro
                        LEFT JOIN Aluguel AS A ON RC.data_inicial = A.data_inicial AND RC.id_cliente = A.id_cliente
                        WHERE A.estado_aluguel IS NULL OR A.estado_aluguel NOT IN ('ATIVO', 'AGENDADO')
                        OR RC.id_carro IS NULL
                        ORDER BY A.data_inicial DESC -- Adicione esta linha para a ordenação
                    """


                cur.execute(sql)
                carros_disponiveis = cur.fetchall()

                con.close()
                cur.close()

                

                return render_template("listar_alugueis_cliente.html", carros=carros_disponiveis, dados=tuplas, nome_cliente=nome, page=page)
            except Exception as err:
                flash(f'Erro na busca de alugueis do cliente: {err}', 'error')
                return redirect(url_for('lista_clientes'))
        else:
            flash(f'Erro na página: Usuário Inexistente', 'error')
            return redirect(url_for('lista_clientes'))
    else:
        flash(f'Erro na METODO INVALIDO!', 'error')
        return redirect(url_for('lista_clientes'))

@app.route('/cliente/aluguel/carros', methods=['POST'])
def carros_do_aluguel():
    if request.method == 'POST':

        page = int(request.args.get('page', 1))
        start_index = (page - 1) * per_page
        end_index = start_index + per_page

        # Obtenha o ID do aluguel do formulário
        id_cliente = request.form.get('id_cliente')
        data_inicial = request.form.get('data_inicial')

        print(id_cliente)
        print(data_inicial)

        # Consulte o banco de dados para obter os carros deste aluguel com base no ID do aluguel
        try:
            con = get_connection()
            cur = con.cursor(dictionary=True)

            sql = """
                SELECT C.*
                FROM Carro AS C
                INNER JOIN RefereCarros AS RC ON C.id_carro = RC.id_carro
                WHERE RC.id_cliente = %s AND RC.data_inicial = %s LIMIT %s,%s
            """

            cur.execute(sql, (id_cliente, data_inicial, start_index, end_index))
            tuplas = cur.fetchall()

            cur.close()
            con.close()

            # Renderize um modelo HTML para exibir os carros
            return render_template("listar_carros_aluguel.html", carros=tuplas, page=page)

        except Exception as err:
            flash(f'Erro ao buscar carros do aluguel: {err}', 'error')
            return redirect(url_for('lista_clientes'))
        

        
@app.route('/novo_aluguel', methods=['POST'])
def novo_aluguel():
    if request.method == 'POST':

        page = int(request.args.get('page', 1))
        start_index = (page - 1) * per_page
        end_index = start_index + per_page

        id_cliente = request.form.get('id_cliente')
        data_inicial = request.form.get('data_inicial')
        estado = request.form.get('estado')
        numero_dias = request.form.get('numero_dias')

        id_cliente
        data_inicial
        data_inicial = data_inicial[:10]
        estado
        numero_dias

        #Verifica a data e retorna o sql a ser usado e o estado a ser cadastrado o aluguel
        sql, estado = verifica_data(data_inicial)

        try:
            con = get_connection()
            cur = con.cursor(dictionary=True)

            
            try:
                print(sql)
                cur.execute(sql)
                carros = cur.fetchall()

            except Exception as err:
                flash(f'Erro na seleção de carros para o aluguel: {err}', 'error')
                return redirect(url_for('lista_clientes'))
        except Exception as err:
            flash(f'Erro ao buscar carros para o aluguel: {err}', 'error')
            return redirect(url_for('lista_clientes'))
        con.close()
        cur.close()

        # Renderize um modelo HTML para exibir os carros
        return render_template("carros_para_alugar.html", carros=carros, id_cliente=id_cliente, data_inicial=data_inicial, estado_aluguel=estado,  numero_dias=numero_dias)


if __name__ == '__main__':
    app.run(host='localhost', port=5000, debug= True)

