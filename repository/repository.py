from connection.connection import Conexao
import shutil
import pandas as pd
from datetime import datetime


def consulta_pdv(loja):
    con = Conexao()
    cursor = con.con_mysql.cursor()

    cursor.execute(f"SELECT cl.loja, cl.pdv, "
                   f"cl.data_inclusao, cl.data_alteracao, "
                   f"cl.status_alt, cl.status_total, cl.status_operador, "
                   f"cl.status_finalizadora, cl.status_manutencao "
                   f"FROM carga_lojas cl "
                   f"WHERE cl.loja = {loja} ")
    consulta = cursor.fetchall()
    con.con_mysql.close()
    cursor.close()
    return consulta


def consulta_pdv_full():
    con = Conexao()
    cursor = con.con_mysql.cursor()

    cursor.execute(f"SELECT cl.loja, cl.pdv, "
                   f"cl.data_inclusao, cl.data_alteracao, "
                   f"cl.status_alt, cl.status_total, cl.status_operador, "
                   f"cl.status_finalizadora, cl.status_manutencao "
                   f"FROM carga_lojas cl "
                   f"order by cl.loja ")
    consulta = cursor.fetchall()
    con.con_mysql.close()
    cursor.close()
    return consulta

def consulta_status_pdv(loja):
    # Abrindo a conexão com o banco e cursor
    con = Conexao()
    cursor = con.con_mysql.cursor()
    # iniciando a consulta
    cursor.execute(f"SELECT "
                   f"cl.loja, cl.pdv, cl.status_alt, cl.status_total "
                   f"FROM carga_lojas cl "
                   f"WHERE cl.loja = {int(loja)} ")
    consulta = cursor.fetchall()
    # Fechando a conexão com o banco e cursor
    con.con_mysql.close()
    cursor.close()
    return consulta

def update_status_pdv(arquivo_retag):

    # Abrindo a conexão com o banco e cursor
    con = Conexao()
    cursor = con.con_mysql.cursor()
    for linha in range(len(arquivo_retag.loja)):
        today = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        l = arquivo_retag.loja[linha]
        p = arquivo_retag.pdv[linha]
        altretag = arquivo_retag.status_alt[linha]
        totretag = arquivo_retag.status_tot[linha]
        cursor.execute(F"UPDATE carga_lojas cl "
                           F"SET cl.status_alt = '{altretag}', cl.status_total = '{totretag}', data_alteracao = '{today}' "
                           F"WHERE cl.loja = {l} AND cl.pdv = {p} ")
    # fazendo o commit das informações
    con.con_mysql.commit()
    # Fechando a conexão com o banco e cursor
    con.con_mysql.close()
    cursor.close()

def insert_status_pdv(arquivo):

    #Abrindo a conexão com o banco e cursor
    con = Conexao()
    cursor = con.con_mysql.cursor()

    for linha in range(len(arquivo.loja)):
        today = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        l = arquivo.loja[linha]
        pRet = arquivo.pdv[linha]
        altRet = arquivo.status_alt[linha]
        totRet = arquivo.status_tot[linha]

        cursor.execute(F"INSERT INTO carga_lojas (loja, pdv, status_alt, data_inclusao, status_total) "
                       F"VALUES({l}, {pRet}, '{altRet}', '{today}', '{totRet}') ")

    # Fazendo o commit das informações
    con.con_mysql.commit()
    # Fechando a conexão com o banco e cursor
    con.con_mysql.close()
    cursor.close()

def busca_arquivo_retag(loja, arquivo):
    # Fazendo a conexão com os Retag Lojas
    if loja == 14:
        retorno = shutil.copy(f"//192.168.141.150/c/log_carga_pdv/{str(arquivo)}",
                              f"./repository/arquivo/{str(arquivo)}")
    elif loja == 21:
        retorno = shutil.copy(f"//192.168.21.100/c/log_carga_pdv/{arquivo}",
                    f"./repository/arquivo/{str(arquivo)}")
    elif loja == 26:
        retorno = shutil.copy(f"//192.168.26.150/c/log_carga_pdv/{str(arquivo)}",
                    f"./repository/arquivo/{str(arquivo)}")
    elif loja == 30:
        retorno = shutil.copy(f"//192.168.30.102/c/log_carga_pdv/{str(arquivo)}",
                    f"./repository/arquivo/{str(arquivo)}")
    elif loja == 49:
        retorno = shutil.copy(f"//10.132.49.101/c/log_carga_pdv/{str(arquivo)}",
                    f"./repository/arquivo/{str(arquivo)}")
    else:
        retorno = shutil.copy(f"//192.168.{loja}.101/c/log_carga_pdv/{str(arquivo)}",
                    f"./repository/arquivo/{str(arquivo)}")

def gera_arquivo(loja):
    try:
        dados = []
        #nome dos arquivos padrão do retag
        name_arq = ['PRALT.txt', 'PRPRD.txt']
        for arquivo in name_arq:
            #copiando os arquivos do Retag
            busca_arquivo_retag(loja, str(arquivo))
            #montando o arquivo da loja
            if str(arquivo) == 'PRALT.txt':
                with open("./repository/arquivo/PRALT.txt") as files:
                    for f in files:
                        a = f.split("|")
                        l = loja
                        p = str(a[1])
                        if a[2] == "ATUALIZADO\n":
                            s = "T"
                        else:
                            s = "F"
                        dado = [l, p, s]
                        dados.append(dado)
                    monta_arq_PRALT = pd.DataFrame(dados, columns=['loja', 'pdv', 'status_alt'])
                    dados = []
            if str(arquivo) == 'PRPRD.txt':
                with open("./repository/arquivo/PRPRD.txt") as files:
                    for f in files:
                        a = f.split("|")
                        p = str(a[1])
                        if a[2] == "ATUALIZADO\n":
                            s = "T"
                        else:
                            s = "F"
                        dado = [p, s]
                        dados.append(dado)
                        monta_arq_PRPRD = pd.DataFrame(dados, columns=['pdv', 'status_tot'])
                    dados = []
        #retonando o arquivo montado
        arquivo = pd.merge(monta_arq_PRALT, monta_arq_PRPRD, how='left', on='pdv')
        return arquivo
    except Exception as E:
        print(E)
        return E

def atualiza_status_manutencao(arquivo):

    # Abrindo a conexão com o banco e cursor
    con = Conexao()
    cursor = con.con_mysql.cursor()
    l = arquivo.loja
    print(l)
    p = arquivo.pdv
    print(p)
    altManut = arquivo.status_manutencao
    print(altManut)
    cursor.execute(F"UPDATE carga_lojas c SET c.status_manutencao = '{altManut}' WHERE c.loja = {l} AND c.pdv = {p} ")
    # fazendo o commit das informações
    con.con_mysql.commit()
    # Fechando a conexão com o banco e cursor
    con.con_mysql.close()
    cursor.close()