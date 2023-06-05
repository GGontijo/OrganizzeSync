from collections import defaultdict
from helpers.data_helper import convert_ofx_to_json
from models.organizze_models import *
from helpers.logger_helper import Logger
from datetime import timedelta, datetime
from services.organizze_service import Organizze_Service

class OrganizzeSync:
    def __init__(self) -> None:
        self.logger = Logger()
        _organizze_service = Organizze_Service(self.logger)
        self.old_transactions = _organizze_service.get_transactions()
        self.categories = _organizze_service.get_categories()
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
    

    def process_new_transactions(self, new_transactions):
        self.logger.log("INFO", f"Processando novas transacoes")
        if self.category_mapping is None:
            self.process_categories()

        # Processar as novas transações e definir a categoria com base na correspondência de descrição
        self.duplicated_transactions = []
        self.unrecognized_transactions = [] # Transações que não deu pra mapear a categoria
        self.processed_transactions = []
        self.ignored_transactions = []
        for new_transaction in new_transactions:
            description = new_transaction.description.lower()
            category_id = self.category_mapping.get(description)
            duplicate_transaction = self.check_existing_transaction(new_transaction)

            if duplicate_transaction["duplicated"]: # Ignora se for uma transação duplicada
                self.duplicated_transactions.append(duplicate_transaction["relationship"])
                continue
            
            if 'pix' in description: # Retirando o pix, pode ter muitos motivos não da pra mapear categoria
                self.ignored_transactions.append({"transaction": description, "motivo": "Transação é um pix!"})
                continue

            if new_transaction.amount_cents > 0: # Ignora se for um crédito (regra complexa demais, ainda não mapeado)
                self.ignored_transactions.append({"transaction": description, "motivo": "Transação não é um Débito!"})
                continue

            if category_id is not None:
                new_transaction = TransactionCreateModel(description=description,
                                                         date=new_transaction.date_posted,
                                                         amount_cents=new_transaction.amount_cents,
                                                         account_id=1,
                                                         category_id=category_id,
                                                         category_name=self.get_category_name_by_id(category_id))
                self.processed_transactions.append(new_transaction)
            else:
                self.unrecognized_transactions.append(description)

                
    
        # Retornar as transações processadas
        return self.processed_transactions
    
    def check_existing_transaction(self, new_transaction):
        description = new_transaction.description.lower()
        amount_cents = new_transaction.amount_cents
        date_posted = datetime.strptime(new_transaction.date_posted[:10], "%Y-%m-%d").date()

        for old_transaction in self.old_transactions:
            old_date = datetime.strptime(old_transaction.date[:10], "%Y-%m-%d").date()
            if description == old_transaction.description.lower() and amount_cents == old_transaction.amount_cents:
                if abs(date_posted - old_date) <= timedelta(days=3):
                    self.logger.log("INFO", f"Ignorando transação {description} de {date_posted}, duplicidade com {old_transaction.description} de {old_transaction.date}...")
                    return {"duplicated": True, "relationship": (description, old_transaction.description.lower())}

        return {"duplicated": False, "relationship": None}

    def get_category_name_by_id(self, category_id):
        for category in self.categories:
            if category.id == category_id:
                return category.name
        return None
    
new = convert_ofx_to_json('teste.ofx')
sync = OrganizzeSync()
result = sync.process_new_transactions(new["transactions"])
print(result)