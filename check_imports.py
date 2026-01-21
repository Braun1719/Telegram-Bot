# check_imports.py
import sys
import os

# Добавляем корневую папку в путь Python
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    # Проверяем все ключевые импорты
    from config import bot_config, db_config
    print("✅ config.py импортирован")
    
    from bot_setup import bot, dp
    print("✅ bot_setup.py импортирован")
    
    from models.states import MaslachTestStates, QuickTestStates
    print("✅ models.states импортирован")
    
    from models.questions import MaslachQuestions, QuickTestQuestions
    print("✅ models.questions импортирован")
    
    from keyboards.main_menu import get_main_keyboard, get_test_cancel_keyboard
    print("✅ keyboards.main_menu импортирован")
    
    from keyboards.maslach_keyboard import get_maslach_keyboard, get_quick_test_keyboard
    print("✅ keyboards.maslach_keyboard импортирован")
    
    from services.test_calculator import TestCalculator
    print("✅ services.test_calculator импортирован")
    
    from services.recommendations import (
        get_maslach_recommendations, 
        get_quick_test_recommendations,
        get_general_prevention_tips
    )
    print("✅ services.recommendations импортирован")
    
    from services.storage import storage
    print("✅ services.storage импортирован")
    
    print("\n🎉 Все импорты работают корректно!")
    print(f"Токен бота: {'установлен' if bot_config.token != 'ВАШ_ТОКЕН_ОТ_BOTFATHER' else 'НЕ установлен'}")
    
except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
    print(f"Путь Python: {sys.path}")
    
    # Показываем структуру проекта
    print("\n📁 Структура проекта:")
    for root, dirs, files in os.walk("."):
        level = root.replace(".", "").count(os.sep)
        indent = " " * 2 * level
        print(f"{indent}{os.path.basename(root)}/")
        subindent = " " * 2 * (level + 1)
        for file in files:
            if file.endswith(".py"):
                print(f"{subindent}{file}")