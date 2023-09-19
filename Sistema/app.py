from flask import Flask, render_template, request, flash, redirect, url_for
import mysql.connector
from util import get_connection
from modulos.clientes import *
from modulos.carros import *
from modulos.aluguel import *
from modulos.pagamento import *
import re


app = Flask(__name__)
app.static_folder = 'static'  # Configure o diretório estático para 'static'
app.config['SECRET_KEY'] = 'LOCACAR'  # Substitua 'sua_chave_secreta_aqui' por uma chave secreta real

per_page = 10 # Número de resultados por página

@app.route('/')
def pagina_principal():

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

    try:
        con = get_connection()
        cur = con.cursor(dictionary=True)
    except Exception as e:
        flash(f'Erro iniciar conexao: {str(e)}', 'error')
    
    try: 
        
        sql = """
                SELECT C.id_cliente, C.nome_cliente, C.telefone_cliente, A.*
                FROM Cliente AS C
                JOIN Aluguel AS A ON C.id_cliente = A.id_cliente
                WHERE A.estado_aluguel IN ('PENDENTE', 'ATIVO', 'AGENDADO', 'FINALIZADO')
            """
            

        cur.execute(sql)
        
        alugueis = cur.fetchall()

        for row in alugueis:
            id_cliente = row['id_cliente']
            id_carro = row['id_carro']
            data_inicial = row['data_inicial']
            valor_devido = row['valor_devido']
            estado_aluguel = row['estado_aluguel']

            if (valor_devido == None) or (estado_aluguel != 'FINALIZADO'):
                value = atualiza_valor_devido(con, cur, id_cliente, id_carro, data_inicial)
                
                if value != 1:
                    return value
            else:
                pass
    
    except Exception as e:
        flash(f'Erro na verificacao: {str(e)}', 'error')

    con.close()
    cur.close()


    flash('Todos os alugueis atualizados!:', 'success')
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

    print(tipo)
    
    # Chama a função lista_carros_especificos com o tipo como parâmetro
    resultados = lista_carros_especificos(tipo)
    return resultados


@app.route('/carro/deletar/<int:id_carro>')
def deletar_carro(id_carro=None):

    if id_carro is not None:
        con = get_connection()
        cur = con.cursor()

        # Verifique se existem registros na tabela Aluguel relacionados a este carro
        sql_verificar_aluguel = "SELECT COUNT(*) FROM Aluguel WHERE id_carro = %s"
        cur.execute(sql_verificar_aluguel, (id_carro,))
        num_registros = cur.fetchone()[0]

        if num_registros > 0:
            # Se houver registros na tabela Aluguel, não permita a exclusão
            cur.close()
            con.close()
            flash('Não é possível excluir o carro. Existem aluguéis associados a ele: ', 'error') 
            return redirect('/carros')
        else:
            # Se não houver registros na tabela Aluguel, exclua o carro
            sql_excluir_carro = "DELETE FROM Carro WHERE id_carro = %s"
            cur.execute(sql_excluir_carro, (id_carro,))
            con.commit()
            cur.close()
            con.close()
            flash('Carro deletado!', 'success') 
            return redirect('/carros')  # Redireciona para a página de listagem de carros
    else:
        flash('Deleção de carro vazia: ', 'error') 
        redirect('/carros')

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
    
    sql += " LIMIT %s, %s;"
    

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

@app.route('/carros/editar/<int:id>')
def editar_carro(id=None):
    if id != None:
        con  = get_connection()
        cur = con.cursor(dictionary=True)
        sql = """select * from Carro where id_carro={}""".format(id)
        cur.execute(sql)
        tuplas = cur.fetchall()

        sql = """select * from Tipo"""
        cur.execute(sql)
        tipos = cur.fetchall()

        con.close()
        cur.close()
        return render_template("editar_carro.html", dados=tuplas, tipos=tipos)
    else:
        return 'Formulário para editar o Carro vazio.'

@app.route('/editar_carro', methods=['POST'])
def editar_carro_func():
    if request.method == 'POST':

        id_carro = request.form.get('id_carro')
        tipo = request.form.get('tipo')
        marca = request.form.get('marca_carro')
        modelo = request.form.get('modelo_carro')
        ano = request.form.get('ano_carro')
        
        print(f"\nTipo: {tipo} Marca: {marca} Modelo: {modelo} Ano: {ano}")

        try:
            con = get_connection()
            cur = con.cursor()
            sql = """UPDATE Carro SET tipo = %s, marca=%s, modelo=%s, ano=%s WHERE id_carro=%s"""
            cur.execute(sql, (tipo, marca, modelo, ano, id_carro))
            con.commit()
            cur.close()
            con.close()
            flash('Carro editado com sucesso!', 'success')  # Mensagem de sucesso
            return redirect(url_for('lista_carros'))

        except mysql.connector.Error as err:
            flash(f'Erro ao cadastrar o carro: {err}', 'error')  # Mensagem de erro
            return redirect(url_for('pagina_principal'))
        except Exception as err:
            flash(f'Erro ao editar o carro: {err}', 'error')  # Mensagem de erro
            return redirect(url_for('lista_carros'))
    else:
        flash('Método inválido para a edição do carro.', 'error')  # Mensagem de erro
        return redirect(url_for('lista_carros'))
    

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
            cur.close()
            con.close()
            return redirect(url_for('pagina_principal'))
        except Exception as err:
            flash(f'Erro ao cadastrar o carro: {err}', 'error')  # Mensagem de erro
            cur.close()
            con.close()
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
            return redirect(url_for('lista_clientes'))

        except mysql.connector.Error as err:
            flash(f'Erro ao cadastrar o Cliente: {err}', 'error')  # Mensagem de erro
            cur.close()
            con.close()
            return redirect(url_for('lista_clientes'))

    else:
        flash('Método inválido para o cadastro de Clientes.', 'error')  # Mensagem de erro
        cur.close()
        con.close()
        return redirect(url_for('lista_clientes'))


@app.route('/cliente/deletar/<int:id_cliente>')
def deletar_cliente(id_cliente=None):

    if id_cliente is not None:
        con = get_connection()
        cur = con.cursor()

        # Verifique se existem registros na tabela Aluguel relacionados a este carro
        sql_verificar_aluguel = "SELECT COUNT(*) FROM Aluguel WHERE id_cliente = %s"
        cur.execute(sql_verificar_aluguel, (id_cliente,))
        num_registros = cur.fetchone()[0]

        if num_registros > 0:
            # Se houver registros na tabela Aluguel, não permita a exclusão
            cur.close()
            con.close()
            flash('Não é possível excluir o cliente. Existem aluguéis associados a ele: ', 'error') 
            return redirect('/clientes')
        else:
            # Se não houver registros na tabela Aluguel, exclua o carro
            sql_excluir_carro = "DELETE FROM Cliente WHERE id_cliente = %s"
            cur.execute(sql_excluir_carro, (id_cliente,))
            con.commit()
            cur.close()
            con.close()
            flash('Cliente deletado!', 'success') 
            return redirect('/clientes')  # Redireciona para a página de listagem de carros
    else:
        flash('Deleção de Cliente vazia: ', 'error') 
        return redirect('/clientes')

@app.route('/cliente/editar/<int:id>')
def editar_cliente(id=None):
    if id != None:
        con  = get_connection()
        cur = con.cursor(dictionary=True)
        sql = """select * from Cliente where id_cliente={}""".format(id)
        cur.execute(sql)

        tuplas = cur.fetchall()

        cur.execute(sql)
        tupla = cur.fetchone()

        telefone = tupla['telefone_cliente']

        # Use uma expressão regular para extrair o DDD e o número e remover o hífen
        match = re.match(r'\((\d{2})\)\s*(\d{5})-(\d{4})', telefone)

        if match:
            ddd = match.group(1)
            numero = match.group(2) + match.group(3)  # Concatenando os grupos para remover o hífen
            print(f"DDD: {ddd}")
            print(f"Número: {numero}")
        else:
            flash('Formato de telefone inválido.', 'error') 
            con.close()
            cur.close()
            return redirect('/clientes')

        con.close()
        cur.close()
        return render_template("editar_cliente.html", dados=tuplas, ddd=ddd, telefone=numero)
    else:
            flash('Formulário para editar o Carro vazio.', 'error') 
            con.close()
            cur.close()
            return redirect('/clientes')

@app.route('/editar_cliente', methods=['POST'])
def editar_cliente_func():
    if request.method == 'POST':

        id_cliente = request.form.get('id_cliente')
        print(f"id: {id_cliente}")
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

            sql = """UPDATE Cliente SET nome_cliente =%s, telefone_cliente=%s WHERE id_cliente=%s"""
            cur.execute(sql, (nome, telefone, id_cliente))
            con.commit()

            cur.close()
            con.close()
            flash('Cliente editado com sucesso!', 'success')  # Mensagem de sucesso
            return redirect(url_for('lista_clientes'))

        except mysql.connector.Error as err:
            flash(f'Erro ao editar o Cliente: {err}', 'error')  # Mensagem de erro
            cur.close()
            con.close()
            return redirect(url_for('lista_clientes'))

    else:
        flash('Método inválido para o editar de Clientes.', 'error')  # Mensagem de erro
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
        cur.close()
        con.close()
        return redirect(url_for('pagina_principal'))

    sql = trata_busca_clientes(especificacoes)



    if sql == -1:
        flash(f'Erro de busca busca Inválida', 'error')  # Mensagem de erro
        con.close()
        cur.close()
        return redirect(url_for('lista_clientes'))        

    sql += " LIMIT %s, %s"

    print(sql)

    try:
        cur.execute(sql, (start_index, end_index))
        tuplas = cur.fetchall()

    except Exception as err:
        flash(f'Erro na busca do cliente: {err}', 'error')  # Mensagem de erro
        con.close()
        cur.close()
        return redirect(url_for('lista_clientes'))
    
    con.close()
    cur.close()

    return render_template("listar_clientes.html", busca=tuplas, page=page)

# -------------- ALUGUEIS ---------------------

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
            con.close()
            cur.close()
            flash(f'Erro ao chamar a procedure: {str(e)}', 'error')

        if id is not None:
            try:
                con = get_connection()
                cur = con.cursor(dictionary=True)

                # Consulta para recuperar os aluguéis do cliente com contagem de carros
                sql = """
                        SELECT A.*
                        FROM Aluguel AS A
                        WHERE id_cliente = %s
                        LIMIT %s, %s
                    """

                cur.execute(sql, (id, start_index, end_index))
                
                tuplas = cur.fetchall()

                con.close()
                cur.close()

                

                return render_template("listar_alugueis_cliente.html", dados=tuplas, nome_cliente=nome, page=page)
            except Exception as err:
                flash(f'Erro na busca de alugueis do cliente: {err}', 'error')
                con.close()
                cur.close()
                return redirect(url_for('lista_clientes'))
        else:
            flash('Erro na página: Usuário Inexistente', 'error')
            con.close()
            cur.close()
            return redirect(url_for('lista_clientes'))
    else:
        flash('Erro na METODO INVALIDO!', 'error')
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
        relatorio = request.form.get('relatorio')

        

        print(id_cliente)
        print(data_inicial)
        print(relatorio)

        # Consulte o banco de dados para obter os carros deste aluguel com base no ID do aluguel
        try:
            con = get_connection()
            cur = con.cursor(dictionary=True)

            sql = """
                SELECT C.*
                FROM Carro AS C
                INNER JOIN Aluguel AS A ON C.id_carro = A.id_carro
                WHERE A.id_cliente = %s AND A.data_inicial = %s LIMIT %s,%s;
            """

            cur.execute(sql, (id_cliente, data_inicial, start_index, end_index))
            tuplas = cur.fetchall()

            cur.close()
            con.close()

            # Renderize um modelo HTML para exibir os carros
            return render_template("listar_carros_aluguel.html", carros=tuplas, relatorio=relatorio, page=page)

        except Exception as err:
            flash(f'Erro ao buscar carros do aluguel: {err}', 'error')
            con.close()
            cur.close()
            return redirect(url_for('lista_clientes'))
    
    else:
        flash('Erro na METODO INVALIDO!', 'error')
        return redirect(url_for('lista_clientes'))
        

        
@app.route('/novo_aluguel', methods=['POST'])
def novo_aluguel():
    if request.method == 'POST':

        page = int(request.args.get('page', 1))
        start_index = (page - 1) * per_page
        end_index = start_index + per_page

        id_cliente = request.form.get('id_cliente')
        data_inicial = request.form.get('data_inicial')
        numero_dias = request.form.get('numero_de_dias')
        estado = ''

        print(id_cliente)
        print(data_inicial)   
        print(numero_dias)                   

        #Verifica a data e retorna o sql a ser usado e o estado a ser cadastrado o aluguel
        sql_carros, estado = verifica_data(data_inicial)

        try:
            con = get_connection()
            cur = con.cursor(dictionary=True)

            
            try:
                cur.execute(sql_carros)
                carros = cur.fetchall()

            except Exception as err:
                flash(f'Erro na seleção de carros para o aluguel: {err}', 'error')
                cur.close()
                con.close()
                return redirect(url_for('lista_clientes'))
        except Exception as err:
            flash(f'Erro ao buscar carros para o aluguel: {err}', 'error')
            cur.close()
            con.close()
            return redirect(url_for('lista_clientes'))
        
        con.close()
        cur.close()

        # Renderize um modelo HTML para exibir os carros
        return render_template("carros_para_alugar.html", carros=carros, id_cliente=id_cliente, data_inicial=data_inicial, estado_aluguel=estado,  numero_dias=numero_dias)

@app.route('/novo_aluguel/cadastrar', methods=['POST'])
def cadastra_aluguel():
    if request.method == 'POST':

        page = int(request.args.get('page', 1))
        start_index = (page - 1) * per_page
        end_index = start_index + per_page

        id_cliente = request.form.get('id_cliente')
        data_inicial = request.form.get('data_inicial')
        estado_aluguel = request.form.get('estado_aluguel')
        numero_dias = request.form.get('numero_dias')
        id_carro = request.form.get('id_carro')

        print(id_cliente)
        print(data_inicial) 
        print(estado_aluguel) 
        print(numero_dias) 
        print(id_carro)                 

        #Verifica a data e retorna o sql a ser usado e o estado a ser cadastrado o aluguel
        sql_data_retorno, sql_tipo = sql_cal_atributos(id_carro)


        try:
            con = get_connection()
            cur = con.cursor(dictionary=True)

            
            try:
                print(sql_data_retorno)
                cur.execute(sql_data_retorno,(data_inicial, numero_dias))
                data_retorno = cur.fetchone()

                print(f"data de retorno {data_retorno['data_retorno']}")

            except Exception as err:
                flash(f'Erro no calculo data_retorno para o aluguel: {err}', 'error')
                cur.close()
                con.close()
                return redirect(url_for('lista_clientes'))
            
            try:
                cur.execute(sql_tipo)
                valores_tipo_carro = cur.fetchall()

            except Exception as err:
                flash(f'Erro em conseguir o tipo do carro: {err}', 'error')
                cur.close()
                con.close()
                return redirect(url_for('lista_clientes'))
            
            try:
                valor_semanal = float(valores_tipo_carro[0]['valor_semanal'])
                valor_diario = float(valores_tipo_carro[0]['valor_diario'])

                print(numero_dias)

                valor_devido = 0

                valor_devido = calcula_valor_devido(valor_semanal, valor_diario, numero_dias)

                if valor_devido == 0:
                    flash('Erro no calulo dos dias do aluguel', 'error')
                    cur.close()
                    con.close()
                    return redirect(url_for('lista_clientes'))
                
            except Exception as err:
                flash(f'Erro nos calulos de valor: {err}', 'error')
                cur.close()
                con.close()
                return redirect(url_for('lista_clientes'))
            
            try:
                sql = """ 
                        INSERT INTO Aluguel (data_inicial, id_cliente, id_carro, estado_aluguel, NumeroDeDias, data_retorno, valor_devido) VALUES
                        (%s, %s, %s, %s, %s, %s, %s)
                        """

                data_retorno_str = data_retorno['data_retorno'].strftime('%Y-%m-%d %H:%M:%S')

                cur.execute(sql, (data_inicial, id_cliente, id_carro, estado_aluguel, numero_dias, data_retorno_str, valor_devido))
                con.commit()

            except Exception as err:
                flash(f'Erro criação do aluguel: {err}', 'error')
                cur.close()
                con.close()
                return redirect(url_for('lista_clientes'))

        except Exception as err:
            flash(f'Erro ao buscar carros para o aluguel: {err}', 'error')
            cur.close()
            con.close()
            return redirect(url_for('lista_clientes'))
        

        con.close()
        cur.close()

        # Renderize um modelo HTML para exibir os clientes
        return redirect(url_for('lista_clientes'))

# ---------------------- CONTROLE DOS ALUGUEIS ----------------

@app.route('/alugueis_pendentes')
def consulta_alugueis():
    page = int(request.args.get('page', 1))
    start_index = (page - 1) * per_page
    end_index = start_index + per_page

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
        cur.close()
        con.close()
        return redirect(url_for('pagina_principal'))

    try:
        con = get_connection()
        cur = con.cursor(dictionary=True)
    except Exception as e:
        flash(f'Erro iniciar conexao: {str(e)}', 'error')
        cur.close()
        con.close()
        return redirect(url_for('pagina_principal'))
    
    try: 
        
        sql = """
                SELECT C.id_cliente, C.nome_cliente, C.telefone_cliente, A.*
                FROM Cliente AS C
                JOIN Aluguel AS A ON C.id_cliente = A.id_cliente
                WHERE A.estado_aluguel = 'PENDENTE' LIMIT %s,%s
            """
            

        cur.execute(sql, (start_index, end_index))
        
        pendentes = cur.fetchall()

        for row in pendentes:
            id_cliente = row['id_cliente']
            id_carro = row['id_carro']
            data_inicial = row['data_inicial']
            valor_devido = row['valor_devido']
            estado_aluguel = row['estado_aluguel']

            if (valor_devido == None) or (estado_aluguel != 'FINALIZADO'):
                value = atualiza_valor_devido(con, cur, id_cliente, id_carro, data_inicial)
                
                if value != 1:
                    return value
            else:
                pass
    
    except Exception as err:
        flash(f'Erro na busca de alugueis pendentes: {err}', 'error')
        cur.close()
        con.close()
        return redirect(url_for('pagina_principal'))
    
    try:
    
        sql = """
                SELECT C.id_cliente, C.nome_cliente, C.telefone_cliente, A.*
                FROM Cliente AS C
                JOIN Aluguel AS A ON C.id_cliente = A.id_cliente
                WHERE A.estado_aluguel = 'ATIVO' LIMIT %s,%s
            """
            

        cur.execute(sql, (start_index, end_index))
        
        ativos = cur.fetchall()

        for row in ativos:
            id_cliente = row['id_cliente']
            id_carro = row['id_carro']
            data_inicial = row['data_inicial']
            valor_devido = row['valor_devido']
            estado_aluguel = row['estado_aluguel']

            if (valor_devido == None) or (estado_aluguel != 'FINALIZADO'):
                value = atualiza_valor_devido(con, cur, id_cliente, id_carro, data_inicial)
                
                if value != 1:
                    return value
            else:
                pass
    
    except Exception as err:
        flash(f'Erro na busca de alugueis ativos: {err}', 'error')
        cur.close()
        con.close()
        return redirect(url_for('pagina_principal'))
    
    try:
    
        sql = """
                SELECT C.id_cliente, C.nome_cliente, C.telefone_cliente, A.*
                FROM Cliente AS C
                JOIN Aluguel AS A ON C.id_cliente = A.id_cliente
                WHERE A.estado_aluguel = 'FINALIZADO' LIMIT %s,%s
            """
            

        cur.execute(sql, (start_index, end_index))
        
        finalizados = cur.fetchall()

        for row in finalizados:
            id_cliente = row['id_cliente']
            id_carro = row['id_carro']
            data_inicial = row['data_inicial']
            valor_devido = row['valor_devido']
            estado_aluguel = row['estado_aluguel']

            if (valor_devido == None) or (estado_aluguel != 'FINALIZADO'):
                value = atualiza_valor_devido(con, cur, id_cliente, id_carro, data_inicial)
                
                if value != 1:
                    return value
            else:
                pass
        
    
    except Exception as err:
        flash(f'Erro na busca de alugueis finalizados: {err}', 'error')
        cur.close()
        con.close()
        return redirect(url_for('pagina_principal'))
    
    try:
    
        sql = """
                SELECT C.id_cliente, C.nome_cliente, C.telefone_cliente, A.*
                FROM Cliente AS C
                JOIN Aluguel AS A ON C.id_cliente = A.id_cliente
                WHERE A.estado_aluguel = 'AGENDADO' LIMIT %s,%s
            """
            

        cur.execute(sql, (start_index, end_index))
        
        agendados = cur.fetchall()

        for row in agendados:
            id_cliente = row['id_cliente']
            id_carro = row['id_carro']
            data_inicial = row['data_inicial']
            valor_devido = row['valor_devido']
            estado_aluguel = row['estado_aluguel']

            if (valor_devido == None) or (estado_aluguel != 'FINALIZADO'):
                value = atualiza_valor_devido(con, cur, id_cliente, id_carro, data_inicial)
                
                if value != 1:
                    return value
            else:
                pass
    
    except Exception as err:
        flash(f'Erro na busca de alugueis agendados: {err}', 'error')
        cur.close()
        con.close()
        return redirect(url_for('pagina_principal'))

    con.close()
    cur.close()

    return render_template("controle_aluguel.html", pendentes=pendentes, qtd_pendentes=len(pendentes), ativos=ativos, qtd_ativos=len(ativos), finalizados=finalizados, qtd_finalizados=len(finalizados), agendados=agendados, qtd_agendados=len(agendados),  page=page)

    

def atualiza_valor_devido(con, cur, id_cliente, id_carro, data_inicial):

    sql_aluguel = "SELECT * FROM Aluguel WHERE id_cliente = %s AND id_carro=%s AND data_inicial = %s"

    sql_tipo = " SELECT valor_semanal, valor_diario, multa_semanal, multa_diaria FROM Tipo as T, Carro as C WHERE  C.tipo = T.nome_tipo AND C.id_carro = %s "

    try:
        cur.execute(sql_tipo, (id_carro,))
        valores_tipo_carro = cur.fetchall()

        cur.execute(sql_aluguel, (id_cliente, id_carro, data_inicial,))
        aluguel_cliente = cur.fetchone()

    except Exception as err:
        flash(f'Erro em conseguir o tipo e aluguel do carro: {err}', 'error')
        cur.close()
        con.close()
        return redirect(url_for('pagina_principal'))
    
    try:
        
        numero_dias = int(aluguel_cliente['NumeroDeDias'])
        valor_semanal = float(valores_tipo_carro[0]['valor_semanal'])
        valor_diario = float(valores_tipo_carro[0]['valor_diario'])
        multa_semanal = float(valores_tipo_carro[0]['multa_semanal'])
        multa_diaria = float(valores_tipo_carro[0]['multa_diaria'])

        valor_devido = 0

        print("Printando:!!!")
        print(numero_dias)
        print(valor_semanal)
        print(valor_diario)

    except Exception as err:
        flash(f'Erro na obtenção de valores: {err}', 'error')
        cur.close()
        con.close()
        return redirect(url_for('pagina_principal'))

    try:

        valor_devido = calcula_valor_devido(valor_semanal, valor_diario, numero_dias)

        if valor_devido == 0:
            flash('Erro na obtencao de dados!', 'error')
            return redirect(url_for('pagina_principal'))
        
        try:
            sql_verifica_multa = """
                                    SELECT DATEDIFF(NOW(), A.data_retorno) AS dias_passados
                                    FROM Aluguel as A
                                    WHERE estado_aluguel = 'PENDENTE' AND id_cliente = %s AND id_carro = %s AND data_inicial = %s
                                    """
            
            cur.execute(sql_verifica_multa, (id_cliente, id_carro, data_inicial,))

            dias_passado = cur.fetchone()

            print("DIAS PASSADOS:\n")
            print(dias_passado)

            if dias_passado != None:
                dias_passados = int(dias_passado['dias_passados'])
            else:
                dias_passados = 0

        except Exception as err:
            flash(f'Erro ao obter dias passados: {err}', 'error')
            cur.close()
            con.close()
            return redirect(url_for('pagina_principal'))


        print (valor_devido)

        if dias_passados > 0:
            valor_devido += calcula_valor_devido(multa_semanal, multa_diaria, dias_passados)
            print (valor_devido)
        

        sql = "UPDATE Aluguel SET valor_devido = %s WHERE id_cliente = %s AND id_carro = %s AND data_inicial = %s"
        
        cur.execute(sql, (valor_devido, id_cliente, id_carro, data_inicial,))
        con.commit()
        
        return 1
        
    except Exception as err:
        flash(f'Erro nos calulos de valor: {err}', 'error')
        cur.close()
        con.close()
        return redirect(url_for('pagina_principal'))


# -------------- TIPOS  ---------------

@app.route('/tabela_de_valores')
def lista_tipos():
    con  = get_connection()
    cur = con.cursor(dictionary=True)

    sql = """select * from Tipo """

    cur.execute(sql)
    tuplas = cur.fetchall()

    con.close()
    cur.close()

    return render_template("listar_tipos.html", dados=tuplas)


@app.route('/tabela_de_valores/editar/<string:nome_tipo>')
def editar_tipos(nome_tipo=None):
    if nome_tipo != None:
        con  = get_connection()
        cur = con.cursor(dictionary=True)
        sql = """ select * from Tipo WHERE nome_tipo=%s"""
        cur.execute(sql,(nome_tipo,))
        tuplas = cur.fetchall()

        con.close()
        cur.close()

        print(nome_tipo)

        return render_template("editar_tipo.html", dados=tuplas, nome=nome_tipo)
    else:
        flash('Nome tipo vazio', 'error')
        cur.close()
        con.close()
        return redirect(url_for('pagina_principal'))

@app.route('/tipo/editar/', methods=['POST'])
def editar_tipos_func():
    if request.method == 'POST':

        nome_tipo= request.form.get('nome_tipo')
        valor_diario = request.form.get('valor_diario')
        valor_semanal = request.form.get('valor_semanal')
        multa_diaria = request.form.get('multa_diaria')
        multa_semanal = request.form.get('multa_semanal')
        
        print(f"\nTipo: {nome_tipo} Diario: {valor_diario} Semanal: {valor_semanal} M. Diaria: {multa_diaria}  M. Semanal: {multa_semanal}")

        try:
            con = get_connection()
            cur = con.cursor()
            sql = sql = """
                        UPDATE Tipo
                        SET nome_tipo = %s, valor_diario=%s, valor_semanal=%s, multa_diaria=%s, multa_semanal=%s WHERE nome_tipo=%s
                        """
            cur.execute(sql, (nome_tipo, valor_diario, valor_semanal, multa_diaria, multa_semanal, nome_tipo))
            con.commit()
            cur.close()
            con.close()

            flash(f'Taxa do Tipo {nome_tipo} editada com sucesso!', 'success')  # Mensagem de sucesso
            return redirect(url_for('lista_tipos'))

        except mysql.connector.Error as err:
            flash(f'Erro ao editar o tipo: {err}', 'error')  # Mensagem de erro
            cur.close()
            con.close()
            return redirect(url_for('lista_tipos'))
        except Exception as err:
            flash(f'Erro ao editar o tipo: {err}', 'error')  # Mensagem de erro
            cur.close()
            con.close()
            return redirect(url_for('lista_tipos'))
    else:
        flash('Método inválido para a edição do carro.', 'error')  # Mensagem de erro
        return redirect(url_for('lista_tipos'))

@app.route('/pagar_aluguel', methods=['POST'])
def pagamento():
    if request.method == 'POST':

        id_cliente= request.form.get('modalIdCliente')
        id_carro = request.form.get('modalIdCarro')
        data_inicial = request.form.get('modaldataInicial')
        data_de_retorno = request.form.get('modaldataRetorno')

        sql = """
                SELECT * FROM Aluguel 
                WHERE data_inicial = %s AND id_cliente = %s AND id_carro = %s
            """
        
        try:
            con = get_connection()
            cur = con.cursor(dictionary=True)

        except Exception as err:
            flash(f'Erro ao conectar no Banco: {err}', 'error')  # Mensagem de erro
            cur.close()
            con.close()
            return redirect(url_for('pagina_principal'))
        

        try:
            cur.execute(sql, (data_inicial, id_cliente, id_carro))

            tupla = cur.fetchall()

            data_do_retorno = tupla[0]['data_retorno']
            estado_aluguel = tupla[0]['estado_aluguel']
            valor_devido = tupla[0]['valor_devido']

            data_de_retorno = str(data_de_retorno)
            data_do_retorno = str(data_do_retorno)

            dias = calcula_dias(data_do_retorno, data_de_retorno)

            if estado_aluguel == 'PENDENTE' and dias < 0:
                flash('Não é permitido pagar em datas passadas a data de retorno se é um pagamento pendente deve ser pago na data atual', 'error')  # Mensagem de erro
                return redirect(url_for('lista_clientes'))
            
            if estado_aluguel == 'ATIVO':

                
                
                if data_do_retorno == data_de_retorno:

                    cur.close()
                    con.close()

                    return render_template("area_pagamento.html", dados=tupla, data_retorno=data_de_retorno, valor_devido=valor_devido)

                else:

                    try:

                        dias = calcula_dias(data_inicial, data_de_retorno) # Calcula o numero de dias que foi alugado o carro até a devolução

                        dias = str(dias)

                    except Exception as err:
                        flash(f'Erro ao calcular o numero de dias: {err}', 'error')  # Mensagem de erro
                        cur.close()
                        con.close()
                        return redirect(url_for('lista_clientes'))
                    
                    try:

                        sql_tipo = """ SELECT valor_semanal, valor_diario
                                        FROM Tipo as T, Carro as C 
                                        WHERE  C.tipo = T.nome_tipo AND C.id_carro = %s """
                        
                        cur.execute(sql_tipo, (id_carro,))
                        tipo = cur.fetchall()

                        valor_semanal = tipo[0]['valor_semanal']
                        valor_diario = tipo[0]['valor_diario']

                        print(f":{valor_semanal}")
                        print(f":{valor_diario}")
                        print(f":{dias}")

                        valor_semanal = str(valor_semanal)
                        valor_diario = str(valor_diario)

                        valor_devido = calcula_valor_devido(valor_semanal, valor_diario, dias)

                        

                    except Exception as err:
                        flash(f'Erro ao calcular o novo valor devido: {err}', 'error')  # Mensagem de erro
                        cur.close()
                        con.close()
                        return redirect(url_for('lista_clientes'))
                    
                    

        except Exception as err:
            flash(f'Erro ao verificar data de retorno: {err}', 'error')  # Mensagem de erro
            cur.close()
            con.close()
            return redirect(url_for('pagina_principal'))
        

        con.close()
        cur.close()


        return render_template("area_pagamento.html", dados=tupla, data_retorno=data_de_retorno, valor_devido=valor_devido)
        

@app.route('/verifica_pagamento', methods=['POST'])
def pagamento_aluguel():
    if request.method == 'POST':

        id_cliente = request.form.get('id_cliente')
        id_carro = request.form.get('id_carro')
        data_inicial = request.form.get('data_inicial')
        valor_devido = float(request.form.get('valor_devido'))
        valor_pago = float(request.form.get('valor_pago'))
        data_retorno = request.form.get('data_retorno')
        relatorio = request.form.get('relatorio')

        print(id_cliente)
        print(id_carro)
        print(data_inicial)
        print(valor_devido)
        print(valor_pago)
        print(relatorio)

        print("Chegou aqui!")

        try:
            con = get_connection()
            cur = con.cursor(dictionary=True)

            print("Chegou aqui!1")

        except Exception as err:
            flash(f'Erro ao conectar no Banco: {err}', 'error')  # Mensagem de erro
            con.close()
            cur.close()
            return redirect(url_for('pagina_principal'))

        if valor_pago > valor_devido:

            print("Chegou aqui!2")
            flash('Erro no pagamento: Valor pago maior que o devido', 'error')  # Mensagem de erro
            con.close()
            cur.close()
            return redirect(url_for('lista_clientes'))
        
        elif valor_pago < valor_devido:

            print("Chegou aqui!3")

            # Valor pago tem que ser maior que 70% do valor devido
            if valor_pago > (valor_devido*0.7):

                valor_devido = valor_devido - valor_pago

                print(valor_devido)
                
                sql = """ UPDATE Aluguel 
                        SET valor_devido = %s, data_inicial=%s, data_retorno=%s, estado_aluguel = 'PENDENTE', NumeroDeDias=1, relatorio=%s
                        WHERE id_cliente = %s AND id_carro = %s AND data_inicial = %s
                        """

                try:

                    print("Chegou aqui!4")

                    cur.execute(sql, (valor_devido, data_retorno, data_retorno, relatorio, id_cliente, id_carro, data_inicial,))
                    con.commit()

                    print("Chegou aqui!11")

                except Exception as err:
                    flash(f'Erro no pagamento: Não foi possivel atualizar o valor da divida({err})', 'error')  # Mensagem de erro
                    con.close()
                    cur.close()
                    return redirect(url_for('lista_clientes'))
                
            else:

                print("Chegou aqui 10")

                flash('Erro no pagamento: Não foi possivel atualizar o valor da divida, o pagamento tem que ser maior que 70% do valor devido', 'error')  # Mensagem de erro
                con.close()
                cur.close()
                return redirect(url_for('lista_clientes'))
            
        elif valor_pago == valor_devido:

            print("Chegou aqui!5")

            sql = """ UPDATE Aluguel 
                        SET estado_aluguel = 'FINALIZADO', relatorio = %s, valor_devido =%s, data_retorno =%s
                        WHERE id_cliente = %s AND id_carro = %s AND data_inicial = %s 
                        
                    """

            try:

                print("Chegou aqui!6")

                cur.execute(sql, (relatorio, valor_pago, data_retorno,id_cliente, id_carro, data_inicial,))
                con.commit()

            except Exception as err:
                flash(f'Erro no pagamento: Não foi possivel atualizar o valor da divida({err})', 'error')  # Mensagem de erro   
                con.close()
                cur.close()
                return redirect(url_for('lista_clientes'))
        
        else:

            print("Chegou aqui!7")

            flash('Algo errado aconteceu!', 'error')
            con.close()
            cur.close()
            return redirect(url_for('pagina_principal'))

        con.close()
        cur.close()

        print("Cheguei no final")
                
        flash('Atualização de Pagamento realizado com sucesso!', 'success')
        return redirect(url_for('lista_clientes'))

    else:
        print("Chegou aqui!7")
        flash('Algo errado aconteceu!', 'error')
        con.close()
        cur.close()
        return redirect(url_for('lista_clientes'))

if __name__ == '__main__':
    app.run(host='localhost', port=5000, debug= True)

