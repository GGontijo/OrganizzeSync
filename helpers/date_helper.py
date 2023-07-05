from datetime import datetime, timedelta, date

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

def count_weekend_days(start_date: date, end_date: date) -> int:
    # Ajustar as datas para o próximo sábado e domingo
    start_date = start_date + timedelta(days=(5 - start_date.weekday()) % 7)
    end_date = end_date - timedelta(days=(end_date.weekday() + 1) % 7)

    # Calcular o número de finais de semana completos
    num_weekends = (end_date - start_date).days // 7

    # Verificar se o final de semana do end_date está completo
    if end_date.weekday() < start_date.weekday():
        num_weekends -= 1

    return num_weekends

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