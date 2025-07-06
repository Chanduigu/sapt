from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import sqlite3

auth_bp = Blueprint('auth', __name__)

def get_db_connection():
    conn = sqlite3.connect('db/sapthagiri.db')
    conn.row_factory = sqlite3.Row
    return conn

@auth_bp.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        user = conn.execute("SELECT * FROM Users WHERE username = ? AND password = ?", 
                            (username, password)).fetchone()
        conn.close()

        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']

            if user['role'] == 'admin':
                return redirect(url_for('auth.admin_dashboard'))
            else:
                return redirect(url_for('auth.worker_dashboard'))
        else:
            flash("Invalid username or password")
            return render_template('login.html')
    return render_template('login.html')

@auth_bp.route('/admin/dashboard')
def admin_dashboard():
    if session.get('role') != 'admin':
        return redirect(url_for('auth.login'))
    return render_template('dashboard.html', role='admin')

@auth_bp.route('/worker/dashboard')
def worker_dashboard():
    if session.get('role') != 'worker':
        return redirect(url_for('auth.login'))
    return render_template('dashboard.html', role='worker')

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))
