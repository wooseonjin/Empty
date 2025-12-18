# app.py 상단 수정
import os
import sqlite3
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# 현재 app.py가 있는 폴더 위치를 자동으로 찾음
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "database.db")

def init_db():
    conn = sqlite3.connect(db_path) # database.db 대신 db_path 사용
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS messages 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, content TEXT, created_at TEXT)''')
    conn.commit()
    conn.close()