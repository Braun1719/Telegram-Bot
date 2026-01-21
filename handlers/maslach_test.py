# handlers/maslach_test.py
from typing import Dict
from aiogram import types
from aiogram.fsm.context import FSMContext

from bot_setup import dp
from models.states import MaslachTestStates
from models.questions import MaslachQuestions
from keyboards.maslach_keyboard import get_maslach_keyboard
from services.test_calculator import TestCalculator
from services.storage import storage
from services.recommendations import get_maslach_recommendations
from keyboards.main_menu import get_test_cancel_keyboard, get_main_keyboard

@dp.message(lambda message: message.text == "📊 Опросник Маслач (10 вопросов)")
async def start_maslach_test(message: types.Message, state: FSMContext):
    """Начало опросника Маслач"""
    await state.set_state(MaslachTestStates.questions)
    await state.update_data(
        current_question=1,
        answers={},
        test_started=True
    )
    
    question = MaslachQuestions.get_question(1)
    await message.answer(
        f"📊 **Опросник Маслач**\n\n"
        f"Вопрос 1 из {len(MaslachQuestions.get_all())}\n\n"
        f"{question.text}\n\n",
        reply_markup=get_maslach_keyboard(),
        parse_mode="Markdown"
    )
    await message.answer(
        "Вы можете отменить тест в любой момент:",
        reply_markup=get_test_cancel_keyboard()
    )

@dp.callback_query(lambda c: c.data.startswith("maslach_"))
async def process_maslach_answer(callback: types.CallbackQuery, state: FSMContext):
    """Обработка ответов Маслач"""
    data = await state.get_data()
    current = data.get('current_question', 1)
    answers = data.get('answers', {})
    
    # Извлекаем оценку (maslach_0 -> 0)
    rating = int(callback.data.split('_')[1])
    answers[current] = rating
    
    # Сохраняем ответ
    await state.update_data(answers=answers)
    
    total_questions = len(MaslachQuestions.get_all())
    
    # Если вопросы закончились
    if current >= total_questions:
        # Рассчитываем результаты
        results = TestCalculator.calculate_maslach(answers)
        full_result = {
            'test_type': 'maslach',
            'scores': results['scores'],
            'interpretation': results['interpretation']
        }
        
        # Сохраняем
        await storage.save_test_result(callback.message.chat.id, full_result)
        
        # Показываем результаты
        await show_maslach_results(callback.message, full_result)
        
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
    
    question = MaslachQuestions.get_question(next_q)
    
    await callback.message.edit_text(
        f"📊 **Опросник Маслач**\n\n"
        f"Вопрос {next_q} из {total_questions}\n\n"
        f"{question.text}\n\n",
        reply_markup=get_maslach_keyboard(),
        parse_mode="Markdown"
    )
    
    await callback.answer()

async def show_maslach_results(message: types.Message, results: Dict):
    """Показ результатов Маслач"""
    interp = results['interpretation']
    
    result_text = (
        f"📊 **РЕЗУЛЬТАТЫ ОПРОСНИКА МАСЛАЧ**\n\n"
        f"**Эмоциональное истощение**: {interp['EE']['score']} баллов ({interp['EE']['level']})\n"
        f"**Деперсонализация**: {interp['DP']['score']} баллов ({interp['DP']['level']})\n"
        f"**Редукция достижений**: {interp['PA']['score']} баллов ({interp['PA']['level']})\n\n"
        f"📈 **Общая оценка**: {interp['overall'].upper()}\n\n"
        "---\n"
        "*Интерпретация:*\n"
        "• **Эмоциональное истощение**: чувство опустошенности\n"
        "• **Деперсонализация**: циничное отношение к работе\n"
        "• **Редукция достижений**: снижение самооценки\n"
    )
    
    await message.answer(result_text, parse_mode="Markdown")
    
    # Показываем рекомендации
    recommendations = get_maslach_recommendations(results)
    await message.answer(recommendations)