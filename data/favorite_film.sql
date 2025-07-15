-- Membuat tabel favorite_film
CREATE TABLE IF NOT EXISTS favorite_film (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_pengguna INT NOT NULL,
    id_film INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unik_favorite (id_pengguna, id_film)
);
