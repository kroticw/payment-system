import logging
import os
from database import (
    init_db, create_account, get_account, get_accounts_by_client,
    create_banknote, get_banknote, get_banknote_by_uuid, 
    update_banknote_status, get_banknotes_by_status, get_all_banknotes
)

# Настройка логирования
logger = logging.getLogger(__name__)

class BankService:
    def __init__(self):
        """Инициализация банковского сервиса"""
        self.db_path = os.environ.get('DB_PATH', 'bank.db')
        logger.info(f"Инициализация банковского сервиса. База данных: {self.db_path}")
    
    def initialize_database(self):
        """Инициализация базы данных"""
        init_db()
        logger.info("База данных инициализирована")
    
    # Методы для работы со счетами
    
    def create_bank_account(self, client_id, initial_balance=0.0):
        """Создание нового банковского счета"""
        try:
            account = create_account(client_id, initial_balance=initial_balance)
            logger.info(f"Создан новый счет для клиента {client_id}")
            return {
                "status": "success",
                "message": "Счет успешно создан",
                "account": account
            }, 200
        except Exception as e:
            logger.error(f"Ошибка при создании счета: {str(e)}")
            return {
                "status": "error", 
                "message": f"Ошибка при создании счета: {str(e)}"
            }, 500
    
    def get_bank_account(self, account_id):
        """Получение информации о банковском счете"""
        try:
            account = get_account(account_id)
            
            if not account:
                logger.warning(f"Счет не найден: {account_id}")
                return {
                    "status": "error", 
                    "message": "Счет не найден"
                }, 404
            
            logger.info(f"Получена информация о счете {account_id}")
            return {
                "status": "success",
                "account": account
            }, 200
        except Exception as e:
            logger.error(f"Ошибка при получении информации о счете: {str(e)}")
            return {
                "status": "error", 
                "message": f"Ошибка при получении информации о счете: {str(e)}"
            }, 500
    
    def list_bank_accounts(self, client_id):
        """Получение списка счетов клиента"""
        try:
            accounts = get_accounts_by_client(client_id)
            logger.info(f"Получен список счетов для клиента {client_id}")
            return {
                "status": "success",
                "accounts": accounts
            }, 200
        except Exception as e:
            logger.error(f"Ошибка при получении списка счетов: {str(e)}")
            return {
                "status": "error", 
                "message": f"Ошибка при получении списка счетов: {str(e)}"
            }, 500
    
    # Методы для работы с банкнотами
    
    def create_new_banknote(self, denomination):
        """Создание новой банкноты"""
        try:
            banknote = create_banknote(denomination)
            logger.info(f"Создана новая банкнота с номиналом {denomination}")
            return {
                "status": "success",
                "message": "Банкнота успешно создана",
                "banknote": banknote
            }, 200
        except ValueError as e:
            logger.warning(f"Ошибка валидации при создании банкноты: {str(e)}")
            return {
                "status": "error", 
                "message": str(e)
            }, 400
        except Exception as e:
            logger.error(f"Ошибка при создании банкноты: {str(e)}")
            return {
                "status": "error", 
                "message": f"Ошибка при создании банкноты: {str(e)}"
            }, 500
    
    def get_banknote_info(self, banknote_id):
        """Получение информации о банкноте по ID"""
        try:
            banknote = get_banknote(banknote_id)
            
            if not banknote:
                logger.warning(f"Банкнота не найдена: {banknote_id}")
                return {
                    "status": "error", 
                    "message": "Банкнота не найдена"
                }, 404
            
            logger.info(f"Получена информация о банкноте {banknote_id}")
            return {
                "status": "success",
                "banknote": banknote
            }, 200
        except Exception as e:
            logger.error(f"Ошибка при получении информации о банкноте: {str(e)}")
            return {
                "status": "error", 
                "message": f"Ошибка при получении информации о банкноте: {str(e)}"
            }, 500
    
    def get_banknote_by_uuid_info(self, banknote_uuid):
        """Получение информации о банкноте по UUID"""
        try:
            banknote = get_banknote_by_uuid(banknote_uuid)
            
            if not banknote:
                logger.warning(f"Банкнота не найдена: {banknote_uuid}")
                return {
                    "status": "error", 
                    "message": "Банкнота не найдена"
                }, 404
            
            logger.info(f"Получена информация о банкноте с UUID {banknote_uuid}")
            return {
                "status": "success",
                "banknote": banknote
            }, 200
        except Exception as e:
            logger.error(f"Ошибка при получении информации о банкноте: {str(e)}")
            return {
                "status": "error", 
                "message": f"Ошибка при получении информации о банкноте: {str(e)}"
            }, 500
    
    def update_banknote_status_info(self, banknote_id, new_status):
        """Обновление статуса банкноты"""
        try:
            # Проверяем, существует ли банкнота
            banknote = get_banknote(banknote_id)
            if not banknote:
                logger.warning(f"Банкнота не найдена: {banknote_id}")
                return {
                    "status": "error", 
                    "message": "Банкнота не найдена"
                }, 404
            
            # Обновляем статус
            if update_banknote_status(banknote_id, new_status):
                logger.info(f"Обновлен статус банкноты {banknote_id} на '{new_status}'")
                return {
                    "status": "success",
                    "message": "Статус банкноты успешно обновлен"
                }, 200
            else:
                logger.warning(f"Не удалось обновить статус банкноты {banknote_id}")
                return {
                    "status": "error", 
                    "message": "Не удалось обновить статус банкноты"
                }, 400
        except ValueError as e:
            logger.warning(f"Ошибка валидации при обновлении статуса банкноты: {str(e)}")
            return {
                "status": "error", 
                "message": str(e)
            }, 400
        except Exception as e:
            logger.error(f"Ошибка при обновлении статуса банкноты: {str(e)}")
            return {
                "status": "error", 
                "message": f"Ошибка при обновлении статуса банкноты: {str(e)}"
            }, 500
    
    def list_banknotes_by_status_info(self, status):
        """Получение списка банкнот по статусу"""
        try:
            banknotes = get_banknotes_by_status(status)
            logger.info(f"Получен список банкнот со статусом '{status}'")
            return {
                "status": "success",
                "banknotes": banknotes
            }, 200
        except ValueError as e:
            logger.warning(f"Ошибка валидации при получении списка банкнот: {str(e)}")
            return {
                "status": "error", 
                "message": str(e)
            }, 400
        except Exception as e:
            logger.error(f"Ошибка при получении списка банкнот: {str(e)}")
            return {
                "status": "error", 
                "message": f"Ошибка при получении списка банкнот: {str(e)}"
            }, 500
    
    def list_all_banknotes_info(self):
        """Получение списка всех банкнот"""
        try:
            banknotes = get_all_banknotes()
            logger.info("Получен список всех банкнот")
            return {
                "status": "success",
                "banknotes": banknotes
            }, 200
        except Exception as e:
            logger.error(f"Ошибка при получении списка всех банкнот: {str(e)}")
            return {
                "status": "error", 
                "message": f"Ошибка при получении списка всех банкнот: {str(e)}"
            }, 500

# Создаем экземпляр сервиса
bank_service = BankService()
