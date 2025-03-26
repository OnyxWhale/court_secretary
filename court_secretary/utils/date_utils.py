from datetime import datetime
from typing import Union
from django.utils import timezone
from django.core.exceptions import ValidationError

def parse_date(date_str: str, format: str = '%Y-%m-%d') -> datetime.date:
    """Парсит строку даты в объект datetime.date."""
    try:
        return datetime.strptime(date_str, format).date()
    except ValueError:
        raise ValidationError(f"Неверный формат даты. Ожидается {format}.")

def validate_date_range(start_date: datetime.date, end_date: Union[datetime.date, None]) -> None:
    """Проверяет, что конечная дата не раньше начальной."""
    if end_date and start_date and end_date < start_date:
        raise ValidationError("Дата окончания не может быть раньше даты начала.")

def get_min_date() -> str:
    """Возвращает минимальную допустимую дату в формате строки."""
    return '2024-08-14'  # Фиксированная минимальная дата из проекта

def is_date_valid(date: datetime.date, min_date: str = get_min_date()) -> bool:
    """Проверяет, что дата не раньше минимальной."""
    return date >= datetime.strptime(min_date, '%Y-%m-%d').date()