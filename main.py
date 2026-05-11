import os
from flask import Flask, request, render_template_string
from google import genai

app = Flask(__name__)

# Используем новый клиент и библиотеку google-genai
client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))

last_answer = "Привет! Я готов к работе."

@app.route('/')
def index():
    return render_template_string(HTML_PAGE, answer=last_answer)

@app.route('/ask')
def ask():
    global last_answer
    query = request.args.get('q', '')
    if not query: return "Пустой запрос"
    
    try:
        # Самый современный способ вызова Gemini
        response = client.models.generate_content(
           model = genai.GenerativeModel('gemini-pro'), 
            contents=query + ". Ответь очень коротко, до 10 слов."
        )
        last_answer = response.text
        return last_answer
    except Exception as e:
        return f"Ошибка ИИ: {str(e)}"

@app.route('/get_answer')
def get_answer():
    return last_answer

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Голосовой помощник</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { background: #121212; color: white; font-family: sans-serif; text-align: center; padding-top: 50px; }
        .btn { background: #007bff; color: white; border: none; padding: 15px 30px; border-radius: 50px; font-size: 20px; cursor: pointer; }
    </style>
</head>
<body>
    <h1>Голосовой помощник</h1>
    <button class="btn" onclick="location.href='/ask?q=какой сегодня день'">Задать вопрос</button>
    <p style="margin-top:20px; color:#00ff00;">Статус: {{ answer }}</p>
</body>
</html>
"""

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
