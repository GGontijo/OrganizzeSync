from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta

def generate_this_month_dates():
    start_of_month = date.today().replace(day=1)
    next_month = start_of_month.replace(day=28) + timedelta(days=4)
    end_of_month = next_month - timedelta(days=next_month.day)
    return start_of_month, end_of_month

def generate_last_month_dates():
    start_of_month = date.today().replace(day=1)
    end_of_last_month = start_of_month - timedelta(days=1)
    start_of_last_month = end_of_last_month.replace(day=1)
    return start_of_last_month, end_of_last_month

def generate_monthly_dates():
    """
    Gera uma lista de tuplas contendo a data de início e fim de cada mês,
    começando a partir de julho de 2021 até o mês atual.
    
    Retorna:
        Uma lista de tuplas contendo as datas de início e fim de cada mês.
    """
    dates = []
    current_date = date(2021, 7, 1).replace(day=1)
    end_date = date.today().replace(day=1)

    while current_date <= end_date:
        next_month = current_date.replace(day=28) + timedelta(days=4)
        end_of_month = next_month - timedelta(days=next_month.day)
        dates.append((current_date, end_of_month))
        current_date = next_month.replace(day=1)

    return dates

def convert_timestamp_to_date(timestamp: str):
    data = datetime.fromtimestamp(float(timestamp)).date()
    return data.strftime("%Y-%m-%d")

def count_weeks(start_date: date, end_date: date) -> int:
    # Ajustar as datas para o início da semana (segunda-feira)
    start_date = start_date - timedelta(days=start_date.weekday())
    end_date = end_date - timedelta(days=end_date.weekday())

    # Calcular o número de semanas completas
    num_weeks = (end_date - start_date).days // 7

    return num_weeks

def get_current_week_dates():
    today = date.today()
    current_weekday = today.weekday()
    start_of_week = today - timedelta(days=current_weekday)
    end_of_week = start_of_week + timedelta(days=6)
    return start_of_week, end_of_week

def get_last_week_dates():
    today = date.today()
    current_weekday = today.weekday()
    start_of_week = today - timedelta(days=current_weekday + 7)
    end_of_week = start_of_week + timedelta(days=6)
    return start_of_week, end_of_week


def get_last_few_week_dates(weeks: int):
    today = date.today()
    current_weekday = today.weekday()
    start_of_week = today - timedelta(days=current_weekday + 7)
    end_of_week = start_of_week + timedelta(days=6)
    last_week_dates = [(start_of_week, end_of_week)]
    for _ in range(weeks - 1): # Subtrai uma semana, pois já foi inserido acima
        start_of_last_week = start_of_week - timedelta(days=7)
        end_of_last_week = end_of_week - timedelta(days=7)
        last_week_dates.append((start_of_last_week, end_of_last_week))
        start_of_week = start_of_last_week
        end_of_week = end_of_last_week
    
    return last_week_dates

def get_last_few_month_dates(months: int):
    today = date.today()
    start_of_month = date(today.year, today.month, 1)
    end_of_month = start_of_month - timedelta(days=1)
    last_month_dates = []
    for _ in range(months):
        new_end_of_month = start_of_month - timedelta(days=1)
        new_start_of_month = date(new_end_of_month.year, new_end_of_month.month, 1)
        last_month_dates.append((new_start_of_month, new_end_of_month))
        start_of_month = new_start_of_month
    
    return last_month_dates

def count_months_between_dates(start_date: date, end_date: date) -> float:
    diff = relativedelta(end_date, start_date)
    #months = diff.years * 12 + diff.months + diff.days / 30
    return diff

def obter_ultimo_dia_util():
    data_atual = date.today()
    dia_semana = data_atual.weekday()

    dias_para_subtrair = 3 if dia_semana == 0 else 1
    while dia_semana >= 5:  # Fim de semana (sábado ou domingo)
        data_atual -= timedelta(days=dias_para_subtrair)
        dia_semana = data_atual.weekday()

    return data_atual
