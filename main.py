import os
from flask import Flask, request, render_template_string
import google.generativeai as genai

app = Flask(__name__)

API_KEY = os.environ.get("GOOGLE_API_KEY")
genai.configure(api_key=API_KEY)

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
        button { padding: 15px 30px; font-size: 18px; border-radius: 50px; border: none; color: white; cursor: pointer; margin: 5px; }
        #micBtn { background: #dc3545; }
        #sendBtn { background: #007bff; }
        input { padding: 15px; font-size: 16px; width: 80%; max-width: 400px; border-radius: 10px; border: none; margin: 10px 0; background: #2a2a2a; color: white; }
        #status { color: #00ff00; margin-top: 10px; min-height: 20px; }
        #result { margin-top: 20px; color: #ccc; border-top: 1px solid #333; padding-top: 20px; text-align: left; max-width: 400px; margin-left: auto; margin-right: auto; }
    </style>
</head>
<body>
    <h1>Голосовой помощник</h1>
    
    <input type="text" id="textInput" placeholder="Введите вопрос..." />
    <br>
    <button id="sendBtn">📝 Отправить текст</button>
    <button id="micBtn">🎤 Голосовой ввод</button>
    
    <div id="status">Нажмите кнопку и говорите, или введите текст</div>
    <div id="result">Ожидание ответа...</div>

    <script>
        const textInput = document.getElementById('textInput');
        const sendBtn = document.getElementById('sendBtn');
        const micBtn = document.getElementById('micBtn');
        const status = document.getElementById('status');
        const resultDiv = document.getElementById('result');
        
        // ========== ОТПРАВКА ТЕКСТА ==========
        function askGemini(query) {
            status.innerText = 'Думаю...';
            resultDiv.innerText = 'Загрузка...';
            
            fetch('/ask?q=' + encodeURIComponent(query))
                .then(r => r.text())
                .then(data => {
                    status.innerText = 'Готово!';
                    resultDiv.innerText = 'Ответ: ' + data;
                })
                .catch(err => {
                    status.innerText = 'Ошибка запроса';
                    resultDiv.innerText = err;
                });
        }
        
        // Кнопка "Отправить текст"
        sendBtn.onclick = () => {
            const text = textInput.value.trim();
            if (text) {
                askGemini(text);
                textInput.value = '';
            }
        };
        
        // Отправка по Enter
        textInput.onkeypress = (e) => {
            if (e.key === 'Enter') {
                const text = textInput.value.trim();
                if (text) {
                    askGemini(text);
                    textInput.value = '';
                }
            }
        };
        
        // ========== ГОЛОСОВОЙ ВВОД ==========
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

        if (SpeechRecognition) {
            const rec = new SpeechRecognition();
            rec.lang = 'ru-RU';

            micBtn.onclick = () => { 
                rec.start(); 
                status.innerText = 'Слушаю...'; 
            };

            rec.onresult = (e) => {
                const text = e.results[0][0].transcript;
                textInput.value = text;
                status.innerText = 'Распознано: ' + text;
                askGemini(text);
            };
            
            rec.onerror = () => {
                status.innerText = 'Ошибка микрофона. Введите текст вручную.';
            };
        } else {
            micBtn.style.display = 'none';
            status.innerText = 'Браузер не поддерживает голос. Используйте ввод текста.';
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
