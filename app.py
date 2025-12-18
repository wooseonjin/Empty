import os
import sqlite3
import datetime
import random
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# PythonAnywhere 경로 최적화
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "database.db")

def init_db():
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS messages 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, content TEXT, emotion TEXT, created_at TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS stats (total_count INTEGER)''')
    c.execute("SELECT * FROM stats")
    if not c.fetchone():
        c.execute("INSERT INTO stats VALUES (0)")
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/burn', methods=['POST'])
def burn_message():
    content = request.form.get('content')
    emotion = request.form.get('emotion', '😶')
    if content and content.strip():
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        c.execute("INSERT INTO messages (content, emotion, created_at) VALUES (?, ?, ?)", (content, emotion, now))
        message_id = c.lastrowid
        c.execute("UPDATE stats SET total_count = total_count + 1")
        conn.commit()
        conn.close()
        
        quotes = [
            "당신의 마음이 한결 가벼워졌기를 바랍니다.",
            "무거운 짐은 여기 두고, 편안한 밤 되세요.",
            "당신은 혼자가 아니에요. 오늘도 수고 많았어요.",
            "비워낸 만큼 당신의 마음엔 평온이 채워질 거예요.",
            "충분히 잘하고 있습니다. 당신을 응원해요."
        ]
        return jsonify({"status": "success", "id": message_id, "quote": random.choice(quotes)})
    return jsonify({"status": "fail", "message": "내용을 입력해주세요."}), 400

@app.route('/info', methods=['GET'])
def get_info():
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT content, emotion, created_at FROM messages ORDER BY id DESC LIMIT 5")
    rows = c.fetchall()
    c.execute("SELECT total_count FROM stats")
    total_fetch = c.fetchone()
    total = total_fetch[0] if total_fetch else 0
    conn.close()
    
    messages = [{"content": row[0], "emotion": row[1], "date": row[2]} for row in rows]
    return jsonify({"messages": messages, "total": total})

@app.route('/delete/<int:msg_id>', methods=['DELETE'])
def delete_message(msg_id):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("DELETE FROM messages WHERE id = ?", (msg_id,))
    conn.commit()
    conn.close()
    return jsonify({"status": "deleted"})

if __name__ == '__main__':
    app.run(debug=True)