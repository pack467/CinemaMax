# trend.py
from app.utils import get_db_connection

def get_trending_films(limit=6, offset=0):
    """
    Mengambil film trending berdasarkan rating tertinggi.
    Support pagination via limit dan offset.
    """
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    sql = """
        SELECT * FROM film
        ORDER BY rating DESC, tahun_rilis DESC
        LIMIT %s
    """
    params = [limit]
    if offset:
        sql += " OFFSET %s"
        params.append(offset)
    cur.execute(sql, tuple(params))
    films = cur.fetchall()
    cur.close()
    conn.close()
    return films

def get_trending_count():
    """
    Mendapatkan jumlah total film trending (untuk pagination).
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM film")
    count = cur.fetchone()[0]
    cur.close()
    conn.close()
    return count
