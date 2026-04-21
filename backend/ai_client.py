# backend/ai_client.py
import requests
import json
import time
from datetime import datetime
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
        
        if not self.api_key or not self.folder_id:
            print("⚠️ API ключи не найдены! Работаем в демо-режиме")
            self.is_demo = True
        else:
            self.is_demo = False
        
        self.url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    
    def complete(self, prompt: str, system_prompt: str = None) -> Dict[str, Any]:
        """
        Отправка запроса к Yandex GPT
        
        Args:
            prompt: Запрос пользователя
            system_prompt: Системная инструкция
        
        Returns:
            Ответ от AI
        """
        
        # Демо-режим (если нет API ключа)
        if self.is_demo:
            return self._demo_response(prompt)
        
        # Формируем сообщения
        messages = []
        
        if system_prompt:
            messages.append({
                "role": "system",
                "text": system_prompt
            })
        
        messages.append({
            "role": "user",
            "text": prompt
        })
        
        # Формируем запрос
        request_body = {
            "modelUri": f"gpt://{self.folder_id}/{self.model}",
            "completionOptions": {
                "stream": False,
                "temperature": float(os.getenv('AI_TEMPERATURE', 0.1)),
                "maxTokens": int(os.getenv('AI_MAX_TOKENS', 2000))
            },
            "messages": messages
        }
        
        headers = {
            "Authorization": f"Api-Key {self.api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            print(f"🤖 Отправка запроса к Yandex GPT...")
            start_time = time.time()
            
            response = requests.post(
                self.url,
                headers=headers,
                json=request_body,
                timeout=30
            )
            
            elapsed = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result['result']['alternatives'][0]['message']['text']
                
                print(f"✅ Ответ получен за {elapsed:.2f} сек")
                
                return {
                    "success": True,
                    "text": ai_response,
                    "usage": result.get('result', {}).get('usage', {}),
                    "response_time": elapsed
                }
            else:
                print(f"❌ Ошибка API: {response.status_code}")
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}",
                    "is_demo": True
                }
                
        except Exception as e:
            print(f"❌ Ошибка запроса: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "is_demo": True
            }
    
    def _demo_response(self, prompt: str) -> Dict[str, Any]:
        """Демо-режим (имитация ответа AI)"""
        
        print("🎭 Демо-режим: имитация AI")
        
        # Простой анализ текста
        text_lower = prompt.lower()
        
        # Определяем приоритет
        if any(word in text_lower for word in ['сроч', 'важн', 'критич']):
            priority = 'high'
        elif any(word in text_lower for word in ['не сроч', 'потом']):
            priority = 'low'
        else:
            priority = 'medium'
        
        # Определяем теги
        tags = []
        tag_keywords = {
            'работа': ['работ', 'офис', 'совещание', 'отчет', 'проект'],
            'учеба': ['учеб', 'диплом', 'курс', 'экзамен', 'лекция'],
            'личное': ['личн', 'дом', 'семья', 'друзья'],
            'покупки': ['купи', 'магазин', 'продукты']
        }
        
        for tag, keywords in tag_keywords.items():
            if any(kw in text_lower for kw in keywords):
                tags.append(tag)
        
        if not tags:
            tags = ['общее']
        
        # Извлекаем заголовок
        title = prompt[:50] + ('...' if len(prompt) > 50 else '')
        
        # Создаем структурированный ответ
        response_text = json.dumps({
            "title": title,
            "description": prompt if len(prompt) > 50 else None,
            "due_date": None,
            "priority": priority,
            "tags": tags,
            "confidence": 0.7
        }, ensure_ascii=False)
        
        return {
            "success": True,
            "text": response_text,
            "is_demo": True,
            "response_time": 0.5
        }

# Создаем глобальный экземпляр
ai_client = YandexGPTClient()