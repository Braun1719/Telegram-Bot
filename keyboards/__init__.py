# keyboards/__init__.py
from .main_menu import get_main_keyboard, get_test_cancel_keyboard
from .maslach_keyboard import get_maslach_keyboard
from .boyko_keyboard import get_boyko_keyboard
from .heck_hess_keyboard import get_heck_hess_keyboard

# Проверяем наличие quick_test_keyboard
try:
    from .maslach_keyboard import get_quick_test_keyboard
except ImportError:
    # Если нет, создаем заглушку
    from aiogram import types
    def get_quick_test_keyboard():
        buttons = [
            [
                types.InlineKeyboardButton(text="0", callback_data="quick_0"),
                types.InlineKeyboardButton(text="1", callback_data="quick_1"),
                types.InlineKeyboardButton(text="2", callback_data="quick_2"),
                types.InlineKeyboardButton(text="3", callback_data="quick_3"),
                types.InlineKeyboardButton(text="4", callback_data="quick_4"),
            ]
        ]
        return types.InlineKeyboardMarkup(inline_keyboard=buttons)

__all__ = [
    'get_main_keyboard',
    'get_test_cancel_keyboard',
    'get_maslach_keyboard',
    'get_boyko_keyboard',
    'get_heck_hess_keyboard',
    'get_quick_test_keyboard'
]