# config.py
import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class BotConfig:
    """Конфигурация бота"""
    token: str = ""
    admin_ids: list = None
    
    def __post_init__(self):
        if self.admin_ids is None:
            self.admin_ids = []

@dataclass
class DatabaseConfig:
    """Конфигурация БД (задел на будущее)"""
    host: Optional[str] = None
    port: Optional[int] = None
    name: Optional[str] = None
    user: Optional[str] = None
    password: Optional[str] = None
    
    @property
    def dsn(self) -> Optional[str]:
        """Data Source Name для PostgreSQL"""
        if all([self.host, self.port, self.name, self.user, self.password]):
            return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"
        return None

# Создаем конфигурацию
bot_config = BotConfig()
db_config = DatabaseConfig()  # Пока пустая, заполним позже