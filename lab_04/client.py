import requests
import json
from cryptography.fernet import Fernet

# Загружаем ключ Fernet
with open("encryption_key.txt", "rb") as f:
    fernet_key = f.read()
cipher = Fernet(fernet_key)

# Пути к сертификатам для mTLS
CA_CERT = "certs/ca_cert.pem"
CLIENT_CERT = "certs/client_cert.pem"
CLIENT_KEY = "certs/client_key.pem"

COORDINATOR_URL = "https://localhost:8000/data"

def send_message(message):
    """Шифрует сообщение и отправляет координатору"""
    encrypted = cipher.encrypt(message.encode('utf-8'))
    
    resp = requests.post(
        COORDINATOR_URL,
        data=encrypted,
        verify=CA_CERT,
        cert=(CLIENT_CERT, CLIENT_KEY),
        timeout=10
    )
    
    return resp

def get_metrics():
    """Получает агрегированные метрики от координатора (Вариант 9)"""
    metrics_url = "https://localhost:8000/metrics"
    resp = requests.get(
        metrics_url,
        verify=CA_CERT,
        cert=(CLIENT_CERT, CLIENT_KEY),
        timeout=10
    )
    return resp.json()

if __name__ == '__main__':
    print("=== Клиент с мониторингом (Вариант 9) ===")
    
    while True:
        print("\nВыберите действие:")
        print("1. Отправить сообщение")
        print("2. Посмотреть метрики производительности")
        print("3. Выйти")
        
        choice = input("Ваш выбор: ")
        
        if choice == "1":
            msg = input("Введите сообщение: ")
            try:
                resp = send_message(msg)
                print(f"Ответ: {resp.json()}")
            except Exception as e:
                print(f"Ошибка: {e}")
                
        elif choice == "2":
            try:
                metrics = get_metrics()
                print("\n=== Агрегированные метрики ===")
                agg = metrics.get("aggregated", {})
                print(f"Общий RPS: {agg.get('total_rps', 0)}")
                print(f"Средняя задержка: {agg.get('average_latency_ms', 0):.2f} мс")
                print(f"Активных серверов: {agg.get('active_servers_count', 0)}")
                print("\nДетали по серверам:")
                for s in metrics.get("servers", []):
                    if s.get("active", True):
                        print(f"  Порт {s.get('server_port')}: RPS={s.get('rps', 0)}, "
                              f"latency={s.get('avg_latency_ms', 0):.2f} мс")
                    else:
                        print(f"  Порт {s.get('server_port')}: НЕАКТИВЕН")
            except Exception as e:
                print(f"Ошибка получения метрик: {e}")
                
        elif choice == "3":
            print("До свидания!")
            break
        else:
            print("Неверный выбор")
