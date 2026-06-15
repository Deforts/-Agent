from flask import Flask, render_template_string, request, jsonify
from agent import run_agent, generate_text_weekly_report
import os

app = Flask(__name__)

REPORT_FILE = "运营月报_高级版.html"

# 主页面 HTML（聊天框 → 月报 → 文字周报）
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>运营智能助手 + 月报看板</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #eef2f5;
            padding: 20px;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 30px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        .chat-section {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
        }
        .chat-container {
            background: white;
            border-radius: 20px;
            overflow: hidden;
            display: flex;
            flex-direction: column;
            height: 500px;
            max-height: 40vh;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        .chat-header {
            background: #2c3e50;
            color: white;
            padding: 15px 20px;
            font-size: 20px;
            font-weight: bold;
            text-align: center;
        }
        .chat-messages {
            flex: 1;
            overflow-y: auto;
            padding: 15px;
            background: #f5f7fa;
        }
        .message {
            margin-bottom: 12px;
            display: flex;
            flex-direction: column;
        }
        .user-message { align-items: flex-end; }
        .assistant-message { align-items: flex-start; }
        .message-bubble {
            max-width: 70%;
            padding: 10px 16px;
            border-radius: 20px;
            font-size: 14px;
            line-height: 1.4;
            word-wrap: break-word;
        }
        .user-message .message-bubble {
            background: #3498db;
            color: white;
            border-bottom-right-radius: 4px;
        }
        .assistant-message .message-bubble {
            background: white;
            color: #2c3e50;
            border: 1px solid #ddd;
            border-bottom-left-radius: 4px;
        }
        .chat-input {
            display: flex;
            padding: 12px;
            background: white;
            border-top: 1px solid #eee;
        }
        .chat-input input {
            flex: 1;
            padding: 10px 15px;
            border: 1px solid #ccc;
            border-radius: 30px;
            font-size: 14px;
            outline: none;
        }
        .chat-input button {
            margin-left: 10px;
            padding: 10px 20px;
            background: #3498db;
            color: white;
            border: none;
            border-radius: 30px;
            cursor: pointer;
            font-weight: bold;
        }
        .chat-input button:hover { background: #2980b9; }
        .loading {
            text-align: center;
            color: #888;
            font-style: italic;
            margin: 10px;
        }
        /* 共用卡片区域样式 */
        .report-section, .text-report-section {
            padding: 20px;
            background: white;
            border-top: 1px solid #e0e0e0;
        }
        .report-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
            flex-wrap: wrap;
        }
        .report-header h2 {
            color: #2c3e50;
            font-size: 22px;
            margin: 0;
        }
        .refresh-btn {
            background: #2ecc71;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 25px;
            cursor: pointer;
            font-weight: bold;
            transition: 0.2s;
        }
        .refresh-btn:hover { background: #27ae60; }
        iframe {
            width: 100%;
            height: 800px;
            border: none;
            border-radius: 20px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
            background: #fafafa;
        }
        .text-report-card {
            background: #f8f9fa;
            border-radius: 20px;
            padding: 20px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
            overflow-x: auto;
        }
        @media (max-width: 768px) {
            iframe {
                height: 500px;
            }
            .chat-container {
                height: 400px;
            }
        }
    </style>
</head>
<body>
<div class="container">
    <!-- 聊天区域 -->
    <div class="chat-section">
        <div class="chat-container">
            <div class="chat-header">
                🤖 产品运营智能助手
            </div>
            <div class="chat-messages" id="chat-messages">
                <div class="message assistant-message">
                    <div class="message-bubble">
                        你好！我是运营数据助手。你可以问我关于 DAU、新增、留存、营收、渠道质量、用户反馈等问题。<br>
                        试试问：<strong>昨天DAU是多少？</strong> 或 <strong>最近一周哪个渠道留存率最高？</strong>
                    </div>
                </div>
            </div>
            <div class="chat-input">
                <input type="text" id="user-input" placeholder="输入你的问题..." autocomplete="off">
                <button id="send-btn">发送</button>
            </div>
        </div>
    </div>

    <!-- 月报区域（上方） -->
    <div class="report-section">
        <div class="report-header">
            <h2>📊 运营数据月报</h2>
            <button class="refresh-btn" onclick="refreshReport()">🔄 刷新报告</button>
        </div>
        <iframe id="report-frame" src="/report" title="运营月报"></iframe>
    </div>

    <!-- 文字周报卡片（下方） -->
    <div class="text-report-section">
        <div class="report-header">
            <h2>📝 文字周报（同比 · 预测 · 异常归因）</h2>
            <button class="refresh-btn" onclick="refreshTextReport()">🔄 刷新</button>
        </div>
        <div id="text-report-content" class="text-report-card">
            加载中...
        </div>
    </div>
</div>

<script>
    const messagesDiv = document.getElementById('chat-messages');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');

    function addMessage(role, content) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${role}-message`;
        const bubble = document.createElement('div');
        bubble.className = 'message-bubble';
        bubble.innerHTML = content.replace(/\\n/g, '<br>');
        messageDiv.appendChild(bubble);
        messagesDiv.appendChild(messageDiv);
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    }

    function showLoading() {
        const loadingDiv = document.createElement('div');
        loadingDiv.id = 'loading';
        loadingDiv.className = 'loading';
        loadingDiv.innerText = '思考中...';
        messagesDiv.appendChild(loadingDiv);
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    }

    function hideLoading() {
        const loading = document.getElementById('loading');
        if (loading) loading.remove();
    }

    async function sendMessage() {
        const question = userInput.value.trim();
        if (!question) return;
        addMessage('user', question);
        userInput.value = '';
        showLoading();
        try {
            const response = await fetch('/ask', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ question: question })
            });
            const data = await response.json();
            hideLoading();
            addMessage('assistant', data.answer);
        } catch (error) {
            hideLoading();
            addMessage('assistant', '抱歉，发生了错误：' + error);
        }
    }

    function refreshReport() {
        const iframe = document.getElementById('report-frame');
        iframe.src = iframe.src;
    }

    function refreshTextReport() {
        fetch('/text_report')
            .then(response => response.text())
            .then(html => {
                document.getElementById('text-report-content').innerHTML = html;
            })
            .catch(err => {
                document.getElementById('text-report-content').innerHTML = '加载失败：' + err;
            });
    }

    refreshTextReport();

    sendBtn.addEventListener('click', sendMessage);
    userInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') sendMessage();
    });
</script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/ask', methods=['POST'])
def ask():
    data = request.get_json()
    question = data.get('question', '')
    try:
        answer = run_agent(question)
        return jsonify({'answer': answer})
    except Exception as e:
        return jsonify({'answer': f'处理出错：{str(e)}'})

@app.route('/report')
def report():
    if os.path.exists(REPORT_FILE):
        with open(REPORT_FILE, 'r', encoding='utf-8') as f:
            return f.read()
    else:
        return "<h3>月报文件未生成，请先运行 generate_web_report.py 生成报告。</h3>"

@app.route('/text_report')
def text_report():
    return generate_text_weekly_report()

if __name__ == '__main__':
    import webbrowser
    import threading

    def open_browser():
        webbrowser.open('http://127.0.0.1:5000')

    threading.Timer(1, open_browser).start()
    app.run(host='0.0.0.0', port=5000, debug=True)