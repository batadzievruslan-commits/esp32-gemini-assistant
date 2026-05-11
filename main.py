import os
import requests
from flask import Flask, request, render_template_string

app = Flask(__name__)

API_KEY = os.environ.get("GOOGLE_API_KEY")

# Прямая ссылка на стабильную версию API v1
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent?key={API_KEY}"

HTML_PAGE = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Gemini Assistant</title>
    <style>
        body { background: #1a1a1a; color: white; font-family: sans-serif; text-align: center; padding: 20px; }
        input { padding: 10px; width: 250px; border-radius: 5px; border: none; }
        button { padding: 10px 20px; background: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer; }
        .error { color: #ff6b6b; border: 1px solid #ff6b6b; padding: 10px; margin-top: 20px; }
        .success { color: #51cf66; }
    </style>
</head>
<body>
    <h2>Голосовой помощник</h2>
    <form action="/ask">
        <input type="text" name="q" placeholder="Введите ваш вопрос..." required>
        <button type="submit">Спросить ИИ</button>
    </form>
    {% if response %}
        <div class="{{ 'error' if 'Ошибка' in response else '' }}">
            <h3>Ответ от ИИ:</h3>
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
    
    # Формируем JSON запрос вручную
    payload = {
        "contents": [{"parts": [{"text": user_query}]}]
    }
    
    try:
        res = requests.post(GEMINI_URL, json=payload)
        data = res.json()
        
        if res.status_code == 200:
            # Извлекаем текст из сложной структуры ответа Google
            ai_text = data['candidates'][0]['content']['parts'][0]['text']
            return render_template_string(HTML_PAGE, response=ai_text)
        else:
            return render_template_string(HTML_PAGE, response=f"Ошибка API: {data.get('error', {}).get('message', 'Неизвестная ошибка')}")
    except Exception as e:
        return render_template_string(HTML_PAGE, response=f"Ошибка сервера: {str(e)}")
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
