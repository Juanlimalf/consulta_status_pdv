from app import router_pdv

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn


tags_metadata = [
    {
        "name": "Monitoramento Pdv",
        "description": "Api responsável por monitorar os checkouts da rede de supermercados Nagumo",
    },
]

description = """O "Monitoramento de Pdv" foi desenvolvido
    para monitorar os checkouts das lojas da rede de supermercados Nagumo.
    O sistema é responsável por verificar se os checkouts receberam as
    atualizações de preços e se os checkouts estão em manutenção.
    Api Desenvolvida por: Juan Lima
    """


app = FastAPI(title="Monitoramento Pdv",
              description=description,
              version="1.0.0",
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


@app.get("/", tags=["Docs"], include_in_schema=False)
async def docs():

    return RedirectResponse(url="/docs")


app.include_router(router=router_pdv, tags=["Monitor Pdv"])


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8005, reload=True)
