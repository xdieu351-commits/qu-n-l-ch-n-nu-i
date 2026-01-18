import streamlit as st
import pandas as pd
import sqlite3
import time
import os

# --- CẤU HÌNH TRANG ---
st.set_page_config(
    page_title="Hệ thống Quản Lý Chăn Nuôi",
    page_icon="🐄",
    layout="wide"
)

# --- PHẦN 1: MODEL & DATABASE (Logic xử lý dữ liệu) ---
class ForestryModel:
    def __init__(self, db_name='chan_nuoi.db'):
        self.db_name = db_name
        self._check_and_init_db()

    def connect(self):
        return sqlite3.connect(self.db_name)

    def _check_and_init_db(self):
        """Tự động tạo bảng nếu chưa có (Tránh lỗi khi deploy lên server mới)"""
        if not os.path.exists(self.db_name):
            conn = self.connect()
            cursor = conn.cursor()
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

    def get_data(self, page=1, page_size=1000, search_query=""):
        conn = self.connect()
        cursor = conn.cursor()
        
        offset = (page - 1) * page_size
        query = "SELECT * FROM du_lieu_chan_nuoi WHERE 1=1"
        params = []

        if search_query:
            query += " AND (huyen LIKE ? OR xa LIKE ?)"
            params.extend([f"%{search_query}%", f"%{search_query}%"])

        # Sắp xếp ID giảm dần (Mới nhất lên đầu) hoặc Tăng dần tùy bạn
        query += " ORDER BY id DESC LIMIT ? OFFSET ?"
        params.extend([page_size, offset])

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        return rows

    def add_record(self, data):
        conn = self.connect()
        cursor = conn.cursor()
        sql = '''INSERT INTO du_lieu_chan_nuoi 
                 (huyen, xa, nam, con_trau, con_bo, con_lon, con_de, tong_xuat_chuong, san_luong_thit)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)'''
        cursor.execute(sql, data)
        conn.commit()
        conn.close()

    def delete_record(self, record_id):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM du_lieu_chan_nuoi WHERE id=?", (record_id,))
        conn.commit()
        conn.close()

# --- PHẦN 2: DỮ LIỆU MẪU (Bắc Kạn) ---
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

# --- PHẦN 3: GIAO DIỆN STREAMLIT (View) ---
@st.cache_resource
def get_model():
    return ForestryModel()

model = get_model()

# --- SIDEBAR: Form Nhập Liệu ---
with st.sidebar:
    st.header("📝 Nhập Liệu / Cập Nhật")
    
    with st.form("entry_form", clear_on_submit=True):
        st.write("Thông tin vật nuôi:")
        
        col_huyen, col_xa = st.columns(2)
        with col_huyen:
            huyen_opt = st.selectbox("Huyện", options=list(DATA_BAC_KAN.keys()))
        with col_xa:
            xa_opt = st.selectbox("Xã", options=DATA_BAC_KAN[huyen_opt])
            
        nam = st.number_input("Năm", min_value=1990, max_value=2100, step=1, value=2024)
        
        c1, c2 = st.columns(2)
        with c1:
            trau = st.number_input("Trâu (con)", min_value=0, step=1)
            bo = st.number_input("Bò (con)", min_value=0, step=1)
        with c2:
            lon = st.number_input("Lợn (con)", min_value=0, step=1)
            de = st.number_input("Dê (con)", min_value=0, step=1)
            
        xuat_chuong = st.number_input("Tổng xuất chuồng (con)", min_value=0, step=1)
        san_luong = st.number_input("Sản lượng thịt (tấn)", min_value=0.0, step=0.1, format="%.2f")
        
        submitted = st.form_submit_button("💾 Lưu Dữ Liệu", type="primary")
        
        if submitted:
            data = (huyen_opt, xa_opt, nam, trau, bo, lon, de, xuat_chuong, san_luong)
            model.add_record(data)
            st.toast("✅ Đã thêm dữ liệu thành công!", icon="🎉")
            time.sleep(1)
            st.rerun()

# --- MAIN PAGE: Hiển thị Bảng ---
st.title("🐄 HỆ THỐNG QUẢN LÝ CHĂN NUÔI")
st.markdown("---")

col_search, col_del = st.columns([3, 1])
with col_search:
    search_query = st.text_input("🔍 Tìm kiếm theo Huyện hoặc Xã:", placeholder="Nhập tên xã/huyện...")

# Lấy dữ liệu
all_data = model.get_data(page=1, page_size=1000, search_query=search_query)
columns = ["ID", "Huyện", "Xã", "Năm", "Trâu", "Bò", "Lợn", "Dê", "Xuất Chuồng", "Sản Lượng Thịt"]
df = pd.DataFrame(all_data, columns=columns)

# Hiển thị bảng
st.dataframe(
    df, 
    use_container_width=True,
    hide_index=True,
    height=600,
    column_config={
        "Năm": st.column_config.NumberColumn(format="%d"),
        "Sản Lượng Thịt": st.column_config.NumberColumn(format="%.2f tấn"),
    }
)

# Chức năng xóa
with col_del:
    st.write("") 
    st.write("") 
    with st.popover("🗑️ Xóa bản ghi"):
        st.write("Nhập ID bản ghi cần xóa:")
        id_to_delete = st.number_input("ID:", min_value=0, step=1, label_visibility="collapsed")
        if st.button("Xác nhận xóa", type="primary"):
            if id_to_delete > 0:
                # Kiểm tra ID có tồn tại trong list hiển thị không (để tránh xóa nhầm)
                if id_to_delete in df["ID"].values:
                    model.delete_record(id_to_delete)
                    st.toast(f"Đã xóa bản ghi ID {id_to_delete}")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("ID không tồn tại!")

st.divider()
st.caption(f"Tổng số bản ghi: {len(df)} | Dữ liệu tỉnh Bắc Kạn")
