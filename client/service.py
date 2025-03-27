import random
import uuid
from math import gcd

List_transaction = []
# Last_Transaction_numb = 0

class Transaction:
    # купюра
    amount = 0
    s1 = 0
    r1 = 0 # затеняющий множитель купюры
    # Платёж
    payment_amount = 0
    # сдача
    t = 0
    ra = 0 # затеняющий множитель сдачи
    def __init__(self, number):
        self.number = number