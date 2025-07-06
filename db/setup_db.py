import sqlite3
import os

# Ensure /db/ directory exists
os.makedirs("db", exist_ok=True)

# Create or connect to DB
conn = sqlite3.connect("db/sapthagiri.db")
c = conn.cursor()

# Drop tables if they exist (for reset)
tables = ['Clients', 'Items', 'ClientItemPrices', 'Users', 'Invoices', 'InvoiceItems']
for table in tables:
    c.execute(f"DROP TABLE IF EXISTS {table}")

# 1. Clients Table
c.execute("""
CREATE TABLE Clients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    shop_name TEXT NOT NULL,
    owner_name TEXT,
    address TEXT,
    phone TEXT
)
""")

# 2. Items Table
c.execute("""
CREATE TABLE Items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    unit TEXT
)
""")

# 3. ClientItemPrices Table
c.execute("""
CREATE TABLE ClientItemPrices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id INTEGER,
    item_id INTEGER,
    price REAL,
    FOREIGN KEY (client_id) REFERENCES Clients(id),
    FOREIGN KEY (item_id) REFERENCES Items(id)
)
""")

# 4. Users Table (admin and workers)
c.execute("""
CREATE TABLE Users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT,
    role TEXT CHECK(role IN ('admin', 'worker')) NOT NULL
)
""")

# ✅ 5. Invoices Table — fixed definition
c.execute("""
CREATE TABLE Invoices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id INTEGER,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    worker TEXT,
    total_amount REAL,
    FOREIGN KEY (client_id) REFERENCES Clients(id)
)
""")

# ✅ 6. InvoiceItems Table — fixed definition
c.execute("""
CREATE TABLE InvoiceItems (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    invoice_id INTEGER,
    item_id INTEGER,
    quantity INTEGER,
    price REAL,
    total REAL,
    FOREIGN KEY (invoice_id) REFERENCES Invoices(id),
    FOREIGN KEY (item_id) REFERENCES Items(id)
)
""")

# Insert sample users
c.execute("INSERT INTO Users (username, password, role) VALUES (?, ?, ?)", ('admin', 'admin123', 'admin'))
c.execute("INSERT INTO Users (username, password, role) VALUES (?, ?, ?)", ('worker1', 'worker123', 'worker'))

# Insert sample clients
c.execute("INSERT INTO Clients (shop_name, owner_name, address, phone) VALUES (?, ?, ?, ?)",
          ('Annapurna Stores', 'Rajesh Kumar', 'Basavanagudi, Bangalore', '9876543210'))
c.execute("INSERT INTO Clients (shop_name, owner_name, address, phone) VALUES (?, ?, ?, ?)",
          ('Sri Lakshmi Traders', 'Lakshmi Devi', 'Tumkur', '9876501234'))

# Insert sample items
c.execute("INSERT INTO Items (name, unit) VALUES (?, ?)", ('Chips 200g', 'pkt'))
c.execute("INSERT INTO Items (name, unit) VALUES (?, ?)", ('Pickle 1kg', 'kg'))
c.execute("INSERT INTO Items (name, unit) VALUES (?, ?)", ('Masala Powder 100g', 'pkt'))

# Prices for Client 1
c.execute("INSERT INTO ClientItemPrices (client_id, item_id, price) VALUES (?, ?, ?)", (1, 1, 20))
c.execute("INSERT INTO ClientItemPrices (client_id, item_id, price) VALUES (?, ?, ?)", (1, 2, 80))
c.execute("INSERT INTO ClientItemPrices (client_id, item_id, price) VALUES (?, ?, ?)", (1, 3, 25))

# Prices for Client 2
c.execute("INSERT INTO ClientItemPrices (client_id, item_id, price) VALUES (?, ?, ?)", (2, 1, 22))
c.execute("INSERT INTO ClientItemPrices (client_id, item_id, price) VALUES (?, ?, ?)", (2, 2, 85))
c.execute("INSERT INTO ClientItemPrices (client_id, item_id, price) VALUES (?, ?, ?)", (2, 3, 28))

# Done!
conn.commit()
conn.close()
print("✅ Database created and populated with sample data.")
