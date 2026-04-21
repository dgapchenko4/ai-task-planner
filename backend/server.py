# backend/server.py
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import re
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

class TaskPlannerAPI(BaseHTTPRequestHandler):
    """Обработчик API запросов"""
    
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
        """Обработка CORS preflight запросов"""
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
                "status": "running"
            })
        elif self.path == '/api/ai/status':
            self.send_json_response({
                "status": "active",
                "ai_provider": "Built-in Parser",
                "is_real_ai": False,
                "timestamp": datetime.now().isoformat()
            })
        else:
            self.send_json_response({"error": "Endpoint not found"}, 404)
    
    def do_POST(self):
        """Обработка POST запросов"""
        
        # Получаем длину и читаем данные
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        try:
            data = json.loads(post_data.decode('utf-8'))
        except json.JSONDecodeError:
            self.send_json_response({"error": "Invalid JSON"}, 400)
            return
        
        # Обработка AI задачи
        if self.path == '/api/ai/process':
            text = data.get('text', '')
            
            if not text:
                self.send_json_response({"error": "Текст не может быть пустым"}, 400)
                return
            
            print(f"📝 Получен текст: {text[:100]}...")
            
            # Парсим задачу
            result = self.parse_task(text)
            
            self.send_json_response({
                "success": True,
                "result": result,
                "is_real_ai": False
            })
        
        # Чат с AI (простой ответ)
        elif self.path == '/api/ai/chat':
            message = data.get('message', '')
            
            if not message:
                self.send_json_response({"error": "Сообщение не может быть пустым"}, 400)
                return
            
            response = self.chat_response(message)
            
            self.send_json_response({
                "success": True,
                "response": response,
                "is_real_ai": False
            })
        
        # Аутентификация (демо)
        elif self.path == '/api/auth/register':
            username = data.get('username', '')
            email = data.get('email', '')
            
            self.send_json_response({
                "success": True,
                "message": "Регистрация успешна",
                "user": {
                    "id": f"user_{int(datetime.now().timestamp())}",
                    "username": username,
                    "email": email
                },
                "token": f"token_{int(datetime.now().timestamp())}"
            })
        
        elif self.path == '/api/auth/login':
            email = data.get('email', '')
            
            self.send_json_response({
                "success": True,
                "message": "Вход выполнен",
                "user": {
                    "id": "demo_user",
                    "username": email.split('@')[0] if '@' in email else email,
                    "email": email
                },
                "token": "demo_token"
            })
        
        else:
            self.send_json_response({"error": "Endpoint not found"}, 404)
    
    def parse_task(self, text):
        """Парсинг задачи из текста"""
        
        now = datetime.now()
        text_lower = text.lower()
        
        # ===== ПАРСИНГ ДАТЫ =====
        due_date = None
        due_date_display = None
        
        # Словарь дней недели
        weekdays = {
            'понедельник': 0, 'понедельника': 0,
            'вторник': 1, 'вторника': 1,
            'среду': 2, 'среды': 2, 'среда': 2,
            'четверг': 3, 'четверга': 3,
            'пятницу': 4, 'пятницы': 4,
            'субботу': 5, 'субботы': 5,
            'воскресенье': 6, 'воскресенья': 6
        }
        
        # Проверяем "сегодня"
        if 'сегодня' in text_lower:
            due_date = now
        # Проверяем "завтра"
        elif 'завтра' in text_lower:
            due_date = now + timedelta(days=1)
        # Проверяем "послезавтра"
        elif 'послезавтра' in text_lower:
            due_date = now + timedelta(days=2)
        # Проверяем дни недели
        else:
            for day_name, day_num in weekdays.items():
                if day_name in text_lower:
                    days_ahead = (day_num - now.weekday() + 7) % 7
                    if days_ahead == 0:
                        days_ahead = 7
                    due_date = now + timedelta(days=days_ahead)
                    break
        
        # Парсинг времени
        if due_date:
            # Ищем время в формате "в 15:00" или "в 15 часов"
            time_patterns = [
                r'в (\d{1,2}):(\d{2})',
                r'в (\d{1,2}) часов? (\d{1,2}) минут?',
                r'в (\d{1,2}) часов?',
                r'к (\d{1,2}) часам?',
                r'(\d{1,2}):(\d{2})'
            ]
            
            hour = 12
            minute = 0
            time_found = False
            
            for pattern in time_patterns:
                match = re.search(pattern, text_lower)
                if match:
                    if len(match.groups()) == 2:
                        hour = int(match.group(1))
                        minute = int(match.group(2))
                    else:
                        hour = int(match.group(1))
                    time_found = True
                    break
            
            # Корректировка для вечера/утра
            if 'вечер' in text_lower and hour < 12:
                hour += 12
            elif 'утра' in text_lower and hour == 12:
                hour = 0
            elif 'дня' in text_lower and hour < 12:
                hour += 12
            
            due_date = due_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
            
            # Форматируем для отображения
            if due_date.date() == now.date():
                due_date_display = f"Сегодня в {due_date.strftime('%H:%M')}"
            elif due_date.date() == (now + timedelta(days=1)).date():
                due_date_display = f"Завтра в {due_date.strftime('%H:%M')}"
            else:
                due_date_display = due_date.strftime('%d.%m.%Y в %H:%M')
        
        # ===== ОПРЕДЕЛЕНИЕ ПРИОРИТЕТА =====
        priority = 'medium'
        if any(word in text_lower for word in ['срочн', 'важн', 'критичн', 'срочно', 'важно']):
            priority = 'high'
        elif any(word in text_lower for word in ['не срочн', 'потом', 'когда будет время']):
            priority = 'low'
        
        # ===== ОПРЕДЕЛЕНИЕ ТЕГОВ =====
        tags = []
        tag_keywords = {
            'работа': ['работ', 'офис', 'совещание', 'отчет', 'проект', 'встреч', 'клиент'],
            'учеба': ['учеб', 'диплом', 'курс', 'экзамен', 'лекц', 'занят', 'студент'],
            'личное': ['личн', 'дом', 'семья', 'друз', 'хобби'],
            'покупки': ['куп', 'магазин', 'продукт', 'шопинг'],
            'здоровье': ['здоров', 'врач', 'спорт', 'трен', 'лекарств']
        }
        
        for tag, keywords in tag_keywords.items():
            if any(kw in text_lower for kw in keywords):
                tags.append(tag)
        
        if not tags:
            tags = ['задача']
        
        # ===== ИЗВЛЕЧЕНИЕ ЗАГОЛОВКА =====
        # Убираем слова-указатели дат для чистого заголовка
        title_clean = text
        remove_patterns = [
            r'сегодня', r'завтра', r'послезавтра',
            r'в \d{1,2}:\d{2}', r'в \d{1,2} часов?',
            r'в \d{1,2} часов? \d{1,2} минут?',
            r'понедельник\w*', r'вторник\w*', r'сред[уы]', r'четверг\w*',
            r'пятниц[уы]', r'суббот[уы]', r'воскресень[ея]'
        ]
        
        for pattern in remove_patterns:
            title_clean = re.sub(pattern, '', title_clean, flags=re.IGNORECASE)
        
        # Убираем лишние пробелы и запятые
        title_clean = re.sub(r'\s+', ' ', title_clean).strip()
        title_clean = re.sub(r'^[,\s]+|[,\s]+$', '', title_clean)
        
        if not title_clean:
            title_clean = text[:50]
        
        if len(title_clean) > 60:
            title = title_clean[:57] + '...'
        else:
            title = title_clean
        
        # Делаем первую букву заглавной
        if title:
            title = title[0].upper() + title[1:]
        
        # ===== ФОРМИРУЕМ РЕЗУЛЬТАТ =====
        result = {
            "title": title,
            "description": None,
            "due_date": due_date.strftime('%Y-%m-%d %H:%M:%S') if due_date else None,
            "due_date_display": due_date_display,
            "priority": priority,
            "tags": tags[:3]
        }
        
        print(f"✅ Результат: {result}")
        return result
    
    def chat_response(self, message):
        """Простой ответ для чата"""
        message_lower = message.lower()
        
        if 'привет' in message_lower:
            return "Привет! 👋 Я AI ассистент. Я помогаю создавать задачи из текста. Просто опишите, что нужно сделать!"
        elif 'задача' in message_lower or 'создай' in message_lower:
            return "Чтобы создать задачу, просто напишите её в главном поле ввода. Например: 'Завтра в 15:00 важное совещание'"
        elif 'помощ' in message_lower:
            return "Я могу:\n• Создавать задачи из текста\n• Определять даты и время\n• Ставить приоритеты\n• Категоризировать задачи"
        elif 'спасиб' in message_lower:
            return "Всегда рад помочь! 😊 Удачи с задачами!"
        else:
            return f"Понял! Я помогу с задачей: '{message[:50]}...' Напишите её в главное поле ввода, и я создам структурированную задачу."
    
    def log_message(self, format, *args):
        """Логирование запросов"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        print(f"[{timestamp}] {format % args}")

def run_server(port=5000):
    """Запуск сервера"""
    server_address = ('0.0.0.0', port)
    httpd = HTTPServer(server_address, TaskPlannerAPI)
    
    print("=" * 50)
    print("🚀 AI Task Planner - Сервер")
    print("=" * 50)
    print(f"📡 Сервер запущен на http://localhost:{port}")
    print(f"🔧 Статус API: http://localhost:{port}/api/ai/status")
    print(f"📝 POST эндпоинт: http://localhost:{port}/api/ai/process")
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