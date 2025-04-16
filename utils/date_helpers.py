from datetime import datetime, timedelta
import pytz

def get_month_name(month_number):
    """
    Retorna o nome do mês em português
    """
    month_names = [
        'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
        'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
    ]
    return month_names[month_number - 1]

def get_month_short_name(month_number):
    """
    Retorna o nome abreviado do mês em português
    """
    month_short_names = [
        'Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun',
        'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'
    ]
    return month_short_names[month_number - 1]

def format_date(date, format_string='%d/%m/%Y'):
    """
    Formata uma data para exibição
    """
    return date.strftime(format_string)

def format_datetime(dt, format_string='%d/%m/%Y %H:%M'):
    """
    Formata um datetime para exibição
    """
    return dt.strftime(format_string)

def get_current_month():
    """
    Retorna o mês atual no fuso horário de São Paulo
    """
    sp_tz = pytz.timezone('America/Sao_Paulo')
    return datetime.now(sp_tz).month

def get_current_year():
    """
    Retorna o ano atual no fuso horário de São Paulo
    """
    sp_tz = pytz.timezone('America/Sao_Paulo')
    return datetime.now(sp_tz).year

def to_local_time(dt):
    """
    Converte um datetime UTC para o fuso horário de São Paulo
    """
    if dt is None:
        return None
    
    # Se o datetime não tem informação de timezone, assume que é UTC
    if dt.tzinfo is None:
        dt = pytz.utc.localize(dt)
    
    # Converte para o fuso horário de São Paulo
    sp_tz = pytz.timezone('America/Sao_Paulo')
    return dt.astimezone(sp_tz)

def format_local_datetime(dt, format_str='%d/%m/%Y %H:%M:%S'):
    """
    Formata um datetime para o fuso horário de São Paulo
    """
    if dt is None:
        return 'Nunca'
    
    local_dt = to_local_time(dt)
    return local_dt.strftime(format_str)

def get_now_sp():
    """
    Retorna o datetime atual no fuso horário de São Paulo
    """
    sp_tz = pytz.timezone('America/Sao_Paulo')
    return datetime.now(sp_tz)