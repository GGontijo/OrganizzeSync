from fastapi import APIRouter, status, Response, FastAPI
from helpers.data_helper import determine_account_id, parse_notification
from helpers.date_helper import convert_timestamp_to_date
from services.telegram_service import Telegram_Service
from organizzesync import OrganizzeSync
from datetime import datetime, timedelta
from models.organizze_models import *
from uvicorn import run

class Server():
    organizze_router = APIRouter()

    def __init__(self, _organizze_instance: OrganizzeSync) -> None:
        Server.organizze_sync = _organizze_instance
        self.api = FastAPI(title='OrganizzeSync', 
                           description='API de sincronização com o Organizze', 
                           version='1.0.0')
        self.api.include_router(Server.organizze_router)
    
    def start(self):
        return run(self.api, port=6556, host='*')
        

    @organizze_router.get("/create")
    def create(response: Response, description: str, date: str, account_id: int = None, title: str = None, lat: str = None, long: str = None):
        try:
            account_determined = next((member for member in EnumOrganizzeAccounts if member.value == account_id), None)
            description_parsed = parse_notification(description=description, account_id=account_determined)
            _date = convert_timestamp_to_date(date)
            amount = description_parsed["amount"] * -1 # As notificações não vem com o valor em negativo
            if title:
                try:
                    _account_id = determine_account_id(title)
                    transaction_obj = TransactionCreateModel(description=description_parsed["place"],
                                                             amount_cents=amount,
                                                             date=_date,
                                                             account_id=_account_id)
                    result = Server.organizze_sync.process_new_transaction(transaction_obj, account_id=account_determined, create_transaction=True)
                    if result:
                        response.status_code = status.HTTP_200_OK
                        return result
                    else:
                        _telegram = Telegram_Service()
                        if (datetime.now().timestamp - _date) > timedelta(minutes=15):
                            lat = None # Limpa os campos para não gerar link do maps, já que provavelmente a localização estará incorreta
                            long = None
                        _telegram.send_import_error(lat, long, description)
                        raise Exception(str(result))
                except KeyError as e:
                    response.status_code = status.HTTP_400_BAD_REQUEST
                    return str(e)

            if account_id:
                try:
                    transaction_obj = TransactionCreateModel(description=description_parsed["place"],
                                                             amount_cents=amount,
                                                             date=_date,
                                                             account_id=account_determined.value)
                    result = Server.organizze_sync.process_new_transaction(transaction_obj, account_id=account_determined, create_transaction=True)
                    if 'sucesso' in result:
                        response.status_code = status.HTTP_200_OK
                        return result
                    else:
                        response.status_code = status.HTTP_400_BAD_REQUEST
                        _telegram = Telegram_Service()
                        if (datetime.now().timestamp - _date) > timedelta(minutes=15):
                            lat = None # Limpa os campos para não gerar link do maps, já que provavelmente a localização estará incorreta
                            long = None
                        _telegram.send_import_error(lat, long, description)
                        raise Exception(str(result))
                except KeyError as e:
                    response.status_code = status.HTTP_400_BAD_REQUEST
                    return str(e)

            raise ValueError('Favor informar apenas um dos parâmetros: [account_id, title].')

        except Exception as e:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return str(e)