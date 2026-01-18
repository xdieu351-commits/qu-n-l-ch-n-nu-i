import sqlite3
import os

DB_NAME = 'chan_nuoi.db' # Có thể đổi tên thành chan_nuoi.db nếu muốn, nhưng nhớ sửa cả bên main.py

def create_database():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Bảng dữ liệu chăn nuôi
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS du_lieu_chan_nuoi (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        huyen TEXT,
        xa TEXT,
        nam INTEGER,
        con_trau INTEGER,
        con_bo INTEGER,
        con_lon INTEGER,
        con_de INTEGER,
        tong_xuat_chuong INTEGER,
        san_luong_thit REAL
    )
    ''')
    
    conn.commit()
    conn.close()
    print(f"Đã khởi tạo database mới với bảng Chăn Nuôi: {DB_NAME}")

if __name__ == "__main__":
    create_database()