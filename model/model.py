from pydantic import BaseModel
from typing import Optional, List

class Message(BaseModel):
    message: str

class Paginacao(BaseModel):
    total: int
    count: int

class ConsultaPdv(BaseModel):
    loja:int
    pdv:Optional[int] = None
    datainclusao:Optional[str] = None
    dataalteracao:Optional[str] = None
    status_alt:Optional[str] = None
    status_total:Optional[str] = None
    status_operador:Optional[str] = None
    status_finalizadora:Optional[str] = None
    status_manutencao:Optional[str] = None
    page_num:Optional[int] = 1
    page_size:Optional[int] = 30