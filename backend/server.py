# backend/server.py (ОБНОВЛЕННАЯ ВЕРСИЯ)
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import time
from datetime import datetime
from ai_client import ai_client
from prompts import TaskPrompts
import re

class TaskPlannerAPI(BaseHTTPRequestHandler):
    """Обработчик API запросов с реальным AI"""
    
    def send_json_response(self, data, status=200):
        """Отправка JSON ответа"""
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))
    
    def do_OPTIONS(self):
        """Обработка CORS"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_GET(self):
        """Обработка GET запросов"""
        if self.path == '/':
            self.send_json_response({
                "message": "AI Task Planner API",
                "version": "2.0",
                "ai_enabled": not ai_client.is_demo,
                "status": "running"
            })
        
        elif self.path == '/api/ai/status':
            self.send_json_response({
                "status": "active",
                "ai_provider": "Yandex GPT" if not ai_client.is_demo else "Demo Mode",
                "is_real_ai": not ai_client.is_demo,
                "timestamp": datetime.now().isoformat()
            })
        
        else:
            self.send_json_response({"error": "Endpoint not found"}, 404)
    
    def do_POST(self):
        """Обработка POST запросов"""
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        try:
            data = json.loads(post_data.decode('utf-8')) if post_data else {}
        except:
            data = {}
        
        # Обработка AI
        if self.path == '/api/ai/process':
            text = data.get('text', '')
            
            if not text:
                self.send_json_response({"error": "Текст не может быть пустым"}, 400)
                return
            
            # Получаем промпт для извлечения задачи
            prompt = TaskPrompts.extract_task_prompt(text)
            
            # Отправляем запрос к Yandex GPT
            response = ai_client.complete(prompt)
            
            if response['success']:
                try:
                    # Парсим JSON ответ от AI
                    ai_text = response['text']
                    
                    # Ищем JSON в ответе
                    json_match = re.search(r'\{.*\}', ai_text, re.DOTALL)
                    if json_match:
                        task_data = json.loads(json_match.group())
                    else:
                        # Если JSON не найден, создаем базовую структуру
                        task_data = {
                            "title": text[:50],
                            "description": text if len(text) > 50 else None,
                            "due_date": None,
                            "priority": "medium",
                            "tags": ["общее"]
                        }
                    
                    self.send_json_response({
                        "success": True,
                        "result": task_data,
                        "is_real_ai": not ai_client.is_demo,
                        "response_time": response.get('response_time', 0)
                    })
                    
                except json.JSONDecodeError as e:
                    self.send_json_response({
                        "success": False,
                        "error": f"Ошибка парсинга JSON: {str(e)}",
                        "raw_response": response['text'][:200]
                    }, 500)
            else:
                self.send_json_response({
                    "success": False,
                    "error": response.get('error', 'Ошибка AI'),
                    "is_demo": True
                }, 500)
        
        # Чат с AI
        elif self.path == '/api/ai/chat':
            message = data.get('message', '')
            history = data.get('history', [])
            
            if not message:
                self.send_json_response({"error": "Сообщение не может быть пустым"}, 400)
                return
            
            # Формируем контекст из истории
            context = "\n".join([f"{h['role']}: {h['text']}" for h in history[-5:]])
            prompt = TaskPrompts.chat_prompt(message, context)
            
            response = ai_client.complete(prompt)
            
            if response['success']:
                self.send_json_response({
                    "success": True,
                    "response": response['text'],
                    "is_real_ai": not ai_client.is_demo
                })
            else:
                self.send_json_response({
                    "success": False,
                    "response": "Извините, произошла ошибка. Попробуйте еще раз.",
                    "error": response.get('error')
                }, 500)
        
        # Регистрация (демо)
        elif self.path == '/api/auth/register':
            username = data.get('username', '')
            email = data.get('email', '')
            
            self.send_json_response({
                "success": True,
                "message": "Регистрация успешна",
                "user": {
                    "id": f"user_{int(time.time())}",
                    "username": username,
                    "email": email
                },
                "token": f"token_{int(time.time())}"
            })
        
        # Логин (демо)
        elif self.path == '/api/auth/login':
            email = data.get('email', '')
            
            self.send_json_response({
                "success": True,
                "message": "Вход выполнен",
                "user": {
                    "id": "demo_user",
                    "username": email.split('@')[0],
                    "email": email
                },
                "token": "demo_token"
            })
        
        else:
            self.send_json_response({"error": "Endpoint not found"}, 404)
    
    def log_message(self, format, *args):
        """Логирование запросов"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        print(f"[{timestamp}] {format % args}")

def run_server(port=5000):
    """Запуск сервера"""
    server_address = ('0.0.0.0', port)
    httpd = HTTPServer(server_address, TaskPlannerAPI)
    
    print("=" * 50)
    print("🚀 AI Task Planner - Сервер с реальным AI")
    print("=" * 50)
    print(f"📡 Сервер запущен на http://localhost:{port}")
    print(f"🤖 AI режим: {'РЕАЛЬНЫЙ Yandex GPT' if not ai_client.is_demo else 'ДЕМО (имитация)'}")
    print(f"🔧 Статус API: http://localhost:{port}/api/ai/status")
    print("=" * 50)
    print("Нажмите Ctrl+C для остановки")
    print("=" * 50)
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Сервер остановлен")
        httpd.server_close()

if __name__ == '__main__':
    run_server()