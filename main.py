# main.py
import asyncio
import logging

from bot_setup import dp, bot
import handlers.commands
import handlers.maslach_test
import handlers.quick_test
import handlers.history
import handlers.boyko_test
import handlers.heck_hess_test
import handlers.cancel_handler  

async def main():
    """Основная функция запуска бота"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger = logging.getLogger(__name__)
    logger.info("Запуск бота для диагностики выгорания...")
    
    # Запускаем бота
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())