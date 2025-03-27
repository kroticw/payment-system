import requests
import logging
import os
import time
import uuid
import sys
from service import *
import paymentMath as pm

# Настройка логирования
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Конфигурация
BANK_SERVER_URL = os.environ.get('BANK_SERVER_URL', 'http://localhost:8080')
CLIENT_PORT = int(os.environ.get('CLIENT_PORT', 5001))
CLIENT_ID = os.environ.get('CLIENT_ID', str(uuid.uuid4())[:8])  # Генерация ID клиента
CLIENT_API_URL = f"http://localhost:{CLIENT_PORT}"


def console_menu(local_account=None):
    getting_n = 0
    getting_divisors = []
    money = 0
    transactionNumber = 0

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
        print("2. Просмотреть мой счет")
        print("3. Оплатить товар")
        print("0. Выход")
        
        choice = input("Выберите пункт меню: ")

        if choice == "1":
          try:
              start_money = int(input("Введите стартовое количество денег: "))
              print(start_money)

              response = requests.post(
                  f"{BANK_SERVER_URL}/api/v1/create-client",
                  json={
                      "start_money": start_money,
                      "client_id": CLIENT_ID,
                  }
              )
              print(response.json())

              result = response.json()
              getting_divisors = result["divisors"]
              getting_n = result["n"]
              money = start_money
          except Exception as e:
              print(e)

        elif choice == "2":
            print(f"на вашем счету {money} у.е.")

        elif choice == '3':
            try:
                max_amount = 2 ** (len(pm.divisors) - 1)
                h = pm.get_h()

                print(f"Максимально возможная сумма: {max_amount}")
                amount = int(input(f"Введите сумму купюры (0..{max_amount}): "))
                if amount > max_amount or amount < 0:
                    print(f"Ошибка: Недопустимый номинал.")
                    continue

                if amount > money:
                    print(f"Ошибка: на балансе нет такого количества денег")
                    continue

                transaction = Transaction(transactionNumber)
                transactionNumber += 1

                # Инициализация купюры
                s1 = random.randint(2, pm.n - 1)
                r1 = pm.generate_blinding_factor(pm.n)
                transaction.amount = amount
                transaction.s1 = s1
                transaction.r1 = r1
                # создаём затенённую купюру
                blinded_msg = pm.create_blinded_message(s1, r1, h, pm.n)

                # отправляем на подпись
                response = requests.post(
                    f"{BANK_SERVER_URL}/api/v1/banknotes",
                    json={"banknote": blinded_msg}
                )
                if response.status_code != 200:
                    print(f"Ошибка: Код ответа {response.status_code}")
                    continue

                banknote_data = response.json()
                if banknote_data.get("status") != "ok":
                    print(f"Ошибка: {banknote_data.get('message', 'Неизвестная ошибка')}")
                    continue

                print(f"Банкнота успешно подписана: {banknote_data['signed_banknote']}!")

                # Снятие затемнения
                signed_bill = pm.unblind_signed(banknote_data['signed_banknote'], r1, pm.n)
                print(f"Подписанная купюра: {signed_bill}")

                # Платеж
                payment_amount = int(input(f"Введите сумму платежа (0..{amount}): "))
                while payment_amount > amount or payment_amount < 0:
                    print("Сумма платежа вне допустимого диапазона!")
                    payment_amount = int(input(f"Введите сумму платежа (0..{amount}): "))

                transaction.payment_amount = payment_amount

                payment_exp = pm.select_amount_exponent(payment_amount, pm.divisors)
                print(f"Экспонента для платежа {payment_amount}: {payment_exp}")

                payment_msg = pm.create_payment_message(signed_bill, payment_exp, pm.n)


                """print(f"Платеж абоненту B: {payment_msg}")"""
                req = {
                    "payment": payment_msg,
                    "s1": s1,  # ТОЛЬКО ДЛЯ ПРОВЕРКИ
                    "payment_exp": payment_exp,
                    "payment_amount": payment_amount,
                    "amount": amount,
                }
                if payment_amount < amount:
                    change_amount = amount - payment_amount
                    t = random.randint(2, pm.n - 1)
                    ra = pm.generate_blinding_factor(pm.n)
                    change_exp = pm.select_amount_exponent(change_amount, pm.divisors)
                    print(f"\nСдача: {change_amount}, экспонента: {change_exp}")

                    blinded_change = pm.create_change_request(t, ra, change_exp, pm.n)

                    req["t"] = t
                    req["ra"] = ra
                    req["blinded_change"] = blinded_change
                    req["change_exp"] = change_exp

                List_transaction.append(transaction)

                response = requests.post(
                    f"{CLIENT_API_URL}/api/v1/payment",
                    json=req
                )

                if response.status_code != 200:
                    print(f"Произошла ошибка оплаты: {response.status_code}")

                post_payment_data = response.json()
                if post_payment_data.get("status") != "ok":
                    print("Оплата завершилась неудачно")

                # local_account += post_payment_data.get("change_bill")

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