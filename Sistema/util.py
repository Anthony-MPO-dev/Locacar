import mysql.connector

# Estabece uma conexao com o servidor de Banco de Dados
def get_connection():
    try:
        con = mysql.connector.connect(option_files = "./config.cnf")
        print("Retornando objeto de conexão")
        return con
    except mysql.connector.Error as err:
        print("Problemas com a conexão com o BD: {}".format(err))
