from flask import Flask, render_template, request, jsonify
import sqlite3
import datetime

app = Flask(__name__)

# --- 데이터베이스 설정 ---
def init_db():
    # database.db 파일을 연결 (없으면 자동 생성)
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    # 고민을 저장할 테이블 생성 (ID, 내용, 작성시간)
    c.execute('''CREATE TABLE IF NOT EXISTS messages 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, content TEXT, created_at TEXT)''')
    conn.commit()
    conn.close()

# 앱이 시작될 때 DB 초기화
init_db()

# --- 페이지 라우팅 ---

# 1. 메인 페이지 (고민 입력창)
@app.route('/')
def index():
    return render_template('index.html')

# 2. 고민 저장하기 (Create)
@app.route('/burn', methods=['POST'])
def burn_message():
    content = request.form.get('content')
    if content:
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        # DB에 저장
        c.execute("INSERT INTO messages (content, created_at) VALUES (?, ?)", 
                  (content, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        message_id = c.lastrowid # 방금 저장된 글의 번호
        conn.commit()
        conn.close()
        
        # 저장된 ID를 돌려줘서, 잠시 후 삭제할 때 쓰게 함
        return jsonify({"status": "success", "id": message_id})
    return jsonify({"status": "fail"}), 400

# 3. 고민 즉시 삭제하기 (Delete) 
@app.route('/delete/<int:msg_id>', methods=['DELETE'])
def delete_message(msg_id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    # 해당 ID의 고민을 삭제
    c.execute("DELETE FROM messages WHERE id = ?", (msg_id,))
    conn.commit()
    conn.close()
    return jsonify({"status": "deleted"})

if __name__ == '__main__':
    app.run(debug=True)