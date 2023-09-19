from datetime import datetime
from dateutil.relativedelta import relativedelta

def calcula_dias(data_inicial_str, data_final_str):
    # Converta as strings em objetos datetime
    data_inicial = datetime.fromisoformat(data_inicial_str)
    data_final = datetime.fromisoformat(data_final_str)

    # Calcule a diferença em meses e dias
    diferenca = relativedelta(data_final, data_inicial)

    
    # Extraia o número de meses e dias da diferença
    meses = diferenca.months
    dias = diferenca.days

    # Converta os valores para um único número de dias considerando os meses
    dias_totais = (meses * 30) + dias

    dias_passados_inteiro = int(dias_totais)

    return dias_passados_inteiro


