import sqlite3
import random
import os

# Dữ liệu mẫu Bắc Kạn
DATA_BAC_KAN = {
    "Thành phố Bắc Kạn": ["Phường Phùng Chí Kiên", "Phường Sông Cầu", "Phường Đức Xuân", "Xã Dương Quang", "Xã Nông Thượng"],
    "Huyện Ba Bể": ["Thị trấn Chợ Rã", "Xã Nam Mẫu", "Xã Khang Ninh", "Xã Quảng Khê", "Xã Đồng Phúc"],
    "Huyện Bạch Thông": ["Thị trấn Phủ Thông", "Xã Lục Bình", "Xã Vi Hương", "Xã Cẩm Giàng", "Xã Quân Hà"],
    "Huyện Chợ Đồn": ["Thị trấn Bằng Lũng", "Xã Bản Thi", "Xã Bình Trung", "Xã Nghĩa Tá", "Xã Phương Viên"],
    "Huyện Chợ Mới": ["Thị trấn Đồng Tâm", "Xã Nông Hạ", "Xã Yên Đĩnh", "Xã Như Cố", "Xã Bình Văn"],
    "Huyện Na Rì": ["Thị trấn Yến Lạc", "Xã Côn Minh", "Xã Kim Hỷ", "Xã Cư Lễ", "Xã Xuân Dương"],
    "Huyện Ngân Sơn": ["Thị trấn Vân Tùng", "Xã Cốc Đán", "Xã Bằng Vân", "Xã Thuần Mang", "Xã Thượng Quan"],
    "Huyện Pác Nặm": ["Xã Bộc Bố", "Xã Cổ Linh", "Xã Nghiên Loan", "Xã Công Bằng", "Xã Nhạn Môn"]
}

DB_PATH = 'chan_nuoi.db'

def seed_data(number_of_records=50):
    if not os.path.exists(DB_PATH):
        print(f"❌ Không tìm thấy file {DB_PATH}. Hãy chạy main.py trước.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Xóa dữ liệu cũ (reset lại từ đầu cho sạch)
    cursor.execute("DELETE FROM du_lieu_chan_nuoi") 
    
    # Reset ID về 1
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='du_lieu_chan_nuoi'")

    print(f"🔄 Đang sinh {number_of_records} bản ghi chăn nuôi Bắc Kạn...")
    data_to_insert = []
    
    districts = list(DATA_BAC_KAN.keys())

    for _ in range(number_of_records):
        # Chọn ngẫu nhiên Huyện và Xã thuộc Huyện đó
        huyen = random.choice(districts)
        xa = random.choice(DATA_BAC_KAN[huyen])
        
        nam = random.randint(2021, 2024)
        
        # Số liệu ngẫu nhiên
        trau = random.randint(50, 500)
        bo = random.randint(100, 1000)
        lon = random.randint(500, 5000)
        de = random.randint(50, 300)
        
        # Logic giả định: Xuất chuồng khoảng 40-60% tổng đàn
        tong_dan = trau + bo + lon + de
        xuat_chuong = int(tong_dan * random.uniform(0.4, 0.6))
        
        # Sản lượng thịt (tấn) ~ trọng lượng trung bình * số xuất chuồng / 1000
        # Giả sử trung bình 1 con (tính gộp) nặng 80kg
        san_luong_thit = round((xuat_chuong * 80) / 1000, 2)

        record = (huyen, xa, nam, trau, bo, lon, de, xuat_chuong, san_luong_thit)
        data_to_insert.append(record)

    sql = '''INSERT INTO du_lieu_chan_nuoi 
             (huyen, xa, nam, con_trau, con_bo, con_lon, con_de, tong_xuat_chuong, san_luong_thit)
             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)'''
    
    cursor.executemany(sql, data_to_insert)
    conn.commit()
    conn.close()
    print(f"✅ Đã thêm xong dữ liệu mẫu Bắc Kạn!")

if __name__ == "__main__":
    seed_data(50) # Tạo 50 bản ghi