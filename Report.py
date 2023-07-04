from datetime import timedelta, datetime, date
from services.organizze_service import Organizze_Service
from helpers.data_helper import convert_amount_to_decimal
from collections import defaultdict
from models.organizze_models import *
from OrganizeSync import OrganizzeSync

class Report:
    def __init__(self, _organizze_instance: OrganizzeSync) -> None:
        self.organizze = _organizze_instance

    def daily_general(self) -> str:
        '''Relatório genérico de gastos gerais diários'''
        self.organizze.update_old_transactions()
        expense: TransactionModel

        today_expenses = list(filter(lambda x: x.date == date.today().strftime('%Y-%m-%d'), self.organizze.old_transactions))
        yesterday_expenses = list(filter(lambda x: x.date == (datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d'), self.organizze.old_transactions))
        one_week_before_expenses = list(filter(lambda x: x.date == (datetime.today() - timedelta(days=7)).strftime('%Y-%m-%d'), self.organizze.old_transactions))

        today = defaultdict(int)
        # Totalizar os gastos por categoria para as transações de hoje
        for expense in today_expenses:
            expense.category_name = self.organizze.get_category_name_by_id(expense.category_id)
            today[expense.category_name] += expense.amount_cents

        yesterday = defaultdict(int)
        # Totalizar os gastos por categoria para as transações de ontem
        for expense in yesterday_expenses:
            expense.category_name = self.organizze.get_category_name_by_id(expense.category_id)
            yesterday[expense.category_name] += expense.amount_cents

        week_before = defaultdict(int)
        # Totalizar os gastos por categoria para as transações de uma semana atrás
        for expense in one_week_before_expenses:
            expense.category_name = self.organizze.get_category_name_by_id(expense.category_id)
            week_before[expense.category_name] += expense.amount_cents

        for category, total in today.items():
            difference = total - yesterday[category]
            percentage = (difference / yesterday[category]) * 100 if yesterday[category] != 0 else 0
            print(f"Categoria: {category}")
            print(f"Gastos hoje: R$ {total / 100:.2f}")
            print(f"Gastos ontem: R$ {yesterday[category] / 100:.2f}")
            print(f"Diferença: R$ {difference / 100:.2f}")
            print(f"Porcentagem: {percentage:.2f}%")
            print("-----")
    

        
