import pika
import json
import sys

credentials = pika.PlainCredentials('user', 'password')
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost', credentials=credentials)
)
channel = connection.channel()

channel.queue_declare(queue='task_queue', durable=True)

if len(sys.argv) < 3:
    print("Использование: python producer.py <task_type> <json_data>")
    print("task_type: schedule, complexity, keyword")
    sys.exit(1)

task_type = sys.argv[1]
json_data = sys.argv[2]

message = {
    'task_type': task_type,
    'data': json.loads(json_data)
}

channel.basic_publish(
    exchange='',
    routing_key='task_queue',
    body=json.dumps(message),
    properties=pika.BasicProperties(delivery_mode=2)
)

print(f"[Producer] Отправлено: {message}")
connection.close()
