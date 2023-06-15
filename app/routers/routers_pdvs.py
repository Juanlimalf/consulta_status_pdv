from ..service import CheckoutsService
from ..models import ResponseCheckouts, UpdateMaintenance, Message, LojaSchema

from fastapi import APIRouter, status
from fastapi.exceptions import HTTPException
from asyncio import run
from apscheduler.schedulers.asyncio import AsyncIOScheduler

"""
Esse projeto foi desenvolvido utilizando o framework FastApi e utiliza uma biblioteca chamada APScheduler para agendar
tarefas de atualização e reset de status dos checkouts.

O "@router_pdv.on_event("startup)" e "@router_pdv.on_event("shutdown)" são eventos do FastApi que são executados quando o projeto é
iniciado e finalizado respectivamente e são usados para iniciar e finalizar o scheduler.
"""

# instanciando a classe de rotas do FastApi
router_pdv = APIRouter()
# instanciando a classe de serviço
service = CheckoutsService()


# Função para atualizar o status dos checkouts no banco de dados
def update_status():
    run(CheckoutsService.update_status_checkout())


# Função para resetar o status dos checkouts no banco de dados
def reset_status():
    run(CheckoutsService.reset_status())
    run(CheckoutsService.update_status_checkout())


# Instanciando o scheduler e adicionando as funções que serão executadas
scheduler = AsyncIOScheduler()
scheduler.add_job(update_status, 'interval', hours=1)
scheduler.add_job(reset_status, 'interval', seconds=30)
scheduler.add_job(reset_status, 'cron', hour=4, minute=0, second=0)


# Eventos do FastApi para iniciar e finalizar o scheduler
@router_pdv.on_event("startup")
def startup_event():
    """ Inicia o scheduler ao iniciar o projeto
    """
    scheduler.start()


@router_pdv.on_event("shutdown")
def shutdown_event():
    """ Finaliza o scheduler ao finalizar o projeto
    """
    scheduler.shutdown()


@router_pdv.get("/pdv", status_code=status.HTTP_200_OK, response_model=ResponseCheckouts)
async def get_checkouts():
    """ Endponit para retornar todos os checkouts cadastrados no banco de dados
    """
    response = service.get_all_checkout()
    if response != []:
        return response
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Nenhum checkout encontrado')


@router_pdv.put("/pdv", status_code=status.HTTP_200_OK, response_model=Message,)
async def update_maintenance(request: UpdateMaintenance):
    """ Endponit para atualizar o status de manutenção do checkout
    """
    response = await service.update_checkout(loja=request.loja, checkout=request.pdv, status_manutencao=request.status_manutencao)

    return response


@router_pdv.delete("/pdv", status_code=status.HTTP_200_OK, response_model=Message,)
async def deleta_pdv(request: LojaSchema):
    """ Endponit para deletar um checkout
    """
    response = service.delete_checkout(loja=request.loja, checkout=request.pdv)

    return response


@router_pdv.put("/pdv/atualizar", status_code=status.HTTP_200_OK)
async def update_status(loja: str = None):
    """Atualiza a lista de checkouts da loja no banco de dados"""
    await CheckoutsService.update_status_checkout(loja=loja)

    return Message(message="Atualizado com sucesso")


@router_pdv.put("/pdv/reset", status_code=status.HTTP_200_OK)
async def reset_status():
    """Atualiza a lista de checkouts da loja no banco de dados"""
    await CheckoutsService.reset_status()
    await CheckoutsService.update_status_checkout()

    return Message(message="Resetado com sucesso")
