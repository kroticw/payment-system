from flask import Flask, request, jsonify
import logging
import os
from service import *

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

@app.route('/api/v1/create-client', methods=['POST'])
def create_client():
    data = request.json
    if not data:
        return jsonify({"status": "error", "message": "Нет данных"}), 400

    if 'start_money' not in data:
        return jsonify({
            "status": "error",
            "message": "start_money is required"
        }), 400

    client =  bank_service.create_client(data['start_money'])

    return jsonify({
        "status": "ok",
        "id": client['id'],
        "n": pm.n,
        "divisors": pm.divisors,
    })


# Подпись новой затенённой банкноты
@app.route('/api/v1/banknotes', methods=['POST'])
def create_new_banknote():
    data = request.json
    if not data:
        return jsonify({"status": "error", "message": "Не указаны данные для подписи банкноты"}), 400
    
    # Проверка необходимых полей
    if 'banknote' not in data:
        return jsonify({"status": "error", "message": "Нет банкноты"}), 400
    
    blinded_banknote = data['banknote']

    result_verify = bank_service.verify_blinded_banknote(blinded_banknote)
    if result_verify:
        signed_banknote = bank_service.sign_banknote(blinded_banknote)
        return jsonify({"status": "ok", "signed_banknote": signed_banknote}), 200
    else:
        return jsonify({"status": "false", "signed_banknote": 0, "message": "Купюра не валидна"}), 200

# Подпись сдачи
@app.route('/api/v1/sign-change', methods=['POST'])
def sign_change():
    data = request.json
    if not data:
        print(f"Ошибка: не данных")
        return jsonify({
            "status": "error",
            "message": "Не указаны данные сдачи"
        }), 400

    # Проверка минимально необходимых полей
    required_fields = ['blinded_change', 'change_exp']
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return jsonify({
            "status": "error",
            "message": f"Отсутствуют обязательные поля: {', '.join(missing_fields)}"
        }), 400


    signed_change_blinded = pm.bank_sign_change(data['blinded_change'], data['change_exp'])
    return jsonify({
        "status": "ok",
        "signed_change_blinded": signed_change_blinded,
    }), 200

# Обработчик ошибок для 404
@app.errorhandler(404)
def not_found(e):
    return jsonify({"status": "error", "message": "Ресурс не найден"}), 404

# Обработчик ошибок для 500
@app.errorhandler(500)
def server_error(e):
    logger.error(f"Внутренняя ошибка сервера: {str(e)}")
    return jsonify({"status": "error", "message": "Внутренняя ошибка сервера"}), 500

@app.errorhandler(403)
def forbidden(e):
    return jsonify({"status": "error", "message": "Нет доступа"}), 403

if __name__ == '__main__':
    # Инициализация базы данных
    bank_service.initialize_database()
    
    # Запуск сервера на всех интерфейсах (0.0.0.0) для доступа из локальной сети
    app.run(host='0.0.0.0', port=8080, debug=True)
    # В производственной среде рекомендуется отключить debug=True
