from datetime import datetime
from dateutil import parser

#pip install python-dateutil


def verifica_data(data_hora_input):

    data_inicial = data_hora_input
    estado = ''
    # Obtenha a data e hora atual
    data_hora_atual = datetime.now()

    # Analise a string para criar um objeto datetime
    data_hora_input = parser.isoparse(data_hora_input)

    # Compare a data e hora atual com a variável do input
    if data_hora_atual < data_hora_input:
        print("A data e hora atual é anterior à data e hora do input.")
        estado = 'AGENDADO'

        #sql_carros = """
         #           SELECT 
          #              C.*
           #         FROM 
            #            Carro AS C
             #       WHERE
              #          C.id_carro IN (
               #             SELECT DISTINCT A.id_carro
                #            FROM Aluguel AS A
                 #           WHERE A.estado_aluguel IN ('ATIVO', 'AGENDADO', 'FINALIZADO')
                  #          AND CalcularDataTerminoAluguel(A.data_inicial, A.NumeroDeDias) <= '"""+data_inicial+"""' -- Data inicial fornecida
                   #     )
                    #"""

    else:
        print("A data e hora atual é igual à data e hora do input.")
        estado = 'ATIVO'

    sql_carros = """
                SELECT C.id_carro, C.tipo, C.marca, C.modelo, C.ano
                FROM Carro AS C
                WHERE C.id_carro NOT IN (
                    SELECT DISTINCT id_carro
                    FROM Aluguel
                    WHERE estado_aluguel IN ('ATIVO', 'AGENDADO', 'PENDENTE')
                )
                ORDER BY C.id_carro;
                """

    return sql_carros, estado

        
def sql_cal_atributos(id_carro):
        
    sql_data_retorno =  "SELECT CalcularDataTerminoAluguel(%s, %s) AS data_retorno"


    sql_tipo = " SELECT valor_semanal, valor_diario FROM Tipo as T, Carro as C WHERE  C.tipo = T.nome_tipo AND C.id_carro = "+id_carro+" "

    return sql_data_retorno, sql_tipo

def calcula_valor_devido(valor_semanal, valor_diario, numero_dias):
    # Converte os valores de entrada para números (int ou float)
    valor_semanal = float(valor_semanal)
    valor_diario = float(valor_diario)
    
    dia = True
    valor = 0
    dias = int(numero_dias)  # Converte o número de dias para um inteiro

    while dia:
        
        while dias > 7:
            valor += valor_semanal
            dias -= 7
        
        while dias > 0:
            valor += valor_diario
            dias -= 1
        
        if dias == 0:
            dia = False;   
            

    return valor

