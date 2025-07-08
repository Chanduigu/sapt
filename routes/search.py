from flask import Blueprint, render_template, request
import sqlite3

search_bp = Blueprint('search', __name__, url_prefix='/search')

def get_db_connection():
    conn = sqlite3.connect('db/sapthagiri.db')
    conn.row_factory = sqlite3.Row
    return conn

@search_bp.route('/', methods=['GET'])
def search_invoices():
    shop_name = request.args.get('shop_name')
    date = request.args.get('date')

    conn = get_db_connection()
    query = """
        SELECT Invoices.id AS invoice_id, Clients.shop_name, Invoices.created_at,
               Invoices.worker, Invoices.total_amount
        FROM Invoices
        JOIN Clients ON Clients.id = Invoices.client_id
        WHERE 1 = 1
    """
    params = []

    if shop_name:
        query += " AND Clients.shop_name LIKE ?"
        params.append(f"%{shop_name}%")

    if date:
        query += " AND DATE(Invoices.created_at) = ?"
        params.append(date)

    results = conn.execute(query, params).fetchall()
    conn.close()

    return render_template('search_invoices.html', results=results)
