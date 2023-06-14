from ..repository import CheckoutsRepository, StoresRepository, FilesRepository
from ..connection import DBconnection
from ..log import logger
from ..models import Message

from fastapi import HTTPException
from datetime import datetime
from pathlib import Path
import asyncio
import os

logger = logger()


class CheckoutsService:
    """ Classe para manipular os dados dos checkouts
    """
    def get_all_checkout(self):
        """Busca todos os checkouts do banco de dados
        """
        logger.info('buscando dados do banco')
        with DBconnection() as session:
            # abrindo conexão com o banco
            repository = CheckoutsRepository(session)

            # buscando dados do banco
            checkouts = repository.get_all_checkout()

            # verificando se a consulta retornou dados
            if not checkouts:
                logger.info('lista de checkouts vazia')
                raise HTTPException(status_code=404, detail='lista de checkouts vazia')

            # transformando os dados em dicionario
            return self.__tratar_dados(checkouts)

    def __tratar_dados(self, datas: list):
        """Transforma os dados em dicionario
        """
        logger.info('transformando os dados em dicionario')
        store_list = []
        checkouts_list = []

        for i in range(1, 55):
            # separando as lojas
            for data in datas:

                # separando os checkouts por loja
                if i == int(data.loja):
                    checkout = {
                        "checkout": data.checkout,
                        "data_inclusao": str(data.data_inclusao),
                        "status_alterada": data.status_alterada,
                        "status_total": data.status_total,
                        "status_manutencao": data.status_manutencao,
                        "data_alteracao": str(data.data_alteracao)
                    }

                    checkouts_list.append(checkout)

            # montando a lista de lojas
            store_list.append(
                {
                    "loja": i,
                    "pdvs": checkouts_list
                }
            )
            checkouts_list = []

        # arquivo de lojas gerado
        lojas_response = {
            "data_atualizacao": str(datetime.now()),
            "lojas": store_list
        }

        return lojas_response

    def insert_checkout(self, loja: str, checkout: str, status_alterada: bool = 0, status_total: bool = 0, status_manutencao: bool = 0):
        """Insere os dados do checkout no banco de dados
        """
        logger.info('inserindo dados do checkout')
        # abrindo conexão com o banco
        with DBconnection() as session:
            # instanciando o repositorio
            repository = CheckoutsRepository(session)

            # buscando dados do banco
            query = repository.get_checkout(loja, checkout)

        # verificando se o checkout já existe
        if not query:
            # inserindo dados do checkout
            repository.insert_checkout(loja, checkout, status_alterada, status_total, status_manutencao)
            session.commit()
            return True

    async def update_checkout(self, loja: str, checkout: str, status_manutencao=0):
        """Atualiza os dados do checkout no banco de dados
        """
        logger.info('atualizando dados do checkout')
        # abrindo conexão com o banco
        with DBconnection() as session:
            # instanciando o repositorio
            repository = CheckoutsRepository(session)

            # buscando dados do banco
            query = repository.get_checkout(loja, checkout)

            # verificando se o checkout já existe
            if query:
                # atualizando dados do checkout
                await repository.update_checkout(loja=loja, checkout=checkout, status_manut=status_manutencao)

                logger.info(f'checkout {checkout} da loja {loja} atualizado com sucesso')

                return Message(message=f'checkout {checkout} da loja {loja} atualizado com sucesso')
            else:
                logger.warning(f'checkout {checkout} da loja {loja} não existe')
                raise HTTPException(status_code=404, detail=f'checkout {checkout} da loja {loja} não existe')

    def delete_checkout(self, loja: str, checkout: str):
        """Deleta os dados do checkout no banco de dados
        """
        logger.info('deletando dados do checkout')

        # abrindo conexão com o banco
        with DBconnection() as session:
            # instanciando o repositorio
            repository = CheckoutsRepository(session)

            # buscando dados do banco
            query = repository.get_checkout(loja, checkout)

            # verificando se o checkout já existe
            if query:
                # deletando dados do checkout
                repository.delete_checkout(loja, checkout)
                logger.info(f'checkout {checkout} da loja {loja} deletado com sucesso')
                return Message(message=f'checkout {checkout} da loja {loja} deletado com sucesso')
            else:
                logger.warning(f'checkout {checkout} da loja {loja} não existe')
                raise HTTPException(status_code=404, detail=f'checkout {checkout} da loja {loja} não existe')

    @classmethod
    async def update_status_checkout(cls, loja=None):
        logger.info('inicio da atualização dos status dos checkouts')

        with DBconnection() as session:
            # instanciando os repositorios
            repositoryStore = StoresRepository(session)
            repositoryCheckout = CheckoutsRepository(session)
            repositoryFile = FilesRepository()

        # buscando dados do banco
        stores = repositoryStore.get_all_store(loja=loja)

        # buscando dados do banco
        df_checkouts_db = repositoryCheckout.get_checkout_df()

        # Atualizando as arquivos do retag
        await cls.get_file_retag(stores=stores)

        # buscando dados do arquivo
        df_checkouts_file = await repositoryFile.get_checkouts_file(list_loja=stores)

        # criando uma chave para fazer a diferença entre os dataframes
        df_checkouts_db['chave'] = df_checkouts_db['loja'].astype(str) + df_checkouts_db['checkout'].astype(str)
        df_checkouts_file['chave'] = df_checkouts_file['loja'].astype(str) + df_checkouts_file['checkout'].astype(str)

        # Separando os dados que não estão no banco de dados e os que estão no banco de dados
        df_dif = df_checkouts_file[~df_checkouts_file['chave'].isin(df_checkouts_db['chave'])]
        df_equal = df_checkouts_file[df_checkouts_file['chave'].isin(df_checkouts_db['chave'])]

        logger.info('Inserindo os dados que não estão no banco')
        # Inserindo os dados que não estão no banco de dados
        if not df_dif.empty:
            repositoryCheckout.insert_checkout_df(dataframe=df_dif)

        # lista de tarefas
        tasks = []

        logger.info('Verificando dados que estão no banco')
        # Verificando se os dados que estão no banco de dados estão atualizados
        for _, row in df_equal.iterrows():

            # separando os dados do dataframe
            loja, checkout, status_alterada, status_total, chave = row

            # buscando os dados do banco de dados ref a chave do dataframe
            checkout_db = df_checkouts_db.loc[df_checkouts_db['chave'] == chave]

            # verificando se os dados do banco de dados são diferentes dos dados do dataframe
            if not checkout_db['status_alterada'].values[0] == status_alterada or not checkout_db['status_total'].values[0] == status_total:
                # crianco a tarefa de atualizar o checkout
                task = asyncio.create_task(
                    repositoryCheckout.update_checkout(
                        loja=loja,
                        checkout=checkout,
                        status_alt=status_alterada,
                        status_tot=status_total
                    )
                )
                tasks.append(task)

        # executando as tarefas em paralelo
        asyncio.gather(*tasks)

        logger.info('fim da atualização dos status dos checkouts')

    @classmethod
    async def reset_status(cls):
        logger.info('iniciando a atualização dos status dos checkouts')
        # abrindo conexão com o banco
        with DBconnection() as session:
            # instanciando os repositorios
            repositoryCheckout = CheckoutsRepository(session)

        # Atualizando os status para 0
        repositoryCheckout.update_all()
        logger.info('fim da atualização dos status dos checkouts')

    @staticmethod
    async def get_file_retag(stores: list):
        """Busca os arquivos do retag e copia para a pasta de arquivos do checkout
        """
        logger.info('inicio da copia dos arquivos do retag')

        # instanciando a classe de arquivos
        files = FilesRepository()

        # lista de tarefas
        tasks = []

        # criando a pasta de arquivos do checkout
        path = "./arquivo"
        os.makedirs(path, exist_ok=True)

        for store in stores:
            loja = store.loja
            path = store.path
            # path = '//192.168.141.150/c/log_carga_pdv'
            task = asyncio.create_task(files.copy_file_retag(path=path, loja=loja))
            tasks.append(task)

        await asyncio.gather(*tasks)

        logger.info('fim da copia dos arquivos do retag')

    @staticmethod
    def update_status(loja: str):
        logger.info('inicio da atualização dos status dos checkouts')


class StoresService:
    """ Classe de serviço para manipulação dos dados das lojas"""
    def get_all_store(self):
        """Busca todos os dados das lojas no banco de dados
        """
        logger.info('buscando dados do banco')
        with DBconnection() as session:
            # abrindo conexão com o banco
            repository = StoresRepository(session)

            # buscando dados do banco
            query = repository.get_all_store()

        return query

    def update_store(self, loja: str, path: str):
        """Atualiza os dados da loja no banco de dados
        """
        logger.info('atualizando lojas')
        with DBconnection() as session:
            # abrindo conexão com o banco
            path = Path(path)

            repository = StoresRepository(session)

            # atualizando os dados da loja
            repository.update_store(loja, path)

            logger.info(f'loja {loja} atualizada com sucesso')

    def insert_loja(self, loja: str, path: str):
        """Insere os dados da loja no banco de dados
        """
        logger.info('inserindo lojas')
        with DBconnection() as session:
            # abrindo conexão com o banco
            path = Path(path)

            repository = StoresRepository(session)

            # inserindo os dados da loja
            repository.insert_store(loja, path)

            logger.info(f'loja {loja} inserida com sucesso')
