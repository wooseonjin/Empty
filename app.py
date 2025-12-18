import os
import sqlite3
import datetime
import random
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# 경로 설정
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
        try:
            conn = sqlite3.connect(db_path)
            c = conn.cursor()
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            c.execute("INSERT INTO messages (content, emotion, created_at) VALUES (?, ?, ?)", (content, emotion, now))
            message_id = c.lastrowid
            c.execute("UPDATE stats SET total_count = total_count + 1")
            conn.commit()
            conn.close()
            
            quotes = ["마음이 한결 가벼워졌길 바라요.", "무거운 짐은 여기 두고 가세요.", "오늘도 충분히 잘해냈어요.", "비워낸 자리에 평온이 깃들 거예요."]
            return jsonify({"status": "success", "id": message_id, "quote": random.choice(quotes)})
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500
    return jsonify({"status": "fail"}), 400

@app.route('/info', methods=['GET'])
def get_info():
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT content, emotion, created_at FROM messages ORDER BY id DESC LIMIT 5")
    rows = c.fetchall()
    c.execute("SELECT total_count FROM stats")
    total = c.fetchone()[0]
    conn.close()
    return jsonify({"messages": [{"content": r[0], "emotion": r[1], "date": r[2]} for r in rows], "total": total})

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