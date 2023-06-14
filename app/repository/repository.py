from ..models import StatusCheckouts, Stores
from ..log import logger

import os
import shutil
from pathlib import Path
import asyncio
import pandas as pd

logger = logger()


class CheckoutsRepository:
    """ Classe para manipular as Checkouts
    """
    def __init__(self, session):
        self.session = session

    def get_all_checkout(self) -> list:
        """ Retorna todos os checkouts de todas as lojas
        """
        query = self.session.query(StatusCheckouts).order_by(StatusCheckouts.loja, StatusCheckouts.checkout).all()
        return query

    def get_checkout(self, loja: int, checkout: int) -> list:
        """ Retorna um checkout de uma loja
        """
        query = self.session.query(StatusCheckouts)\
            .filter(StatusCheckouts.loja == int(loja), StatusCheckouts.checkout == int(checkout))\
            .order_by(StatusCheckouts.checkout).first()
        return query

    def get_checkout_df(self):
        """ Retorna todos os checkouts de todas as lojas em um dataframe do pandas
        """
        # buscando os dados do banco e transformando em um dataframe
        checkouts = pd.read_sql_table('status_checkouts', self.session.bind)

        checkouts = checkouts.drop(columns=["id", "data_inclusao", "data_alteracao", "status_manutencao"])

        # retornando os dados em um dataframe
        return checkouts

    async def update_checkout(self, loja: int, checkout: int, status_alt: bool = None,
                              status_tot: bool = None, status_manut: bool = None):
        """ Atualiza o status de um checkout
        """
        query = self.session.query(StatusCheckouts).filter(StatusCheckouts.loja == int(loja), StatusCheckouts.checkout == int(checkout)).first()

        if status_alt is not None:
            query.status_alterada = status_alt

        if status_tot is not None:
            query.status_total = status_tot

        if status_manut is not None:
            query.status_manutencao = status_manut

        self.session.commit()

    def update_all(self):
        """ Atualiza todos os checkouts com status 0
        """
        self.session.query(StatusCheckouts).update(
            {StatusCheckouts.status_alterada: 0, StatusCheckouts.status_total: 0, StatusCheckouts.status_manutencao: 0}
        )
        self.session.commit()

    def insert_checkout(self, loja, checkout, status_alterada=0, status_total=0, status_manutencao=0):
        """ Insere um checkout
        """
        try:
            session = self.session.session
            checkout = StatusCheckouts(
                loja=loja,
                checkout=checkout,
                status_alterada=status_alterada,
                status_total=status_total,
                status_manutencao=status_manutencao
            )
            session.add(checkout)
        except Exception:
            logger.error('Erro ao inserir checkout')
            raise Exception('Erro ao inserir checkout')

    def insert_checkout_df(self, dataframe):
        """ Insere um checkout
        """
        # Removendo a coluna chave
        dataframe = dataframe.drop(columns=['chave'])

        # Inserindo os dados no banco de dados com o pandas
        dataframe.to_sql('status_checkouts', self.session.bind, if_exists='append', index=False)

    def delete_checkout(self, loja: int, checkout: int):
        """ Deleta um checkout
        """
        query = self.session.query(StatusCheckouts).filter(
            StatusCheckouts.loja == int(loja),
            StatusCheckouts.checkout == int(checkout)
        ).first()

        self.session.delete(query)
        self.session.commit()


class StoresRepository:
    """ Classe para manipular as lojas
    """
    def __init__(self, session):
        self.session = session

    def get_all_store(self, loja: int = None) -> list:
        """ Retorna todas as lojas
        """
        # Verifica se foi passado o número da loja
        if loja is not None:
            query = self.session.query(Stores).filter(Stores.loja == int(loja)).all()
        else:
            query = self.session.query(Stores).all()

        # Retorna a query
        return query

    def insert_store(self, number: int, path: str):
        """ Insere uma loja
        """
        store = Stores(
            loja=number,
            path=path
        )

        self.session.add(store)
        self.session.commit()

    def update_store(self, number: str, path: str):
        """ Atualiza o caminho da loja
        """
        query = self.session.query(Stores).filter(Stores.loja == number).first()
        query.path = path
        self.session.commit()

    def delete_store(self, number: str):
        """ Deleta uma loja
        """
        query = self.session.query(Stores).filter(Stores.loja == number).first()
        self.session.delete(query)
        self.session.commit()


class FilesRepository:
    """ Classe para manipular os arquivos
    """
    async def copy_file_retag(self, path: str, loja: str):
        """ Copia os arquivos do retag para a pasta da loja
        """
        # Verifica se a pasta da loja existe
        self.__check_file(loja)
        # Cria o caminho da pasta da loja
        path_file = Path(f"./arquivo/{loja}")
        await asyncio.sleep(0)
        try:
            # Copia os arquivos do retag para a pasta da loja
            shutil.copytree(path, path_file)
        except FileNotFoundError:
            logger.error(f"Caminho {path} da pasta retag não encontrado")
            pass

    async def get_checkouts_file(self, list_loja: str) -> list:
        """ Gera uma lista com os dados do checkout que foram retirados do arquivo do retag e deleta o arquivo do retag
        """
        data_list = pd.DataFrame(columns=['LOJA', 'CHECKOUT', 'ALTERADA', 'TOTAL'])

        for loja in list_loja:
            # Cria o caminho do arquivo do retag
            path_file = Path(f"./arquivo/{loja.loja}/log_carga_pdv.txt")
            try:
                # Abre o arquivo do retag
                with open(path_file) as file:
                    # Percorre o arquivo
                    data_list = pd.concat([data_list, pd.read_csv(file, sep=';')])

                # Deleta o arquivo do retag
                shutil.rmtree("f./arquivo/{loja.loja}")
            except FileNotFoundError:
                # logger.error(f"Arquivo log_carga_pdv.txt não encontrado na pasta da loja {loja.loja}")
                pass

        # Alterar o nome das colunas
        data_list.columns = ["loja", "checkout", "status_alterada", "status_total"]

        # Retorna os dados do checkout
        return data_list

    def __check_file(self, loja):
        """ Verifica se a pasta da loja existe, se existir deleta"""
        # Cria o caminho da pasta da loja
        path = Path(f"./arquivo/{loja}")
        # Verifica se a pasta da loja existe e deleta
        if os.path.exists(path):
            shutil.rmtree(path)
