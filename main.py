import os
from flask import Flask, request, render_template_string
import google.generativeai as genai

app = Flask(__name__)

API_KEY = os.environ.get("GOOGLE_API_KEY")
genai.configure(api_key=API_KEY)

# Пробуем сначала lite-версию — она меньше нагружена
model = genai.GenerativeModel('models/gemini-2.5-flash-lite')

last_answer = "Привет! Я готов к работе."

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Gemini Assistant</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: sans-serif; text-align: center; padding: 20px; background: #121212; color: white; }
        button { padding: 20px 40px; font-size: 20px; border-radius: 50px; border: none; background: #007bff; color: white; cursor: pointer; margin-bottom: 20px; }
        #status { color: #00ff00; margin-top: 10px; min-height: 20px; }
        #result { margin-top: 20px; color: #ccc; border-top: 1px solid #333; padding-top: 20px; }
    </style>
</head>
<body>
    <h1>Голосовой помощник</h1>
    <button id="micBtn">🎤 Задать вопрос</button>
    <div id="status">Нажмите кнопку и говорите</div>
    <div id="result">Ожидание ответа...</div>

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
                status.innerText = 'Обработка: ' + text;
                
                fetch('/ask?q=' + encodeURIComponent(text))
                    .then(r => r.text())
                    .then(data => {
                        status.innerText = 'Отправлено на ESP32!';
                        resultDiv.innerText = 'ИИ ответил: ' + data;
                    })
                    .catch(err => {
                        status.innerText = 'Ошибка запроса';
                        resultDiv.innerText = err;
                    });
            };
        } else {
            status.innerText = 'Браузер не поддерживает голос';
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
    query = request.args.get('q', '')
    if not query:
        return "Пустой запрос"
    
    try:
        response = model.generate_content(
            query + ". Ответь одной короткой фразой, не больше 60 символов."
        )
        last_answer = response.text.strip()
        return last_answer
    except Exception as e:
        last_answer = "Ошибка ИИ"
        return f"Ошибка ИИ: {str(e)}"

@app.route('/get_answer')
def get_answer():
    return last_answer

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
