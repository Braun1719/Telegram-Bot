# handlers/heck_hess_test.py
from typing import Dict
from aiogram import types
from aiogram.fsm.context import FSMContext

from bot_setup import dp
from models.states import HeckHessTestStates
from models.questions import HeckHessTestQuestions
from keyboards.heck_hess_keyboard import get_heck_hess_keyboard
from services.test_calculator import TestCalculator
from services.storage import storage
from services.recommendations import get_heck_hess_recommendations
from keyboards.main_menu import get_test_cancel_keyboard, get_main_keyboard

@dp.message(lambda message: message.text == "🏥 Тест Хека-Хесса (21 вопрос)")
async def start_heck_hess_test(message: types.Message, state: FSMContext):
    """Начало теста Хека-Хесса"""
    await state.set_state(HeckHessTestStates.questions)
    await state.update_data(
        current_question=1,
        answers={},
        test_started=True
    )
    
    # Получаем текст вопроса
    question_obj = HeckHessTestQuestions.get_question(1)
    question_text = question_obj.text
    
    await message.answer(
        f"🏥 **Тест Хека-Хесса для ИТ-специалистов**\n\n"
        f"Вопрос 1 из {len(HeckHessTestQuestions.get_all())}\n\n"
        f"**{question_text}**\n\n"
        f"Оцените от 0 до 3, где:\n"
        f"0 - нет/никогда\n"
        f"1 - иногда\n"
        f"2 - часто\n"
        f"3 - постоянно/всегда",
        reply_markup=get_heck_hess_keyboard(),
        parse_mode="Markdown"
    )
    await message.answer(
        "Вы можете отменить тест в любой момент:",
        reply_markup=get_test_cancel_keyboard()
    )

@dp.callback_query(lambda c: c.data.startswith("heck_"))
async def process_heck_hess_answer(callback: types.CallbackQuery, state: FSMContext):
    """Обработка ответов теста Хека-Хесса"""
    data = await state.get_data()
    current = data.get('current_question', 1)
    answers = data.get('answers', {})
    
    # Извлекаем оценку (heck_0 -> 0)
    rating = int(callback.data.split('_')[1])
    answers[current] = rating
    
    # Сохраняем ответ
    await state.update_data(answers=answers)
    
    total_questions = len(HeckHessTestQuestions.get_all())
    
    # Если вопросы закончились
    if current >= total_questions:
        # Рассчитываем результаты
        results = TestCalculator.calculate_heck_hess_test(answers)
        full_result = {
            'test_type': 'heck_hess',
            'scores': results
        }
        
        # Сохраняем
        await storage.save_test_result(callback.message.chat.id, full_result)
        
        # Показываем результаты
        await show_heck_hess_results(callback.message, results)
        
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
    
    # Получаем текст вопроса
    question_obj = HeckHessTestQuestions.get_question(next_q)
    question_text = question_obj.text
    
    await callback.message.edit_text(
        f"🏥 **Тест Хека-Хесса для ИТ-специалистов**\n\n"
        f"Вопрос {next_q} из {total_questions}\n\n"
        f"**{question_text}**\n\n"
        f"Оцените от 0 до 3, где:\n"
        f"0 - нет/никогда\n"
        f"1 - иногда\n"
        f"2 - часто\n"
        f"3 - постоянно/всегда",
        reply_markup=get_heck_hess_keyboard(),
        parse_mode="Markdown"
    )
    
    await callback.answer()

async def show_heck_hess_results(message: types.Message, results: Dict):
    """Показ результатов теста Хека-Хесса"""
    total_score = results.get('total_score', 0)
    overall_level = results.get('overall_level', 'не определено')
    interpretation = results.get('interpretation', '')
    color = results.get('color', '🏥')
    burnout_risk = results.get('burnout_risk', 'не определен')
    recommendations = results.get('recommendations', [])
    scales = results.get('scales', {})
    
    result_text = (
        f"{color} **РЕЗУЛЬТАТЫ ТЕСТА ХЕКА-ХЕССА ДЛЯ ИТ-СПЕЦИАЛИСТОВ**\n\n"
        f"**Общий балл:** {total_score} из 63\n"
        f"**Уровень симптомов:** {overall_level.upper()}\n"
        f"**Риск выгорания:** {burnout_risk.upper()}\n\n"
        f"**Интерпретация:** {interpretation}\n\n"
        "---\n"
        "**АНАЛИЗ ПО ШКАЛАМ:**\n\n"
    )
    
    # Анализ по шкалам
    for scale_name, scale_data in scales.items():
        scale_desc = HeckHessTestQuestions.get_scale_description(scale_name)
        result_text += (
            f"**{scale_name.upper()}:** {scale_data.get('score', 0)} баллов "
            f"({scale_data.get('level', '').upper()})\n"
            f"*{scale_desc}*\n"
            f"*{scale_data.get('description', '')}*\n\n"
        )
    
    # Рекомендации
    if recommendations:
        result_text += "**РЕКОМЕНДАЦИИ ДЛЯ ИТ-СПЕЦИАЛИСТА:**\n"
        for rec in recommendations[:5]:  # Показываем до 5 рекомендаций
            result_text += f"{rec}\n"
    
    # Интерпретация баллов
    result_text += (
        "\n**ШКАЛА ОЦЕНКИ:**\n"
        "• 0-7 баллов: Норма - отсутствие значимых признаков\n"
        "• 8-12 баллов: Субдепрессия - легкие симптомы\n"
        "• 13-18 баллов: Умеренная депрессия\n"
        "• 19-24 баллов: Выраженная депрессия\n"
        "• 25+ баллов: Тяжелая депрессия\n\n"
        "⚠️ **Примечание:** Тест оценивает депрессивные симптомы, "
        "которые часто сопровождают профессиональное выгорание."
    )
    
    await message.answer(result_text, parse_mode="Markdown")
    
    # Дополнительные рекомендации
    if total_score > 12:
        await message.answer(
            "💡 **СПЕЦИАЛЬНЫЕ РЕКОМЕНДАЦИИ ДЛЯ IT-ПРОФЕССИОНАЛОВ:**\n"
            "1. Установите 'технологические выходные' - день без гаджетов\n"
            "2. Практикуйте 'deep work' с фокусом на одной задаче\n"
            "3. Используйте блокировщики соцсетей во время работы\n"
            "4. Регулярно делайте перерывы для глаз и осанки\n"
            "5. Рассмотрите работу с психотерапевтом, специализирующимся на IT",
            parse_mode="Markdown"
        )