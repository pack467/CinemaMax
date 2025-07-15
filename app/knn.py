# knn.py - Improved Recommendation System
from app.utils import get_db_connection
from collections import Counter
import math
import random

def get_all_genres():
    """Ambil seluruh genre unik di database film."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT genres FROM film")
    genres_list = set()
    for (genres,) in cur.fetchall():
        if genres:
            for g in genres.split(','):
                stripped = g.strip()
                if stripped:
                    genres_list.add(stripped)
    cur.close()
    conn.close()
    return sorted(genres_list)

def get_user_genre_profile(user_id):
    """Hitung preferensi genre user dari riwayat tonton."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT f.genres, r.waktu_tonton FROM riwayat_tonton r
        JOIN film f ON r.id_film = f.id
        WHERE r.id_pengguna = %s
        ORDER BY r.waktu_tonton DESC
    """, (user_id,))
    
    genre_counts = Counter()
    total_films = 0
    
    for genres, waktu_tonton in cur.fetchall():
        if not genres:
            continue
            
        total_films += 1
        # Berikan bobot lebih pada film yang baru ditonton
        time_weight = min(1.0, total_films / 10.0)
        
        for g in genres.split(','):
            genre = g.strip()
            if genre:
                genre_counts[genre] += 1.0 * time_weight
    
    # Normalisasi ke bentuk probabilitas
    if total_films > 0:
        for genre in genre_counts:
            genre_counts[genre] = genre_counts[genre] / total_films
    
    cur.close()
    conn.close()
    return genre_counts

def get_user_preferred_genres(user_id, min_threshold=0.1):
    """Dapatkan set genre yang disukai user."""
    user_genre_profile = get_user_genre_profile(user_id)
    if not user_genre_profile:
        return set()
    
    preferred_genres = set()
    sorted_genres = sorted(user_genre_profile.items(), key=lambda x: x[1], reverse=True)
    
    # Ambil genre dengan skor di atas threshold atau minimal 3 genre teratas
    for genre, score in sorted_genres:
        if score >= min_threshold or len(preferred_genres) < 3:
            preferred_genres.add(genre)
        if len(preferred_genres) >= 5:  # Maksimal 5 genre
            break
    
    return preferred_genres

def get_candidate_films(user_id):
    """Film yang belum ditonton user dengan data tambahan."""
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT f.*, 
               (SELECT COUNT(*) FROM riwayat_tonton rt WHERE rt.id_film = f.id) as popularity_count
        FROM film f 
        WHERE f.id NOT IN (
            SELECT COALESCE(id_film, 0) FROM riwayat_tonton WHERE id_pengguna = %s
        )
    """, (user_id,))
    films = cur.fetchall()
    cur.close()
    conn.close()
    return films

def calculate_jaccard_similarity(set_a, set_b):
    """Hitung Jaccard Similarity antara dua set."""
    if not set_a or not set_b:
        return 0.0
    
    intersection = len(set_a.intersection(set_b))
    union = len(set_a.union(set_b))
    
    return intersection / union if union > 0 else 0.0

def get_film_genres_set(film_genres):
    """Convert string genre film menjadi set."""
    if not film_genres:
        return set()
    return set(g.strip() for g in film_genres.split(',') if g.strip())

def normalize_rating(rating, min_rating=0, max_rating=10):
    """Normalisasi rating ke rentang 0-1."""
    return (float(rating) - min_rating) / (max_rating - min_rating)

def normalize_year(year, min_year=2020, max_year=2025):
    """Normalisasi tahun rilis ke rentang 0-1."""
    return (year - min_year) / (max_year - min_year)

def calculate_final_score(jaccard_score, rating, year, w1=0.6, w2=0.25, w3=0.15):
    """
    Hitung skor akhir menggunakan formula yang disarankan:
    Skor Akhir = (J × w1) + (R × w2) + (T × w3)
    
    Updated weights to match Word formula:
    - w1 = 0.6 (Jaccard Similarity - prioritas utama)
    - w2 = 0.25 (Rating - sesuai formula Word)
    - w3 = 0.15 (Tahun rilis - sesuai formula Word)
    
    Note: Popularitas dihapus dari formula untuk menyesuaikan dengan Word
    """
    normalized_rating = normalize_rating(rating)
    normalized_year = normalize_year(year)
    
    final_score = (jaccard_score * w1) + (normalized_rating * w2) + (normalized_year * w3)
    return final_score

def apply_diversity_penalty(recommended_films, candidate_film, penalty_factor=0.03):
    """Terapkan penalty untuk diversity - lebih ringan."""
    if not recommended_films:
        return 0
    
    candidate_genres = get_film_genres_set(candidate_film['genres'])
    overlap_count = 0
    
    for rec_film in recommended_films:
        rec_genres = get_film_genres_set(rec_film['genres'])
        if candidate_genres & rec_genres:
            overlap_count += 1
    
    # Penalty ringan dan hanya berlaku setelah beberapa film
    if len(recommended_films) < 8:
        return 0
    
    return overlap_count * penalty_factor

def knn_recommendation_improved(user_id, top_n=6, offset=0):
    """
    Algoritma rekomendasi yang mengikuti formula Word:
    1. Hitung Jaccard Similarity untuk semua film kandidat
    2. Filter film dengan Jaccard >= threshold
    3. Hitung skor akhir menggunakan formula: (J × 0.6) + (R × 0.25) + (T × 0.15)
    4. Urutkan berdasarkan skor akhir
    5. Terapkan diversity penalty yang ringan
    
    Formula disesuaikan dengan Word Document:
    - Jaccard: 60%
    - Rating: 25% 
    - Tahun Rilis: 15%
    - Popularitas: Dihapus dari formula utama
    """
    user_preferred_genres = get_user_preferred_genres(user_id)
    
    # Fallback untuk user baru
    if not user_preferred_genres:
        return get_fallback_recommendations(user_id, top_n, offset)
    
    candidate_films = get_candidate_films(user_id)
    if not candidate_films:
        return []
    
    # Tahap 1: Hitung Jaccard Similarity untuk semua film
    films_with_scores = []
    jaccard_threshold = 0.3  # Threshold minimum untuk Jaccard
    
    for film in candidate_films:
        film_genres = get_film_genres_set(film['genres'])
        jaccard_score = calculate_jaccard_similarity(user_preferred_genres, film_genres)
        
        # Filter berdasarkan Jaccard threshold
        if jaccard_score >= jaccard_threshold:
            final_score = calculate_final_score(
                jaccard_score, 
                film['rating'], 
                film['tahun_rilis']
            )
            films_with_scores.append((final_score, jaccard_score, film))
    
    # Jika tidak ada film yang memenuhi threshold, turunkan threshold
    if not films_with_scores:
        jaccard_threshold = 0.1
        for film in candidate_films:
            film_genres = get_film_genres_set(film['genres'])
            jaccard_score = calculate_jaccard_similarity(user_preferred_genres, film_genres)
            
            if jaccard_score >= jaccard_threshold:
                final_score = calculate_final_score(
                    jaccard_score, 
                    film['rating'], 
                    film['tahun_rilis']
                )
                films_with_scores.append((final_score, jaccard_score, film))
    
    # Tahap 2: Urutkan berdasarkan skor akhir
    films_with_scores.sort(key=lambda x: x[0], reverse=True)
    
    # Tahap 3: Shuffle untuk variasi (dengan seed konsisten)
    random.seed(user_id)
    top_candidates = films_with_scores[:min(len(films_with_scores), 50)]
    random.shuffle(top_candidates)
    
    # Tahap 4: Seleksi final dengan diversity penalty
    recommended = []
    
    for final_score, jaccard_score, film in top_candidates:
        diversity_penalty = apply_diversity_penalty(recommended, film)
        adjusted_score = final_score - diversity_penalty
        
        # Terima film jika skor masih positif atau belum cukup rekomendasi
        min_threshold = 0.1
        min_count = 20 if top_n is None else max(15, top_n * 2)
        
        if adjusted_score > min_threshold or len(recommended) < min_count:
            recommended.append(film)
        
        # Batasi untuk unlimited request
        if top_n is None and len(recommended) >= 80:
            break
    
    # Tahap 5: Pagination
    if isinstance(top_n, int) and top_n > 0:
        paginated = recommended[offset:offset + top_n]
        
        # Tambahkan fallback jika masih kurang
        if len(paginated) < top_n:
            extra_needed = top_n - len(paginated)
            existing_ids = {f['id'] for f in recommended}
            
            fallback_films = get_fallback_recommendations(
                user_id, extra_needed, 0, exclude_ids=existing_ids
            )
            paginated.extend(fallback_films)
        
        return paginated[:top_n]
    
    return recommended

def get_fallback_recommendations(user_id, limit, offset, exclude_ids=None):
    """
    Rekomendasi fallback berdasarkan popularitas dan rating.
    Popularitas tetap digunakan untuk fallback meskipun dihapus dari formula utama.
    """
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    
    exclude_condition = ""
    params = [user_id]
    
    if exclude_ids:
        placeholders = ",".join(["%s"] * len(exclude_ids))
        exclude_condition = f"AND f.id NOT IN ({placeholders})"
        params.extend(list(exclude_ids))
    
    sql = f"""
        SELECT f.*, 
               (SELECT COUNT(*) FROM riwayat_tonton rt WHERE rt.id_film = f.id) as popularity_count
        FROM film f 
        WHERE f.id NOT IN (
            SELECT COALESCE(id_film, 0) FROM riwayat_tonton WHERE id_pengguna = %s
        )
        {exclude_condition}
        ORDER BY f.rating DESC, popularity_count DESC, f.tahun_rilis DESC
    """
    
    if limit and limit > 0:
        sql += " LIMIT %s"
        params.append(limit)
        if offset:
            sql += " OFFSET %s"
            params.append(offset)
    
    cur.execute(sql, tuple(params))
    films = cur.fetchall()
    cur.close()
    conn.close()
    return films

def recommend_by_genre(user_id, limit=6, offset=0):
    """
    Fungsi utama untuk rekomendasi berdasarkan genre.
    Menggunakan formula Word: (J × 0.6) + (R × 0.25) + (T × 0.15)
    """
    if not user_id:
        return get_fallback_recommendations(None, limit, offset)
    
    return knn_recommendation_improved(user_id, top_n=limit, offset=offset)

def get_recommendation_debug_info(user_id, film_id):
    """
    Dapatkan informasi debug untuk rekomendasi tertentu.
    Updated untuk menampilkan formula Word yang baru.
    """
    user_preferred_genres = get_user_preferred_genres(user_id)
    
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM film WHERE id = %s", (film_id,))
    film = cur.fetchone()
    cur.close()
    conn.close()
    
    if not film:
        return None
    
    film_genres = get_film_genres_set(film['genres'])
    jaccard_score = calculate_jaccard_similarity(user_preferred_genres, film_genres)
    final_score = calculate_final_score(jaccard_score, film['rating'], film['tahun_rilis'])
    
    return {
        'user_preferred_genres': list(user_preferred_genres),
        'film_genres': list(film_genres),
        'genre_intersection': list(user_preferred_genres.intersection(film_genres)),
        'jaccard_similarity': jaccard_score,
        'normalized_rating': normalize_rating(film['rating']),
        'normalized_year': normalize_year(film['tahun_rilis']),
        'final_score': final_score,
        'formula_breakdown': {
            'jaccard_component': jaccard_score * 0.6,
            'rating_component': normalize_rating(film['rating']) * 0.25,
            'year_component': normalize_year(film['tahun_rilis']) * 0.15
        },
        'formula_info': {
            'description': 'Formula Word: (Jaccard × 0.6) + (Rating × 0.25) + (Year × 0.15)',
            'weights': {
                'jaccard': '60%',
                'rating': '25%',
                'year': '15%',
                'popularity': 'Removed from main formula (only used in fallback)'
            }
        }
    }

def get_user_stats(user_id):
    """Dapatkan statistik user untuk debugging."""
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    
    # Hitung total film yang sudah ditonton
    cur.execute("SELECT COUNT(*) as watched_count FROM riwayat_tonton WHERE id_pengguna = %s", (user_id,))
    watched_count = cur.fetchone()['watched_count']
    
    # Hitung total film yang tersedia
    cur.execute("SELECT COUNT(*) as total_films FROM film")
    total_films = cur.fetchone()['total_films']
    
    # Hitung distribusi genre yang sudah ditonton
    cur.execute("""
        SELECT f.genres FROM riwayat_tonton r
        JOIN film f ON r.id_film = f.id
        WHERE r.id_pengguna = %s
    """, (user_id,))
    
    genre_distribution = Counter()
    for row in cur.fetchall():
        if row['genres']:
            for genre in row['genres'].split(','):
                genre = genre.strip()
                if genre:
                    genre_distribution[genre] += 1
    
    cur.close()
    conn.close()
    
    return {
        'watched_count': watched_count,
        'total_films': total_films,
        'unwatched_count': total_films - watched_count,
        'genre_distribution': dict(genre_distribution.most_common(10)),
        'preferred_genres': list(get_user_preferred_genres(user_id)),
        'formula_info': {
            'current_formula': '(Jaccard × 0.6) + (Rating × 0.25) + (Year × 0.15)',
            'weights': {
                'jaccard_similarity': '60%',
                'rating': '25%',
                'year': '15%',
                'popularity': 'Only used in fallback recommendations'
            }
        }
    }