import os
import requests
from flask import Flask, request, render_template_string

app = Flask(__name__)

# Берем ключ из настроек Render (Environment Variables)
API_KEY = os.environ.get("GOOGLE_API_KEY")

# Было: gemini-1.5-flash
# Стало: gemini-pro (самая совместимая версия для старых и новых проектов)
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={API_KEY}"

HTML_PAGE = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Gemini Assistant</title>
    <style>
        body { background: #1a1a1a; color: white; font-family: sans-serif; text-align: center; padding: 20px; }
        .container { max-width: 500px; margin: auto; background: #2d2d2d; padding: 30px; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.5); }
        input { padding: 12px; width: 80%; border-radius: 8px; border: none; margin-bottom: 20px; font-size: 16px; }
        button { padding: 12px 25px; background: #007bff; color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; }
        button:hover { background: #0056b3; }
        .status { margin-top: 20px; color: #aaa; font-size: 0.9em; }
    </style>
</head>
<body>
    <div class="container">
        <h2>Голосовой помощник</h2>
        <p>Дипломный проект (KSTU)</p>
        <form action="/ask">
            <input type="text" name="q" placeholder="Введите ваш вопрос..." required>
            <br>
            <button type="submit">Спросить ИИ</button>
        </form>
        <div class="status">Статус сервера: <span style="color: #51cf66;">LIVE</span></div>
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
        return "<h1>Ошибка:</h1><p>Вы ничего не ввели.</p><a href='/'>Назад</a>"
    
    # Формируем JSON-запрос для Google Gemini API
    payload = {
        "contents": [{
            "parts": [{"text": user_query}]
        }]
    }
    
    try:
        # Прямой POST-запрос через библиотеку requests
        res = requests.post(GEMINI_URL, json=payload, timeout=10)
        data = res.json()
        
        if res.status_code == 200:
            # Извлекаем текст ответа из структуры Google JSON
            ai_text = data['candidates'][0]['content']['parts'][0]['text']
            
            # Выводим ответ на отдельной странице для теста
            return f"""
            <body style="background: #1a1a1a; color: white; font-family: sans-serif; padding: 40px; text-align: center;">
                <div style="max-width: 600px; margin: auto; background: #2d2d2d; padding: 20px; border-radius: 10px; text-align: left;">
                    <h2 style="color: #51cf66;">Ответ Gemini:</h2>
                    <p style="line-height: 1.6; font-size: 18px;">{ai_text}</p>
                    <hr style="border: 0.5px solid #444; margin: 20px 0;">
                    <a href="/" style="color: #007bff; text-decoration: none; font-weight: bold;">← Задать другой вопрос</a>
                </div>
            </body>
            """
        else:
            # Если API вернуло ошибку (например, 404 или 400)
            return f"<h1>Ошибка API:</h1><pre style='color: red;'>{str(data)}</pre><a href='/'>Назад</a>"
            
    except Exception as e:
        # Если проблема с интернетом или самим сервером
        return f"<h1>Ошибка сервера:</h1><p>{str(e)}</p><a href='/'>Назад</a>"

if __name__ == "__main__":
    # Порт для Render
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
