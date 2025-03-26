from abc import ABC, abstractmethod

class BaseParser(ABC):
    """Абстрактный базовый класс для парсеров."""
    @abstractmethod
    def parse(self, max_pages: int) -> None:
        """Парсит указанное количество страниц."""
        pass