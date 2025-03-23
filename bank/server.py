from flask import Flask, request, jsonify
import logging

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

# Здесь можно добавить дополнительные маршруты для различных операций
# Например:
# @app.route('/api/v1/transaction', methods=['POST'])
# def create_transaction():
#     data = request.json
#     # Обработка транзакции
#     return jsonify({"status": "success", "transaction_id": "..."})

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
    # Запуск сервера на всех интерфейсах (0.0.0.0) для доступа из локальной сети
    app.run(host='0.0.0.0', port=8080, debug=True)
    # В производственной среде рекомендуется отключить debug=True
