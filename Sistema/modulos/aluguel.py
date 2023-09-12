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
        estado == 'AGENDADO'

        sql = """
                SELECT 
                    C.*
                FROM 
                    Carro AS C
                WHERE
                    C.id_carro IN (
                        SELECT DISTINCT RC.id_carro
                        FROM RefereCarros AS RC
                        INNER JOIN Aluguel AS A ON RC.data_inicial = A.data_inicial
                        WHERE A.estado_aluguel IN ('ATIVO', 'AGENDADO', 'FINALIZADO')
                        AND CalcularDataTerminoAluguel(A.data_inicial, A.NumeroDeDias) <= '"""+data_inicial+"""' -- Data inicial fornecida
                    )
                """
    else:
        print("A data e hora atual é igual à data e hora do input.")
        estado = 'ATIVO'

        sql = """
                SELECT C.id_carro, C.tipo, C.marca, C.modelo, C.ano
                FROM Carro AS C
                LEFT JOIN RefereCarros AS RC ON C.id_carro = RC.id_carro
                LEFT JOIN Aluguel AS A ON RC.data_inicial = A.data_inicial AND RC.id_cliente = A.id_cliente
                WHERE A.estado_aluguel IS NULL OR A.estado_aluguel NOT IN ('ATIVO', 'AGENDADO')
                OR RC.id_carro IS NULL
            """

        return sql, estado

        
        