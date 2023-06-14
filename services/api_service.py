from fastapi import FastAPI
from fastapi import APIRouter, status, Response
from helpers.data_helper import convert_amount_to_cents
from OrgannizeSync import OrganizzeSync
from datetime import date
from models.organizze_models import *
from uvicorn import run

organizze_router = APIRouter()

@organizze_router.get("/create")
def create(description: str, amount: str, date: date, account_id: int):
    try:
        _organizze_sync = OrganizzeSync()



        transaction_obj = TransactionCreateModel(description=description,
                                                 date=date,
                                                 amount_cents=convert_amount_to_cents(amount))
        _organizze_sync.process_new_transactions()
        pass

    except Exception as e:
        raise f'Houve um erro ao criar transação via API: {str(e)}'




class Server():
    
    def __init__(self) -> None:
        self.api = FastAPI(title='OrganizzeSync', 
                           description='API de sincronização com o Organizze', 
                           version='1.0.0')
        self.api.include_router(organizze_router)

    async def run_server(self, _Organizze_instance: OrganizzeSync):

        run(self.api, port=6556, host='0.0.0.0')