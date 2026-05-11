import os
import requests
from flask import Flask, request, render_template_string

app = Flask(__name__)

# Берем ключ из Environment Variables в Render
API_KEY = os.environ.get("GOOGLE_API_KEY")

# URL для модели 1.5 Flash (самая быстрая и актуальная)
# Замени строку 11 на эту:
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"

# Простой HTML-интерфейс для проверки работы
HTML_PAGE = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Gemini Voice Assistant</title>
    <style>
        body { background: #121212; color: #e0e0e0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
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
        return "Ошибка: пустой запрос"

    # Формируем структуру запроса для Google
    payload = {
        "contents": [{
            "parts": [{"text": user_query}]
        }]
    }

    try:
        # Отправляем запрос на сервер Google
        response = requests.post(GEMINI_URL, json=payload, timeout=10)
        result = response.json()

        if response.status_code == 200:
            # Извлекаем текст ответа
            ai_response = result['candidates'][0]['content']['parts'][0]['text']
            
            # Возвращаем чистый текст (это важно для ESP32)
            return ai_response
        else:
            # Если Google вернул ошибку (например, 404 или 403)
            return f"Ошибка API: {result.get('error', {}).get('message', 'Неизвестная ошибка')}"

    except Exception as e:
        return f"Ошибка сервера: {str(e)}"

if __name__ == "__main__":
    # Render использует переменную PORT
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
