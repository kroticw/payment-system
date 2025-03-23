from flask import Flask, request, jsonify
import logging
import os
from service import bank_service
from main import SERVER_PUBLIC_KEY_PATH, SERVER_PRIVATE_KEY_PATH

# Настройка логирования
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Создание экземпляра Flask
app = Flask(__name__)

# Базовый маршрут для проверки доступности сервера
@app.route('/', methods=['GET'])
def home():
    return jsonify({"status": "online", "message": "Банковский сервер работает"})

# Пример маршрута для будущего использования
@app.route('/api/v1/status', methods=['GET'])
def status():
    return jsonify({
        "status": "ok",
        "version": "1.0.0",
        "connections": 0
    })

# Создание нового банковского счета
@app.route('/api/v1/accounts', methods=['POST'])
def create_bank_account():
    data = request.json
    if not data:
        return jsonify({"status": "error", "message": "Не указаны данные для создания счета"}), 400
    
    # Проверка необходимых полей
    if 'client_id' not in data:
        return jsonify({"status": "error", "message": "Не указан идентификатор клиента"}), 400
    
    client_id = data['client_id']
    initial_balance = data.get('initial_balance', 0.0)
    
    response, status_code = bank_service.create_bank_account(client_id, initial_balance)
    return jsonify(response), status_code

# Получение информации о счете
@app.route('/api/v1/accounts/<account_id>', methods=['GET'])
def get_bank_account(account_id):
    response, status_code = bank_service.get_bank_account(account_id)
    return jsonify(response), status_code

# Получение списка счетов клиента
@app.route('/api/v1/accounts', methods=['GET'])
def list_bank_accounts():
    client_id = request.args.get('client_id')
    if not client_id:
        return jsonify({"status": "error", "message": "Не указан идентификатор клиента"}), 400
    
    response, status_code = bank_service.list_bank_accounts(client_id)
    return jsonify(response), status_code

# Создание новой банкноты
@app.route('/api/v1/banknotes', methods=['POST'])
def create_new_banknote():
    data = request.json
    if not data:
        return jsonify({"status": "error", "message": "Не указаны данные для создания банкноты"}), 400
    
    # Проверка необходимых полей
    if 'denomination' not in data:
        return jsonify({"status": "error", "message": "Не указан номинал банкноты"}), 400
    
    denomination = data['denomination']
    
    response, status_code = bank_service.create_new_banknote(denomination)
    return jsonify(response), status_code

# Получение информации о банкноте по ID
@app.route('/api/v1/banknotes/<int:banknote_id>', methods=['GET'])
def get_banknote_info(banknote_id):
    response, status_code = bank_service.get_banknote_info(banknote_id)
    return jsonify(response), status_code

# Получение информации о банкноте по UUID
@app.route('/api/v1/banknotes/uuid/<banknote_uuid>', methods=['GET'])
def get_banknote_by_uuid_endpoint(banknote_uuid):
    response, status_code = bank_service.get_banknote_by_uuid_info(banknote_uuid)
    return jsonify(response), status_code

# Обновление статуса банкноты
@app.route('/api/v1/banknotes/<int:banknote_id>/status', methods=['PUT'])
def update_banknote_status_endpoint(banknote_id):
    data = request.json
    if not data:
        return jsonify({"status": "error", "message": "Не указаны данные для обновления статуса"}), 400
    
    # Проверка необходимых полей
    if 'status' not in data:
        return jsonify({"status": "error", "message": "Не указан новый статус банкноты"}), 400
    
    new_status = data['status']
    
    response, status_code = bank_service.update_banknote_status_info(banknote_id, new_status)
    return jsonify(response), status_code

# Получение списка банкнот по статусу
@app.route('/api/v1/banknotes/status/<status>', methods=['GET'])
def list_banknotes_by_status(status):
    response, status_code = bank_service.list_banknotes_by_status_info(status)
    return jsonify(response), status_code

# Получение списка всех банкнот
@app.route('/api/v1/banknotes', methods=['GET'])
def list_all_banknotes():
    response, status_code = bank_service.list_all_banknotes_info()
    return jsonify(response), status_code

# Обработчик ошибок для 404
@app.errorhandler(404)
def not_found(e):
    return jsonify({"status": "error", "message": "Ресурс не найден"}), 404

# Обработчик ошибок для 500
@app.errorhandler(500)
def server_error(e):
    logger.error(f"Внутренняя ошибка сервера: {str(e)}")
    return jsonify({"status": "error", "message": "Внутренняя ошибка сервера"}), 500

if __name__ == '__main__':
    # Инициализация базы данных
    bank_service.initialize_database()
    
    # Запуск сервера на всех интерфейсах (0.0.0.0) для доступа из локальной сети
    app.run(host='0.0.0.0', port=8080, debug=True)
    # В производственной среде рекомендуется отключить debug=True
