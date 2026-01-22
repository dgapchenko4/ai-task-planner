"""
Простой скрипт для запуска FastAPI приложения.
"""

import uvicorn

if __name__ == "__main__":
    # Запускаем сервер
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )