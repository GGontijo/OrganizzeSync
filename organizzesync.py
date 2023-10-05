from collections import defaultdict
from helpers.data_helper import match_strings, convert_ofx_to_json
from models.organizze_models import *
from helpers.logger_helper import Logger
from datetime import timedelta, datetime, date
from services.organizze_service import Organizze_Service
import time


class OrganizzeSync:
    def __init__(self, service: Organizze_Service, logger: Logger) -> None:
        self.logger = logger
        self._organizze_service = service
        self.old_transactions: list
        self.old_transactions = self._organizze_service.get_transactions()
        self.categories = self._organizze_service.get_categories()
        self.accounts = self._organizze_service.get_accounts()
        self.category_mapping = None
        if self.category_mapping is None:
            self.process_categories()
        self.duplicated_transactions = []
        self.unrecognized_transactions = [] # Transações que não deu pra mapear a categoria
        self.processed_transactions = []
        self.ignored_transactions = []

    def update_old_transactions(self, timespan: int = None, resync: bool = False):
        max_date = max(self.old_transactions, key=lambda transaction: transaction.date).date
        if timespan:
            new_transactions = self._organizze_service.get_transactions(data_inicio=(date.today() - timedelta(days=timespan)).strftime('%Y-%m-%d'), data_fim=date.today().strftime('%Y-%m-%d'))
        elif resync:
            new_transactions = self._organizze_service.get_transactions()
        else:
            new_transactions = self._organizze_service.get_transactions(data_inicio=max_date, data_fim=date.today().strftime('%Y-%m-%d'))

        # Filtrar apenas os itens novos com base nos IDs não existentes em old_transactions
        old_ids = set(transaction.id for transaction in self.old_transactions)
        new_transactions_filtered = [transaction for transaction in new_transactions if transaction.id not in old_ids]
        if new_transactions_filtered:
            for transaction in new_transactions_filtered:
                self.old_transactions.append(transaction) # Atualiza a base de transações em memória

        # Filtrar apenas os itens removidos com base nos IDs não existentes em new_transactions
        new_ids = set(transaction.id for transaction in new_transactions)

        if timespan:
            removed_transactions = [transaction for transaction in self.old_transactions if transaction.date >= (date.today() - timedelta(days=timespan)).strftime('%Y-%m-%d') and transaction.id not in new_ids]
        if resync:
            removed_transactions = [transaction for transaction in self.old_transactions if transaction.id not in new_ids]
        else:
            removed_transactions = [transaction for transaction in self.old_transactions if transaction.date >= max_date and transaction.date <= date.today().strftime('%Y-%m-%d') and transaction.id not in new_ids]
            
        if removed_transactions:
            for transaction in removed_transactions:
                self.old_transactions.remove(transaction)  # Remove as transações removidas

    def process_categories(self):
        # Criar um dicionário para armazenar as categorias mais utilizadas por descrição
        self.category_mapping = defaultdict(list) # Categorias mapeadas de acordo com a maior utilização
        self.category_mapping_raw = defaultdict(list) # Dados brutos para fim de analises
        self.logger.log("INFO", f"Processando transacoes por categorias")
    
        # Filtrar transações antigas com base na descrição
        for old_transaction in self.old_transactions:
            description = old_transaction.description.lower()
            category_id = old_transaction.category_id
            self.category_mapping[description].append(category_id)
            if not any(category_id in category.keys() for category in self.category_mapping_raw[description]): # Evita inserir categoria duplicada
                self.category_mapping_raw[description].append({category_id: self.get_category_name_by_id(category_id)})
    
        # Determinar a categoria mais utilizada para cada descrição
        for description, categories in self.category_mapping.items():
            most_common_category = max(set(categories), key=categories.count)
            self.category_mapping[description] = most_common_category
        
        self.logger.log("INFO", f"{len(self.category_mapping)} Transacoes processadas e categorias padrão mapeadas!")
    
    def process_ofx_transactions(self):
        '''TO-DO Ler arquivo OFX e chamar process new transaction'''
        self.logger.log("INFO", f"Processando novas transacoes")
        pass

    def process_new_transaction(self, new_transaction: TransactionCreateModel, account_id: EnumOrganizzeAccounts, create_transaction: bool = False, ignore_duplicates: bool = False) -> str:
        '''Processar as novas transações e definir a categoria com base na correspondência de descrição'''
        self.update_old_transactions()
        self.account_id = account_id.value
        new_transaction: TransactionCreateModel # Typing hint

        # Limpeza de listas
        self.duplicated_transactions = []
        self.unrecognized_transactions = []
        self.processed_transactions = []
        self.ignored_transactions = []

        description = new_transaction.description.lower()

        if 'pix' in description or 'ted' in description or 'doc' in description or 'transferencia' in description or 'pagamento' in description: # Retirando transferências, pode ter muitos motivos não da pra mapear categoria
            self.ignored_transactions.append({"transaction": description, "motivo": "Transação é uma transferência!"})
            return "Transação é uma transferência!"

        if 'cdb' in description or 'aplicacao' in description or 'resgate' in description: # Retirando qualquer movimentação referente a aporte ou resgate de investimentos, falta mapear transferencias
            self.ignored_transactions.append({"transaction": description, "motivo": "Transação é um investimento!"})
            return "Transação é um investimento!"

        if new_transaction.amount_cents > 0: # Ignora se for um crédito (regra complexa demais, ainda não mapeado)
            self.ignored_transactions.append({"transaction": description, "motivo": "Transação é um crédito!"})
            return "Transação é um crédito!"

        category_id = self.category_mapping.get(description)

        if category_id is None: # Se não foi possível determinar a categoria pela descrição exata, procurar descrições próximas
            category_id = self.determine_category(description)

        if category_id is None: # Se não foi possível determinar a categoria por descrições próximas, ignorar..
            self.unrecognized_transactions.append(description)
            return "Não foi possível determinar uma categoria!"

        new_transaction.account_id=self.account_id
        new_transaction.category_name=self.get_category_name_by_id(category_id)
        new_transaction.category_id = category_id
        new_transaction.tags=[{"name": "API"}]

        if not ignore_duplicates: # Utilizar deste tag quando não for um processamento em lote de .ofx
            duplicate_transaction = self.check_existing_transaction(new_transaction)

            if duplicate_transaction and duplicate_transaction["duplicated"]: # Ignora se for uma transação duplicada
                self.duplicated_transactions.append(duplicate_transaction["relationship"])
                return f"Esta Movimentação já foi lançada anteriormente: {duplicate_transaction['relationship']}"

        if create_transaction:
            self._organizze_service.create_transaction(new_transaction)
            return f'Movimentação criada com sucesso! {new_transaction.description} | Categoria: {new_transaction.category_name}'
    
    
    def delete_all_api_transactions(self):
        self.update_old_transactions()
        self.logger.log("WARNING", f"CUIDADO! Essa ação irá deletar todas as transações inseridas via API no Organizze!")
        self.logger.log("WARNING", f"Arguardando 15 segundos antes de iniciar...")
        time.sleep(15)

        [self._organizze_service.delete_transaction(transaction) for transaction  in self.old_transactions if "[API]" in transaction.description] # TO-DO Considerar pela tag também

    def check_existing_transaction(self, new_transaction: TransactionCreateModel):
        '''O Objetivo principal desse método é checar se uma transação nova (à ser inserida) já não existe na base do Organizze.'''

        new_description = new_transaction.description.lower()
        new_amount_cents = new_transaction.amount_cents
        new_date_posted = datetime.strptime(new_transaction.date[:10], "%Y-%m-%d").date()

        if new_transaction.date == date.today():
            return {"duplicated": False, "relationship": None}
        

        # Filtrando old_transactions pelo account_id para mitigar falsos positivos
        for old_transaction in list(filter(lambda x: x.account_id == self.account_id, self.old_transactions)): 
            old_transaction: TransactionModel # Typing hint

            if '[API]' in old_transaction.description: # É preciso limpar as descrições de transações já inseridas via API
                old_transaction.description = old_transaction.description.split(" - Inserido Via [API]")[0].strip()
            
            old_date = datetime.strptime(old_transaction.date[:10], "%Y-%m-%d").date()

            # Checagem exata (mesma descrição, valor igual e datas iguais ou próximas)
            if new_description == old_transaction.description.lower() and new_amount_cents == old_transaction.amount_cents: 
                if abs(new_date_posted - old_date) <= timedelta(days=3):
                    self.logger.log("INFO", f"Ignorando transação {new_description} de {new_date_posted}, duplicidade com {old_transaction.description.lower()} de {old_transaction.date}...")
                    return {"duplicated": True, "relationship": ((new_description, new_transaction.date), (old_transaction.description.lower(), old_transaction.date))}
            
            # Casos aonde a descrição foi alterada
            if new_date_posted == old_date and new_amount_cents == old_transaction.amount_cents and new_description != old_transaction.description.lower(): 
                if match_strings(new_description, old_transaction.description.lower(), simillar=False, threshold=2):
                    self.logger.log("INFO", f"Ignorando transação {new_description} de {new_date_posted}, duplicidade com {old_transaction.description.lower()} de {old_transaction.date}...")
                    return {"duplicated": True, "relationship": ((new_description, new_transaction.date), (old_transaction.description.lower(), old_transaction.date))}
            
            if abs(new_date_posted - old_date) <= timedelta(days=2) and new_amount_cents == old_transaction.amount_cents and new_description != old_transaction.description.lower(): 
                if match_strings(new_description, old_transaction.description.lower(), simillar=False, threshold=1):
                    self.logger.log("INFO", f"Ignorando transação {new_description} de {new_date_posted}, duplicidade com {old_transaction.description.lower()} de {old_transaction.date}...")
                    return {"duplicated": True, "relationship": ((new_description, new_transaction.date), (old_transaction.description.lower(), old_transaction.date))}
                
                if new_date_posted == old_date and new_transaction.category_id == old_transaction.category_id:
                    self.logger.log("INFO", f"Ignorando transação {new_description} de {new_date_posted}, duplicidade com {old_transaction.description.lower()} de {old_transaction.date}...")
                    return {"duplicated": True, "relationship": ((new_description, new_transaction.date), (old_transaction.description.lower(), old_transaction.date))}
                
            if abs(new_date_posted - old_date) <= timedelta(days=3) and new_amount_cents == old_transaction.amount_cents and new_description != old_transaction.description.lower() and old_transaction.category_id == new_transaction.category_id:
                if match_strings(new_description, old_transaction.description.lower(), simillar=False, threshold=1):
                    self.logger.log("INFO", f"Ignorando transação {new_description} de {new_date_posted}, duplicidade com {old_transaction.description.lower()} de {old_transaction.date}...")
                    return {"duplicated": True, "relationship": ((new_description, new_transaction.date), (old_transaction.description.lower(), old_transaction.date))}
        
        return {"duplicated": False, "relationship": None}
    
    def determine_category(self, transaction_description: str) -> int:
        if self.category_mapping is None:
            self.process_categories()
        
        description = transaction_description.lower()

        for old_transaction in self.old_transactions: 
            old_transaction: TransactionModel # Typing hint

            if old_transaction.amount_cents > 0: # Ignorar transações de crédito, somente débitos deverão ser mapeados
                continue

            if match_strings(description, old_transaction.description.lower(), simillar=False, threshold=2):
                return old_transaction.category_id

        return None
        

    def get_category_name_by_id(self, category_id: int):
        for category in self.categories:
            if category.id == category_id:
                return category.name
        return None
    
#new = convert_ofx_to_json('teste.ofx')
#sync = OrganizzeSync()
#result = sync.process_new_transactions(new["transactions"],account_id=4375850,create_transaction=True)
#result = sync.delete_all_api_transactions()
#print(result)
