from pydantic import BaseModel, Field
from typing import Optional


class Message(BaseModel):
    message: str = Field(..., example="Success")


class Checkouts(BaseModel):
    checkout: str = Field(..., example="101")
    data_inclusao: str = Field(..., example="2023-01-01 00:00:00")
    status_alterada: Optional[bool] = Field(..., example=True)
    status_total: Optional[bool] = Field(..., example=True)
    status_manutencao: Optional[bool] = Field(..., example=False)
    data_alteracao: Optional[str] = Field(..., example="2023-01-01 00:00:00")


class LojaSchema(BaseModel):
    loja: str = Field(..., example="14")
    pdv: str = Field(..., example="101")


class Loja(BaseModel):
    loja: str = Field(..., example="14")
    pdvs: list[Checkouts]


class ResponseCheckouts(BaseModel):
    data_atualizacao: str = Field(..., example="2023-01-01 00:00:00")
    lojas: list[Loja]


class UpdateMaintenance(LojaSchema):
    status_manutencao: bool = Field(..., example=1)
