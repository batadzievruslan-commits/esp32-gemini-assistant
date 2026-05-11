import os
from flask import Flask, request
import google.generativeai as genai

app = Flask(__name__)

# Настройка API
API_KEY = os.environ.get("GOOGLE_API_KEY")
genai.configure(api_key=API_KEY)

# Мы используем это имя модели, так как оно самое универсальное для v1 API
model = genai.GenerativeModel('gemini-1.0-pro')

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Gemini Assistant</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { background: #121212; color: white; font-family: sans-serif; text-align: center; padding-top: 50px; }
        .btn { background: #007bff; border: none; color: white; padding: 15px 32px; border-radius: 30px; font-size: 20px; cursor: pointer; }
    </style>
</head>
<body>
    <h1>Голосовой помощник</h1>
    <form action="/ask">
        <input type="hidden" name="q" value="Привет, как дела?">
        <button type="submit" class="btn">🎤 Задать вопрос</button>
    </form>
    <br>
    <div id="result">
        {% if response %}
            <p style="color: #00ff00;">Отправлено на ESP32!</p>
            <hr>
            <p>ИИ ответил: {{ response }}</p>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_PAGE)

@app.route('/ask')
def ask():
    user_query = request.args.get('q', 'Привет')
    try:
        # Прямой вызов генерации
        response = model.generate_content(user_query)
        return render_template_string(HTML_PAGE, response=response.text)
    except Exception as e:
        return render_template_string(HTML_PAGE, response=f"Ошибка: {str(e)}")

from flask import render_template_string
