from markupsafe import escape

def trata_busca_carros(especificacoes):
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
    
    return sql