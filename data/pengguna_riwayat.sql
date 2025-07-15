
CREATE TABLE pengguna (
    id_pengguna INT PRIMARY KEY AUTO_INCREMENT,
    nama_pengguna VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    kata_sandi VARCHAR(255) NOT NULL,
    tanggal_lahir DATE,
    nomor_telepon VARCHAR(20),
    foto_profil VARCHAR(255),
    dibuat_pada DATETIME DEFAULT CURRENT_TIMESTAMP,
    diperbarui_pada DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE riwayat_kata_sandi (
    id_riwayat INT PRIMARY KEY AUTO_INCREMENT,
    id_pengguna INT NOT NULL,
    kata_sandi_lama VARCHAR(255) NOT NULL,
    diubah_pada DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_pengguna) REFERENCES pengguna(id_pengguna) ON DELETE CASCADE
);
