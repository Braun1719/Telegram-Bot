# keyboards/boyko_keyboard.py
from aiogram import types

def get_boyko_keyboard():
    """Клавиатура для теста Бойко"""
    buttons = [
        [
            types.InlineKeyboardButton(text="Да", callback_data="boyko_yes"),
            types.InlineKeyboardButton(text="Иногда", callback_data="boyko_sometimes"),
            types.InlineKeyboardButton(text="Нет", callback_data="boyko_no"),
        ]
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=buttons)