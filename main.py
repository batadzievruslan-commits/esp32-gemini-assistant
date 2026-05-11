import os
import requests
import time
from flask import Flask, request, render_template_string

app = Flask(__name__)

# Берём ключ из Environment Variables в Render
API_KEY = os.environ.get("GOOGLE_API_KEY")

# Проверка наличия ключа при запуске
if not API_KEY:
    raise RuntimeError("GOOGLE_API_KEY не найден в переменных окружения!")

# Актуальная модель Gemini
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1/models/gemini-2.0-flash:generateContent?key={API_KEY}"

HTML_PAGE = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Gemini Voice Assistant</title>
    <style>
        body { background: #121212; color: #e0e0e0; font-family: 'Segoe UI', sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .card { background: #1e1e1e; padding: 2rem; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); width: 100%; max-width: 400px; text-align: center; border: 1px solid #333; }
        h2 { color: #fff; margin-bottom: 1.5rem; font-weight: 300; }
        input { width: 100%; padding: 12px; margin-bottom: 1rem; border-radius: 8px; border: 1px solid #444; background: #252525; color: white; box-sizing: border-box; }
        button { width: 100%; padding: 12px; border: none; border-radius: 8px; background: #007bff; color: white; font-weight: bold; cursor: pointer; transition: 0.3s; }
        button:hover { background: #0056b3; }
        .footer { margin-top: 1.5rem; font-size: 0.8rem; color: #666; }
    </style>
</head>
<body>
    <div class="card">
        <h2>Голосовой помощник</h2>
        <form action="/ask">
            <input type="text" name="q" placeholder="Введите вопрос..." required>
            <button type="submit">Спросить Gemini</button>
        </form>
        <div class="footer">KSTU Diploma Project • Статус: LIVE</div>
    </div>
</body>
</html>
"""


@app.route('/')
def index():
    """Главная страница с формой"""
    return render_template_string(HTML_PAGE)


@app.route('/ask')
def ask():
    """Обработка вопроса и получение ответа от Gemini с повторными попытками"""
    user_query = request.args.get('q')
    
    # Проверка на пустой запрос
    if not user_query:
        return "Ошибка: пустой запрос", 400

    payload = {
        "contents": [{
            "parts": [{"text": user_query}]
        }]
    }
    
    headers = {'Content-Type': 'application/json'}

    # Пробуем до 3 раз с задержкой
    max_retries = 3
    for attempt in range(max_retries):
        try:
            # Отправляем POST запрос к Google AI API
            response = requests.post(
                GEMINI_URL, 
                json=payload, 
                headers=headers, 
                timeout=15
            )
            
            # Если успешно — возвращаем ответ
            if response.status_code == 200:
                result = response.json()
                try:
                    ai_response = result['candidates'][0]['content']['parts'][0]['text']
                    return ai_response
                except (KeyError, IndexError) as e:
                    return f"Ошибка: неожиданный формат ответа от API", 500
            
            # Если превышен лимит — ждём и пробуем снова
            elif response.status_code == 429:
                if attempt < max_retries - 1:
                    time.sleep(7)  # Ждём 7 секунд (чуть больше, чем просит Google)
                    continue
                else:
                    return "Превышен лимит запросов. Пожалуйста, подождите минуту и попробуйте снова.", 429
            
            # Другие ошибки API
            else:
                error_msg = "Неизвестная ошибка API"
                try:
                    error_data = response.json()
                    error_msg = error_data.get('error', {}).get('message', 'Неизвестная ошибка')
                except:
                    error_msg = f"HTTP {response.status_code}: {response.text[:200]}"
                
                return f"Ошибка API: {error_msg}", response.status_code

        except requests.exceptions.Timeout:
            if attempt < max_retries - 1:
                time.sleep(2)
                continue
            return "Ошибка: превышено время ожидания ответа от API", 504
        except requests.exceptions.ConnectionError:
            return "Ошибка: не удалось подключиться к API Gemini", 502
        except Exception as e:
            print(f"Неожиданная ошибка: {str(e)}")
            return f"Ошибка сервера: {str(e)}", 500
    
    return "Не удалось получить ответ после нескольких попыток", 500


# Для локальной разработки
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
