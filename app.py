import os
import sqlite3
import datetime
import random
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "database.db")

def init_db():
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    # messages 테이블에 'emotion' 컬럼 추가
    c.execute('''CREATE TABLE IF NOT EXISTS messages 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, content TEXT, emotion TEXT, created_at TEXT)''')
    # 총 비움 횟수를 저장할 테이블 (간단하게 구현)
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
    emotion = request.form.get('emotion', '😶') # 기본값 무표정
    if content:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        c.execute("INSERT INTO messages (content, emotion, created_at) VALUES (?, ?, ?)", (content, emotion, now))
        message_id = c.lastrowid
        # 전체 카운트 증가
        c.execute("UPDATE stats SET total_count = total_count + 1")
        conn.commit()
        conn.close()
        
        # 위로 명언 리스트
        quotes = [
            "오늘 하루도 정말 고생 많았어요.",
            "당신의 마음이 조금 더 가벼워졌길 바라요.",
            "가끔은 쉬어가도 괜찮아요. 당신은 충분히 잘하고 있어요.",
            "어두운 밤이 지나면 반드시 밝은 아침이 와요.",
            "당신의 소중한 마음을 이곳에 잘 비워냈습니다."
        ]
        return jsonify({"status": "success", "id": message_id, "quote": random.choice(quotes)})
    return jsonify({"status": "fail"}), 400

@app.route('/info', methods=['GET'])
def get_info():
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    # 최근 5개 메시지
    c.execute("SELECT content, emotion, created_at FROM messages ORDER BY id DESC LIMIT 5")
    rows = c.fetchall()
    # 총 비움 횟수
    c.execute("SELECT total_count FROM stats")
    total = c.fetchone()[0]
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