import pandas as pd
from fastapi.responses import JSONResponse
from repository import repository
from datetime import datetime
from log.log import log


logger = log()


def monta_consulta_pdv_loja(start, end, page_size):
    try:
        lojas = repository.consulta_pdv_full()
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
        logger.info('arquivo enviado')
        return { "data_atualização": today, "lojas": lista_lojas[start:end], "paginacao": [{"total": data_length, "count": page_size}]}
    except Exception as E:
        logger.error(E)
        return JSONResponse(status_code=404, content={"message": "Não encontrado"})


def atualiza_status_pdv(arquivo):
    try:
        response = repository.atualiza_status_manutencao(arquivo)
        logger.info('arquivo atualizado')
        return JSONResponse(status_code=200, content={"message": 'Atualizado com Sucesso'})
    except Exception as E:
        logger.error(E)
        return JSONResponse(status_code=404, content={"message": "Não encontrado"})


def deletaPdv(arquivo):
    try:
        response = repository.deletaPdv(arquivo)
        logger.info('arquivo deletado')
        return JSONResponse(status_code=200, content={"message": 'Pdv Deletado com Sucesso'})
    except Exception as E:
        logger.error(E)
        return JSONResponse(status_code=404, content={"message": "Não encontrado"})


def gera_arquivos(loja):
    try:
        if loja == 5 or loja > 55:
            pass
        else:
            arquivo_retag = repository.gera_arquivo(int(loja))
            consulta_banco = pd.DataFrame(repository.consulta_status_pdv(loja),
                                          columns=['loja', 'pdv', 'status_alt', 'status_tot'])

            if arquivo_retag is None:
                logger.warning('Arquivo loja {loja} não encontrado!')
                return JSONResponse(status_code=404, content={"message": f'Arquivo loja {loja} não encontrado!'})

            elif consulta_banco.empty is True:
                repository.insert_status_pdv(arquivo_retag)
                logger.info('Arquivos PDVs loja {loja} Atualizados com Sucesso!')
                return JSONResponse(status_code=200, content={"message": f"Arquivos PDVs loja {loja} Atualizados com Sucesso!"})

            elif len(arquivo_retag) > len(consulta_banco):
                dif_pdv = pd.concat([arquivo_retag, consulta_banco]).drop_duplicates(subset=['pdv'], keep=False, ignore_index=True)
                repository.insert_status_pdv(dif_pdv)
                logger.info('Arquivos PDVs loja {loja} Atualizados com Sucesso!')
                return JSONResponse(status_code=200, content={"message": f"Arquivos PDVs loja {loja} Atualizados com Sucesso!"})

            else:
                repository.update_status_pdv(arquivo_retag)
                logger.info('Arquivos PDVs loja {loja} Atualizados com Sucesso!')
                return JSONResponse(status_code=200, content={"message": f"Arquivos PDVs loja {loja} Atualizados com Sucesso!"})
    except Exception as E:
        logger.error(E)
        return JSONResponse(status_code=404, content={"message": "Não encontrado"})


def gera_arquivos_geral():
    for loja in range(1, 55, 1):
        gera_arquivos(loja=loja)

    response = {"message": "Atualizados com Sucesso!"}
    return JSONResponse(status_code=200, content=response)
