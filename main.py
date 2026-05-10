import os
from flask import Flask, request, render_template_string
import google.generativeai as genai

app = Flask(__name__)

# Твой ключ API (потом вынесем в переменные окружения для безопасности)
API_KEY = "ключ_появится_чуть_позже"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# Переменная для хранения последнего ответа
last_answer = "Жду вопроса..."

# HTML-страница с кнопкой микрофона
HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Gemini Assistant Control</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: sans-serif; text-align: center; padding: 20px; background: #121212; color: white; }
        button { padding: 20px 40px; font-size: 20px; border-radius: 50px; border: none; background: #007bff; color: white; cursor: pointer; }
        #status { margin-top: 20px; color: #888; }
    </style>
</head>
<body>
    <h1>Голосовой помощник</h1>
    <button id="micBtn">🎤 Задать вопрос</button>
    <div id="status">Нажмите кнопку и говорите</div>
    <div id="result" style="margin-top: 30px; font-style: italic;"></div>

    <script>
        const btn = document.getElementById('micBtn');
        const status = document.getElementById('status');
        const resultDiv = document.getElementById('result');
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

        if (SpeechRecognition) {
            const rec = new SpeechRecognition();
            rec.lang = 'ru-RU';

            btn.onclick = () => { rec.start(); status.innerText = 'Слушаю...'; };

            rec.onresult = (e) => {
                const text = e.results[0][0].transcript;
                resultDiv.innerText = 'Вы сказали: ' + text;
                status.innerText = 'Отправляю в Gemini...';
                
                fetch('/ask?q=' + encodeURIComponent(text))
                    .then(r => r.text())
                    .then(data => {
                        status.innerText = 'Готово! ESP32 скоро получит ответ.';
                        resultDiv.innerText = 'Gemini: ' + data;
                    });
            };
        } else {
            status.innerText = 'Ваш браузер не поддерживает распознавание речи.';
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_PAGE)

@app.route('/ask')
def ask():
    global last_answer
    query = request.args.get('q', 'Привет')
    try:
        response = model.generate_content(query + ". Ответь очень коротко, до 10 слов.")
        last_answer = response.text
        return last_answer
    except Exception as e:
        return f"Ошибка: {str(e)}"

@app.route('/get_answer')
def get_answer():
    return last_answer

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
