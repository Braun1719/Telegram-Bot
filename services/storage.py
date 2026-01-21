# services/storage.py
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from datetime import datetime

class IStorage(ABC):
    """Интерфейс для хранилища данных (для будущей PostgreSQL)"""
    
    @abstractmethod
    async def save_test_result(self, chat_id: int, test_data: Dict) -> None:
        pass
    
    @abstractmethod
    async def get_user_history(self, chat_id: int, limit: int = 10) -> List[Dict]:
        pass
    
    @abstractmethod
    async def get_statistics(self, chat_id: int) -> Optional[Dict]:
        pass

class MemoryStorage(IStorage):
    """Временное хранилище в памяти (заменится на PostgreSQL)"""
    
    def __init__(self):
        self._storage: Dict[int, List[Dict]] = {}
    
    async def save_test_result(self, chat_id: int, test_data: Dict) -> None:
        """Сохранение результата теста"""
        if chat_id not in self._storage:
            self._storage[chat_id] = []
        
        test_data['timestamp'] = datetime.now().isoformat()
        self._storage[chat_id].append(test_data)
        
        # Ограничиваем историю
        if len(self._storage[chat_id]) > 20:
            self._storage[chat_id] = self._storage[chat_id][-20:]
    
    async def get_user_history(self, chat_id: int, limit: int = 10) -> List[Dict]:
        """Получение истории тестов"""
        if chat_id in self._storage:
            return self._storage[chat_id][-limit:]
        return []
    
    async def get_statistics(self, chat_id: int) -> Optional[Dict]:
        """Получение статистики"""
        history = await self.get_user_history(chat_id)
        if not history:
            return None
        
        stats = {
            'total_tests': len(history),
            'last_test_date': history[-1]['timestamp'],
            'test_types': {},
            'trend': 'недостаточно данных'
        }
        
        # Анализ тренда
        maslach_tests = [h for h in history if h.get('test_type') == 'maslach']
        if len(maslach_tests) >= 2:
            last_ee = maslach_tests[-1].get('scores', {}).get('EE', 0)
            prev_ee = maslach_tests[-2].get('scores', {}).get('EE', 0)
            stats['trend'] = 'улучшение' if last_ee < prev_ee else 'ухудшение' if last_ee > prev_ee else 'стабильно'
        
        return stats

# Создаем экземпляр хранилища
storage = MemoryStorage()