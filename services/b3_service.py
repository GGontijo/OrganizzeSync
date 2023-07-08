from helpers.config_helper import Config
from helpers.logger_helper import Logger
from helpers.date_helper import generate_monthly_dates
from models.b3_models import *
from datetime import datetime
import urllib3
import requests
import json


class B3_Service:
    def __init__(self, logger: Logger, token: str) -> None:
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning) # Desabilita mensagem de aviso da verificação de SSL
        _config = Config()
        _config_data = _config.get_config("b3")
        self.url_base = _config_data["url"]
        self.headers = {
            "Host": f"{self.url_base.split('//')[1]}",
            "Authorization": f"{token}"
        }
        self.logger = logger
    
    def get_proventos(self, dataInicio: str, dataFim: str):
        try:
            self.logger.log("INFO", "Obtendo proventos da B3")
            response = requests.get(f"{self.url_base}/extrato-eventos-provisionados/v1/recebidos?dtf={dataFim}&dti={dataInicio}", headers=self.headers, verify=False)
            extrato_data = json.loads(response.content)
            return [MesProventos(**data) for data in extrato_data["d"]]
        
        except requests.exceptions.RequestException as e:
            error_message = f'Erro ao obter proventos da B3: {str(e)}'
            self.logger.log("ERROR", error_message)
            raise Exception(error_message)
        
    def get_movimentacoes(self, dataInicio: str, dataFim: str):
        try:
            self.logger.log("INFO", "Obtendo proventos da B3")
            response = requests.get(f"{self.url_base}/extrato-movimentacao/v2/movimentacao?dataFim={dataFim}&dataInicio={dataInicio}", headers=self.headers, verify=False)
            extrato_data = json.loads(response.content)
            return [MesMovimentos(**data) for data in extrato_data["itens"]]
        
        except requests.exceptions.RequestException as e:
            error_message = f'Erro ao obter proventos da B3: {str(e)}'
            self.logger.log("ERROR", error_message)
            raise Exception(error_message)