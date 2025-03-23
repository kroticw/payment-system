#!/usr/bin/env python3
import sys
import os
import argparse
import logging
import signal
from Crypto.PublicKey import RSA
from service import bank_service

# Пути к ключам
SERVER_PRIVATE_KEY_PATH = "server_private_key.pem"
SERVER_PUBLIC_KEY_PATH = "server_public_key.pem"

def generate_server_keys():
    if not os.path.exists(SERVER_PRIVATE_KEY_PATH):
        print("Генерация ключей RSA для сервера...")
        key = RSA.generate(2048)

        private_key = key.export_key()
        public_key = key.publickey().export_key()
        # Сохранение приватного ключа
        with open(SERVER_PRIVATE_KEY_PATH, "wb") as f:
            f.write(private_key)

        # Сохранение публичного ключа
        with open(SERVER_PUBLIC_KEY_PATH, "wb") as f:
            f.write(public_key)

        print("Ключи сгенерированы и сохранены")
    else:
        with open(SERVER_PRIVATE_KEY_PATH, "rb") as f:
            private_key = f.read()
        with open(SERVER_PUBLIC_KEY_PATH, "rb") as f:
            public_key = f.read()

    return private_key, public_key

# Настройка логирования
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_server(private_key, public_key):
    """Запуск серверной части (API)"""
    import server
    logger.info("Запуск банковского сервера...")
    
    # Инициализация базы данных
    bank_service.initialize_database()
    bank_service.set_keys(private_key, public_key)
    
    # Запуск Flask приложения
    server.app.run(host='0.0.0.0', port=8080, debug=False, use_reloader=False)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Запуск банковского сервера")
    parser.add_argument('--debug', action='store_true', 
                        help='Запуск в режиме отладки')
    
    args = parser.parse_args()
    
    # Обработка сигналов прерывания
    def signal_handler(sig, frame):
        logger.info("Получен сигнал прерывания, завершение работы...")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)

    private, public = generate_server_keys()

    try:
        run_server(private, public)
    except Exception as e:
        logger.error(f"Ошибка при запуске сервера: {str(e)}")
        sys.exit(1) 