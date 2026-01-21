# bot_setup.py
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config import bot_config

# Инициализация бота и диспетчера
bot = Bot(token=bot_config.token)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Импортируем обработчики (будет инициализировано позже)
__all__ = ['bot', 'dp', 'setup_handlers']