from flask import Blueprint, render_template, request, redirect, url_for, session
import sqlite3

# ✅ Blueprint for admin
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# ✅ DB connection helper
def get_db_connection():
    conn = sqlite3.connect('db/sapthagiri.db')
    conn.row_factory = sqlite3.Row
    return conn

# ========== CLIENTS ==========
@admin_bp.route('/clients')
def manage_clients():
    if session.get('role') != 'admin':
        return redirect(url_for('auth.login'))

    conn = get_db_connection()
    clients = conn.execute('SELECT * FROM Clients').fetchall()
    conn.close()
    return render_template('admin_clients.html', clients=clients)

@admin_bp.route('/clients/add', methods=['POST'])
def add_client():
    if session.get('role') != 'admin':
        return redirect(url_for('auth.login'))

    shop_name = request.form['shop_name']
    owner_name = request.form['owner_name']
    address = request.form['address']
    phone = request.form['phone']

    conn = get_db_connection()
    conn.execute("""
        INSERT INTO Clients (shop_name, owner_name, address, phone) 
        VALUES (?, ?, ?, ?)""",
        (shop_name, owner_name, address, phone)
    )
    conn.commit()
    conn.close()
    return redirect(url_for('admin.manage_clients'))

@admin_bp.route('/clients/delete/<int:client_id>')
def delete_client(client_id):
    if session.get('role') != 'admin':
        return redirect(url_for('auth.login'))

    conn = get_db_connection()
    conn.execute("DELETE FROM Clients WHERE id = ?", (client_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin.manage_clients'))

# ========== ITEMS ==========
@admin_bp.route('/items')
def manage_items():
    if session.get('role') != 'admin':
        return redirect(url_for('auth.login'))

    conn = get_db_connection()
    items = conn.execute('SELECT * FROM Items').fetchall()
    conn.close()
    return render_template('admin_items.html', items=items)

@admin_bp.route('/items/add', methods=['POST'])
def add_item():
    if session.get('role') != 'admin':
        return redirect(url_for('auth.login'))

    name = request.form['name']
    unit = request.form['unit']

    conn = get_db_connection()
    conn.execute("INSERT INTO Items (name, unit) VALUES (?, ?)", (name, unit))
    conn.commit()
    conn.close()
    return redirect(url_for('admin.manage_items'))

@admin_bp.route('/items/delete/<int:item_id>')
def delete_item(item_id):
    if session.get('role') != 'admin':
        return redirect(url_for('auth.login'))

    conn = get_db_connection()
    conn.execute("DELETE FROM Items WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin.manage_items'))

# ========== CLIENT PRICES ==========
@admin_bp.route('/clients/<int:client_id>/prices', methods=['GET', 'POST'])
def prices(client_id):
    if session.get('role') != 'admin':
        return redirect(url_for('auth.login'))

    conn = get_db_connection()

    # Get client details
    client = conn.execute("SELECT * FROM Clients WHERE id = ?", (client_id,)).fetchone()
    items = conn.execute("SELECT * FROM Items").fetchall()
    prices_data = conn.execute("SELECT * FROM ClientItemPrices WHERE client_id = ?", (client_id,)).fetchall()
    price_dict = {row["item_id"]: row["price"] for row in prices_data}

    if request.method == 'POST':
        for item in items:
            price_val = request.form.get(f"price_{item['id']}")
            if price_val:
                try:
                    price_val = float(price_val)
                    existing = conn.execute("""
                        SELECT * FROM ClientItemPrices 
                        WHERE client_id = ? AND item_id = ?
                    """, (client_id, item['id'])).fetchone()

                    if existing:
                        conn.execute("""
                            UPDATE ClientItemPrices 
                            SET price = ? WHERE client_id = ? AND item_id = ?
                        """, (price_val, client_id, item['id']))
                    else:
                        conn.execute("""
                            INSERT INTO ClientItemPrices (client_id, item_id, price)
                            VALUES (?, ?, ?)
                        """, (client_id, item['id'], price_val))
                except ValueError:
                    continue  # Skip invalid price input

        conn.commit()
        conn.close()
        return redirect(url_for('admin.manage_clients'))

    conn.close()
    return render_template('admin_client_prices.html', client=client, items=items, price_dict=price_dict)
