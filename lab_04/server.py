import sys
import time
import json
from collections import deque
from threading import Lock

from flask import Flask, request, jsonify
from cryptography.fernet import Fernet
import ssl

app = Flask(__name__)

# ========== Метрики для варианта 9 ==========
request_times = deque(maxlen=100)  # храним времена последних 100 запросов
latencies = deque(maxlen=100)      # храним задержки последних 100 запросов
metrics_lock = Lock()

# Загружаем ключ Fernet
with open("encryption_key.txt", "rb") as f:
    fernet_key = f.read()
cipher = Fernet(fernet_key)

# Загружаем сертификаты для mTLS
SERVER_CERT = "certs/server_cert.pem"
SERVER_KEY = "certs/server_key.pem"
CA_CERT = "certs/ca_cert.pem"

def record_metric(duration):
    """Записывает метрики для варианта 9"""
    with metrics_lock:
        request_times.append(time.time())
        latencies.append(duration)

def get_current_rps():
    """Вычисляет RPS за последнюю секунду"""
    with metrics_lock:
        if not request_times:
            return 0.0
        now = time.time()
        recent = [t for t in request_times if now - t <= 1.0]
        return len(recent)

def get_average_latency():
    """Средняя задержка за последние запросы"""
    with metrics_lock:
        if not latencies:
            return 0.0
        return sum(latencies) / len(latencies)

@app.route('/data', methods=['POST'])
def handle_data():
    start_time = time.time()
    
    encrypted_data = request.get_data()
    
    try:
        decrypted = cipher.decrypt(encrypted_data)
        message = decrypted.decode('utf-8')
        
        response = {
            "status": "ok",
            "server_port": sys.argv[1] if len(sys.argv) > 1 else "unknown",
            "received": message,
            "processed": f"Echo: {message}"
        }
        
        duration = time.time() - start_time
        record_metric(duration)
        
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/metrics', methods=['GET'])
def get_metrics():
    """Эндпоинт для сбора метрик координатором (Вариант 9)"""
    return jsonify({
        "rps": get_current_rps(),
        "avg_latency_ms": get_average_latency() * 1000,
        "total_requests_in_history": len(request_times)
    })

if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5001
    
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(SERVER_CERT, SERVER_KEY)
    context.load_verify_locations(CA_CERT)
    context.verify_mode = ssl.CERT_REQUIRED
    
    app.run(host='0.0.0.0', port=port, ssl_context=context, debug=False)
