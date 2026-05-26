import grpc
from concurrent import futures
import task_service_pb2
import task_service_pb2_grpc
import re

class TaskServiceServicer(task_service_pb2_grpc.TaskServiceServicer):
    
    # Задание 1: Планирование задач
    def ScheduleTask(self, request, context):
        message = f"Задача '{request.task_name}' запланирована на {request.scheduled_time}"
        print(f"[gRPC] {message}")
        return task_service_pb2.TaskResponse(message=message)
    
    # Задание 2: Анализ сложности текста
    def AnalyzeTextComplexity(self, request, context):
        words = re.findall(r'\b\w+\b', request.text.lower())
        sentences = [s for s in re.split(r'[.!?]+', request.text) if s.strip()]
        
        word_count = len(words)
        sentence_count = len(sentences) if sentences else 1
        readability_index = word_count / sentence_count
        
        if readability_index < 10:
            complexity_level = "Легкий"
        elif readability_index < 20:
            complexity_level = "Средний"
        else:
            complexity_level = "Сложный"
        
        print(f"[gRPC] слов={word_count}, предл={sentence_count}, индекс={readability_index:.2f}, уровень={complexity_level}")
        
        return task_service_pb2.ComplexityResponse(
            complexity_level=complexity_level,
            readability_index=readability_index,
            word_count=word_count,
            sentence_count=sentence_count
        )
    
    # Задание 3: Поиск по ключевым словам
    def CountKeywordOccurrences(self, request, context):
        words = re.findall(r'\b\w+\b', request.text.lower())
        occurrences = words.count(request.keyword.lower())
        print(f"[gRPC] ключевое слово='{request.keyword}', вхождений={occurrences}")
        return task_service_pb2.KeywordResponse(occurrences=occurrences)


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    task_service_pb2_grpc.add_TaskServiceServicer_to_server(TaskServiceServicer(), server)
    server.add_insecure_port('[::]:50051')
    print("[gRPC Server] Запущен на порту 50051")
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
