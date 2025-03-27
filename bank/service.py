import logging
import os
from Crypto.PublicKey import RSA
from Crypto.PublicKey.RSA import RsaKey
import paymentMath as pm

# Настройка логирования
logger = logging.getLogger(__name__)

class Client:
    def __init__(self, id, start_money):
        self.id = id
        self.start_money = start_money

class BankService:
    list_clients = []
    def __init__(self):
        """Инициализация банковского сервиса"""
        # self.db_path = os.environ.get('DB_PATH', 'bank.db')
        # logger.info(f"Инициализация банковского сервиса. База данных: {self.db_path}")

    def create_client(self, start_money, uid):
        client = Client(uid, start_money)
        self.list_clients.append(client)
        return client

    # Методы для работы с банкнотами

    """ TODO: реализовать проверку банкноты"""
    def verify_blinded_banknote(self, banknote):
        return True

    # Подписывает затенённую банкноту
    def sign_banknote(self, blinded_banknote):
        return pm.bank_sign_blinded(blinded_banknote)



# Создаем экземпляр сервиса
bank_service = BankService()
