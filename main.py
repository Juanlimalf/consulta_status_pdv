from model import model
from service import service
from fastapi import FastAPI
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

tags_metadata = [{
    "name": "ApiConsultaPdv",
    "description": "Documentação API Consulta PDV"
}]
app = FastAPI(title="ApiConsultaPdv",
              description="Documentação API Consulta PDV",
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

@app.get("/consultaPdv", tags=["Consulta"], status_code=200)
def consulta_pdv2(page_num:int=1,page_size:int=30):
    busca_consulta = service.monta_consulta_pdv_full()
    consulta = service.trata_consulta(busca_consulta)
    length = len(consulta)
    start = (page_num - 1) * page_size
    end = start + page_size
    response = {"lojas": consulta[start:end], "paginacao": [{"total": length, "count": page_size}]}
    return response

@app.get("/consultaPdv/{loja}", tags=["Consulta"], status_code=200)
def consulta_pdv(loja:int,page_num:int=1,page_size:int=30):
    start = (page_num - 1) * page_size
    end = start + page_size
    busca_consulta = service.monta_consulta_pdv(loja, start, end, page_size)
    return busca_consulta

@app.get("/buscaPdvsLojas", tags=["Consulta"], status_code=200)
def busca_pdv_lojas(page_num: int = 1, page_size: int = 30):
    start = (page_num - 1) * page_size
    end = start + page_size
    carga = service.monta_consulta_pdv_loja(start, end, page_size)
    response = service.trata_consulta(carga)
    return response

@app.put("/atualizaStatusManutencao", response_model=model.Message , tags=["Atualiza/Deleta"], status_code=200)
def atualiza_status(alteracao: model.AtualizaStatusPdv):
    response = service.atualiza_status_pdv(alteracao)
    return response

@app.delete("/deletaPdv", response_model=model.Message, tags=["Atualiza/Deleta"], status_code=200)
def deleta_pdv(deletaPdv: model.deletaPdv):
    response = service.deletaPdv(deletaPdv)
    return response



if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=6008, log_level="info")