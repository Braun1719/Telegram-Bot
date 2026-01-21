# keyboards/main_menu.py
from aiogram import types

def get_main_keyboard():
    """Главное меню с тестами для ИТ-специалистов"""
    buttons = [
        [types.KeyboardButton(text="⚡ Быстрый тест (10 вопросов)")],
        [types.KeyboardButton(text="📊 Опросник Маслач (10 вопросов)")],
        [types.KeyboardButton(text="🧠 Тест Бойко (20 вопросов)")],
        [types.KeyboardButton(text="🏥 Тест Хека-Хесса (21 вопрос)")],
        [types.KeyboardButton(text="📈 Мои результаты")],
        [types.KeyboardButton(text="ℹ️ О выгорании в IT")],
    ]
    return types.ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

def get_test_cancel_keyboard():
    """Клавиатура для отмены теста"""
    buttons = [
        [types.KeyboardButton(text="❌ Отменить тест")]
    ]
    return types.ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

def get_back_to_main_keyboard():
    """Кнопка возврата в главное меню"""
    buttons = [
        [types.KeyboardButton(text="🏠 Главное меню")]
    ]
    return types.ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)