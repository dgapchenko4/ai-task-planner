from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime, timedelta
import os
import re
import json
import requests
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

# ============================================================================
# КЛАСС ДЛЯ РАБОТЫ С YANDEX GPT
# ============================================================================
class YandexGPT:
    def __init__(self):
        self.api_key = os.getenv('YANDEX_API_KEY')
        self.folder_id = os.getenv('YANDEX_FOLDER_ID')
        self.url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
        
        if not self.api_key or not self.folder_id:
            print("⚠️ API ключи не найдены! Используем встроенный парсер")
            self.is_ready = False
        else:
            print("✅ Yandex GPT готов к работе")
            self.is_ready = True
    
    def analyze_task(self, user_text):
        if not self.is_ready:
            return self._local_parser(user_text)
        
        prompt = self._build_prompt(user_text)
        ai_response = self._call_yandex_gpt(prompt)
        
        if ai_response is None:
            return self._local_parser(user_text)
        
        cleaned_response = self._clean_json_response(ai_response)
        try:
            return json.loads(cleaned_response)
        except:
            return self._local_parser(user_text)
    
    def _build_prompt(self, user_text):
        today = datetime.now().strftime('%Y-%m-%d')
        tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        
        return f"""Ты - AI ассистент в планировщике задач. Сегодня {today}.

Входной текст: "{user_text}"

Верни ТОЛЬКО JSON в формате:
{{"title": "название", "due_date": "ГГГГ-ММ-ДД ЧЧ:ММ:СС или null", "priority": "high/medium/low", "tags": ["тег1", "тег2"]}}

Правила:
- "сегодня" → {today}
- "завтра" → {tomorrow}
- "срочно", "важно" → priority = "high"

Пример: "Завтра важная встреча" → {{"title": "Важная встреча", "due_date": "{tomorrow} 12:00:00", "priority": "high", "tags": ["работа"]}}"""
    
    def _call_yandex_gpt(self, prompt):
        headers = {"Authorization": f"Api-Key {self.api_key}", "Content-Type": "application/json"}
        body = {
            "modelUri": f"gpt://{self.folder_id}/yandexgpt-lite",
            "completionOptions": {"stream": False, "temperature": 0.1, "maxTokens": 500},
            "messages": [{"role": "user", "text": prompt}]
        }
        try:
            response = requests.post(self.url, headers=headers, json=body, timeout=30)
            if response.status_code == 200:
                return response.json()['result']['alternatives'][0]['message']['text']
        except:
            pass
        return None
    
    def _clean_json_response(self, raw_text):
        match = re.search(r'\{.*\}', raw_text, re.DOTALL)
        return match.group(0) if match else raw_text
    
    def _local_parser(self, text):
        print("🎭 Используем встроенный парсер")
        text_lower = text.lower()
        
        due_date = None
        due_date_display = None
        
        if 'завтра' in text_lower:
            due_date = datetime.now() + timedelta(days=1)
            due_date = due_date.replace(hour=12, minute=0, second=0)
            due_date_display = "Завтра в 12:00"
        elif 'сегодня' in text_lower:
            due_date = datetime.now().replace(hour=12, minute=0, second=0)
            due_date_display = "Сегодня в 12:00"
        
        due_date_str = due_date.strftime('%Y-%m-%d %H:%M:%S') if due_date else None
        
        priority = 'high' if any(w in text_lower for w in ['сроч', 'важн']) else 'medium'
        
        tags = ['задача']
        if 'работ' in text_lower:
            tags = ['работа']
        elif 'куп' in text_lower:
            tags = ['покупки']
        
        title = text[:50].capitalize()
        
        return {
            "title": title,
            "due_date": due_date_str,
            "due_date_display": due_date_display if due_date else "Без срока",
            "priority": priority,
            "tags": tags
        }

gpt = YandexGPT()

# ============================================================================
# API ЭНДПОИНТЫ
# ============================================================================

@app.route('/api/ai/status', methods=['GET'])
def ai_status():
    return jsonify({
        "status": "active",
        "is_real_ai": gpt.is_ready,
        "time": datetime.now().strftime('%H:%M:%S')
    })

@app.route('/api/ai/process', methods=['POST', 'OPTIONS'])
def process_task():
    if request.method == 'OPTIONS':
        return '', 200
    
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400
    
    user_text = data.get('text', '')
    if not user_text:
        return jsonify({"error": "Текст не может быть пустым"}), 400
    
    print(f"📝 Получен текст: {user_text}")
    result = gpt.analyze_task(user_text)
    print(f"✅ Результат: {result}")
    
    return jsonify({
        "success": True,
        "task": {
            "id": int(datetime.now().timestamp() * 1000),
            "title": result.get('title', user_text[:50]),
            "due_date": result.get('due_date'),
            "due_date_display": result.get('due_date_display', 'Без срока'),
            "priority": result.get('priority', 'medium'),
            "tags": result.get('tags', ['задача']),
            "completed": False
        },
        "is_real_ai": gpt.is_ready
    })

# ============================================================================
# ЗАПУСК
# ============================================================================
if __name__ == '__main__':
    print("=" * 50)
    print("🚀 AI TASK PLANNER - СЕРВЕР ЗАПУЩЕН")
    print("=" * 50)
    print("📡 http://localhost:5000")
    print("🔍 GET  /api/ai/status")
    print("📝 POST /api/ai/process")
    print("=" * 50)
    print(f"🤖 Режим: {'Yandex GPT' if gpt.is_ready else 'Встроенный парсер'}")
    print("=" * 50)
    app.run(debug=True, host='0.0.0.0', port=5000)