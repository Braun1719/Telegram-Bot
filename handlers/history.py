# handlers/history.py
from typing import Dict, List
from aiogram import types
from aiogram.fsm.context import FSMContext

from bot_setup import dp
from services.storage import storage
from keyboards.main_menu import get_main_keyboard
from services.recommendations import get_general_prevention_tips

# Словарь для преобразования типов тестов в читаемые названия
TEST_TYPE_NAMES = {
    "maslach": "📊 Опросник Маслач",
    "quick": "⚡ Быстрый тест",
    "boyko": "📋 Тест Бойко",
    "psm": "🧠 PSM-опросник",
    "sppb": "🔥 Тест СППБ",
    "heck_hess": "📝 Тест Хекка-Хесса",
    "unknown": "❓ Неизвестный тест"
}

@dp.message(lambda message: message.text == "📈 Мои результаты")
async def show_user_history(message: types.Message):
    """Показ истории тестов пользователя"""
    history = await storage.get_user_history(message.chat.id)
    stats = await storage.get_statistics(message.chat.id)
    
    if not history:
        await message.answer(
            "📭 У вас пока нет сохраненных тестов.\n\n"
            "Пройдите хотя бы один тест для отслеживания динамики:",
            reply_markup=get_main_keyboard()
        )
        return
    
    # Формируем сообщение со статистикой
    stats_text = "📊 ВАША СТАТИСТИКА\n\n"
    stats_text += f"• Всего тестов: {stats.get('total_tests', 0)}\n"
    if stats.get('last_test_date'):
        stats_text += f"• Последний тест: {stats['last_test_date'][:10]}\n"
    if stats.get('trend') and stats['trend'] != 'недостаточно данных':
        stats_text += f"• Тренд: {stats['trend']}\n"
    stats_text += "\n"
    
    # Группируем по типам тестов
    test_counts = {}
    for test in history:
        test_type = test.get('test_type', 'unknown')
        test_counts[test_type] = test_counts.get(test_type, 0) + 1
    
    stats_text += "Распределение по тестам:\n"
    for test_type, count in test_counts.items():
        name = TEST_TYPE_NAMES.get(test_type, f"Тест: {test_type}")
        stats_text += f"• {name}: {count}\n"
    
    await message.answer(stats_text)
    
    # Показываем последние 3 теста подробнее
    if history:
        last_tests_text = "\n📝 ПОСЛЕДНИЕ РЕЗУЛЬТАТЫ:\n\n"
        
        for i, test in enumerate(history[:3], 1):
            test_type = test.get('test_type', 'unknown')
            date = test.get('timestamp', '')[:10] if test.get('timestamp') else 'дата неизвестна'
            name = TEST_TYPE_NAMES.get(test_type, f"Тест: {test_type}")
            
            last_tests_text += f"{i}. {name} ({date})\n"
            
            # Получаем scores из теста
            scores = test.get('scores', {})
            
            # Форматирование результатов для каждого типа теста
            if test_type == 'maslach':
                # Для Маслач
                if 'interpretation' in scores:
                    interpretation = scores.get('interpretation', {})
                    ee = interpretation.get('EE', {}).get('score', 0)
                    dp = interpretation.get('DP', {}).get('score', 0)
                    pa = interpretation.get('PA', {}).get('score', 0)
                    overall = interpretation.get('overall', '')
                else:
                    ee = scores.get('EE', 0)
                    dp = scores.get('DP', 0)
                    pa = scores.get('PA', 0)
                    overall = scores.get('overall', '')
                
                last_tests_text += f"   ЭИ: {ee} | ДП: {dp} | ПД: {pa}\n"
                if overall:
                    last_tests_text += f"   {overall}\n"
                    
            elif test_type == 'quick':
                # Для быстрого теста - есть вложенная структура
                inner_scores = scores.get('scores', {})
                if inner_scores:
                    # Берем данные из вложенного scores
                    total = inner_scores.get('total', 0)
                    max_score = inner_scores.get('max', 40)
                    level = inner_scores.get('level', '')
                    risk = inner_scores.get('risk', '')
                else:
                    # Если нет вложенной структуры, берем из корня scores
                    total = scores.get('total', 0)
                    max_score = scores.get('max', 40)
                    level = scores.get('level', '')
                    risk = scores.get('risk', '')
                
                last_tests_text += f"   Баллы: {total}/{max_score}\n"
                if level:
                    last_tests_text += f"   Уровень: {level}\n"
                if risk and risk != level:  # Если risk отличается от level
                    last_tests_text += f"   {risk}\n"
                
            elif test_type == 'boyko':
                # Для теста Бойко
                phases = scores.get('phases', {})
                overall = scores.get('overall', '')
                risk_level = scores.get('risk_level', '')
                dominant_phase = scores.get('dominant_phase', '')
                
                # Суммируем баллы из всех фаз
                total_score = sum(phases.values()) if phases else 0
                
                last_tests_text += f"   Общий балл: {total_score}\n"
                if risk_level:
                    last_tests_text += f"   Уровень риска: {risk_level}\n"
                
                if dominant_phase:
                    # Преобразуем номер фазы в читаемый вид
                    phase_names = {
                        'фаза1': 'Напряжение',
                        'фаза2': 'Резистенция', 
                        'фаза3': 'Истощение',
                        'фаза4': 'Деформация'
                    }
                    phase_name = phase_names.get(dominant_phase, dominant_phase)
                    last_tests_text += f"   Доминирующая фаза: {phase_name}\n"
                
            elif test_type == 'heck_hess':
                # Для теста Хекка-Хесса
                total_score = scores.get('total_score', 0)
                overall_level = scores.get('overall_level', '')
                interpretation = scores.get('interpretation', '')
                burnout_risk = scores.get('burnout_risk', '')
                
                last_tests_text += f"   Баллы: {total_score}/63\n"
                if overall_level:
                    last_tests_text += f"   Уровень: {overall_level}\n"
                if interpretation:
                    last_tests_text += f"   {interpretation}\n"
                if burnout_risk:
                    last_tests_text += f"   Риск выгорания: {burnout_risk}\n"
                
            elif test_type == 'psm':
                # Для PSM-опросника
                total_score = scores.get('total_score', 0)
                level = scores.get('level', '')
                interpretation = scores.get('interpretation', '')
                
                last_tests_text += f"   Баллы: {total_score}\n"
                if level:
                    last_tests_text += f"   Уровень стресса: {level}\n"
                if interpretation:
                    last_tests_text += f"   {interpretation}\n"
                    
            elif test_type == 'sppb':
                # Для теста СППБ
                total_score = scores.get('total_score', 0)
                stage = scores.get('stage', '')
                level = scores.get('level', '')
                
                last_tests_text += f"   Баллы: {total_score}\n"
                if stage:
                    last_tests_text += f"   Стадия: {stage}\n"
                if level:
                    last_tests_text += f"   Уровень: {level}\n"
                
            else:
                # Для неизвестных типов тестов
                # Пробуем найти общий балл в разных местах
                total_score = (
                    scores.get('total_score') or 
                    scores.get('total') or 
                    scores.get('score') or 
                    0
                )
                
                if total_score:
                    last_tests_text += f"   Общий балл: {total_score}\n"
                
                # Показываем основные результаты
                for key in ['level', 'phase', 'overall', 'risk_level', 'risk', 'interpretation', 'result']:
                    value = scores.get(key)
                    if value:
                        key_display = {
                            'level': 'Уровень',
                            'phase': 'Фаза',
                            'overall': 'Результат',
                            'risk_level': 'Уровень риска',
                            'risk': 'Риск',
                            'interpretation': 'Интерпретация',
                            'result': 'Результат'
                        }.get(key, key)
                        last_tests_text += f"   {key_display}: {value}\n"
                        break
            
            last_tests_text += "\n"
        
        await message.answer(last_tests_text)
    
    # Совет по профилактике
    await message.answer(
        "💡 СОВЕТ: Регулярное тестирование (раз в 1-2 месяца) "
        "помогает отслеживать динамику и вовремя принимать меры.\n\n"
        "Рекомендуется проходить разные тесты для комплексной оценки."
    )

@dp.message(lambda message: message.text == "ℹ️ О выгорании в IT")
async def show_about(message: types.Message):
    """Информация о проекте"""
    about_text = (
        "👨‍💻 ВЫГОРАНИЕ В IT-СФЕРЕ\n\n"
        "Что такое профессиональное выгорание?\n"
        "Это состояние эмоционального, физического и ментального истощения, "
        "вызванное длительным стрессом на работе.\n\n"
        "Особенности в IT:\n"
        "• Постоянные дедлайны и обновления технологий\n"
        "• Многочасовое сидение за компьютером\n"
        "• Высокая концентрация внимания\n"
        "• Отсутствие физической активности\n"
        "• Синдром самозванца и перфекционизм\n\n"
        "Три основных признака (по Маслач):\n"
        "1. 💔 Эмоциональное истощение\n"
        "2. 🧊 Деперсонализация (цинизм, отстраненность)\n"
        "3. 📉 Редукция достижений (снижение продуктивности)\n\n"
        "Фазы выгорания (по Бойко):\n"
        "• Напряжение: тревожность, неудовлетворенность\n"
        "• Резистенция: эмоциональное отстранение, цинизм\n"
        "• Истощение: эмоциональный дефицит, психосоматика\n"
        "• Деформация: профессиональная деградация\n\n"
        "Доступные тесты в боте:\n"
        "• 📊 Опросник Маслач - оценка трех компонентов выгорания\n"
        "• ⚡ Быстрый тест - экспресс-оценка состояния\n"
        "• 📋 Тест Бойко - определение фазы выгорания\n"
        "• 🧠 PSM-опросник - оценка профессионального стресса\n"
        "• 🔥 Тест СППБ - диагностика психического выгорания\n"
        "• 📝 Тест Хекка-Хесса - оценка уровня тревоги\n\n"
        "Профилактика для IT-специалистов:\n"
        "• Установите границы рабочего времени\n"
        "• Делайте регулярные перерывы (правило 20-20-20)\n"
        "• Практикуйте физические упражнения\n"
        "• Развивайте хобби вне работы\n"
        "• Общайтесь с коллегами и друзьями\n\n"
        "⚠️ ВАЖНО: Бот не ставит диагнозы и не заменяет "
        "профессиональную медицинскую помощь.\n"
        "При серьезных симптомах обратитесь к специалисту!"
    )
    
    await message.answer(about_text)
    
    # Показываем советы по профилактике
    prevention_tips = get_general_prevention_tips()
    if isinstance(prevention_tips, list):
        tips_text = "\n".join(prevention_tips[:8])  # Показываем первые 8 советов
        await message.answer(tips_text)
    else:
        await message.answer(prevention_tips[:500])  # Первые 500 символов