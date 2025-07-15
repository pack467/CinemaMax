from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from app.utils import get_db_connection

auth = Blueprint('auth', __name__, template_folder='templates')

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM pengguna WHERE email = %s", (email,))
        user = cur.fetchone()
        cur.close()
        conn.close()
        if user and check_password_hash(user['kata_sandi'], password):
            session['user_id'] = user['id_pengguna']
            session['user_name'] = user['nama_pengguna']
            return redirect(url_for('main.beranda'))
        else:
            flash("Email atau password salah!", "danger")
    return render_template('login.html')

@auth.route('/register', methods=['POST'])
def register():
    nama = request.form.get('nama')
    email = request.form.get('email')
    password = request.form.get('password')
    password_confirm = request.form.get('password_confirm')
    if password != password_confirm:
        flash("Konfirmasi password tidak cocok.", "danger")
        return redirect(url_for('auth.login'))
    conn = get_db_connection()
    cur = conn.cursor()
    hashed_pw = generate_password_hash(password)
    try:
        cur.execute("INSERT INTO pengguna (nama_pengguna, email, kata_sandi) VALUES (%s, %s, %s)",
                    (nama, email, hashed_pw))
        conn.commit()
        flash("Registrasi berhasil, silakan login!", "success")
    except Exception as e:
        flash("Email sudah terdaftar!", "danger")
    finally:
        cur.close()
        conn.close()
    return redirect(url_for('auth.login'))

@auth.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))
