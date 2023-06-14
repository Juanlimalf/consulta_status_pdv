from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func


Base = declarative_base()


class StatusCheckouts(Base):
    __tablename__ = 'status_checkouts'
    id = Column(Integer, primary_key=True, autoincrement=True)
    loja = Column(String(3), nullable=False)
    checkout = Column(String(3), nullable=False)
    data_inclusao = Column(DateTime, server_default=func.now())
    status_alterada = Column(Boolean, nullable=False, default=0)
    status_total = Column(Boolean, nullable=False, default=0)
    status_manutencao = Column(Boolean, nullable=False, default=0)
    data_alteracao = Column(DateTime, onupdate=func.now())

    def __repr__(self):
        return f"""[{self.loja}, {self.checkout}, {self.data_inclusao}, {self.status_alterada}, {self.status_total}, {self.status_manutencao}, {self.data_alteracao}]"""


class Stores(Base):
    __tablename__ = 'stores'
    loja = Column(String(3), primary_key=True, nullable=False)
    path = Column(String(150), nullable=False)

    def __repr__(self):
        return f"""[{self.loja}, {self.path}]"""
