from flask import render_template
from app.utils import get_db_connection

@main.route('/beranda')
def beranda():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    
    # Banner (ambil 3 film dengan rating tertinggi)
    cur.execute("SELECT * FROM film ORDER BY rating DESC LIMIT 3")
    banner = cur.fetchall()
    # Rekomendasi (misal 10 film genre action, atau sesuai algoritma kamu)
    cur.execute("SELECT * FROM film ORDER BY RAND() LIMIT 6")
    rekomendasi = cur.fetchall()
    # Terbaru (10 film paling baru)
    cur.execute("SELECT * FROM film ORDER BY tahun_rilis DESC LIMIT 6")
    terbaru = cur.fetchall()
    # Tren (10 film rating tinggi atau view terbanyak)
    cur.execute("SELECT * FROM film ORDER BY rating DESC LIMIT 6 OFFSET 3")
    tren = cur.fetchall()
    cur.close()
    conn.close()
    return render_template(
        'beranda.html',
        user_name=session['user_name'],
        banner=banner,
        rekomendasi=rekomendasi,
        terbaru=terbaru,
        tren=tren
    )

@main.route('/profile')
def profile():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('auth.login'))
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM pengguna WHERE id_pengguna = %s", (user_id,))
    user = cur.fetchone()
    cur.close()
    conn.close()
    if not user:
        return "User tidak ditemukan", 404
    return render_template(
        'profile.html',
        user=user
    )
