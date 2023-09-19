from markupsafe import escape


def trata_busca_clientes(especificacoes):
    if len(especificacoes) > 0:

        if especificacoes[0] != '':
            especificacoes[0] = especificacoes[0].upper()  

        if especificacoes[2] != '':
            if len(especificacoes[2]) > 5:
                numero = especificacoes[2]
                especificacoes[2] = numero[:5] + "-" + numero[5:]

        sql = "select * from Cliente "

        atributo = ['nome_cliente', 'telefone_cliente']

        if especificacoes[0] != '' and especificacoes[1] != '' and especificacoes[2] != '':
            sql += f"where {atributo[0]} LIKE '{escape(especificacoes[0])}%' and {atributo[1]} LIKE '({escape(especificacoes[1])}) {escape(especificacoes[2])}%'"
        elif especificacoes[0] != '' and especificacoes[1] != '':
            sql += f"where {atributo[0]} LIKE '{escape(especificacoes[0])}%' and {atributo[1]} LIKE '({escape(especificacoes[1])})%'"
        elif especificacoes[0] != '' and especificacoes[1] == '':
            sql += f"where {atributo[0]} LIKE '{escape(especificacoes[0])}%'"
        elif especificacoes[0] == '' and especificacoes[1] != '' and especificacoes[2] != '':
            sql += f"where {atributo[1]} LIKE '({escape(especificacoes[1])}) {escape(especificacoes[2])}%'"
        elif especificacoes[0] == '' and especificacoes[1] == '' and especificacoes[2] != '':
            sql += f"where {atributo[1]} LIKE '(__) {escape(especificacoes[2])}%'"
        elif especificacoes[0] == '' and especificacoes[1] != '' and especificacoes[2] == '':
            sql += f"where {atributo[1]} LIKE '({escape(especificacoes[1])})%'"
        else:
            sql = -1

        return sql