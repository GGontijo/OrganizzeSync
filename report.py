from datetime import timedelta, datetime, date
from services.telegram_service import Telegram_Service
from services.organizze_service import Organizze_Service
from helpers.data_helper import convert_amount_to_decimal, generate_report_image
from helpers.date_helper import generate_this_month_dates, count_weekend_days, count_weeks, get_current_week_dates, get_last_week_dates, generate_last_month_dates, get_last_few_week_dates, get_last_few_month_dates
from collections import defaultdict
from models.organizze_models import *
from organizzesync import OrganizzeSync
import schedule
import time

class Report:
    def __init__(self, _organizze_instance: OrganizzeSync, service: Organizze_Service) -> None:
        self.organizze = _organizze_instance
        self.organizze_service = service
        self.telegram = Telegram_Service()

    def monthly_expenses(self) -> str:
        '''Relatório genérico de gastos gerais mensais'''
        self.organizze.update_old_transactions(timespan=10)
        expense: TransactionModel

        last_six_months_dates = get_last_few_month_dates(6)
        last_month_dates = generate_last_month_dates()
        this_month_dates = generate_this_month_dates()

        last_month_first_day = last_month_dates[0]
        last_month_last_day = last_month_dates[1]

        this_month_first_day = this_month_dates[0]
        this_month_last_day = this_month_dates[1]


        second_month_before_first_day = last_six_months_dates[1][0]
        second_month_before_last_day = last_six_months_dates[1][1]

        third_month_before_first_day = last_six_months_dates[2][0]
        third_month_before_last_day = last_six_months_dates[2][1]

        fourth_month_before_first_day = last_six_months_dates[3][0]
        fourth_monthbefore_last_day = last_six_months_dates[3][1]

        fifth_month_before_first_day = last_six_months_dates[4][0]
        fifth_monthbefore_last_day = last_six_months_dates[4][1]

        sixth_month_before_first_day = last_six_months_dates[5][0]
        sixth_monthbefore_last_day = last_six_months_dates[5][1]

        category_last_month_expenses = defaultdict(int)
        category_this_month_expenses = defaultdict(int)

        this_month_total_spent: int = 0
        last_month_total_spent: int = 0

        last_six_months_average_spent: int = 0

        last_month_expenses = list(filter(lambda x: last_month_first_day <= datetime.strptime(x.date, '%Y-%m-%d').date() <= last_month_last_day and x.amount_cents <= 0 and x.category_id != 71967491 and x.category_id != 71967481, self.organizze.old_transactions))
        this_month_expenses = list(filter(lambda x: this_month_first_day <= datetime.strptime(x.date, '%Y-%m-%d').date() <= this_month_last_day and x.amount_cents <= 0 and x.category_id != 71967491 and x.category_id != 71967481, self.organizze.old_transactions))

        month_before_total_spent = sum(expense.amount_cents for expense in list(filter(lambda x: last_month_first_day <= datetime.strptime(x.date, '%Y-%m-%d').date() <= last_month_last_day and x.amount_cents <= 0 and x.category_id != 71967491 and x.category_id != 71967481, self.organizze.old_transactions)))
        
        month_before_result_amount = sum(expense.amount_cents for expense in list(filter(lambda x: last_month_first_day <= datetime.strptime(x.date, '%Y-%m-%d').date() <= last_month_last_day and x.category_id != 71967491 and x.category_id != 71967481, self.organizze.old_transactions)))
        this_month_result_amount = sum(expense.amount_cents for expense in list(filter(lambda x: this_month_first_day <= datetime.strptime(x.date, '%Y-%m-%d').date() <= this_month_last_day and x.category_id != 71967491 and x.category_id != 71967481, self.organizze.old_transactions)))

        second_month_before_total_expent = sum(expense.amount_cents for expense in list(filter(lambda x: second_month_before_first_day <= datetime.strptime(x.date, '%Y-%m-%d').date() <= second_month_before_last_day and x.amount_cents <= 0 and x.category_id != 71967491 and x.category_id != 71967481, self.organizze.old_transactions)))
        third_month_before_total_expent = sum(expense.amount_cents for expense in list(filter(lambda x: third_month_before_first_day <= datetime.strptime(x.date, '%Y-%m-%d').date() <= third_month_before_last_day and x.amount_cents <= 0 and x.category_id != 71967491 and x.category_id != 71967481, self.organizze.old_transactions)))
        fourth_month_before_total_expent = sum(expense.amount_cents for expense in list(filter(lambda x: fourth_month_before_first_day <= datetime.strptime(x.date, '%Y-%m-%d').date() <= fourth_monthbefore_last_day and x.amount_cents <= 0 and x.category_id != 71967491 and x.category_id != 71967481, self.organizze.old_transactions)))
        fifth_month_before_total_expent = sum(expense.amount_cents for expense in list(filter(lambda x: fifth_month_before_first_day <= datetime.strptime(x.date, '%Y-%m-%d').date() <= fifth_monthbefore_last_day and x.amount_cents <= 0 and x.category_id != 71967491 and x.category_id != 71967481, self.organizze.old_transactions)))
        sixth_month_before_total_expent = sum(expense.amount_cents for expense in list(filter(lambda x: sixth_month_before_first_day <= datetime.strptime(x.date, '%Y-%m-%d').date() <= sixth_monthbefore_last_day and x.amount_cents <= 0 and x.category_id != 71967491 and x.category_id != 71967481, self.organizze.old_transactions)))


        last_six_months_average_spent = (month_before_total_spent + second_month_before_total_expent + third_month_before_total_expent + fourth_month_before_total_expent + fifth_month_before_total_expent + sixth_month_before_total_expent) / 6

        # Totalizar os gastos por categoria para as transações do mês anterior
        for expense in this_month_expenses:
            expense.category_name = self.organizze.get_category_name_by_id(expense.category_id)
            category_this_month_expenses[expense.category_name] += expense.amount_cents
            this_month_total_spent += expense.amount_cents

        # Totalizar os gastos por categoria para as transações do mês anterior
        for expense in last_month_expenses:
            expense.category_name = self.organizze.get_category_name_by_id(expense.category_id)
            category_last_month_expenses[expense.category_name] += expense.amount_cents
            last_month_total_spent += expense.amount_cents

        percentage_diff_month_total = ((this_month_total_spent - last_month_total_spent) / last_month_total_spent) * 100 if last_month_total_spent != 0 else 0.00
        percentage_diff_month_result = ((this_month_result_amount - month_before_result_amount) / month_before_result_amount) * 100 if month_before_result_amount != 0 else 0.00

        categories_to_display = sorted(category_this_month_expenses.items(), key=lambda x: x[1]) # Preciso do total de paginação da categoria para fazer o contador

        total_pages = len(categories_to_display) // 7 + (1 if len(categories_to_display) % 7 != 0 else 0) + 1

        report = f"Relatório mensal de Gastos ({date.today().strftime('%m-%Y')}):\n\n"

        report += "[Resultado deste Mês]:\n"

        report += f"Resultado do mês anterior: R$ {convert_amount_to_decimal(month_before_result_amount):.2f}\n"
        report += f"Resultado deste mês: [R$ {convert_amount_to_decimal(this_month_result_amount):.2f}]\n"
        report += f"diferença em relação ao mês anterior: {percentage_diff_month_result:.2f}%\n"
        report += "\n"

        report += "[Gastos deste Mês]:\n"
        
        report += f"Média de gastos mensal (últimos 6 meses): R$ {convert_amount_to_decimal(last_six_months_average_spent):.2f}\n"
        report += f"Total gasto no mês anterior: R$ {convert_amount_to_decimal(last_month_total_spent):.2f}\n"
        report += f"Total gasto neste mês: [R$ {convert_amount_to_decimal(this_month_total_spent):.2f}]\n"
        report += f"diferença em relação ao mês anterior: {percentage_diff_month_total:.2f}%\n"
        report += "\n"
        
        report += "\n"

        message = f'{date.today().strftime("%m-%Y")}: Relatório mensal 1/{total_pages}'

        self.telegram.send_image(generate_report_image(report), message)

        report = '' # Limpa o Report

        
        # Todas as categorias com pelo menos um gasto neste mês
        report += "[Todas as categorias]:\n"

        current_page = 1

        for index, (category, monthly_amount) in enumerate(categories_to_display, start=1):
            if index > 1:
                current_page = (index - 1) // 7 + 2

            previous_month_amount = category_last_month_expenses[category]
            percentage_diff_month = ((monthly_amount - previous_month_amount) / previous_month_amount) * 100 if previous_month_amount != 0 else 0.00

            report += f"Categoria: {category}\n"
            report += f"Gastos no mês anterior: R$ {convert_amount_to_decimal(previous_month_amount):.2f}\n"
            report += f"Gastos no mês atual: [R$ {convert_amount_to_decimal(monthly_amount):.2f}]\n"
            report += f"diferença em relação ao mês anterior: {percentage_diff_month:.2f}%\n"
            report += "\n"

            if index % 7 == 0 or index == len(categories_to_display):
                message = f'{date.today().strftime("%m-%Y")}: Relatório mensal {current_page}/{total_pages}'
                self.telegram.send_image(generate_report_image(report), message)
                report = ""  # Reinicia o relatório para a próxima parte
                current_page += 1

    def weekly(self) -> str:
        '''Relatório genérico de gastos gerais semanais'''
        self.organizze.update_old_transactions(timespan=10)
        expense: TransactionModel
        
        this_month_dates = generate_this_month_dates()
        this_week_dates = get_current_week_dates()
        last_week_dates = get_last_week_dates()
        last_four_weeks_dates = get_last_few_week_dates(4)

        this_week_first_day = this_week_dates[0]
        this_week_last_day = this_week_dates[1]

        this_month_first_day = this_month_dates[0]
        this_month_last_day = this_month_dates[1] 

        last_week_first_day = last_week_dates[0]
        last_week_last_day = last_week_dates[1]

        second_week_before_first_day = last_four_weeks_dates[1][0]
        second_week_before_last_day = last_four_weeks_dates[1][1]

        third_week_before_first_day = last_four_weeks_dates[2][0]
        third_week_before_last_day = last_four_weeks_dates[2][1]

        fourth_week_before_first_day = last_four_weeks_dates[3][0]
        fourth_week_before_last_day = last_four_weeks_dates[3][1]
        
        category_last_week_expenses = defaultdict(int)
        
        category_this_week_expenses = defaultdict(int)

        this_week_total_spent: int = 0
        this_month_total_spent: int = 0

        last_four_weeks_average_spent: int = 0

        this_month_expenses = list(filter(lambda x: this_month_first_day <= datetime.strptime(x.date, '%Y-%m-%d').date() <= this_month_last_day and x.amount_cents <= 0 and x.category_id != 71967491 and x.category_id != 71967481, self.organizze.old_transactions))

        
        this_week_expenses = list(filter(lambda x: this_week_first_day <= datetime.strptime(x.date, '%Y-%m-%d').date() <= this_week_last_day and x.amount_cents <= 0 and x.category_id != 71967491 and x.category_id != 71967481, self.organizze.old_transactions))
        last_week_expenses = list(filter(lambda x: last_week_first_day <= datetime.strptime(x.date, '%Y-%m-%d').date() <= last_week_last_day and x.amount_cents <= 0 and x.category_id != 71967491 and x.category_id != 71967481, self.organizze.old_transactions))
        
        last_week_total_expent = sum(expense.amount_cents for expense in last_week_expenses)
        second_week_before_total_expent = sum(expense.amount_cents for expense in list(filter(lambda x: second_week_before_first_day <= datetime.strptime(x.date, '%Y-%m-%d').date() <= second_week_before_last_day and x.amount_cents <= 0 and x.category_id != 71967491 and x.category_id != 71967481, self.organizze.old_transactions)))
        third_week_before_total_expent = sum(expense.amount_cents for expense in list(filter(lambda x: third_week_before_first_day <= datetime.strptime(x.date, '%Y-%m-%d').date() <= third_week_before_last_day and x.amount_cents <= 0 and x.category_id != 71967491 and x.category_id != 71967481, self.organizze.old_transactions)))
        fourth_week_before_total_expent = sum(expense.amount_cents for expense in list(filter(lambda x: fourth_week_before_first_day <= datetime.strptime(x.date, '%Y-%m-%d').date() <= fourth_week_before_last_day and x.amount_cents <= 0 and x.category_id != 71967491 and x.category_id != 71967481, self.organizze.old_transactions)))

        last_four_weeks_average_spent = (last_week_total_expent + second_week_before_total_expent + third_week_before_total_expent + fourth_week_before_total_expent) / 4
        
        for expense in this_week_expenses:
            expense.category_name = self.organizze.get_category_name_by_id(expense.category_id)
            category_this_week_expenses[expense.category_name] += expense.amount_cents
            this_week_total_spent += expense.amount_cents

        for expense in this_month_expenses:
            this_month_total_spent += expense.amount_cents
        
        for expense in last_week_expenses:
            expense.category_name = self.organizze.get_category_name_by_id(expense.category_id)
            category_last_week_expenses[expense.category_name] += expense.amount_cents

        report = f"Relatório semanal de Gastos ({date.today().strftime('%m-%Y')}):\n\n"

        report += "[Gastos desta Semana]:\n"
        report += f"Total gasto neste mês: R$ {convert_amount_to_decimal(this_month_total_spent):.2f}\n"
        report += f"Média de gastos semanal (últimas 4 semanas): R$ {convert_amount_to_decimal(last_four_weeks_average_spent):.2f}\n"
        report += f"Total gasto na semana anterior: R$ {convert_amount_to_decimal(last_week_total_expent):.2f}\n"
        report += f"Total gasto nesta semana: R$ {convert_amount_to_decimal(this_week_total_spent):.2f}\n"
        
        report += "\n"

        # Todas as categorias com pelo menos um gasto nesta semana
        report += "[Todas as categorias]:\n"
        for category, weekly_amount in sorted(category_this_week_expenses.items(), key=lambda x: x[1]):
            previous_week_amount = category_last_week_expenses[category]
            percentage_diff_week = ((weekly_amount - previous_week_amount) / previous_week_amount) * 100 if previous_week_amount != 0 else 0.00
            
            report += f"Categoria: {category}\n"
            report += f"Gastos na semana anterior: R$ {convert_amount_to_decimal(previous_week_amount):.2f}\n"
            report += f"Gastos na semana atual: R$ {convert_amount_to_decimal(weekly_amount):.2f}\n"
            report += f"diferença em relação a semana anterior: {percentage_diff_week:.2f}%\n"
            report += "\n"
        
        report += "\n"

        message = f'{this_week_first_day.strftime("%d-%m-%Y")} até {this_week_last_day.strftime("%d-%m-%Y")}: Relatório semanal'

        self.telegram.send_image(generate_report_image(report), message)
        

    def daily(self) -> str:
        '''Relatório genérico de gastos gerais diários'''
        self.organizze.update_old_transactions(timespan=3)
        self.budgets = self.organizze_service.get_budgets()
        budget: BudgetModel
        expense: TransactionModel
        this_month_first_day: datetime
        this_month_last_day: datetime

        this_month_dates = generate_this_month_dates()
        this_week_dates = get_current_week_dates()
        last_week_dates = get_last_week_dates()
    
        today_date = date.today()
        yesterday_date = today_date - timedelta(days=1)
        this_month_first_day = this_month_dates[0]
        this_month_last_day = this_month_dates[1]
        this_week_first_day = this_week_dates[0]
        this_week_last_day = this_week_dates[1]
        last_week_first_day = last_week_dates[0]
        last_week_last_day = last_week_dates[1]

        month_days_remaining = (this_month_last_day - today_date).days
        month_weekend_remaining = count_weekend_days(today_date, this_month_last_day)
        month_week_remaining = count_weeks(today_date, this_month_last_day)

        category_today_expenses = defaultdict(int)
        category_month_to_date_expenses = defaultdict(int)
        category_week_to_date_expenses = defaultdict(int)
        category_last_week_expenses = defaultdict(int)

        last_seven_days_total_spent: int = 0
        today_total_spent: int = 0
        yesterday_total_spent: int = 0

        today_expenses = list(filter(lambda x: x.date == yesterday_date.strftime('%Y-%m-%d') and x.amount_cents < 0 and x.category_id != 71967491 and x.category_id != 71967481, self.organizze.old_transactions))
        yesterday_expenses = list(filter(lambda x: x.date == date.today().strftime('%Y-%m-%d') and x.amount_cents < 0 and x.category_id != 71967491 and x.category_id != 71967481, self.organizze.old_transactions))
        this_month_expenses = list(filter(lambda x: this_month_first_day <= datetime.strptime(x.date, '%Y-%m-%d').date() <= this_month_last_day and x.amount_cents < 0 and x.category_id != 71967491 and x.category_id != 71967481, self.organizze.old_transactions))
        this_week_expenses = list(filter(lambda x: this_week_first_day <= datetime.strptime(x.date, '%Y-%m-%d').date() <= this_week_last_day and x.amount_cents < 0 and x.category_id != 71967491 and x.category_id != 71967481, self.organizze.old_transactions))
        last_week_expenses = list(filter(lambda x: last_week_first_day <= datetime.strptime(x.date, '%Y-%m-%d').date() <= last_week_last_day and x.amount_cents < 0 and x.category_id != 71967491 and x.category_id != 71967481, self.organizze.old_transactions))
        last_seven_days_expenses = list(filter(lambda x: (date.today() - timedelta(days=7)) <= datetime.strptime(x.date, '%Y-%m-%d').date() <= date.today() and x.amount_cents < 0 and x.category_id != 71967491 and x.category_id != 71967481, self.organizze.old_transactions))

        # Totalizar os gastos por categoria para as transações de hoje
        for expense in today_expenses:
            expense.category_name = self.organizze.get_category_name_by_id(expense.category_id)
            category_today_expenses[expense.category_name] += expense.amount_cents

            today_total_spent += expense.amount_cents # Gasto total de hoje

        for expense in yesterday_expenses:
            yesterday_total_spent += expense.amount_cents # Gasto total de ontem

        # Totalizar os gastos por categoria para as transações do mês atual
        for expense in this_month_expenses:
            expense.category_name = self.organizze.get_category_name_by_id(expense.category_id)
            category_month_to_date_expenses[expense.category_name] += expense.amount_cents

        # Totalizar os gastos por categoria para as transações da semana atual
        for expense in this_week_expenses:
            expense.category_name = self.organizze.get_category_name_by_id(expense.category_id)
            category_week_to_date_expenses[expense.category_name] += expense.amount_cents

        for expense in last_week_expenses:
            expense.category_name = self.organizze.get_category_name_by_id(expense.category_id)
            category_last_week_expenses[expense.category_name] += expense.amount_cents

        # Média de gasto diário da semana anterior
        for expense in last_seven_days_expenses:
            last_seven_days_total_spent += expense.amount_cents
        
        report = f"Relatório diário de Gastos ({date.today().strftime('%d-%m-%Y')}):\n\n"

        # Média de gastos por dia da semana anterior e total de gasto no dia atual
        report += "[Gastos de hoje]:\n"
        report += f"Média gasto diário (últimos 7 dias): R$ {convert_amount_to_decimal(last_seven_days_total_spent / 7):.2f}\n"
        report += f"Total gasto ontem: R$ {convert_amount_to_decimal(yesterday_total_spent):.2f}\n"
        report += f"Total gasto hoje: R$ {convert_amount_to_decimal(today_total_spent):.2f}\n"
        
        report += "\n"

        # Todas as metas
        report += "[Todas as metas]:\n"
        for budget in self.budgets:
            budget_goal = budget.amount_in_cents
            budget_spent = budget.total
            budget_remaining = budget_goal - budget_spent
            daily_limit = budget_remaining / month_days_remaining if month_days_remaining != 0 else 0.00
            weekly_limit = budget_remaining / month_week_remaining if month_week_remaining != 0 else 0.00
            weekend_limit = budget_remaining / month_weekend_remaining if month_weekend_remaining != 0 else 0.00
        
            report += f"Meta de {budget.category_name}:\n"
            report += f"Valor definido da meta: R$ {convert_amount_to_decimal(budget_goal):.2f}\n"
            report += f"meta atingida: {round((budget_spent / budget_goal) * 100, 1)}% (Valor restante: R$ {convert_amount_to_decimal(budget_remaining):.2f})\n"
            report += f"Valor restante por dia: R$ {convert_amount_to_decimal(daily_limit):.2f}\n"
            report += f"Valor restante por semana: R$ {convert_amount_to_decimal(weekly_limit):.2f}\n"
            report += f"Valor restante nos finais de semana: R$ {convert_amount_to_decimal(weekend_limit):.2f}\n"
            report += "\n"
        
        report += "\n\n"

        message = f'{date.today().strftime("%d-%m-%Y")}: Relatório diário 1/3'

        self.telegram.send_image(generate_report_image(report), message)

        report = '' # Limpa o Report

        # Categorias gastos no dia
        report += "[Categorias no dia]:\n"
        for category, daily_amount in category_today_expenses.items():
            monthly_amount = abs(category_month_to_date_expenses[category]) # Para o calculo preciso do valor positivo
            budget = next((i for i in self.budgets if i.category_name == category), None)
            
            report += f"Categoria: {category}\n"
            report += f"Gastos hoje: R$ {convert_amount_to_decimal(daily_amount):.2f}\n"
            report += f"Gastos no mês até o dia atual: R$ {convert_amount_to_decimal(monthly_amount):.2f}\n"
            if budget:
                remaining_budget = budget.amount_in_cents - monthly_amount
                percentage = round(abs((daily_amount / budget.amount_in_cents) * 100), 1) if remaining_budget != 0 else 0.0
                report += f"Corresponde à: {round(percentage, 1)}% da meta (Valor restante: R$ {convert_amount_to_decimal(remaining_budget):.2f})\n"
            report += "\n"
            
        report += "\n"

        message = f'{date.today().strftime("%Y-%m-%d")}: Relatório diário 2/3'

        self.telegram.send_image(generate_report_image(report), message)

        report = '' # Limpa o Report
        
        # Categorias gastos na semana
        report += "[Categorias na semana]:\n"
        
        for category, weekly_amount in sorted(category_week_to_date_expenses.items(), key=lambda x: x[1]):
            previous_week_amount = category_last_week_expenses[category]
            percentage_diff = ((weekly_amount - previous_week_amount) / previous_week_amount) * 100 if previous_week_amount != 0 else 0.00
            
            report += f"Categoria: {category}\n"
            report += f"Gastos na semana anterior: R$ {convert_amount_to_decimal(previous_week_amount):.2f}\n"
            report += f"Gastos na semana até o dia atual: R$ {convert_amount_to_decimal(weekly_amount):.2f}\n"
            report += f"diferença: {round(percentage_diff, 1)}%\n"
            report += "\n"
        
        report += "\n"
        
        message = f'{date.today().strftime("%Y-%m-%d")}: Relatório diário 3/3'

        self.telegram.send_image(generate_report_image(report), message)

    def schedule(self):
        schedule.every().day.at("18:00").do(self.daily)
        schedule.every().sunday.at("07:00").do(self.weekly)
        # Falta configurar envio mensal!


    def run_scheduled(self):
        schedule.run_pending()

