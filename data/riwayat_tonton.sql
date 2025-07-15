
CREATE TABLE IF NOT EXISTS riwayat_tonton ( 
    id_riwayat INT PRIMARY KEY AUTO_INCREMENT,
    id_pengguna INT NOT NULL,
    id_film INT NOT NULL,
    waktu_tonton DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_pengguna) REFERENCES pengguna(id_pengguna) ON DELETE CASCADE,
    FOREIGN KEY (id_film) REFERENCES film(id) ON DELETE CASCADE
);
