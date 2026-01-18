import sqlite3

class ForestryModel:
    def __init__(self, db_name='chan_nuoi.db'):
        self.db_name = db_name

    def connect(self):
        return sqlite3.connect(self.db_name)

    # --- READ ---
    # --- READ (with Pagination & Search) ---
    def get_data(self, page=1, page_size=10, search_query=""):
        conn = self.connect()
        cursor = conn.cursor()
        
        offset = (page - 1) * page_size
        query = "SELECT * FROM du_lieu_chan_nuoi WHERE 1=1"
        params = []

        if search_query:
            query += " AND (huyen LIKE ? OR xa LIKE ?)"
            params.extend([f"%{search_query}%", f"%{search_query}%"])

        # --- SỬA Ở DÒNG DƯỚI NÀY ---
        # Cũ: query += " ORDER BY id DESC LIMIT ? OFFSET ?"
        # Mới: Đổi DESC thành ASC
        query += " ORDER BY id ASC LIMIT ? OFFSET ?"  
        
        params.extend([page_size, offset])

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        return rows

    def get_total_count(self, search_query=""):
        conn = self.connect()
        cursor = conn.cursor()
        query = "SELECT COUNT(*) FROM du_lieu_chan_nuoi WHERE 1=1"
        params = []
        
        if search_query:
            query += " AND (huyen LIKE ? OR xa LIKE ?)"
            params.extend([f"%{search_query}%", f"%{search_query}%"])
            
        cursor.execute(query, params)
        count = cursor.fetchone()[0]
        conn.close()
        return count

    # --- CREATE ---
    def add_record(self, data):
        conn = self.connect()
        cursor = conn.cursor()
        # data gồm: huyen, xa, nam, trau, bo, lon, de, xuat_chuong, thit
        sql = '''INSERT INTO du_lieu_chan_nuoi 
                 (huyen, xa, nam, con_trau, con_bo, con_lon, con_de, tong_xuat_chuong, san_luong_thit)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)'''
        cursor.execute(sql, data)
        conn.commit()
        conn.close()

    # --- UPDATE ---
    def update_record(self, record_id, data):
        conn = self.connect()
        cursor = conn.cursor()
        sql = '''UPDATE du_lieu_chan_nuoi SET
                 huyen=?, xa=?, nam=?, con_trau=?, con_bo=?, con_lon=?, con_de=?, 
                 tong_xuat_chuong=?, san_luong_thit=?
                 WHERE id=?'''
        cursor.execute(sql, data + (record_id,))
        conn.commit()
        conn.close()

    # --- DELETE ---
    def delete_record(self, record_id):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM du_lieu_chan_nuoi WHERE id=?", (record_id,))
        conn.commit()
        conn.close()