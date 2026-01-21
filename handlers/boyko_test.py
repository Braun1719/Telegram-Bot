# handlers/boyko_test.py
from typing import Dict
from aiogram import types
from aiogram.fsm.context import FSMContext

from bot_setup import dp
from models.states import BoykoTestStates
from models.questions import BoykoTestQuestions
from keyboards.boyko_keyboard import get_boyko_keyboard
from services.test_calculator import TestCalculator
from services.storage import storage
from services.recommendations import get_boyko_recommendations
from keyboards.main_menu import get_test_cancel_keyboard, get_main_keyboard

@dp.message(lambda message: message.text == "🧠 Тест Бойко (20 вопросов)")
async def start_boyko_test(message: types.Message, state: FSMContext):
    """Начало теста Бойко для ИТ-специалистов"""
    await state.set_state(BoykoTestStates.questions)
    await state.update_data(
        current_question=1,
        answers={},
        test_started=True
    )
    
    question_text = BoykoTestQuestions.get_question_text(1)
    await message.answer(
        f"💻 **Тест Бойко для ИТ-специалистов**\n\n"
        f"Вопрос 1 из {len(BoykoTestQuestions.get_all())}\n\n"
        f"**{question_text}**",
        reply_markup=get_boyko_keyboard(),
        parse_mode="Markdown"
    )
    await message.answer(
        "Вы можете отменить тест в любой момент:",
        reply_markup=get_test_cancel_keyboard()
    )

@dp.callback_query(lambda c: c.data.startswith("boyko_"))
async def process_boyko_answer(callback: types.CallbackQuery, state: FSMContext):
    """Обработка ответов теста Бойко"""
    data = await state.get_data()
    current = data.get('current_question', 1)
    answers = data.get('answers', {})
    
    # Извлекаем ответ (boyko_yes -> "yes")
    answer = callback.data.split('_')[1]
    answers[current] = answer
    
    # Сохраняем ответ
    await state.update_data(answers=answers)
    
    total_questions = len(BoykoTestQuestions.get_all())
    
    # Если вопросы закончились
    if current >= total_questions:
        # Рассчитываем результаты
        results = TestCalculator.calculate_boyko_test(answers)
        full_result = {
            'test_type': 'boyko',
            'scores': results,
            'phases': results['phases'],
            'percentages': results['percentages']
        }
        
        # Сохраняем
        await storage.save_test_result(callback.message.chat.id, full_result)
        
        # Показываем результаты
        await show_boyko_results(callback.message, full_result)
        
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
    
    question_text = BoykoTestQuestions.get_question_text(next_q)
    
    await callback.message.edit_text(
        f"💻 **Тест Бойко для ИТ-специалистов**\n\n"
        f"Вопрос {next_q} из {total_questions}\n\n"
        f"**{question_text}**",
        reply_markup=get_boyko_keyboard(),
        parse_mode="Markdown"
    )
    
    await callback.answer()

async def show_boyko_results(message: types.Message, results: Dict):
    """Показ результатов теста Бойко для ИТ-специалистов"""
    scores = results['scores']
    
    # Основная информация
    result_text = (
        f"{scores.get('color', '💻')} **РЕЗУЛЬТАТЫ ТЕСТА БОЙКО ДЛЯ ИТ-СПЕЦИАЛИСТОВ**\n\n"
        f"**Общий уровень:** {scores.get('overall', '')}\n"
        f"**Общий процент выгорания:** {scores.get('total_percentage', 0)}%\n"
        f"**Уровень риска:** {scores.get('risk_level', '').upper()}\n"
        f"**Ключевая проблема:** {scores.get('indicator_phase', '').upper()}\n\n"
        "---\n"
        "**ДЕТАЛЬНЫЙ АНАЛИЗ ПО ФАЗАМ:**\n\n"
    )
    
    # Детали по фазам
    percentages = scores.get('percentages', {})
    phase_levels = scores.get('phase_levels', {})
    
    phases = ["фаза1", "фаза2", "фаза3", "фаза4"]
    for phase in phases:
        percentage = percentages.get(phase, 0)
        level_info = phase_levels.get(phase, {})
        emoji = level_info.get('emoji', '⚪')
        level = level_info.get('level', 'не определен')
        
        description = BoykoTestQuestions.get_phase_description(phase)
        
        result_text += (
            f"{emoji} **{phase.upper()}** - {percentage}% ({level})\n"
            f"*{description}*\n"
        )
        
        # Показываем характеристики для проблемных фаз (выше 25%)
        if percentage > 25:
            characteristics = BoykoTestQuestions.get_phase_characteristics(phase)
            if characteristics:
                result_text += "Характерные симптомы:\n"
                for char in characteristics[:2]:
                    result_text += f"• {char}\n"
        
        result_text += "\n"
    
    # Интерпретация
    result_text += (
        "---\n"
        "**ИНТЕРПРЕТАЦИЯ ДЛЯ ИТ-СПЕЦИАЛИСТА:**\n"
        "• **ФАЗА 1 (Напряжение)** - начальные признаки выгорания\n"
        "• **ФАЗА 2 (Резистенция)** - профессиональный цинизм и отстраненность\n"
        "• **ФАЗА 3 (Истощение)** - эмоциональное и физическое истощение\n"
        "• **ФАЗА 4 (Деформация)** - профессиональная деградация\n\n"
        "**Рекомендации для ИТ-специалиста:**\n"
    )
    
    # Рекомендации по индикаторной фазе
    indicator_phase = scores.get('indicator_phase', 'фаза1')
    recommendations = BoykoTestQuestions.get_it_specific_recommendations(indicator_phase)
    if recommendations:
        for rec in recommendations[:3]:
            result_text += f"• {rec}\n"
    
    await message.answer(result_text, parse_mode="Markdown")
    
    # Дополнительные рекомендации
    if scores.get('total_percentage', 0) > 50:
        await message.answer(
            "⚠️ **ВАЖНО ДЛЯ ИТ-СПЕЦИАЛИСТА:** При уровне выгорания выше 50% рекомендуется:\n"
            "1. Обсудить нагрузку и дедлайны с руководителем\n"
            "2. Пройти медицинское обследование (зрение, осанка, нервная система)\n"
            "3. Взять отпуск для полного отдыха от компьютера\n"
            "4. Обратиться к психологу, специализирующемуся на IT-профессионалах",
            parse_mode="Markdown"
        )