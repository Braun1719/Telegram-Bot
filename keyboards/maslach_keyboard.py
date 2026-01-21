# keyboards/maslach_keyboard.py
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_maslach_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для ответов по шкале Маслач (0-6)"""
    buttons = []
    
    # Варианты ответов с описанием
    options = [
        ("0", "Никогда"),
        ("1", "Очень редко"),
        ("2", "Редко"),
        ("3", "Иногда"),
        ("4", "Часто"),
        ("5", "Очень часто"),
        ("6", "Ежедневно")
    ]
    
    for value, text in options:
        buttons.append([
            InlineKeyboardButton(
                text=f"{value} - {text}",
                callback_data=f"maslach_{value}"
            )
        ])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_quick_test_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для быстрого теста (0-4)"""
    buttons = []
    
    options = [
        ("0", "Никогда"),
        ("1", "Редко"),
        ("2", "Иногда"),
        ("3", "Часто"),
        ("4", "Постоянно")
    ]
    
    # Размещаем в два ряда для компактности
    row1 = []
    row2 = []
    
    for i, (value, text) in enumerate(options):
        btn = InlineKeyboardButton(
            text=f"{value} - {text}",
            callback_data=f"quick_{value}"
        )
        if i < 2:
            row1.append(btn)
        else:
            row2.append(btn)
    
    return InlineKeyboardMarkup(inline_keyboard=[row1, row2])