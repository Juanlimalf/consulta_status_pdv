from model import model
from service import service
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

tags_metadata = [{
    "name": "Api Monitoramento Pdv",
    "description": "Documentação API Monitoramento de PDVs"
}]


app = FastAPI(title="Api Monitoramento Pdv",
              description="Documentação API Monitoramento PDV",
              version="0.0.1",
              openapi_tags=tags_metadata)


origins = [
    "*",
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/pdv", tags=["Monit Pdv"], status_code=200)
def busca_pdv_lojas(page_num: int = 1, page_size: int = 5):
    start = (page_num - 1) * page_size
    end = start + page_size
    response = service.monta_consulta_pdv_loja(start, end, page_size)
    return response


@app.put("/pdv", response_model=model.Message , tags=["Monit Pdv"], status_code=200)
def atualiza_status(alteracao: model.AtualizaStatusPdv):
    response = service.atualiza_status_pdv(alteracao)
    return response


@app.delete("/pdv", response_model=model.Message, tags=["Monit Pdv"], status_code=200)
def deleta_pdv(deletaPdv: model.DeletaPdv):
    response = service.deletaPdv(deletaPdv)
    return response


@app.put("/pdv/atualiza", response_model=model.Message, tags=["Monit Pdv"], status_code=200)
async def atualiza_loja(loja:int):

    response = service.gera_arquivos(loja)
    return response


@app.put("/pdv/atualiza/geral", response_model=model.Message, tags=["Monit Pdv"], status_code=200)
async def atualiza_loja():

    response = service.gera_arquivos_geral()

    return response
