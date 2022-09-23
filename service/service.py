import pandas
import pandas as pd
from fastapi.responses import JSONResponse
from model import model
import repository.repository
from datetime import datetime


def monta_consulta_pdv_loja(start,end, page_size):
    lojas = repository.repository.consulta_pdv_full()
    lista_lojas = []
    lista_pdv = []
    count = 0
    today = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    i = 1
    while i < 54:
        for linha in lojas:
            if linha[0] == str(i):
                loja = linha[0]
                monta_jason = {
                    "pdv": linha[1],
                    "status_alt": linha[4],
                    "status_total": linha[5],
                    "status_operador": linha[6],
                    "status_finalizadora": linha[7],
                    "status_manutencao": linha[8]
                }
                lista_pdv.append(monta_jason)
                count = 1
            else:
                pass
        if count == 1:
            lista = {
                f"loja_{loja}": lista_pdv
            }
            lista_lojas.append(lista)
            lista_pdv = []
        count = 0
        i += 1
    data_length = len(lista_lojas)
    return { "data_atualização": today, "lojas": lista_lojas[start:end], "paginacao": [{"total": data_length, "count": page_size}]}


def monta_consulta_pdv(loja, start, end, page_size):
    consulta = []
    busca_consulta = repository.repository.consulta_pdv(loja)
    if busca_consulta == []:
        return JSONResponse(status_code=404, content={"message": "Não encontrado"})
    else:
        length = len(busca_consulta)
        for linha in busca_consulta:
            consulta.append(model.ConsultaPdv(
                loja=linha[0],
                pdv=linha[1],
                datainclusao=str(linha[2]),
                dataalteracao=str(linha[3]),
                status_alt=linha[4],
                status_total=linha[5],
                status_operador=linha[6],
                status_finalizadora=linha[7],
                status_manutencao=linha[8]
            ))

        return {"lojas": consulta[start:end], "paginacao": [{"total": length, "count": page_size}]}


def monta_consulta_pdv_full():
    busca_consulta = repository.repository.consulta_pdv_full()
    consulta = []
    for linha in busca_consulta:
        consulta.append(model.ConsultaPdv(
            loja=linha[0],
            pdv=linha[1],
            datainclusao=str(linha[2]),
            dataalteracao=str(linha[3]),
            status_alt=linha[4],
            status_total=linha[5],
            status_operador=linha[6],
            status_finalizadora=linha[7],
            status_manutencao=linha[8]
        ))
    return consulta

def trata_consulta(consulta):
    if consulta == []:
        return JSONResponse(status_code=404, content={"message": "Não encontrado"})
    else:
        return consulta


def atualiza_status_pdv(arquivo):
    response = repository.repository.atualiza_status_manutencao(arquivo)
    return response


def deletaPdv(arquivo):
    response = repository.repository.deletaPdv(arquivo)
    return response


def gera_arquivos():
    #for loja in range(1,54):
    loja = 14
    if loja == 5 or loja > 54:
        pass
    else:
        arquivo_retag = repository.repository.gera_arquivo(loja)
        arquivo = repository.repository.consulta_status_pdv(loja)
        consulta_banco = pd.DataFrame(arquivo, columns=['loja', 'pdv', 'status_alt', 'status_tot'])
        if arquivo == []:
            repository.repository.insert_status_pdv(arquivo_retag)
        elif len(arquivo_retag) != len(consulta_banco):
            dif_pdv = pd.concat([arquivo_retag, consulta_banco]).drop_duplicates(subset=['pdv'], keep=False, ignore_index=True)
            repository.repository.insert_status_pdv(dif_pdv)
        else:
            repository.repository.update_status_pdv(arquivo_retag)