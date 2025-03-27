from math import gcd
from functools import reduce

# Массив делителей (доступен и клиенту, и серверу)
divisors = [3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67,
            71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137,
            139, 149, 151, 157, 163, 167, 173]

# Параметры системы (секретные для сервера)
p = 91480584166578905373273495367858856924625303800544241237892516956359041631323
q = 80239100220322239951066602079734678804545438199680465293877204586565106798709
# открытый ключ
n = p * q
phi = (p - 1) * (q - 1)
h = reduce(lambda x, y: x * y, divisors) # e - открытый ключ

# Серверные функции
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

def bank_sign_blinded(blinded_msg):
    h_inv = mod_inverse(h, phi)
    return pow(blinded_msg, h_inv, n)

def bank_sign_change(blinded_change, change_exp):
    change_exp_inv = mod_inverse(change_exp, phi)
    return pow(blinded_change, change_exp_inv, n)