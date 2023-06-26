from helpers.config_helper import Config
from helpers.logger_helper import Logger
from helpers.date_helper import generate_monthly_dates
from models.organizze_models import *
from datetime import datetime
import urllib3
import requests
import json


class Organizze_Service:
    def __init__(self, logger: Logger) -> None:
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning) # Desabilita mensagem de aviso da verificação de SSL
        _config = Config()
        _config_data = _config.get_config("organizze")
        self.username = _config_data["username"]
        self.token = _config_data["token"]
        self.url_base = _config_data["url"]
        self.logger = logger

    def get_balances(self, account_id: int=None):
        try:
            if account_id:
                self.logger.log("INFO", f"Obtendo saldos das conta bancaria {account_id}")
                response = requests.get(f"{self.url_base}/balances?account_id{account_id}", auth=(self.username, self.token), verify=False)
                balances_data = json.loads(response.content)
                return BalanceModel(**balances_data)
            
            self.logger.log("INFO", "Obtendo saldos das contas bancarias")
            response = requests.get(f"{self.url_base}/balances", auth=(self.username, self.token), verify=False)
            balances_data = json.loads(response.content)
            return BalanceModel(**balances_data)
        
        except requests.exceptions.RequestException as e:
            error_message = f'Erro ao obter saldos das contas bancarias: {str(e)}'
            self.logger.log("ERROR", error_message)
            raise Exception(error_message)

    def get_budgets(self):
        try:
            self.logger.log("INFO", "Obtendo metas")
            response = requests.get(f"{self.url_base}/budgets", auth=(self.username, self.token), verify=False)
            budgets_data = json.loads(response.content)
            budgets = [BudgetModel(**data) for data in budgets_data]
            for budget in budgets:
                category = self.get_categories(budget.category_id)
                budget.category_name = category.name
            return budgets
     
        except requests.exceptions.RequestException as e:
            error_message = f'Erro ao obter metas: {str(e)}'
            self.logger.log("ERROR", error_message)
            raise Exception(error_message)

    def get_accounts(self):
        try:
            self.logger.log("INFO", "Obtendo contas bancarias")
            response = requests.get(f"{self.url_base}/accounts", auth=(self.username, self.token), verify=False)
            accounts_data = json.loads(response.content)
            return [AccountModel(**data) for data in accounts_data]
        except requests.exceptions.RequestException as e:
            error_message = f'Erro ao obter contas bancarias: {str(e)}'
            self.logger.log("ERROR", error_message)
            raise Exception(error_message)

    def get_transactions(self, data_inicio=None, data_fim=None):
        try:
            if data_inicio is not None and data_fim is not None: # Se for passado filtro de data
                start_date = datetime.strptime(data_inicio, "%Y-%m-%d")
                end_date = datetime.strptime(data_fim, "%Y-%m-%d")
                self.logger.log("INFO", f"Obtendo transacoes de {str(start_date)[:10]} ate {str(end_date)[:10]}")
                response = requests.get(f"{self.url_base}/transactions?start_date={start_date}&end_date={end_date}", auth=(self.username, self.token), verify=False)
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
                                if 'aplicacao' in transaction.description:
                                    pass
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

    def get_categories(self, category_id: int=None):
        try:
            if category_id:
                self.logger.log("INFO", f"Obtendo categoria {category_id}")
                response = requests.get(f"{self.url_base}/categories/{category_id}", auth=(self.username, self.token), verify=False)
                categories_data = json.loads(response.content)
                return CategoryModel(**categories_data)
            
            self.logger.log("INFO", "Obtendo categorias")
            response = requests.get(f"{self.url_base}/categories", auth=(self.username, self.token), verify=False)
            categories_data = json.loads(response.content)
            return [CategoryModel(**data) for data in categories_data]
        except Exception as e:
            error_message = f'Erro ao obter categorias: {str(e)}'
            self.logger.log("ERROR", error_message)
            raise Exception(error_message)
        
    def create_transaction(self, movimentacao: TransactionCreateModel):
        try:
            #movimentacao.description = movimentacao.description + ' - ' + 'Inserido Via [API]' -- Não é mais necessário, utilizar tag {"name": "API"}
            movimentacao.notes = f'Inserido via API em {datetime.now().strftime("%d-%m-%Y %H:%M:%S")}'
            movimentacao.tags = [{"name": "API"}]
            response = requests.post(f'{self.url_base}/transactions', json=movimentacao.to_dict(), auth=(self.username, self.token), verify=False)
            if response.status_code == 201:
                self.logger.log("INFO", f"Movimentação criada com sucesso: {movimentacao.description} | Categoria: {movimentacao.category_name}")
            else:
                error_message = f'Erro ao criar a movimentação: {movimentacao.description} Detalhes: {response.content}'
                self.logger.log("ERROR", error_message)
                raise Exception(error_message)

        except Exception as e:
            error_message = f'Nao foi possivel criar a movimentação! Detalhes: {e}'
            self.logger.log("ERROR", error_message)
            raise Exception(error_message)
        
    def delete_transaction(self, movimentacao: TransactionModel):
        try:
            response = requests.delete(f'{self.url_base}/transactions/{movimentacao.id}', auth=(self.username, self.token), verify=False)
            if response.status_code == 200:
                self.logger.log("INFO", f"Movimentação deletada com sucesso: {movimentacao.description}")
            else:
                error_message = f'Erro ao deletar a movimentação: {movimentacao.description} Detalhes: {response.content}'
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
            response = requests.get(f"{self.url_base}/transactions?start_date={start_date}&end_date={end_date}", auth=(self.username, self.token), verify=False)
            self.logger.log("INFO", f"Obtendo {len(json.loads(response.content))} transacoes de {str(start_date)[:10]} ate {str(end_date)[:10]}")
            transactions.append(json.loads(response.content))

        return transactions