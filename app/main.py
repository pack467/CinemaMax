from flask import Blueprint, render_template, session, redirect, url_for, request, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from app.utils import get_db_connection
from app.knn import recommend_by_genre
from app.trend import get_trending_films, get_trending_count
from app.new import get_new_films, get_new_count
import os

main = Blueprint('main', __name__, template_folder='templates')
UPLOAD_FOLDER = 'app/static/images'
PER_PAGE = 18

def get_user_profile():
    user_id = session.get('user_id')
    if not user_id:
        return None
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM pengguna WHERE id_pengguna=%s", (user_id,))
    user = cur.fetchone()
    cur.close()
    conn.close()
    return user

def get_knn_count(user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT COUNT(*) FROM film WHERE id NOT IN (
            SELECT id_film FROM riwayat_tonton WHERE id_pengguna = %s
        )
    """, (user_id,))
    count = cur.fetchone()[0]
    cur.close()
    conn.close()
    return count

@main.route('/')
def home():
    return redirect(url_for('main.beranda'))

@main.route('/beranda')
def beranda():
    user_id = session.get('user_id')
    user_name = session.get('user_name')
    user = get_user_profile()

    trending_film = get_trending_films(limit=1)
    trending_film = trending_film[0] if trending_film else {}

    new_film = get_new_films(limit=1)
    new_film = new_film[0] if new_film else {}

    rekomendasi = recommend_by_genre(user_id, limit=6) if user_id else []
    recommended_film = rekomendasi[0] if rekomendasi else {}

    banner = [trending_film, new_film, recommended_film]

    terbaru = get_new_films(limit=6)
    tren = get_trending_films(limit=6)

    return render_template(
        'beranda.html',
        user_name=user_name,
        user=user,
        banner=banner,
        rekomendasi=rekomendasi,
        terbaru=terbaru,
        tren=tren
    )

@main.route('/serial')
def serial():
    user = get_user_profile()
    user_name = session.get('user_name')
    return render_template('serial.html', user=user, user_name=user_name)

@main.route('/serial_data')
def serial_data():
    user = get_user_profile()
    user_id = session.get('user_id')
    filter_name = request.args.get('filter', 'trending')
    page = int(request.args.get('page', 1))
    offset = (page - 1) * PER_PAGE

    if filter_name == 'recommended':
        all_rekom = recommend_by_genre(user_id, limit=None) if user_id else []
        total = len(all_rekom)
        all_film = all_rekom[offset:offset + PER_PAGE]
    elif filter_name == 'new':
        all_film = get_new_films(limit=PER_PAGE, offset=offset)
        total = get_new_count()
    else:
        all_film = get_trending_films(limit=PER_PAGE, offset=offset)
        total = get_trending_count()

    films_json = []
    for film in all_film:
        films_json.append({
            'id': film['id'],
            'judul': film['judul'],
            'tahun_rilis': film['tahun_rilis'],
            'rating': float(film['rating']),
            'gambar_portrait': film['gambar_portrait'],
            'genres': film['genres'],
            'genres_list': [g.strip() for g in film['genres'].split(',')] if film['genres'] else []
        })

    return jsonify({
        'films': films_json,
        'total': total
    })

@main.route('/genre')
def genre():
    user = get_user_profile()
    user_name = session.get('user_name')
    return render_template('genre.html', user=user, user_name=user_name)

@main.route('/genre_data')
def genre_data():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    if request.args.get('all_genres'):
        cur.execute("SELECT genres FROM film")
        genres_set = set()
        for row in cur.fetchall():
            for g in (row['genres'] or '').split(','):
                g = g.strip()
                if g:
                    genres_set.add(g)
        cur.close()
        conn.close()
        return jsonify({'genres': sorted(genres_set)})

    genre = request.args.get('genre', '')
    page = int(request.args.get('page', 1))
    offset = (page - 1) * PER_PAGE
    cur.execute(
        "SELECT * FROM film WHERE genres LIKE %s ORDER BY rating DESC, tahun_rilis DESC LIMIT %s OFFSET %s",
        (f"%{genre}%", PER_PAGE, offset)
    )
    films = cur.fetchall()
    cur.execute("SELECT COUNT(*) FROM film WHERE genres LIKE %s", (f"%{genre}%",))
    total = cur.fetchone()['COUNT(*)']
    cur.close()
    conn.close()
    films_json = []
    for film in films:
        genres_list = [g.strip() for g in (film['genres'] or '').split(',')] if film['genres'] else []
        films_json.append({
            'id': film['id'],
            'judul': film['judul'],
            'tahun_rilis': film['tahun_rilis'],
            'rating': float(film['rating']),
            'gambar_portrait': film['gambar_portrait'],
            'genres': film['genres'],
            'genres_list': genres_list
        })
    return jsonify({'films': films_json, 'total': total})

@main.route('/favorite')
def favorite():
    user = get_user_profile()
    user_name = session.get('user_name')
    favorite_films = []
    if user:
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT f.* FROM favorite_film fav
            JOIN film f ON fav.id_film = f.id
            WHERE fav.id_pengguna = %s
            ORDER BY fav.created_at DESC
        """, (user['id_pengguna'],))
        favorite_films = cur.fetchall()
        cur.close()
        conn.close()
    return render_template('favorite.html', user=user, user_name=user_name, favorite_films=favorite_films)

@main.route('/toggle_favorite', methods=['POST'])
def toggle_favorite():
    user_id = session.get('user_id')
    film_id = request.form.get('film_id')
    if not user_id or not film_id:
        return jsonify({'success': False, 'msg': 'Not logged in or invalid film id'})
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM favorite_film WHERE id_pengguna=%s AND id_film=%s", (user_id, film_id))
    already_fav = cur.fetchone()
    if already_fav:
        cur.execute("DELETE FROM favorite_film WHERE id_pengguna=%s AND id_film=%s", (user_id, film_id))
        conn.commit()
        is_favorite = False
    else:
        cur.execute(
            "INSERT INTO favorite_film (id_pengguna, id_film, created_at) VALUES (%s, %s, NOW())",
            (user_id, film_id)
        )
        conn.commit()
        is_favorite = True
    cur.close()
    conn.close()
    return jsonify({'success': True, 'is_favorite': is_favorite})

@main.route('/watch')
def watch():
    film_id = request.args.get('id')
    user_id = session.get('user_id')
    user_name = session.get('user_name')
    user = get_user_profile()

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM film WHERE id = %s", (film_id,))
    film = cur.fetchone()

    # === Tambahan: cek status favorite ===
    is_favorite = False
    if user_id and film:
        cur.execute("SELECT 1 FROM favorite_film WHERE id_pengguna=%s AND id_film=%s", (user_id, film_id))
        is_favorite = cur.fetchone() is not None

    # sistem rekomendasi
    related_films = []
    if film and user_id:
        recommendations = recommend_by_genre(user_id, limit=4)
        related_films = [rec for rec in recommendations if rec['id'] != int(film_id)][:4]
        if len(related_films) < 4:
            needed = 4 - len(related_films)
            existing_ids = [rec['id'] for rec in related_films] + [int(film_id)]
            genre_list = [g.strip() for g in film['genres'].split(',')] if film['genres'] else []
            if genre_list:
                genre_filter = '|'.join(genre_list)
                placeholders = ','.join(['%s'] * len(existing_ids))
                cur.execute(f"""
                    SELECT * FROM film 
                    WHERE id NOT IN ({placeholders}) 
                    AND genres REGEXP %s 
                    ORDER BY rating DESC, tahun_rilis DESC 
                    LIMIT %s
                """, tuple(existing_ids + [genre_filter, needed]))
                additional_films = cur.fetchall()
                related_films.extend(additional_films)
    elif film:
        genre_list = [g.strip() for g in film['genres'].split(',')] if film['genres'] else []
        if genre_list:
            genre_filter = '|'.join(genre_list)
            cur.execute("""
                SELECT * FROM film 
                WHERE id != %s AND genres REGEXP %s 
                ORDER BY rating DESC, tahun_rilis DESC 
                LIMIT 4
            """, (film_id, genre_filter))
            related_films = cur.fetchall()
    cur.close()
    conn.close()

    # auto-insert ke riwayat_tonton
    if user_id and film_id and film:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM riwayat_tonton WHERE id_pengguna=%s AND id_film=%s", (user_id, film_id))
        if not cur.fetchone():
            cur.execute(
                "INSERT INTO riwayat_tonton (id_pengguna, id_film) VALUES (%s, %s)",
                (user_id, film_id)
            )
            conn.commit()
        cur.close()
        conn.close()

    if not film:
        return "Film tidak ditemukan", 404

    return render_template(
        'watch.html',
        film=film,
        related_films=related_films,
        user=user,
        user_name=user_name,
        is_favorite=is_favorite
    )

@main.route('/search')
def search():
    query = request.args.get('q', '').strip()
    user = get_user_profile()
    user_name = session.get('user_name')
    page = int(request.args.get('page', 1))
    per_page = 18
    offset = (page - 1) * per_page
    
    # Ambil parameter filter dari URL
    selected_genres = request.args.getlist('genres')  # Multiple genres
    selected_year = request.args.get('year', 'all')
    selected_rating = request.args.get('rating', 'all')
    selected_series = request.args.get('series', 'trending')

    results = []
    total = 0

    if query or selected_genres or selected_year != 'all' or selected_rating != 'all':
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        
        # Build base query
        base_query = """
            SELECT * FROM film
            WHERE 1=1
        """
        count_query = """
            SELECT COUNT(*) as total FROM film
            WHERE 1=1
        """
        
        params = []
        
        # Add search text filter
        if query:
            base_query += " AND (judul LIKE %s OR genres LIKE %s OR tahun_rilis LIKE %s)"
            count_query += " AND (judul LIKE %s OR genres LIKE %s OR tahun_rilis LIKE %s)"
            search_param = f"%{query}%"
            params.extend([search_param, search_param, search_param])
        
        # Add genre filter
        if selected_genres:
            genre_conditions = []
            for genre in selected_genres:
                genre_conditions.append("genres LIKE %s")
                params.append(f"%{genre}%")
            base_query += " AND (" + " OR ".join(genre_conditions) + ")"
            count_query += " AND (" + " OR ".join(genre_conditions) + ")"
        
        # Add year filter - Updated to handle individual years
        if selected_year != 'all':
            # Check if it's a single year or range
            if selected_year.isdigit():
                # Single year
                base_query += " AND tahun_rilis = %s"
                count_query += " AND tahun_rilis = %s"
                params.extend([int(selected_year)])
            elif '-' in selected_year:
                # Range (for backward compatibility)
                start_year, end_year = selected_year.split('-')
                base_query += " AND tahun_rilis BETWEEN %s AND %s"
                count_query += " AND tahun_rilis BETWEEN %s AND %s"
                params.extend([int(start_year), int(end_year)])
        
        # Add rating filter
        if selected_rating != 'all':
            if '-' in selected_rating:
                start_rating, end_rating = selected_rating.split('-')
                base_query += " AND rating BETWEEN %s AND %s"
                count_query += " AND rating BETWEEN %s AND %s"
                params.extend([float(start_rating), float(end_rating)])
        
        # Add sorting based on series filter
        if selected_series == 'new':
            base_query += " ORDER BY tahun_rilis DESC, id DESC"
        elif selected_series == 'recommended':
            base_query += " ORDER BY (rating * 0.7 + (tahun_rilis - 2000) * 0.3) DESC"
        else:  # trending
            base_query += " ORDER BY rating DESC, tahun_rilis DESC"
        
        # Execute count query
        cur.execute(count_query, params)
        total = cur.fetchone()['total']
        
        # Execute main query with pagination
        base_query += " LIMIT %s OFFSET %s"
        params.extend([per_page, offset])
        
        cur.execute(base_query, params)
        results = cur.fetchall()
        
        cur.close()
        conn.close()

    return render_template(
        'search.html',
        query=query,
        results=results,
        total=total,
        page=page,
        per_page=per_page,
        user=user,
        user_name=user_name,
        selected_genres=selected_genres,
        selected_year=selected_year,
        selected_rating=selected_rating,
        selected_series=selected_series
    )

@main.route('/profile', methods=['GET', 'POST'])
def profile():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('auth.login'))

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM pengguna WHERE id_pengguna = %s", (user_id,))
    user = cur.fetchone()

    if request.method == 'POST':
        nama_pengguna = request.form.get('nama_pengguna')
        email = request.form.get('email')
        tanggal_lahir = request.form.get('tanggal_lahir') or None
        nomor_telepon = request.form.get('nomor_telepon') or None

        foto_file = request.files.get('foto_profil')
        foto_profil = user['foto_profil']
        if foto_file and foto_file.filename != '':
            filename = secure_filename(foto_file.filename)
            foto_file.save(os.path.join(UPLOAD_FOLDER, filename))
            foto_profil = filename

        try:
            cur.execute("""
                UPDATE pengguna SET nama_pengguna=%s, email=%s, tanggal_lahir=%s, nomor_telepon=%s, foto_profil=%s
                WHERE id_pengguna=%s
            """, (nama_pengguna, email, tanggal_lahir, nomor_telepon, foto_profil, user_id))
            conn.commit()
            flash('Profil berhasil diperbarui.', 'success')
            session['user_name'] = nama_pengguna
        except Exception as e:
            flash('Gagal memperbarui profil.', 'danger')

        cur.execute("SELECT * FROM pengguna WHERE id_pengguna = %s", (user_id,))
        user = cur.fetchone()

    cur.close()
    conn.close()
    return render_template('profile.html', user=user)

@main.route('/ganti_password', methods=['POST'])
def ganti_password():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('auth.login'))

    password_lama = request.form.get('password_lama')
    password_baru = request.form.get('password_baru')
    password_konfirmasi = request.form.get('password_konfirmasi')

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM pengguna WHERE id_pengguna = %s", (user_id,))
    user = cur.fetchone()

    if not user or not check_password_hash(user['kata_sandi'], password_lama):
        flash('Password lama salah.', 'danger')
        cur.close()
        conn.close()
        return redirect(url_for('main.profile'))

    if password_baru != password_konfirmasi:
        flash('Password baru dan konfirmasi tidak cocok.', 'danger')
        cur.close()
        conn.close()
        return redirect(url_for('main.profile'))

    if check_password_hash(user['kata_sandi'], password_baru):
        flash('Password baru tidak boleh sama dengan password lama.', 'danger')
        cur.close()
        conn.close()
        return redirect(url_for('main.profile'))

    cur2 = conn.cursor()
    cur2.execute("SELECT id_riwayat FROM riwayat_kata_sandi WHERE id_pengguna=%s", (user_id,))
    row = cur2.fetchone()
    if row:
        cur2.execute(
            "UPDATE riwayat_kata_sandi SET kata_sandi_lama=%s, diubah_pada=NOW() WHERE id_pengguna=%s",
            (password_lama, user_id)
        )
    else:
        cur2.execute(
            "INSERT INTO riwayat_kata_sandi (id_pengguna, kata_sandi_lama) VALUES (%s, %s)",
            (user_id, password_lama)
        )

    hashed_pw = generate_password_hash(password_baru)
    cur2.execute(
        "UPDATE pengguna SET kata_sandi=%s WHERE id_pengguna=%s",
        (hashed_pw, user_id)
    )

    conn.commit()
    cur.close()
    cur2.close()
    conn.close()
    flash('Password berhasil diperbarui.', 'success')
    return redirect(url_for('main.profile'))
