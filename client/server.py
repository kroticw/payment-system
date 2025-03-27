import random

from flask import Flask, request, jsonify
import requests
import logging
import os
import uuid
from functools import wraps
import paymentMath as pm
import service
from clientSide import CLIENT_API_URL
from service import Transaction

# Настройка логирования
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Создание экземпляра Flask
app = Flask(__name__)

# Конфигурация
BANK_SERVER_URL = os.environ.get('BANK_SERVER_URL', 'http://localhost:8080')
CLIENT_PORT = int(os.environ.get('CLIENT_PORT', 5001))
CLIENT_ID = os.environ.get('CLIENT_ID', str(uuid.uuid4())[:8])  # Генерация ID клиента

# Вспомогательная функция для обработки ошибок при запросах к банку
def handle_bank_request(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except requests.RequestException as e:
            logger.error(f"Ошибка при обращении к банковскому серверу: {str(e)}")
            return jsonify({
                "status": "error",
                "message": "Не удалось связаться с банковским сервером"
            }), 503
    return wrapper

# Базовый маршрут
@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "status": "online", 
        "message": "Клиентский сервер работает",
        "bank_server": BANK_SERVER_URL,
        "client_id": CLIENT_ID
    })

# Проверка соединения с банковским сервером
@app.route('/api/v1/check-bank', methods=['GET'])
@handle_bank_request
def check_bank_connection():
    response = requests.get(f"{BANK_SERVER_URL}/api/v1/status")
    if response.status_code == 200:
        return jsonify({
            "status": "ok",
            "bank_status": response.json()
        })
    else:
        return jsonify({
            "status": "error",
            "message": f"Код ответа банковского сервера: {response.status_code}"
        }), 400

# Пример маршрута для создания транзакции
@app.route('/api/v1/payment', methods=['POST'])
@handle_bank_request
def get_payment():
    data = request.json
    if not data:
        return jsonify({"status": "error", "message": "Не указаны данные транзакции"}), 400
    
    # Проверка минимально необходимых полей
    required_fields = ['payment', 's1', 'payment_exp', 'payment', 'payment_amount']
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return jsonify({
            "status": "error", 
            "message": f"Отсутствуют обязательные поля: {', '.join(missing_fields)}"
        }), 400

    # Проверка платежа клиентом
    verified_payment = pm.verify_payment(data['payment'], pm.get_h(), data['payment_exp'], pm.n)
    print(f"Проверка клиентом (должно быть равно s1): {verified_payment}")
    print(f"Исходный s1: {data['s1']}")

    if data['payment_amount'] < data['amount']:
        if 'blinded_change' not in data or 'change_exp' not in data:
            return jsonify({
                "status": "error",
                "message": "не хватает обязательных полей для сдачи"
            })

        response = requests.post(f"{BANK_SERVER_URL}/api/v1/sign-change", json={
            "blinded_change": data['blinded_change'],
            "change_exp": data['change_exp'],
        })

        data = response.json()
        print(f"Банк вернул подписанную сдачу: {data['signed_change_blinded']}")

        response = requests.post(f"{CLIENT_API_URL}/api/v1/payment", json={
            "signed_change_blinded": data['signed_change_blinded'],
            "change_exp": data['change_exp'],
        })
        data = response.json()
        #TODO: Дописать зачисление денег на счёт продавца


@app.route('/api/v1/verify-change', methods=['POST'])
def verify_change():
    data = request.json
    if not data:
        return jsonify({
            "status": "error",
            "message": "не указаны данные со сдачей"
        }), 400

    if 'signed_change_blinded' not in data:
        return jsonify({
            "status": "error",
            "message": "нет необходимого поля signed_change_blinded"
        })

    if 'change_exp' not in data:
        return jsonify({
            "status": "error",
            "message": "нет необходимого поля change_exp"
        })

    last_transaction: Transaction = service.List_transaction[-1]
    # Снятие затемнения сдачи
    change_bill = pm.unblind_change(data['signed_change_blinded'], last_transaction.ra, pm.n)
    print(f"Полученная сдача: {change_bill}")

    # Проверка сдачи
    verified_change = pow(change_bill, data['change_exp'], pm.n)
    print(f"Проверка сдачи (должно быть равно t): {verified_change}")
    print(f"Исходное t: {last_transaction.t}")



# Обработчик ошибок для 404
@app.errorhandler(404)
def not_found(e):
    return jsonify({"status": "error", "message": "Ресурс не найден"}), 404

# Обработчик ошибок для 500
@app.errorhandler(500)
def server_error(e):
    logger.error(f"Внутренняя ошибка клиентского сервера: {str(e)}")
    return jsonify({"status": "error", "message": "Внутренняя ошибка сервера"}), 500

if __name__ == '__main__':
    logger.info(f"Клиентский сервер запускается на порту {CLIENT_PORT}")
    logger.info(f"Банковский сервер доступен по адресу: {BANK_SERVER_URL}")
    logger.info(f"ID клиента: {CLIENT_ID}")
    
    app.run(host='0.0.0.0', port=CLIENT_PORT, debug=True, use_reloader=False)
