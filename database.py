import sqlite3
from datetime import datetime

DB_NAME = "ssc_bot.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        full_name TEXT,
        language TEXT DEFAULT 'English',
        join_date TEXT,
        last_active TEXT,
        streak INTEGER DEFAULT 0,
        total_tests INTEGER DEFAULT 0,
        total_correct INTEGER DEFAULT 0,
        total_wrong INTEGER DEFAULT 0,
        total_score REAL DEFAULT 0
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS test_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        exam_type TEXT,
        subject TEXT,
        score REAL,
        accuracy REAL,
        time_taken INTEGER,
        total_questions INTEGER,
        date TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS weak_topics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        topic TEXT,
        mistake_count INTEGER DEFAULT 1
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS saved_questions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        question TEXT,
        answer TEXT,
        topic TEXT,
        exam TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS streak_log (
        user_id INTEGER PRIMARY KEY,
        last_streak_date TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS scheduled_tests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        exam_name TEXT,
        time_slot TEXT,
        enabled INTEGER DEFAULT 1
    )
    """)

    conn.commit()
    conn.close()


def add_user(user_id, username, full_name):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT OR IGNORE INTO users (
        user_id,
        username,
        full_name,
        join_date,
        last_active
    ) VALUES (?, ?, ?, ?, ?)
    """, (
        user_id,
        username,
        full_name,
        datetime.now().isoformat(),
        datetime.now().isoformat()
    ))

    conn.commit()
    conn.close()


def update_last_active(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE users
    SET last_active = ?
    WHERE user_id = ?
    """, (
        datetime.now().isoformat(),
        user_id
    ))

    conn.commit()
    conn.close()


def save_test_history(
    user_id,
    exam_type,
    subject,
    score,
    accuracy,
    time_taken,
    total_questions
):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO test_history (
        user_id,
        exam_type,
        subject,
        score,
        accuracy,
        time_taken,
        total_questions,
        date
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        exam_type,
        subject,
        score,
        accuracy,
        time_taken,
        total_questions,
        datetime.now().isoformat()
    ))

    conn.commit()
    conn.close()


def add_weak_topic(user_id, topic):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT id, mistake_count
    FROM weak_topics
    WHERE user_id = ? AND topic = ?
    """, (user_id, topic))

    result = cursor.fetchone()

    if result:
        cursor.execute("""
        UPDATE weak_topics
        SET mistake_count = mistake_count + 1
        WHERE id = ?
        """, (result[0],))
    else:
        cursor.execute("""
        INSERT INTO weak_topics (
            user_id,
            topic,
            mistake_count
        ) VALUES (?, ?, 1)
        """, (user_id, topic))

    conn.commit()
    conn.close()


def get_user_progress(user_id):
    conn = get_connection()
    cursor = conn
