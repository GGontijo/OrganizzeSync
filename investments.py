from organizzesync import OrganizzeSync
from helpers.logger_helper import Logger
from models.organizze_models import *
from datetime import datetime, date

class Investments:
    def __init__(self, logger: Logger, organizze: OrganizzeSync) -> None:
        self.logger = logger
        self.organizze = organizze

    def sync_renda_fixa(self, valor_liquido: int):
        # self.organizze.update_old_transactions(resync=True)
        movimentacoes_rendimentos = list(filter(lambda x: x.account_id == EnumOrganizzeAccounts.RENDA_FIXA.value and x.category_id == 71967471, self.organizze.old_transactions))
        print(movimentacoes_rendimentos)

        # Converter a data do transaction mais recente para o tipo datetime.date
        transaction_mais_recente = max(movimentacoes_rendimentos, key=lambda x: datetime.strptime(x.date, '%Y-%m-%d').date())

        # Filtrar transações do mês do transaction mais recente
        transacoes_mes_atual = [transaction for transaction in movimentacoes_rendimentos if transaction.date.startswith(transaction_mais_recente.date[:7])]

        # Calcular quantidade de meses completos desde o mês do transaction mais recente até hoje
        quantidade_meses_completos = (date.today().year - int(transaction_mais_recente.date[:4])) * 12 + (date.today().month - int(transaction_mais_recente.date[5:7])) - 1

        # Calcular valor proporcional por mês
        valor_proporcional_mes = valor_liquido / quantidade_meses_completos if quantidade_meses_completos > 0 else valor_liquido

        # Calcular valor a ser distribuído para cada mês
        valores_distribuidos = [valor_proporcional_mes for _ in range(quantidade_meses_completos)]

        # Distribuir valor restante para o mês atual
        valor_restante = valor_liquido - (valor_proporcional_mes * quantidade_meses_completos)
        valores_distribuidos.append(valor_restante)

        # Imprimir valores distribuídos por mês
        print(valores_distribuidos)
        print('')
