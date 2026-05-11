import os
import requests
from flask import Flask, request, render_template_string

app = Flask(__name__)

# Берем ключ из настроек Render
API_KEY = os.environ.get("GOOGLE_API_KEY")

# Мы добавляем префикс models/, который обязателен для прямых вызовов v1
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash-latest:generateContent?key={API_KEY}"

HTML_PAGE = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Gemini Assistant</title>
    <style>
        body { background: #1a1a1a; color: white; font-family: sans-serif; text-align: center; padding: 20px; }
        input { padding: 10px; width: 250px; border-radius: 5px; border: none; margin-bottom: 10px; }
        button { padding: 10px 20px; background: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer; }
        .response-box { background: #2d2d2d; padding: 15px; border-radius: 10px; margin-top: 20px; text-align: left; display: inline-block; max-width: 80%; }
    </style>
</head>
<body>
    <h2>Голосовой помощник (Дипломный проект)</h2>
    <form action="/ask">
        <input type="text" name="q" placeholder="Введите ваш вопрос..." required>
        <button type="submit">Спросить ИИ</button>
    </form>
    {% if response %}
        <div class="response-box">
            <h3 style="color: #51cf66;">Ответ от Gemini:</h3>
            <p>{{ response }}</p>
        </div>
    {% endif %}
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
        return render_template_string(HTML_PAGE, response="Введите вопрос!")
    
    # Формируем структуру запроса вручную
    payload = {
        "contents": [{"parts": [{"text": user_query}]}]
    }
    
    try:
        res = requests.post(GEMINI_URL, json=payload)
        data = res.json()
        
        if res.status_code == 200:
            # Парсим ответ от Google
            ai_text = data['candidates'][0]['content']['parts'][0]['text']
            return render_template_string(HTML_PAGE, response=ai_text)
        else:
            error_msg = data.get('error', {}).get('message', 'Ошибка API')
            return render_template_string(HTML_PAGE, response=f"Ошибка: {error_msg}")
    except Exception as e:
        return render_template_string(HTML_PAGE, response=f"Ошибка сервера: {str(e)}")

if __name__ == "__main__":
    # Render передает порт через переменную окружения
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
