import requests
import logging
import os
import time
import uuid
import sys
from service import *

# Настройка логирования
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Конфигурация
BANK_SERVER_URL = os.environ.get('BANK_SERVER_URL', 'http://localhost:8080')
CLIENT_PORT = int(os.environ.get('CLIENT_PORT', 5001))
CLIENT_ID = os.environ.get('CLIENT_ID', str(uuid.uuid4())[:8])  # Генерация ID клиента
CLIENT_API_URL = f"http://localhost:{CLIENT_PORT}"

def console_menu():
    """Консольное меню для взаимодействия с банковской системой"""
    print(f"\nБанковский клиент запущен")
    print(f"ID клиента: {CLIENT_ID}")
    print(f"Банковский сервер: {BANK_SERVER_URL}")
    print(f"Клиентский API: {CLIENT_API_URL}")
    
    while True:
        print("\n==== Клиентское меню ====")
        print(f"Клиент ID: {CLIENT_ID}")
        print(f"Банк: {BANK_SERVER_URL}")
        print("1. Создать счет в банке")
        print("2. Просмотреть мои счета")
        print("3. Оплатить товар")
        print("0. Выход")
        
        choice = input("Выберите пункт меню: ")
        
        if choice == '1':
            try:
                initial_balance = float(input("Введите начальный баланс (по умолчанию 0): ") or "0")
            except ValueError:
                print("Ошибка: Введите корректное число для баланса")
                continue
                
            try:
                response = requests.post(
                    f"{CLIENT_API_URL}/api/v1/create-account",
                    json={
                        "initial_balance": initial_balance,
                        "client_public_key": get_client_public_key().decode()
                    }
                )
                if response.status_code == 200:
                    account_data = response.json()
                    if account_data.get("status") == "success":
                        print(f"Счет успешно создан! ID: {account_data['account']['id']}")
                    else:
                        print(f"Ошибка: {account_data.get('message', 'Неизвестная ошибка')}")

                    save_server_public_key(account_data['server_public_key'])

                else:
                    print(f"Ошибка: Код ответа {response.status_code}")
            except Exception as e:
                print(f"Ошибка при создании счета: {str(e)}")
                
        elif choice == '2':
            try:
                response = requests.get(f"{CLIENT_API_URL}/api/v1/accounts")
                if response.status_code == 200:
                    accounts_data = response.json()
                    if accounts_data.get("status") == "success":
                        accounts = accounts_data.get("accounts", [])
                        if accounts:
                            print("\nСписок счетов:")
                            for account in accounts:
                                print(f"ID: {account['id']}, Баланс: {account['balance']} RUB, Создан: {account['created_at']}")
                        else:
                            print("У вас пока нет счетов в банке")
                    else:
                        print(f"Ошибка: {accounts_data.get('message', 'Неизвестная ошибка')}")
                else:
                    print(f"Ошибка: Код ответа {response.status_code}")
            except Exception as e:
                print(f"Ошибка при получении списка счетов: {str(e)}")
        
        elif choice == '3':
            try:
                valid_denominations = [100, 200, 500, 1000, 2000, 5000]
                print("Доступные номиналы банкнот:", valid_denominations)
                
                try:
                    denomination = int(input("Введите номинал банкноты, которой хотите оплатить товар: "))
                    if denomination not in valid_denominations:
                        print(f"Ошибка: Недопустимый номинал. Допустимые значения: {valid_denominations}")
                        continue
                except ValueError:
                    print("Ошибка: Введите корректное целое число")
                    continue

                req = get_request_on_banknote(denomination)
                
                response = requests.post(
                    f"{BANK_SERVER_URL}/api/v1/banknotes",
                    json={"denomination": denomination}
                )
                
                if response.status_code == 200:
                    banknote_data = response.json()
                    if banknote_data.get("status") == "success":
                        print(f"Банкнота успешно создана!")
                        print(f"ID: {banknote_data['banknote']['id']}")
                        print(f"UUID: {banknote_data['banknote']['uuid']}")
                        print(f"Номинал: {banknote_data['banknote']['denomination']}")
                        print(f"Статус: {banknote_data['banknote']['status']}")
                    else:
                        print(f"Ошибка: {banknote_data.get('message', 'Неизвестная ошибка')}")
                else:
                    print(f"Ошибка: Код ответа {response.status_code}")
            except Exception as e:
                print(f"Ошибка при создании банкноты: {str(e)}")

        elif choice == '0':
            print("Выход из меню")
            break
            
        else:
            print("Неверный выбор, попробуйте снова")
        
        time.sleep(1)

def check_server_connection():
    """Проверка соединения с сервером"""
    try:
        response = requests.get(f"{CLIENT_API_URL}")
        if response.status_code == 200:
            logger.info("Клиентский сервер доступен")
            return True
    except:
        pass
    
    logger.warning("Клиентский сервер недоступен")
    return False

if __name__ == '__main__':
    print("Запуск банковского клиента...")
    
    # Проверяем, запущен ли клиентский сервер
    if not check_server_connection():
        print("ВНИМАНИЕ: Клиентский сервер недоступен или не запущен.")
        print(f"Некоторые операции могут быть недоступны.")
        print(f"Убедитесь, что сервер запущен на {CLIENT_API_URL}")
    
    try:
        console_menu()
    except KeyboardInterrupt:
        print("\nВыход из клиента")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Ошибка при работе клиента: {str(e)}")
        print(f"Произошла ошибка: {str(e)}")
        sys.exit(1) 