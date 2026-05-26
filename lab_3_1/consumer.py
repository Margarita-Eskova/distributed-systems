import pika
import grpc
import json
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'grpc_part'))

import task_service_pb2
import task_service_pb2_grpc

def process_via_grpc(task_type, data):
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = task_service_pb2_grpc.TaskServiceStub(channel)
        
        if task_type == 'schedule':
            request = task_service_pb2.TaskRequest(
                task_name=data['task_name'],
                scheduled_time=data['scheduled_time']
            )
            response = stub.ScheduleTask(request)
            return response.message
        
        elif task_type == 'complexity':
            request = task_service_pb2.TextRequest(text=data['text'])
            response = stub.AnalyzeTextComplexity(request)
            return (f"Сложность: {response.complexity_level}, "
                   f"Индекс: {response.readability_index:.2f}, "
                   f"Слов: {response.word_count}, "
                   f"Предложений: {response.sentence_count}")
        
        elif task_type == 'keyword':
            request = task_service_pb2.KeywordRequest(
                text=data['text'],
                keyword=data['keyword']
            )
            response = stub.CountKeywordOccurrences(request)
            return f"Вхождений слова '{data['keyword']}': {response.occurrences}"
        
        else:
            return f"Неизвестный тип: {task_type}"

def main():
    credentials = pika.PlainCredentials('user', 'password')
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='localhost', credentials=credentials)
    )
    channel = connection.channel()
    
    channel.queue_declare(queue='task_queue', durable=True)
    
    print('[*] Consumer ожидает сообщений. Нажмите CTRL+C для выхода')
    
    def callback(ch, method, properties, body):
        try:
            message = json.loads(body.decode())
            task_type = message['task_type']
            data = message['data']
            
            print(f"\n[Consumer] Получено: тип={task_type}, данные={data}")
            result = process_via_grpc(task_type, data)
            print(f"[Consumer] Результат: {result}")
        except Exception as e:
            print(f"[Consumer] Ошибка: {e}")
        finally:
            ch.basic_ack(delivery_tag=method.delivery_tag)
    
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue='task_queue', on_message_callback=callback)
    channel.start_consuming()

if __name__ == '__main__':
    main()
