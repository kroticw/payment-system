import sqlite3
import os
import uuid
import logging
from datetime import datetime

# Настройка логирования
logger = logging.getLogger(__name__)

# Путь к базе данных
DB_PATH = os.environ.get('DB_PATH', 'bank.db')

def init_db():
    """Инициализация базы данных и создание необходимых таблиц"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Создание таблицы bank_account, если она не существует
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS bank_account (
        id TEXT PRIMARY KEY,
        client_id TEXT NOT NULL,
        balance REAL DEFAULT 0.0,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )
    ''')
    
    # Создание таблицы banknote для хранения ID валидных купюр
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS banknote (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        uuid TEXT UNIQUE NOT NULL,
        denomination INTEGER NOT NULL,
        status TEXT CHECK(status IN ('в обращении', 'не в обращении', 'снята с обращения')) DEFAULT 'не в обращении'
    )
    ''')
    
    conn.commit()
    conn.close()
    logger.info(f"База данных инициализирована: {DB_PATH}")

def create_account(client_id, initial_balance=0.0):
    """Создание нового банковского счета"""
    # Генерация уникального ID для счета
    account_id = str(uuid.uuid4())
    now = datetime.now().isoformat()
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Вставка нового счета
        cursor.execute(
            "INSERT INTO bank_account (id, client_id, balance, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
            (account_id, client_id, initial_balance, now, now)
        )
        
        conn.commit()
        conn.close()
        
        logger.info(f"Создан новый счет: {account_id} для клиента: {client_id}")
        
        return {
            "id": account_id,
            "client_id": client_id,
            "balance": initial_balance,
            "created_at": now
        }
    
    except Exception as e:
        logger.error(f"Ошибка при создании счета: {str(e)}")
        raise

def get_account(account_id):
    """Получение информации о счете по ID"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, client_id, balance, created_at, updated_at FROM bank_account WHERE id = ?", (account_id,))
        account = cursor.fetchone()
        conn.close()
        
        if not account:
            return None
        
        return {
            "id": account[0],
            "client_id": account[1],
            "balance": account[2],
            "created_at": account[4],
            "updated_at": account[5]
        }
    
    except Exception as e:
        logger.error(f"Ошибка при получении информации о счете: {str(e)}")
        raise

def get_accounts_by_client(client_id):
    """Получение списка счетов клиента"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, client_id, balance, created_at, updated_at FROM bank_account WHERE client_id = ?", (client_id,))
        accounts = cursor.fetchall()
        conn.close()
        
        result = []
        for account in accounts:
            result.append({
                "id": account[0],
                "client_id": account[1],
                "balance": account[2],
                "created_at": account[4],
                "updated_at": account[5]
            })
        
        return result
    
    except Exception as e:
        logger.error(f"Ошибка при получении списка счетов: {str(e)}")
        raise

def update_account_balance(account_id, new_balance):
    """Обновление баланса счета"""
    try:
        now = datetime.now().isoformat()
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute(
            "UPDATE bank_account SET balance = ?, updated_at = ? WHERE id = ?",
            (new_balance, now, account_id)
        )
        
        if cursor.rowcount == 0:
            conn.close()
            return False
            
        conn.commit()
        conn.close()
        
        logger.info(f"Обновлен баланс счета {account_id}: {new_balance}")
        return True
    
    except Exception as e:
        logger.error(f"Ошибка при обновлении баланса счета: {str(e)}")
        raise

# Функции для работы с банкнотами

def create_banknote(denomination):
    """Создание новой банкноты"""
    # Проверка, что номинал корректный
    valid_denominations = [100, 200, 500, 1000, 5000]
    if denomination not in valid_denominations:
        raise ValueError(f"Недопустимый номинал. Разрешены только: {valid_denominations}")
    
    banknote_uuid = str(uuid.uuid4())
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO banknote (uuid, denomination, status) VALUES (?, ?, ?)",
            (banknote_uuid, denomination, 'не в обращении')
        )
        
        banknote_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        logger.info(f"Создана новая банкнота: {banknote_uuid}, номинал: {denomination}")
        
        return {
            "id": banknote_id,
            "uuid": banknote_uuid,
            "denomination": denomination,
            "status": 'не в обращении'
        }
    
    except Exception as e:
        logger.error(f"Ошибка при создании банкноты: {str(e)}")
        raise

def get_banknote(banknote_id):
    """Получение информации о банкноте по ID"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, uuid, denomination, status FROM banknote WHERE id = ?", (banknote_id,))
        banknote = cursor.fetchone()
        conn.close()
        
        if not banknote:
            return None
        
        return {
            "id": banknote[0],
            "uuid": banknote[1],
            "denomination": banknote[2],
            "status": banknote[3]
        }
    
    except Exception as e:
        logger.error(f"Ошибка при получении информации о банкноте: {str(e)}")
        raise

def get_banknote_by_uuid(banknote_uuid):
    """Получение информации о банкноте по UUID"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, uuid, denomination, status FROM banknote WHERE uuid = ?", (banknote_uuid,))
        banknote = cursor.fetchone()
        conn.close()
        
        if not banknote:
            return None
        
        return {
            "id": banknote[0],
            "uuid": banknote[1],
            "denomination": banknote[2],
            "status": banknote[3]
        }
    
    except Exception as e:
        logger.error(f"Ошибка при получении информации о банкноте: {str(e)}")
        raise

def update_banknote_status(banknote_id, new_status):
    """Обновление статуса банкноты"""
    valid_statuses = ['в обращении', 'не в обращении', 'снята с обращения']
    if new_status not in valid_statuses:
        raise ValueError(f"Недопустимый статус. Разрешены только: {valid_statuses}")
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute(
            "UPDATE banknote SET status = ? WHERE id = ?",
            (new_status, banknote_id)
        )
        
        if cursor.rowcount == 0:
            conn.close()
            return False
            
        conn.commit()
        conn.close()
        
        logger.info(f"Обновлен статус банкноты {banknote_id}: {new_status}")
        return True
    
    except Exception as e:
        logger.error(f"Ошибка при обновлении статуса банкноты: {str(e)}")
        raise

def get_banknotes_by_status(status):
    """Получение списка банкнот по статусу"""
    valid_statuses = ['в обращении', 'не в обращении', 'снята с обращения']
    if status not in valid_statuses:
        raise ValueError(f"Недопустимый статус. Разрешены только: {valid_statuses}")
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, uuid, denomination, status FROM banknote WHERE status = ?", (status,))
        banknotes = cursor.fetchall()
        conn.close()
        
        result = []
        for banknote in banknotes:
            result.append({
                "id": banknote[0],
                "uuid": banknote[1],
                "denomination": banknote[2],
                "status": banknote[3]
            })
        
        return result
    
    except Exception as e:
        logger.error(f"Ошибка при получении списка банкнот по статусу: {str(e)}")
        raise

def get_all_banknotes():
    """Получение списка всех банкнот"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, uuid, denomination, status FROM banknote")
        banknotes = cursor.fetchall()
        conn.close()
        
        result = []
        for banknote in banknotes:
            result.append({
                "id": banknote[0],
                "uuid": banknote[1],
                "denomination": banknote[2],
                "status": banknote[3]
            })
        
        return result
    
    except Exception as e:
        logger.error(f"Ошибка при получении списка всех банкнот: {str(e)}")
        raise 