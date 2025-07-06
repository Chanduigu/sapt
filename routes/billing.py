from flask import Blueprint, render_template, request, redirect, url_for, session
import sqlite3
import pdfkit
import os

billing_bp = Blueprint('billing', __name__, url_prefix='/billing')

# ✅ PDFKit config - adjust if needed
PDFKIT_PATH = r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
config = pdfkit.configuration(wkhtmltopdf=PDFKIT_PATH)

def get_db_connection():
    conn = sqlite3.connect('db/sapthagiri.db')
    conn.row_factory = sqlite3.Row
    return conn

# ---------- STEP 1: Client Selection ----------
@billing_bp.route('/select')
def select_client():
    if session.get('role') != 'worker':
        return redirect(url_for('auth.login'))

    conn = get_db_connection()
    clients = conn.execute('SELECT * FROM Clients').fetchall()
    conn.close()
    return render_template('select_client.html', clients=clients)

# ---------- STEP 2: Invoice Generation ----------
@billing_bp.route('/invoice/<int:client_id>', methods=['GET', 'POST'])
def generate_invoice(client_id):
    if session.get('role') != 'worker':
        return redirect(url_for('auth.login'))

    conn = get_db_connection()
    client = conn.execute("SELECT * FROM Clients WHERE id = ?", (client_id,)).fetchone()
    items = conn.execute("SELECT * FROM Items").fetchall()

    price_data = conn.execute("""
        SELECT item_id, price FROM ClientItemPrices
        WHERE client_id = ?
    """, (client_id,)).fetchall()
    prices = {row["item_id"]: row["price"] for row in price_data}

    if request.method == 'POST':
        quantities = {int(k.split('_')[1]): int(v) for k, v in request.form.items() if v and v.isdigit()}
        invoice_items = []
        total = 0

        for item in items:
            qty = quantities.get(item['id'], 0)
            price = prices.get(item['id'], 0)
            if qty > 0:
                subtotal = qty * price
                total += subtotal
                invoice_items.append((item['id'], qty, price))

        if invoice_items:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO Invoices (client_id, worker) VALUES (?, ?)", 
                           (client_id, session.get('username')))
            invoice_id = cursor.lastrowid

            for item_id, qty, price in invoice_items:
                cursor.execute("INSERT INTO InvoiceItems (invoice_id, item_id, quantity, price) VALUES (?, ?, ?, ?)",
                               (invoice_id, item_id, qty, price))
            conn.commit()
            conn.close()

            return redirect(url_for('billing.view_invoice', invoice_id=invoice_id))

        conn.close()
        return redirect(url_for('billing.generate_invoice', client_id=client_id))

    conn.close()
    return render_template('generate_invoice.html', client=client, items=items, prices=prices)

# ---------- VIEW INVOICE ----------
@billing_bp.route('/view/<int:invoice_id>')
def view_invoice(invoice_id):
    if session.get('role') != 'worker':
        return redirect(url_for('auth.login'))

    conn = get_db_connection()
    invoice = conn.execute("SELECT * FROM Invoices WHERE id = ?", (invoice_id,)).fetchone()
    client = conn.execute("SELECT * FROM Clients WHERE id = ?", (invoice['client_id'],)).fetchone()

    items = conn.execute("""
        SELECT Items.name, Items.unit, InvoiceItems.price, InvoiceItems.quantity
        FROM InvoiceItems
        JOIN Items ON Items.id = InvoiceItems.item_id
        WHERE InvoiceItems.invoice_id = ?
    """, (invoice_id,)).fetchall()

    conn.close()

    total = sum(item['price'] * item['quantity'] for item in items)
    return render_template("invoice.html", client=client, items=items, total=total,
                           date=invoice['created_at'], invoice_id=invoice_id, is_pdf=False)

# ---------- EXPORT TO PDF ----------
@billing_bp.route('/export/pdf/<int:invoice_id>')
def export_invoice_pdf(invoice_id):
    if session.get('role') != 'worker':
        return redirect(url_for('auth.login'))

    conn = get_db_connection()
    invoice = conn.execute("SELECT * FROM Invoices WHERE id = ?", (invoice_id,)).fetchone()
    client = conn.execute("SELECT * FROM Clients WHERE id = ?", (invoice['client_id'],)).fetchone()

    items = conn.execute("""
        SELECT Items.name, Items.unit, InvoiceItems.price, InvoiceItems.quantity
        FROM InvoiceItems
        JOIN Items ON Items.id = InvoiceItems.item_id
        WHERE InvoiceItems.invoice_id = ?
    """, (invoice_id,)).fetchall()

    conn.close()

    total = sum(item['price'] * item['quantity'] for item in items)
    html = render_template("invoice.html", client=client, items=items, total=total,
                           date=invoice['created_at'], invoice_id=invoice_id, is_pdf=True)

    pdf = pdfkit.from_string(html, False, configuration=config)

    return (
        pdf,
        200,
        {
            'Content-Type': 'application/pdf',
            'Content-Disposition': f'attachment; filename=invoice_{invoice_id}.pdf'
        }
    )
