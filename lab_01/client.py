import grpc
import auth_service_pb2
import auth_service_pb2_grpc

def run():
    channel = grpc.insecure_channel('localhost:50051')
    stub = auth_service_pb2_grpc.AuthServiceStub(channel)
    
    print("\n" + "="*50)
    print("ТЕСТ 1: Успешный вход (alice / secret123)")
    print("="*50)
    
    response = stub.Login(auth_service_pb2.CredentialsRequest(
        username="alice",
        password="secret123"
    ))
    print(f"Успех: {response.success}")
    print(f"Сообщение: {response.message}")
    print(f"Токен: {response.token[:30]}..." if response.token else "Токен не получен")
    
    print("\n" + "="*50)
    print("ТЕСТ 2: Неверный пароль (alice / wrong)")
    print("="*50)
    
    response = stub.Login(auth_service_pb2.CredentialsRequest(
        username="alice",
        password="wrong"
    ))
    print(f"Успех: {response.success}")
    print(f"Сообщение: {response.message}")
    
    print("\n" + "="*50)
    print("ТЕСТ 3: Несуществующий пользователь (eve / pass)")
    print("="*50)
    
    response = stub.Login(auth_service_pb2.CredentialsRequest(
        username="eve",
        password="pass"
    ))
    print(f"Успех: {response.success}")
    print(f"Сообщение: {response.message}")

if __name__ == "__main__":
    run()
