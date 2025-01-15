import sqlite3

# Подключение к базе данных
def get_db_connection():
    conn = sqlite3.connect('subscriptions.db')
    conn.row_factory = sqlite3.Row
    return conn

# Функция для создания или обновления таблицы базы данных
def create_or_update_database():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Создаем таблицу, если её нет
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS subscriptions (
        user_id INTEGER PRIMARY KEY,
        paid_date TEXT,
        expiry_date TEXT,
        free_used BOOLEAN DEFAULT 0
    )
    """)

    # Проверяем, есть ли столбец free_used
    try:
        cursor.execute("ALTER TABLE subscriptions ADD COLUMN free_used BOOLEAN DEFAULT 0")
    except sqlite3.OperationalError as e:
        if "duplicate column name" not in str(e).lower():
            raise

    conn.commit()
    conn.close()

# Функция для получения информации о подписке
def get_subscription(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM subscriptions WHERE user_id = ?", (user_id,))
    subscription = cursor.fetchone()
    conn.close()
    return subscription

# Функция для обновления подписки
def update_subscription(user_id, paid_date, expiry_date):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT OR REPLACE INTO subscriptions (user_id, paid_date, expiry_date, free_used)
    VALUES (?, ?, ?, COALESCE((SELECT free_used FROM subscriptions WHERE user_id = ?), 0))
    """, (user_id, paid_date, expiry_date, user_id))
    conn.commit()
    conn.close()


def add_or_update_user(user_id):
    """
    Добавляет нового пользователя, если он еще не существует.

    :param user_id: ID пользователя в Telegram
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Проверяем, существует ли пользователь
    cursor.execute("SELECT * FROM subscriptions WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()

    if not user:
        # Пользователь не существует, создаем запись
        cursor.execute(
            """
            INSERT INTO subscriptions (user_id)
            VALUES (?)
            """,
            (user_id,)
        )

    conn.commit()
    conn.close()