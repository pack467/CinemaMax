# Install Python (jika belum ada)
# Download dari https://www.python.org/downloads/

# Masuk ke folder project
cd nama-folder-project

# Buat virtual environment
python -m venv venv

# Aktifkan virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependensi
pip install -r requirements.txt

# Import database (misal MySQL)
# mysql -u username -p nama_database < backup.sql

# Jalankan aplikasi
flask run
# atau
python main.py
#   C i n e m a M a x  
 #   C i n e m a M a x  
 