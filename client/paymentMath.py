import random
from math import gcd
from functools import reduce
# from server import bank_sign_blinded, bank_sign_change  # Импорт серверных функций

# Массив делителей (доступен и клиенту, и серверу)
divisors = [3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67,
            71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137,
            139, 149, 151, 157, 163, 167, 173]

# Параметры системы (доступны клиенту)
n = 7340319761155748661749371063757287359076613120562021623339822878007388760496894682101855614243031851692369942145494922651206179917235015123962197550362007


# Клиентские функции
def mod_inverse(a, m):
    def extended_gcd(a, b):
        if a == 0:
            return b, 0, 1
        gcd, x1, y1 = extended_gcd(b % a, a)
        x = y1 - (b // a) * x1
        y = x1
        return gcd, x, y

    _, x, _ = extended_gcd(a, m)
    return (x % m + m) % m


def generate_blinding_factor(n):
    while True:
        r = random.randint(2, n - 1)
        if gcd(r, n) == 1:
            return r


def select_amount_exponent(amount, divisors):
    """Выбор экспоненты на основе двоичного представления суммы"""
    if amount < 0 or amount >= 2 ** len(divisors):
        raise ValueError(f"Сумма должна быть в диапазоне 0..{2 ** (len(divisors) - 1)}")
    binary = bin(amount)[2:].zfill(len(divisors))
    selected_divisors = [divisors[i] for i in range(len(divisors)) if binary[len(divisors) - 1 - i] == '1']
    return reduce(lambda x, y: x * y, selected_divisors) if selected_divisors else 1


def create_blinded_message(s, r, exp, n):
    return (s * pow(r, exp, n)) % n


def unblind_signed(signed_msg, r, n):
    r_inv = mod_inverse(r, n)
    return (signed_msg * r_inv) % n


def create_payment_message(signed_bill, payment_exp, n):
    return pow(signed_bill, payment_exp, n)


def create_change_request(t, ra, change_exp, n):
    return (t * pow(ra, change_exp, n)) % n


def unblind_change(signed_change, ra, n):
    ra_inv = mod_inverse(ra, n)
    return (signed_change * ra_inv) % n


def verify_payment(payment_msg, h, payment_exp, n):
    check_exp = h // payment_exp
    return pow(payment_msg, check_exp, n)

def get_h():
    return reduce(lambda x, y: x * y, divisors)

# def main():
#     max_amount = 2 ** (len(divisors) - 1)
#     h = reduce(lambda x, y: x * y, divisors)  # Клиент знает h для проверки
#
#     print(f"Максимально возможная сумма: {max_amount}")
#     amount = int(input(f"Введите сумму купюры (0..{max_amount}): "))
#     if amount > max_amount or amount < 0:
#         print("Сумма вне допустимого диапазона!")
#         return
#
#     try:
#         initial_exp = select_amount_exponent(amount, divisors)
#         print(f"Экспонента для суммы {amount}: {initial_exp}")
#
#         # Инициализация купюры
#         s1 = random.randint(2, n - 1)
#         r1 = generate_blinding_factor(n)
#         blinded_msg = create_blinded_message(s1, r1, h, n)
#         print(f"Отправлено в банк: {blinded_msg}")
#
#         # Запрос подписи у банка
#         signed_blinded = bank_sign_blinded(blinded_msg)
#         print(f"Банк вернул: {signed_blinded}")
#
#         # Снятие затемнения
#         signed_bill = unblind_signed(signed_blinded, r1, n)
#         print(f"Подписанная купюра: {signed_bill}")
#
#         # Платеж
#         payment_amount = int(input(f"Введите сумму платежа (0..{amount}): "))
#         if payment_amount > amount or payment_amount < 0:
#             print("Сумма платежа вне допустимого диапазона!")
#             return
#
#         payment_exp = select_amount_exponent(payment_amount, divisors)
#         print(f"Экспонента для платежа {payment_amount}: {payment_exp}")
#
#         payment_msg = create_payment_message(signed_bill, payment_exp, n)
#         print(f"Платеж абоненту B: {payment_msg}")
#
#         # Проверка платежа клиентом
#         verified_payment = verify_payment(payment_msg, h, payment_exp, n)
#         print(f"Проверка клиентом (должно быть равно s1): {verified_payment}")
#         print(f"Исходный s1: {s1}")
#
#         # Запрос сдачи
#         if payment_amount < amount:
#             change_amount = amount - payment_amount
#             t = random.randint(2, n - 1)
#             ra = generate_blinding_factor(n)
#             change_exp = select_amount_exponent(change_amount, divisors)
#             print(f"\nСдача: {change_amount}, экспонента: {change_exp}")
#
#             blinded_change = create_change_request(t, ra, change_exp, n)
#             print(f"Запрос на сдачу отправлен в банк: {blinded_change}")
#
#             # Запрос подписи сдачи у банка
#             signed_change_blinded = bank_sign_change(blinded_change, change_exp)
#             print(f"Банк вернул подписанную сдачу: {signed_change_blinded}")
#
#             # Снятие затемнения сдачи
#             change_bill = unblind_change(signed_change_blinded, ra, n)
#             print(f"Полученная сдача: {change_bill}")
#
#             # Проверка сдачи
#             verified_change = pow(change_bill, change_exp, n)
#             print(f"Проверка сдачи (должно быть равно t): {verified_change}")
#             print(f"Исходное t: {t}")
#         else:
#             print("Сдача не требуется")
#
#     except ValueError as e:
#         print(e)
#
#
# if __name__ == "__main__":
#     main()