# backend/ai_client.py
import requests
import json
import time
import re
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import os
from dotenv import load_dotenv

load_dotenv()

class YandexGPTClient:
    """Клиент для работы с Yandex GPT API"""
    
    def __init__(self):
        self.api_key = os.getenv('YANDEX_API_KEY')
        self.folder_id = os.getenv('YANDEX_FOLDER_ID')
        self.model = os.getenv('AI_MODEL', 'yandexgpt-lite')
        
        if not self.api_key or not self.folder_id or self.api_key == 'ваш_api_ключ_сюда':
            print("⚠️ API ключи не найдены! Работаем в демо-режиме")
            self.is_demo = True
        else:
            self.is_demo = False
            print("✅ Режим реального AI (Yandex GPT)")
        
        self.url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    
    def extract_task_with_ai(self, user_text: str) -> Dict[str, Any]:
        """Извлечение задачи с правильным парсингом дат"""
        
        now = datetime.now()
        today = now.strftime('%Y-%m-%d')
        tomorrow = (now + timedelta(days=1)).strftime('%Y-%m-%d')
        
        prompt = f"""Ты - AI ассистент в планировщике задач. Сегодня {today}.

Входной текст: "{user_text}"

Проанализируй текст и извлеки:
1. Название задачи (кратко, 5-7 слов)
2. ДАТУ и ВРЕМЯ (если указаны)
3. Приоритет (high/medium/low)
4. Теги (2-3 штуки)

ПРАВИЛА ОПРЕДЕЛЕНИЯ ДАТЫ:
- "сегодня" → {today}
- "завтра" → {tomorrow}
- "послезавтра" → {(now + timedelta(days=2)).strftime('%Y-%m-%d')}
- "в понедельник" → найди ближайший понедельник
- "во вторник" → найди ближайший вторник
- "в среду" → найди ближайшую среду
- "в четверг" → найди ближайший четверг
- "в пятницу" → найди ближайшую пятницу
- "в субботу" → найди ближайшую субботу
- "в воскресенье" → найди ближайшее воскресенье

ПРАВИЛА ОПРЕДЕЛЕНИЯ ВРЕМЕНИ:
- "в 15:00" → 15:00:00
- "в 3 часа дня" → 15:00:00
- "в 10 утра" → 10:00:00
- "вечером" → 19:00:00
- "утром" → 09:00:00
- "в обед" → 13:00:00

ПРИМЕРЫ:
Вход: "Завтра в 15:00 важное совещание по диплому"
Ответ: {{"title": "Совещание по диплому", "due_date": "{tomorrow} 15:00:00", "priority": "high", "tags": ["работа", "диплом"]}}

Вход: "Купить продукты"
Ответ: {{"title": "Купить продукты", "due_date": null, "priority": "low", "tags": ["покупки"]}}

Вход: "Срочный отчет сегодня к 18 часам"
Ответ: {{"title": "Срочный отчет", "due_date": "{today} 18:00:00", "priority": "high", "tags": ["работа", "срочно"]}}

Вход: "Встреча в пятницу в 10 утра"
Ответ: {{"title": "Встреча", "due_date": "2024-01-26 10:00:00", "priority": "medium", "tags": ["работа"]}}

Верни ТОЛЬКО JSON, без пояснений, в точном формате:
{{"title": "название", "due_date": "ГГГГ-ММ-ДД ЧЧ:ММ:СС" или null, "priority": "high/medium/low", "tags": ["тег1", "тег2"]}}"""

        response = self._call_yandex_gpt(prompt)
        
        if response['success']:
            try:
                task_data = json.loads(response['text'])
                
                # Проверяем и исправляем дату
                if task_data.get('due_date') and task_data['due_date'] != 'null':
                    # Парсим дату
                    parsed_date = self._parse_date_from_text(task_data['due_date'], user_text)
                    if parsed_date:
                        task_data['due_date'] = parsed_date
                    else:
                        task_data['due_date'] = None
                else:
                    task_data['due_date'] = None
                
                return task_data
            except json.JSONDecodeError:
                return self._manual_parse(user_text)
        else:
            return self._manual_parse(user_text)
    
    def _parse_date_from_text(self, date_str: str, original_text: str) -> Optional[str]:
        """Парсинг даты из текста"""
        
        now = datetime.now()
        text_lower = original_text.lower()
        
        # Словарь дней недели
        weekdays = {
            'понедельник': 0, 'понедельника': 0, 'пнд': 0,
            'вторник': 1, 'вторника': 1, 'втр': 1,
            'среду': 2, 'среды': 2, 'ср': 2, 'среда': 2,
            'четверг': 3, 'четверга': 3, 'чтв': 3, 'чт': 3,
            'пятницу': 4, 'пятницы': 4, 'птн': 4, 'пт': 4,
            'субботу': 5, 'субботы': 5, 'сбт': 5, 'сб': 5,
            'воскресенье': 6, 'воскресенья': 6, 'вск': 6, 'вс': 6
        }
        
        due_date = None
        
        # Проверяем на "сегодня"
        if 'сегодня' in text_lower:
            due_date = now
        
        # Проверяем на "завтра"
        elif 'завтра' in text_lower:
            due_date = now + timedelta(days=1)
        
        # Проверяем на "послезавтра"
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
        
        # Если дата не найдена, возвращаем None
        if not due_date:
            return None
        
        # Парсим время
        time_match = re.search(r'в (\d{1,2})(?::(\d{2}))?\s*(?:часов?)?', text_lower)
        if not time_match:
            time_match = re.search(r'(\d{1,2})(?::(\d{2}))?\s*(?:часов?)?', text_lower)
        
        if time_match:
            hour = int(time_match.group(1))
            minute = int(time_match.group(2)) if time_match.group(2) else 0
            
            # Корректировка для вечернего времени
            if 'вечер' in text_lower and hour < 12:
                hour += 12
            elif 'утра' in text_lower and hour == 12:
                hour = 0
            elif 'дня' in text_lower and hour < 12:
                hour += 12
            
            due_date = due_date.replace(hour=hour, minute=minute, second=0)
        else:
            # Если время не указано, ставим 12:00
            due_date = due_date.replace(hour=12, minute=0, second=0)
        
        return due_date.strftime('%Y-%m-%d %H:%M:%S')
    
    def _manual_parse(self, text: str) -> Dict[str, Any]:
        """Ручной парсинг без AI"""
        
        now = datetime.now()
        text_lower = text.lower()
        
        # Парсинг даты
        due_date = None
        
        if 'сегодня' in text_lower:
            due_date = now
        elif 'завтра' in text_lower:
            due_date = now + timedelta(days=1)
        elif 'послезавтра' in text_lower:
            due_date = now + timedelta(days=2)
        else:
            # Дни недели
            weekdays = {
                'понедельник': 0, 'вторник': 1, 'среду': 2, 'среда': 2,
                'четверг': 3, 'пятницу': 4, 'субботу': 5, 'воскресенье': 6
            }
            for day_name, day_num in weekdays.items():
                if day_name in text_lower:
                    days_ahead = (day_num - now.weekday() + 7) % 7
                    if days_ahead == 0:
                        days_ahead = 7
                    due_date = now + timedelta(days=days_ahead)
                    break
        
        # Парсинг времени
        if due_date:
            time_match = re.search(r'в (\d{1,2})(?::(\d{2}))?', text_lower)
            if time_match:
                hour = int(time_match.group(1))
                minute = int(time_match.group(2)) if time_match.group(2) else 0
                due_date = due_date.replace(hour=hour, minute=minute, second=0)
            else:
                due_date = due_date.replace(hour=12, minute=0, second=0)
        
        due_date_str = due_date.strftime('%Y-%m-%d %H:%M:%S') if due_date else None
        
        # Приоритет
        if any(w in text_lower for w in ['сроч', 'важн', 'критич']):
            priority = 'high'
        elif any(w in text_lower for w in ['не сроч', 'потом']):
            priority = 'low'
        else:
            priority = 'medium'
        
        # Теги
        tags = []
        tag_map = {
            'работа': ['работ', 'офис', 'совещание', 'отчет', 'проект'],
            'учеба': ['учеб', 'диплом', 'курс', 'экзамен'],
            'покупки': ['купи', 'магазин', 'продукты'],
            'личное': ['личн', 'дом', 'семья', 'друзья']
        }
        for tag, keywords in tag_map.items():
            if any(kw in text_lower for kw in keywords):
                tags.append(tag)
        if not tags:
            tags = ['общее']
        
        # Заголовок
        title = text[:50] + ('...' if len(text) > 50 else '')
        
        return {
            "title": title,
            "due_date": due_date_str,
            "priority": priority,
            "tags": tags[:3]
        }
    
    def _call_yandex_gpt(self, prompt: str) -> Dict[str, Any]:
        """Вызов Yandex GPT API"""
        
        if self.is_demo:
            return self._manual_response(prompt)
        
        request_body = {
            "modelUri": f"gpt://{self.folder_id}/{self.model}",
            "completionOptions": {
                "stream": False,
                "temperature": 0.1,
                "maxTokens": 500
            },
            "messages": [{"role": "user", "text": prompt}]
        }
        
        headers = {
            "Authorization": f"Api-Key {self.api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(self.url, headers=headers, json=request_body, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                ai_text = result['result']['alternatives'][0]['message']['text']
                return {"success": True, "text": ai_text}
            else:
                return {"success": False, "error": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _manual_response(self, prompt: str) -> Dict[str, Any]:
        """Ответ в демо-режиме"""
        # Извлекаем текст из промпта
        match = re.search(r'Входной текст: "([^"]+)"', prompt)
        if match:
            text = match.group(1)
            return {"success": True, "text": json.dumps(self._manual_parse(text), ensure_ascii=False)}
        
        return {"success": True, "text": '{"title": "Задача", "due_date": null, "priority": "medium", "tags": ["общее"]}'}
    
    def chat_with_ai(self, user_message: str, context: str = "") -> str:
        """Чат с AI ассистентом"""
        
        prompt = f"""Ты - дружелюбный AI ассистент в приложении для планирования задач.

{context}

Пользователь: {user_message}

Ответь кратко, по делу и дружелюбно. Используй эмодзи где уместно."""

        response = self._call_yandex_gpt(prompt)
        
        if response['success']:
            return response['text']
        else:
            return "Извините, произошла ошибка. Попробуйте еще раз."


# Создаем глобальный экземпляр
ai_client = YandexGPTClient()