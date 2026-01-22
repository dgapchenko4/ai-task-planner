import requests
import json

BASE_URL = "http://localhost:8000"

def test_api():
    print("Тестирование API...\n")
    
    # 1. Проверка корневого эндпоинта
    print("1. Проверка корневого эндпоинта:")
    response = requests.get(f"{BASE_URL}/")
    print(f"   Статус: {response.status_code}")
    print(f"   Ответ: {json.dumps(response.json(), indent=2)}")
    
    # 2. Получение списка задач (должен быть пустым)
    print("\n2. Получение списка задач:")
    response = requests.get(f"{BASE_URL}/tasks?skip=0&limit=10")
    print(f"   Статус: {response.status_code}")
    print(f"   Ответ: {json.dumps(response.json(), indent=2)}")
    
    # 3. Создание новой задачи
    print("\n3. Создание новой задачи:")
    response = requests.post(
        f"{BASE_URL}/tasks",
        params={"title": "Тестовая задача", "description": "Описание тестовой задачи"}
    )
    print(f"   Статус: {response.status_code}")
    print(f"   Ответ: {json.dumps(response.json(), indent=2)}")
    
    # 4. Получение созданной задачи
    print("\n4. Получение списка задач после создания:")
    response = requests.get(f"{BASE_URL}/tasks")
    print(f"   Статус: {response.status_code}")
    data = response.json()
    print(f"   Всего задач: {data['total']}")
    
    if data['tasks']:
        task_id = data['tasks'][0]['id']
        print(f"   ID первой задачи: {task_id}")
        
        # 5. Получение задачи по ID
        print(f"\n5. Получение задачи с ID {task_id}:")
        response = requests.get(f"{BASE_URL}/tasks/{task_id}")
        print(f"   Статус: {response.status_code}")
        print(f"   Ответ: {json.dumps(response.json(), indent=2)}")
    
    print("\n✅ Тестирование завершено!")

if __name__ == "__main__":
    test_api()