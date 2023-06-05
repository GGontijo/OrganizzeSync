from helpers.config_helper import Config
from helpers.logger_helper import Logger
from helpers.date_helper import generate_monthly_dates
from models.organizze_models import *
from datetime import datetime
import requests
import json


class Organizze_Service:
    def __init__(self) -> None:
        _config = Config()
        _config_data = _config.get_config("organizze")
        self.username = _config_data["username"]
        self.token = _config_data["token"]
        self.url_base = _config_data["url"]
        self.log_file = "logs.txt"
        self.logger = Logger(self.log_file)

    def get_transactions(self, data_inicio=None, data_fim=None):
        try:
            if data_inicio is not None and data_fim is not None: # Se for passado filtro de data
                start_date = datetime.strptime(data_inicio, "%Y-%m-%d")
                end_date = datetime.strptime(data_fim, "%Y-%m-%d")
                self.logger.log("INFO", f"Obtendo transacoes de {start_date} ate {end_date}")
                response = requests.get(f"{self.url_base}/transactions?start_date={start_date}&end_date={end_date}", auth=(self.username, self.token))
                transactions_data = json.loads(response.content)
            else:
                self.logger.log("INFO", "Obtendo transacoes mensais")
                transactions_data = self.get_transactions_monthly_dates() # Sem filtro de data

            transactions = []

            if isinstance(transactions_data, list):
                if all(isinstance(item, dict) for item in transactions_data):
                    # transactions_data é uma lista de objetos
                    for data in transactions_data:
                        try:
                            transaction = TransactionModel(**data)
                            transactions.append(transaction)

                        except KeyError:
                            self.logger.log("WARNING", "Dados de transação incompletos. A transação será ignorada.")

                    return transactions
                
                elif all(isinstance(item, list) and len(item) > 0 and isinstance(item[0], dict) for item in transactions_data):
                    # transactions_data é uma lista de listas
                    for data in transactions_data:
                        for item in data:
                            try:
                                transaction = TransactionModel(**item)
                                transactions.append(transaction)
                            except KeyError:
                                self.logger.log("WARNING", "Dados de transação incompletos. A transação será ignorada.")

                    return transactions
                         
                else:
                    self.logger.log("WARNING", "Formato inválido para transactions_data. As transações serão ignoradas.")
            else:
                self.logger.log("WARNING", "Formato inválido para transactions_data. As transações serão ignoradas.")


        except requests.exceptions.RequestException as e:
            error_message = f'Erro ao obter transações: {str(e)}'
            self.logger.log("ERROR", error_message)
            raise Exception(error_message)

    def get_categories(self):
        try:
            self.logger.log("INFO", "Obtendo categorias")
            response = requests.get(f"{self.url_base}/categories", auth=(self.username, self.token))
            categories_data = json.loads(response.content)
            self.categories = [CategoryModel(**data) for data in categories_data]
            return self.categories
        except Exception as e:
            error_message = f'Nao foi possivel concluir a requisicao! Detalhes: {e}'
            self.logger.log("ERROR", error_message)
            raise Exception(error_message)

        
    def create_transaction(self, movimentacao: TransactionCreateModel):
        try:
            response = requests.post(f'{self.url_base}/transactions', json=movimentacao, auth=(self.username, self.token))
            if response.status_code == 201:
                self.logger.log("INFO", "Movimentação criada com sucesso")
            else:
                error_message = f'Erro ao criar a movimentação: {response.content}'
                self.logger.log("ERROR", error_message)
                raise Exception(error_message)

        except Exception as e:
            error_message = f'Nao foi possivel criar a movimentação! Detalhes: {e}'
            self.logger.log("ERROR", error_message)
            raise Exception(error_message)

    def get_transactions_monthly_dates(self):
        dates = generate_monthly_dates()
        transactions = []

        for start_date, end_date in dates:
            self.logger.log("INFO", f"Obtendo transacoes de {start_date} ate {end_date}")
            response = requests.get(f"{self.url_base}/transactions?start_date={start_date}&end_date={end_date}", auth=(self.username, self.token))
            transactions.append(json.loads(response.content))

        return transactions

