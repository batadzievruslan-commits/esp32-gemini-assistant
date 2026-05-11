import os
from flask import Flask, request, render_template_string
from google import genai

app = Flask(__name__)

# Инициализация клиента через новую библиотеку
client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))

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
        <input type="text" name="q" placeholder="Ваш вопрос..." style="padding: 10px; border-radius: 5px;">
        <button type="submit" class="btn">🎤 Спросить</button>
    </form>
    <br>
    {% if response %}
        <div style="margin-top: 20px; padding: 20px; border: 1px solid #333; display: inline-block;">
            <p style="color: #00ff00;">Ответ от ИИ:</p>
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
    user_query = request.args.get('q', 'Привет')
    try:
        # Прямой вызов модели 1.5 Flash через новый клиент
        response = client.models.generate_content(
            model = genai.GenerativeModel('gemini-pro'),
            contents=user_query
        )
        return render_template_string(HTML_PAGE, response=response.text)
    except Exception as e:
        return render_template_string(HTML_PAGE, response=f"Ошибка: {str(e)}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
