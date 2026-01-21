# handlers/cancel_handler.py
from aiogram import types
from aiogram.fsm.context import FSMContext

from bot_setup import dp
from keyboards.main_menu import get_main_keyboard

@dp.message(lambda message: message.text == "❌ Отменить тест")
async def cancel_test(message: types.Message, state: FSMContext):
    """Отмена текущего теста"""
    current_state = await state.get_state()
    if current_state is None:
        return
    
    await state.clear()
    await message.answer(
        "Тест отменен. Возвращаю в главное меню:",
        reply_markup=get_main_keyboard()
    )