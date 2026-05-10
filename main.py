import os
from flask import Flask, request, render_template_string
import google.generativeai as genai

app = Flask(__name__)

# 1. Настройка API Ключа (берем из настроек Render)
API_KEY = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=API_KEY)

# 2. Инициализация модели (используем стабильную версию)
# Если 1.5-flash не сработает, библиотека сама выберет доступную
try:
    model = genai.GenerativeModel('gemini-1.5-flash')
except:
    model = genai.GenerativeModel('gemini-pro')

# Переменная для хранения последнего ответа для ESP32
last_answer = "Ожидаю вопроса от комиссии..."

# 3. HTML-интерфейс для телефона
HTML_PAGE = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Assistant Control</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; text-align: center; padding: 40px 20px; background: #0f0f0f; color: #e0e0e0; }
        .container { max-width: 400px; margin: auto; background: #1e1e1e; padding: 30px; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
        h1 { color: #fff; font-size: 24px; margin-bottom: 30px; }
        button { 
            padding: 20px 40px; font-size: 18px; border-radius: 50px; border: none; 
            background: linear-gradient(45deg, #007bff, #00c6ff); color: white; 
            cursor: pointer; transition: transform 0.2s, box-shadow 0.2s; font-weight: bold;
        }
        button:active { transform: scale(0.95); }
        #status { margin-top: 25px; color: #aaa; font-size: 14px; }
        #result { margin-top: 25px; padding: 15px; border-top: 1px solid #333; color: #00ffcc; line-height: 1.5; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Голосовой помощник</h1>
        <button id="micBtn">🎤 Задать вопрос</button>
        <div id="status">Нажмите кнопку и говорите</div>
        <div id="result"></div>
    </div>

    <script>
        const btn = document.getElementById('micBtn');
        const status = document.getElementById('status');
        const resultDiv = document.getElementById('result');
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

        if (SpeechRecognition) {
            const rec = new SpeechRecognition();
            rec.lang = 'ru-RU';

            btn.onclick = () => { 
                rec.start(); 
                status.innerText = 'Слушаю вас...'; 
                btn.style.opacity = '0.5';
            };

            rec.onresult = (e) => {
                const text = e.results[0][0].transcript;
                resultDiv.innerText = 'Вы: ' + text;
                status.innerText = 'Думаю...';
                
                fetch('/ask?q=' + encodeURIComponent(text))
                    .then(r => r.text())
                    .then(data => {
                        status.innerText = 'Ответ отправлен на ESP32';
                        resultDiv.innerText = 'AI: ' + data;
                        btn.style.opacity = '1';
                    })
                    .catch(err => {
                        status.innerText = 'Ошибка связи с ИИ';
                        btn.style.opacity = '1';
                    });
            };
            
            rec.onerror = () => {
                status.innerText = 'Ошибка микрофона. Попробуйте еще раз.';
                btn.style.opacity = '1';
            };
        } else {
            status.innerText = 'Ваш браузер не поддерживает голос. Используйте Chrome или Safari.';
        }
    </script>
</body>
</html>
"""

# 4. Логика обработки запросов
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
        # Добавляем инструкцию отвечать коротко для маленького OLED экрана
        response = model.generate_content(f"Ответь на русском языке, очень кратко (максимум 10 слов): {query}")
        last_answer = response.text.strip()
        return last_answer
    except Exception as e:
        return f"Ошибка ИИ: {str(e)}"

# 5. Эндпоинт, который будет опрашивать ESP32
@app.route('/get_answer')
def get_answer():
    return last_answer

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
