# keyboards/heck_hess_keyboard.py
from aiogram import types

def get_heck_hess_keyboard():
    """Клавиатура для теста Хека-Хесса"""
    buttons = [
        [
            types.InlineKeyboardButton(text="0", callback_data="heck_0"),
            types.InlineKeyboardButton(text="1", callback_data="heck_1"),
            types.InlineKeyboardButton(text="2", callback_data="heck_2"),
            types.InlineKeyboardButton(text="3", callback_data="heck_3"),
        ]
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=buttons)