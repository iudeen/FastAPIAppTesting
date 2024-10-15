import sqlite3

from subscription import Subscription


# SQLite connection dependency
def get_db():  # pragma: no cover
    db_name = "subscriptions.db"
    conn = sqlite3.connect(db_name)
    try:
        yield conn
    finally:
        conn.close()


# Function to create the subscriptions table
def create_table(conn: sqlite3.Connection):
    cursor = conn.cursor()
    cursor.execute(
        '''
    CREATE TABLE IF NOT EXISTS subscriptions
                      (id INTEGER PRIMARY KEY AUTOINCREMENT,
                       user_name TEXT NOT NULL,
                       plan TEXT NOT NULL,
                       start_date TEXT NOT NULL,
                       end_date TEXT NULLABLE,
                       cancelled INTEGER NOT NULL,
                       paused INTEGER NOT NULL,
                       paused_at TEXT NULLABLE,
                       resumed_at TEXT NULLABLE)
                       '''
    )
    conn.commit()


# Function to insert a new subscription
def create_subscription(db: sqlite3.Connection, user_name: str, plan: str):
    sub = Subscription(user_name=user_name, plan=plan)
    cursor = db.cursor()
    cursor.execute('''INSERT INTO subscriptions (user_name, plan, start_date, end_date, cancelled, paused, paused_at, resumed_at)
                      VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                   (sub.user_name, sub.plan, sub.start_date, sub.end_date, sub.cancelled, sub.paused, sub.paused_at,
                    sub.resumed_at))
    db.commit()
    subscription_id = cursor.lastrowid
    return subscription_id


# Function to fetch a subscription by ID and return a Subscription object
def get_subscription_by_id(db: sqlite3.Connection, subscription_id: int):
    cursor = db.cursor()
    subscription = cursor.execute("SELECT * FROM subscriptions WHERE id=?", (subscription_id,)).fetchone()

    if subscription:
        return Subscription(
            user_name=subscription[1],
            plan=subscription[2],
            start_date=subscription[3],
            end_date=subscription[4],
            cancelled=bool(subscription[5]),
            paused=bool(subscription[6]),
            paused_at=subscription[7],
            resumed_at=subscription[8]
        )
    return None


# Function to update a subscription after changes
def update_subscription(db: sqlite3.Connection, subscription_id: int, subscription: Subscription):
    cursor = db.cursor()
    cursor.execute('''UPDATE subscriptions SET 
                      plan=?, start_date=?, end_date=?, cancelled=?, paused=?, paused_at=?, resumed_at=? 
                      WHERE id=?''',
                   (subscription.plan, subscription.start_date, subscription.end_date, int(subscription.cancelled),
                    int(subscription.paused), subscription.paused_at, subscription.resumed_at, subscription_id))
    db.commit()


# Function to fetch all subscriptions
def get_all_subscriptions(db: sqlite3.Connection):
    cursor = db.cursor()
    subscriptions = cursor.execute("SELECT * FROM subscriptions").fetchall()
    return subscriptions
