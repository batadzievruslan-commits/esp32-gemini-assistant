import os
import re
import requests
import time
from flask import Flask, request, render_template_string

app = Flask(__name__)

API_KEY = os.environ.get("GOOGLE_API_KEY")

if not API_KEY:
    raise RuntimeError("GOOGLE_API_KEY не найден в переменных окружения!")

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
    return render_template_string(HTML_PAGE)


@app.route('/ask')
def ask():
    user_query = request.args.get('q')
    
    if not user_query:
        return "Ошибка: пустой запрос", 400

    payload = {
        "contents": [{
            "parts": [{"text": user_query}]
        }]
    }
    
    headers = {'Content-Type': 'application/json'}

    max_retries = 5  # Увеличил до 5 попыток
    
    for attempt in range(max_retries):
        try:
            response = requests.post(
                GEMINI_URL, 
                json=payload, 
                headers=headers, 
                timeout=30  # Увеличил таймаут
            )
            
            # Успешный ответ
            if response.status_code == 200:
                result = response.json()
                try:
                    ai_response = result['candidates'][0]['content']['parts'][0]['text']
                    return ai_response
                except (KeyError, IndexError):
                    return "Ошибка: неожиданный формат ответа от API", 500
            
            # Превышен лимит — ждём и пробуем снова
            elif response.status_code == 429:
                if attempt < max_retries - 1:
                    # Пробуем извлечь время ожидания из ответа Google
                    wait_time = 8  # По умолчанию 8 секунд
                    try:
                        error_data = response.json()
                        error_msg = error_data.get('error', {}).get('message', '')
                        # Ищем "retry in X.Xs"
                        match = re.search(r'retry in (\d+\.?\d*)s', error_msg)
                        if match:
                            wait_time = float(match.group(1)) + 1  # +1 секунда для надёжности
                    except:
                        pass
                    
                    print(f"Лимит превышен, жду {wait_time:.1f} сек... (попытка {attempt + 1}/{max_retries})")
                    time.sleep(wait_time)
                    continue
                else:
                    return "Превышен лимит запросов. Подождите 1-2 минуты и попробуйте снова.", 429
            
            # Другие ошибки API
            else:
                error_msg = "Неизвестная ошибка API"
                try:
                    error_data = response.json()
                    error_msg = error_data.get('error', {}).get('message', 'Неизвестная ошибка')
                except:
                    error_msg = f"HTTP {response.status_code}"
                
                return f"Ошибка API: {error_msg}", response.status_code

        except requests.exceptions.Timeout:
            if attempt < max_retries - 1:
                time.sleep(3)
                continue
            return "Ошибка: сервер Google не отвечает (таймаут)", 504
        except requests.exceptions.ConnectionError:
            return "Ошибка: не удалось подключиться к API Gemini", 502
        except Exception as e:
            print(f"Неожиданная ошибка: {str(e)}")
            return f"Ошибка сервера: {str(e)}", 500
    
    return "Не удалось получить ответ после всех попыток", 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
