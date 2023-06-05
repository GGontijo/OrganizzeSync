from datetime import datetime, timedelta

def generate_monthly_dates():
    """
    Gera uma lista de tuplas contendo a data de início e fim de cada mês,
    começando a partir de julho de 2021 até o mês atual.
    
    Retorna:
        Uma lista de tuplas contendo as datas de início e fim de cada mês.
    """
    dates = []
    current_date = datetime(2021, 7, 1).replace(day=1)
    end_date = datetime.now().replace(day=1)

    while current_date <= end_date:
        next_month = current_date.replace(day=28) + timedelta(days=4)
        end_of_month = next_month - timedelta(days=next_month.day)
        dates.append((current_date, end_of_month))
        current_date = next_month.replace(day=1)

    return dates