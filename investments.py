from organizzesync import OrganizzeSync
from helpers.logger_helper import Logger
from models.organizze_models import *
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from helpers.date_helper import *

class Investments:   
    def __init__(self, logger: Logger, organizze: OrganizzeSync) -> None:
        self.logger = logger
        self.organizze = organizze

    def sync_renda_fixa(self, valor_liquido: int):
        diferença_meses: relativedelta
        # self.organizze.update_old_transactions(resync=True) # Atualiza a base inteira de dados
        movimentacoes_rendimentos = list(filter(lambda x: x.account_id == EnumOrganizzeAccounts.RENDA_FIXA.value and x.category_id == 71967471, self.organizze.old_transactions))
        print(movimentacoes_rendimentos)

        # Obter a data do transaction mais recente
        transaction_mais_recente = max(movimentacoes_rendimentos, key=lambda x: datetime.strptime(x.date, '%Y-%m-%d').date())
        transaction_date_mais_recente = datetime.strptime(transaction_mais_recente.date, '%Y-%m-%d').date()

        diferença_meses = count_months_between_dates(transaction_date_mais_recente, datetime.today().date())

        # Possui algum mês incompleto
        if diferença_meses.days > 0:
            




       # valores_mensais = []
       # valor_mensal_completo = valor_liquido / meses_completos
       # valor_parcial_final = valor_liquido * dias_parcela_final / total_dias_final

       # for _ in range(meses_completos):
       #     valores_mensais.append(valor_mensal_completo)

        #valores_mensais.append(valor_parcial_final)

        print('a')

        
        
