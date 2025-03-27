#!/usr/bin/env python3
import sys
import os
import argparse
import threading
import time
import logging
import clientSide
import importlib
from Crypto.PublicKey import RSA
import signal

# Настройка логирования
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def run_server():
    """Запуск серверной части (API)"""
    import server
    logger.info("Запуск серверной части...")
    
    # Динамически импортируем и запускаем сервер
    if hasattr(server, 'app') and hasattr(server, 'CLIENT_PORT'):
        # Запускаем Flask приложение
        server.app.run(host='0.0.0.0', port=server.CLIENT_PORT, debug=False, use_reloader=False)
    else:
        logger.error("Не удалось запустить сервер")
        sys.exit(1)

def run_client():
    """Запуск консольного клиента"""
    logger.info("Запуск консольного клиента...")
    try:
        clientSide.console_menu()
    except Exception as e:
        logger.error(f"Ошибка при запуске клиента: {str(e)}")
        sys.exit(1)

def run_both():
    """Запуск и сервера, и клиента параллельно"""
    logger.info("Запуск системы в полнофункциональном режиме...")
    
    # Запуск сервера в отдельном потоке
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    # Даем серверу время на запуск
    time.sleep(2)
    
    # Запуск клиента в основном потоке
    try:
        run_client()
    except KeyboardInterrupt:
        logger.info("Получен сигнал остановки")
    finally:
        logger.info("Завершение работы...")
        sys.exit(0)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Запуск банковского клиента")
    parser.add_argument('--mode', '-m', type=str, choices=['server', 'client', 'both'], 
                        default='both', help='Режим запуска: server, client или both (по умолчанию)')
    
    args = parser.parse_args()
    
    # Обработка сигналов прерывания
    def signal_handler(sig, frame):
        logger.info("Получен сигнал прерывания, завершение работы...")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)


    try:
        if args.mode == 'server':
            run_server()
        elif args.mode == 'client':
            run_client()
        else:  # both
            run_both()
    except Exception as e:
        logger.error(f"Ошибка при запуске: {str(e)}")
        sys.exit(1) 