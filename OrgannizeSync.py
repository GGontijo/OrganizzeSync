from collections import defaultdict
from helpers.data_helper import convert_ofx_to_json
from helpers.data_helper import match_strings
from models.organizze_models import *
from helpers.logger_helper import Logger
from datetime import timedelta, datetime
from services.organizze_service import Organizze_Service
import time




class OrganizzeSync:
    def __init__(self) -> None:
        self.logger = Logger()
        self._organizze_service = Organizze_Service(self.logger)
        self.old_transactions = self._organizze_service.get_transactions()
        self.categories = self._organizze_service.get_categories()
        self.accounts = self._organizze_service.get_accounts()
        self.category_mapping = None

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
    

    def process_new_transactions(self, new_transactions, account_id: int, create_transaction: bool = False):
        self.logger.log("INFO", f"Processando novas transacoes")
        if self.category_mapping is None:
            self.process_categories()

        # Processar as novas transações e definir a categoria com base na correspondência de descrição
        self.duplicated_transactions = []
        self.unrecognized_transactions = [] # Transações que não deu pra mapear a categoria
        self.processed_transactions = []
        self.ignored_transactions = []

        for new_transaction in new_transactions:
            new_transaction: TransactionCreateModel # Typing hint

            description = new_transaction.description.lower()

            if 'pix' in description or 'ted' in description or 'doc' in description or 'transferencia' in description: # Retirando transferências, pode ter muitos motivos não da pra mapear categoria
                self.ignored_transactions.append({"transaction": description, "motivo": "Transação é uma transferência!"})
                continue

            if 'cdb' in description or 'aplicacao' in description or 'resgate' in description: # Retirando qualquer movimentação referente a aporte ou resgate de investimentos, falta mapear transferencias
                self.ignored_transactions.append({"transaction": description, "motivo": "Transação é um investimento!"})
                continue

            if new_transaction.amount_cents > 0: # Ignora se for um crédito (regra complexa demais, ainda não mapeado)
                self.ignored_transactions.append({"transaction": description, "motivo": "Transação é um Crédito!"})
                continue

            category_id = self.category_mapping.get(description)

            if category_id is None: # Se não foi possível determinar a categoria pela descrição exata, procurar descrições próximas
                category_id = self.determine_category(description)

            duplicate_transaction = self.check_existing_transaction(new_transaction)

            if duplicate_transaction["duplicated"]: # Ignora se for uma transação duplicada
                self.duplicated_transactions.append(duplicate_transaction["relationship"])
                continue

            if category_id is not None:
                new_transaction = TransactionCreateModel(description=description,
                                                         date=new_transaction.date_posted,
                                                         amount_cents=new_transaction.amount_cents,
                                                         account_id=account_id,
                                                         category_id=category_id,
                                                         category_name=self.get_category_name_by_id(category_id),
                                                         notes='',
                                                         tags=[])
                self.processed_transactions.append(new_transaction)
            else:
                self.unrecognized_transactions.append(description)
        
        if create_transaction:
            self.logger.log("WARNING", f"CUIDADO! Flag de inserção no Organizze ativada!")
            self.logger.log("WARNING", f"Arguardando 5 segundos antes de iniciar as inserções...")
            time.sleep(5)
            for transaction in self.processed_transactions:
                self._organizze_service.create_transaction(transaction)

        # Retornar as transações processadas
        return self.processed_transactions
    
    
    def delete_all_api_transactions(self):
        self.logger.log("WARNING", f"CUIDADO! Essa ação irá deletar todas as transações inseridas via API no Organizze!")
        self.logger.log("WARNING", f"Arguardando 15 segundos antes de iniciar...")
        time.sleep(15)

        [self._organizze_service.delete_transaction(transaction) for transaction  in self.old_transactions if "[API]" in transaction.description]

    def check_existing_transaction(self, new_transaction):
        new_description = new_transaction.description.lower()
        new_amount_cents = new_transaction.amount_cents
        new_date_posted = datetime.strptime(new_transaction.date_posted[:10], "%Y-%m-%d").date()

        for old_transaction in self.old_transactions: 
            old_transaction: TransactionModel # Typing hint

            if '[API]' in old_transaction.description: # É preciso limpar as descrições de transações já inseridas via API
                old_transaction.description = old_transaction.description.split(" - Inserido Via [API]")[0].strip()
            
            old_date = datetime.strptime(old_transaction.date[:10], "%Y-%m-%d").date()
            if new_description == old_transaction.description.lower() and new_amount_cents == old_transaction.amount_cents: # Checagem exata (mesma descrição, valor igual e datas iguais ou próximas)
                if abs(new_date_posted - old_date) <= timedelta(days=3):
                    self.logger.log("INFO", f"Ignorando transação {new_description} de {new_date_posted}, duplicidade com {old_transaction.description.lower()} de {old_transaction.date}...")
                    return {"duplicated": True, "relationship": (new_description, old_transaction.description.lower())}
            
            if new_date_posted == old_date and new_amount_cents == old_transaction.amount_cents and new_description != old_transaction.description.lower(): # Casos aonde a descrição foi alterada
                if match_strings(new_description, old_transaction.description.lower(), simillar=False, threshold=2):
                    self.logger.log("INFO", f"Ignorando transação {new_description} de {new_date_posted}, duplicidade com {old_transaction.description.lower()} de {old_transaction.date}...")
                    return {"duplicated": True, "relationship": (new_description, old_transaction.description.lower())}
            
            if abs(new_date_posted - old_date) <= timedelta(days=3) and new_amount_cents % 1 != 0 and new_amount_cents == old_transaction.amount_cents and new_description != old_transaction.description.lower(): # Casos aonde a descrição foi alterada e não são da mesma data
                if match_strings(new_description, old_transaction.description.lower(), simillar=False, threshold=2):
                    self.logger.log("INFO", f"Ignorando transação {new_description} de {new_date_posted}, duplicidade com {old_transaction.description.lower()} de {old_transaction.date}...")
                    return {"duplicated": True, "relationship": (new_description, old_transaction.description.lower())}
                
            if new_date_posted == old_date and new_amount_cents % 1 != 0 and 
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
    
new = convert_ofx_to_json('teste.ofx')
sync = OrganizzeSync()
#result = sync.process_new_transactions(new["transactions"],4375871,create_transaction=True)
result = sync.delete_all_api_transactions()
print(result)
