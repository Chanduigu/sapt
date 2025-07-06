from flask import Flask
from routes.auth import auth_bp
from routes.admin import admin_bp
from routes.billing import billing_bp

import os
import sqlite3

app = Flask(__name__)
app.secret_key = 'sapthagiri-foods'

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(billing_bp)

# ✅ Ensure DB and sample data exist on first deploy
def init_db_if_needed():
    db_path = "db/sapthagiri.db"
    if not os.path.exists(db_path):
        os.makedirs("db", exist_ok=True)
        conn = sqlite3.connect(db_path)
        c = conn.cursor()

        # Create tables
        c.execute("""
        CREATE TABLE IF NOT EXISTS Users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT, password TEXT, role TEXT
        )""")

        c.execute("""
        CREATE TABLE IF NOT EXISTS Clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            shop_name TEXT, owner_name TEXT, address TEXT, phone TEXT
        )""")

        c.execute("""
        CREATE TABLE IF NOT EXISTS Items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT, unit TEXT
        )""")

        c.execute("""
        CREATE TABLE IF NOT EXISTS ClientItemPrices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER,
            item_id INTEGER,
            price REAL
        )""")

        c.execute("""
        CREATE TABLE IF NOT EXISTS Invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER,
            worker TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )""")

        c.execute("""
        CREATE TABLE IF NOT EXISTS InvoiceItems (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_id INTEGER,
            item_id INTEGER,
            quantity INTEGER,
            price REAL
        )""")

        # Insert sample users
        c.execute("INSERT INTO Users (username, password, role) VALUES (?, ?, ?)", ("admin", "admin123", "admin"))
        c.execute("INSERT INTO Users (username, password, role) VALUES (?, ?, ?)", ("worker1", "worker123", "worker"))

        conn.commit()
        conn.close()
        print("✅ Database initialized with sample users.")

# ✅ Call initializer
init_db_if_needed()

# ✅ Production entry
if __name__ == '__main__':
    app.run(debug=True)
