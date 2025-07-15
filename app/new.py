# new.py
from app.utils import get_db_connection

def get_new_films(limit=6, offset=0):
    """
    Mengambil film-film terbaru berdasarkan tahun rilis dan ID.
    Support pagination via limit dan offset.
    """
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    sql = """
        SELECT * FROM film
        ORDER BY tahun_rilis DESC, id DESC
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

def get_new_count():
    """
    Mendapatkan jumlah total film (untuk pagination baru).
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM film")
    count = cur.fetchone()[0]
    cur.close()
    conn.close()
    return count
