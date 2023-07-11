from organizzesync import OrganizzeSync
from helpers.logger_helper import Logger
from models.organizze_models import *
from helpers.data_helper import convert_amount_to_cents, convert_amount_to_decimal
from decimal import Decimal
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from helpers.date_helper import *
from services.organizze_service import Organizze_Service

class Investments:   
    def __init__(self, logger: Logger, organizze: OrganizzeSync, organizze_service: Organizze_Service) -> None:
        self.logger = logger
        self.organizze = organizze
        self.organizze_service = organizze_service

    def sync_renda_fixa(self, valor_liquido: float):
        self.organizze.update_old_transactions(resync=True) # Atualiza a base inteira de dados
        saldo_conta = sum(x.amount_cents for x in list(filter(lambda x: x.account_id == EnumOrganizzeAccounts.RENDA_FIXA.value, self.organizze.old_transactions)))

        valor_faltante = round(valor_liquido - convert_amount_to_decimal(saldo_conta), 2)
        movimentacoes_rendimentos = list(filter(lambda x: x.account_id == EnumOrganizzeAccounts.RENDA_FIXA.value and x.category_id == 71967471, self.organizze.old_transactions))
        transactions_list = []

        # Obter a data do transaction mais recente
        transaction_mais_recente = max(movimentacoes_rendimentos, key=lambda x: datetime.strptime(x.date, '%Y-%m-%d').date())
        transaction_date_mais_recente = datetime.strptime(transaction_mais_recente.date, '%Y-%m-%d').date()

        diff_meses = count_months_between_dates(transaction_date_mais_recente, datetime.today().date())

        current_date = datetime.today()

        total_meses = diff_meses.months
        total_dias = diff_meses.days

        valor_proporcional_mes = valor_faltante / (total_meses + (total_dias / 30.0))

        for _ in range(total_meses):
            current_date = current_date.replace(day=1) - timedelta(days=1)
            transactions_list.append(TransactionCreateModel(
                description= f'Rendimento CDB Liquido aferido em {datetime.today().date()}',
                date= current_date.strftime("%Y-%m-%d"),
                category_id= 71967471,
                amount_cents= convert_amount_to_cents(valor_proporcional_mes),
                category_name= self.organizze.get_category_name_by_id(71967471),
                account_id= EnumOrganizzeAccounts.RENDA_FIXA.value
            ))

        # Distribuir o valor proporcional para os dias restantes
        if total_dias:
            valor_dias_restantes = valor_proporcional_mes * (total_dias / 30.0)
            transactions_list.append(TransactionCreateModel(
                description= f'Rendimento CDB Liquido aferido em {datetime.today().date()} - Parcial ref a {total_dias} dias',
                date= datetime.today().strftime("%Y-%m-%d"),
                category_id= 71967471,
                amount_cents= convert_amount_to_cents(valor_dias_restantes),
                category_name= self.organizze.get_category_name_by_id(71967471),
                account_id= EnumOrganizzeAccounts.RENDA_FIXA.value
            ))
        
        for i in transactions_list:
            self.organizze_service.create_transaction(i)

        