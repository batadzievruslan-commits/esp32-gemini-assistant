import os
from flask import Flask, request, render_template_string
import google.generativeai as genai

app = Flask(__name__)

# Настройка API ключа из переменных окружения Render
API_KEY = os.environ.get("GOOGLE_API_KEY")

# ВНИМАНИЕ: Мы форсируем использование версии v1 и протокола rest, 
# чтобы уйти от ошибки 404/v1beta
genai.configure(api_key=API_KEY, transport='rest')

# Используем самую стабильную модель
model = genai.GenerativeModel('gemini-pro')

HTML_PAGE = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Gemini Voice Assistant</title>
    <style>
        body { background-color: #121212; color: white; font-family: sans-serif; text-align: center; padding: 20px; }
        .container { max-width: 500px; margin: auto; background: #1e1e1e; padding: 20px; border-radius: 15px; shadow: 0 4px 10px rgba(0,0,0,0.5); }
        input { width: 80%; padding: 10px; border-radius: 5px; border: none; margin-bottom: 10px; }
        button { background-color: #007bff; color: white; border: none; padding: 10px 20px; border-radius: 20px; cursor: pointer; font-size: 16px; }
        button:hover { background-color: #0056b3; }
        .response-box { margin-top: 20px; padding: 15px; border: 1px solid #333; border-radius: 10px; background: #252525; text-align: left; }
        .status { color: #00ff00; font-size: 14px; margin-bottom: 10px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Голосовой помощник</h1>
        <form action="/ask" method="get">
            <input type="text" name="q" placeholder="Введите ваш вопрос..." required>
            <br>
            <button type="submit">🎤 Спросить ИИ</button>
        </form>

        {% if response %}
            <div class="response-box">
                <div class="status">● Ответ получен и готов для ESP32</div>
                <strong>Ответ от ИИ:</strong>
                <p>{{ response }}</p>
            </div>
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
    user_query = request.args.get('q', '')
    if not user_query:
        return render_template_string(HTML_PAGE)
    
    try:
        # Генерация контента
        result = model.generate_content(user_query)
        return render_template_string(HTML_PAGE, response=result.text)
    except Exception as e:
        # Выводим ошибку прямо в интерфейс для диагностики
        return render_template_string(HTML_PAGE, response=f"Ошибка: {str(e)}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
