from flask import Flask, request, jsonify
import requests
import logging
import os
from functools import wraps

# Настройка логирования
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Создание экземпляра Flask
app = Flask(__name__)

# Конфигурация
BANK_SERVER_URL = os.environ.get('BANK_SERVER_URL', 'http://localhost:8080')
CLIENT_PORT = int(os.environ.get('CLIENT_PORT', 5001))

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
        "bank_server": BANK_SERVER_URL
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
@app.route('/api/v1/transaction', methods=['POST'])
@handle_bank_request
def create_transaction():
    data = request.json
    if not data:
        return jsonify({"status": "error", "message": "Не указаны данные транзакции"}), 400
    
    # Проверка минимально необходимых полей
    required_fields = ['amount', 'recipient']
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return jsonify({
            "status": "error", 
            "message": f"Отсутствуют обязательные поля: {', '.join(missing_fields)}"
        }), 400
    
    # Отправка запроса на банковский сервер
    # Этот эндпоинт пока не реализован на банковском сервере, 
    # но будет готов для будущей интеграции
    # response = requests.post(
    #     f"{BANK_SERVER_URL}/api/v1/transaction", 
    #     json=data
    # )
    # return jsonify(response.json()), response.status_code
    
    # Временная заглушка
    return jsonify({
        "status": "success", 
        "message": "Транзакция зарегистрирована",
        "transaction_id": "sample-id-12345"
    })

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
    app.run(host='0.0.0.0', port=CLIENT_PORT, debug=True)
