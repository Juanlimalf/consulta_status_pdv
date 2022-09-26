from model import model
from service import service
from fastapi import FastAPI
import uvicorn
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
def deleta_pdv(deletaPdv: model.deletaPdv):
    response = service.deletaPdv(deletaPdv)
    return response

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=6008, log_level="info")