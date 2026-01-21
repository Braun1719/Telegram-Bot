# handlers/quick_test.py
from typing import Dict
from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter

from bot_setup import dp
from models.states import QuickTestStates
from models.questions import QuickTestQuestions
from services.test_calculator import TestCalculator
from services.storage import storage
from keyboards.main_menu import get_main_keyboard, get_test_cancel_keyboard

@dp.message(lambda message: message.text == "⚡ Быстрый тест (10 вопросов)")
async def start_quick_test(message: types.Message, state: FSMContext):
    """Начало быстрого теста для ИТ"""
    await state.set_state(QuickTestStates.questions)
    await state.update_data(
        current_question=1,
        answers=[],
        test_started=True
    )
    
    question = QuickTestQuestions.get_question(1)
    await message.answer(
        f"⚡ **Быстрый тест на выгорание для ИТ-специалистов**\n\n"
        f"Вопрос 1 из 10\n\n"
        f"{question}\n\n"
        f"Оцените от 0 до 4, где:\n"
        f"0 - никогда\n"
        f"1 - редко\n"
        f"2 - иногда\n"
        f"3 - часто\n"
        f"4 - всегда",
        reply_markup=get_quick_keyboard()
    )
    await message.answer(
        "Вы можете отменить тест в любой момент:",
        reply_markup=get_test_cancel_keyboard()
    )

@dp.callback_query(lambda c: c.data.startswith("quick_"), StateFilter(QuickTestStates.questions))
async def process_quick_answer(callback: types.CallbackQuery, state: FSMContext):
    """Обработка ответов быстрого теста"""
    data = await state.get_data()
    current = data.get('current_question', 1)
    answers = data.get('answers', [])
    
    # Извлекаем оценку (quick_3 -> 3)
    rating = int(callback.data.split('_')[1])
    answers.append(rating)
    
    # Сохраняем ответ
    await state.update_data(answers=answers)
    
    # Если вопросы закончились
    if current >= 10:
        # Рассчитываем результаты
        results = TestCalculator.calculate_quick_test(answers)
        full_result = {
            'test_type': 'quick',
            'scores': results
        }
        
        # Сохраняем
        await storage.save_test_result(callback.message.chat.id, full_result)
        
        # Показываем результаты
        await show_quick_results(callback.message, results)
        
        # Сбрасываем состояние
        await state.clear()
        await callback.message.answer(
            "Возвращаю в главное меню:",
            reply_markup=get_main_keyboard()
        )
        await callback.answer()
        return
    
    # Следующий вопрос
    next_q = current + 1
    await state.update_data(current_question=next_q)
    
    question = QuickTestQuestions.get_question(next_q)
    
    await callback.message.edit_text(
        f"⚡ **Быстрый тест на выгорание для ИТ-специалистов**\n\n"
        f"Вопрос {next_q} из 10\n\n"
        f"{question}\n\n"
        f"Оцените от 0 до 4, где:\n"
        f"0 - никогда\n"
        f"1 - редко\n"
        f"2 - иногда\n"
        f"3 - часто\n"
        f"4 - всегда",
        reply_markup=get_quick_keyboard()
    )
    
    await callback.answer()

async def show_quick_results(message: types.Message, results: Dict):
    """Показ результатов быстрого теста"""
    scores = results.get('scores', {})
    recommendations = results.get('recommendations', [])
    
    result_text = (
        f"{scores.get('color', '⚡')} **РЕЗУЛЬТАТЫ БЫСТРОГО ТЕСТА ДЛЯ ИТ-СПЕЦИАЛИСТОВ**\n\n"
        f"**Общий балл:** {scores.get('total', 0)} из {scores.get('max', 40)}\n"
        f"**Уровень риска:** {scores.get('level', '').upper()}\n"
        f"**Оценка:** {scores.get('risk', '')}\n\n"
        "---\n"
        "**ИНТЕРПРЕТАЦИЯ:**\n"
        "• 0-10 баллов: Низкий риск, хорошая адаптация к работе в ИТ\n"
        "• 11-20 баллов: Умеренный риск, рекомендуется профилактика\n"
        "• 21-30 баллов: Высокий риск, требуются изменения в рабочем процессе\n"
        "• 31-40 баллов: Критический риск, необходимы срочные меры\n\n"
    )
    
    if recommendations:
        result_text += "**РЕКОМЕНДАЦИИ ДЛЯ ИТ-СПЕЦИАЛИСТА:**\n"
        for rec in recommendations:
            result_text += f"{rec}\n"
    
    await message.answer(result_text, parse_mode="Markdown")
    
    # Дополнительные советы
    if scores.get('total', 0) > 20:
        await message.answer(
            "💡 **СОВЕТЫ ДЛЯ ИТ-СПЕЦИАЛИСТОВ:**\n"
            "1. Установите 'цифровой детокс' - время без устройств\n"
            "2. Практикуйте правило 20-20-20: каждые 20 минут смотрите 20 секунд на объект в 20 футах\n"
            "3. Используйте техники тайм-менеджмента (Pomodoro, Time blocking)\n"
            "4. Регулярно делайте физические упражнения для борьбы с сидячим образом жизни",
            parse_mode="Markdown"
        )

def get_quick_keyboard():
    """Клавиатура для быстрого теста"""
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