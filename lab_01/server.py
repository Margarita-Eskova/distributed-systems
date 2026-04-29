import grpc
from concurrent import futures
import time
import hashlib
import auth_service_pb2
import auth_service_pb2_grpc

USER_DB = {
    "alice": "secret123",
    "bob": "qwerty",
    "admin": "admin123"
}

def generate_token(username):
    token_string = f"{username}_{int(time.time())}_secure_hash"
    return hashlib.sha256(token_string.encode()).hexdigest()

class AuthServiceServicer(auth_service_pb2_grpc.AuthServiceServicer):
    
    def Login(self, request, context):
        print(f"[СЕРВЕР] Запрос от: {request.username}")
        
        if request.username not in USER_DB:
            return auth_service_pb2.AuthResponse(
                success=False,
                token="",
                message=f"Пользователь '{request.username}' не найден"
            )
        
        if USER_DB[request.username] != request.password:
            return auth_service_pb2.AuthResponse(
                success=False,
                token="",
                message="Неверный пароль"
            )
        
        token = generate_token(request.username)
        print(f"[СЕРВЕР] Успешный вход для {request.username}")
        
        return auth_service_pb2.AuthResponse(
            success=True,
            token=token,
            message=f"Добро пожаловать, {request.username}!"
        )

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    auth_service_pb2_grpc.add_AuthServiceServicer_to_server(
        AuthServiceServicer(), 
        server
    )
    server.add_insecure_port('[::]:50051')
    server.start()
    print("[СЕРВЕР] Запущен на порту 50051...")
    server.wait_for_termination()

if __name__ == "__main__":
    serve()
