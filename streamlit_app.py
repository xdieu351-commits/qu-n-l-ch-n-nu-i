import streamlit as st
import pandas as pd
import sqlite3
import time
import os

# --- 1. CẤU HÌNH TRANG ---
st.set_page_config(
    page_title="Hệ thống Quản Lý Chăn Nuôi",
    page_icon="🐄",
    layout="wide"
)

# --- 2. MODEL & DATABASE (Logic xử lý dữ liệu) ---
class ForestryModel:
    def __init__(self, db_name='chan_nuoi.db'):
        self.db_name = db_name
        self._check_and_init_db()

    def connect(self):
        return sqlite3.connect(self.db_name)

    def _check_and_init_db(self):
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
        
        # Sắp xếp ID giảm dần để thấy cái mới nhất
        query = "SELECT * FROM du_lieu_chan_nuoi WHERE 1=1"
        params = []

        if search_query:
            query += " AND (huyen LIKE ? OR xa LIKE ?)"
            params.extend([f"%{search_query}%", f"%{search_query}%"])

        query += " ORDER BY id DESC"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        return rows

    def get_record_by_id(self, record_id):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM du_lieu_chan_nuoi WHERE id=?", (record_id,))
        row = cursor.fetchone()
        conn.close()
        return row

    def add_record(self, data):
        conn = self.connect()
        cursor = conn.cursor()
        sql = '''INSERT INTO du_lieu_chan_nuoi 
                 (huyen, xa, nam, con_trau, con_bo, con_lon, con_de, tong_xuat_chuong, san_luong_thit)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)'''
        cursor.execute(sql, data)
        conn.commit()
        conn.close()

    def update_record(self, record_id, data):
        conn = self.connect()
        cursor = conn.cursor()
        # data ở đây không bao gồm ID
        sql = '''UPDATE du_lieu_chan_nuoi SET
                 huyen=?, xa=?, nam=?, con_trau=?, con_bo=?, con_lon=?, con_de=?, 
                 tong_xuat_chuong=?, san_luong_thit=?
                 WHERE id=?'''
        # Thêm record_id vào cuối tuple data
        cursor.execute(sql, data + (record_id,))
        conn.commit()
        conn.close()

    def delete_record(self, record_id):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM du_lieu_chan_nuoi WHERE id=?", (record_id,))
        conn.commit()
        conn.close()

# --- 3. DỮ LIỆU MẪU BẮC KẠN ---
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

# --- 4. GIAO DIỆN CHÍNH ---
@st.cache_resource
def get_model():
    return ForestryModel()

model = get_model()

# --- SIDEBAR: KHU VỰC NHẬP/SỬA ---
with st.sidebar:
    st.header("🛠️ Công cụ Quản lý")
    
    # Chế độ: Thêm mới hoặc Cập nhật
    mode = st.radio("Chọn chức năng:", ["Thêm mới", "Cập nhật bản ghi"], horizontal=True)
    
    # Biến lưu giá trị mặc định cho form
    default_vals = {
        "huyen": list(DATA_BAC_KAN.keys())[0],
        "xa": "",
        "nam": 2024, "trau": 0, "bo": 0, "lon": 0, "de": 0, "xc": 0, "sl": 0.0
    }
    
    current_id = None
    
    # Nếu chọn chế độ Cập Nhật -> Hiện ô nhập ID để tìm
    if mode == "Cập nhật bản ghi":
        st.info("Nhập ID của bản ghi cần sửa:")
        col_search_id, col_btn_load = st.columns([2, 1])
        with col_search_id:
            input_id = st.number_input("ID bản ghi", min_value=1, step=1, label_visibility="collapsed")
        
        # Logic lấy dữ liệu cũ lên form
        record = model.get_record_by_id(input_id)
        if record:
            st.success(f"Đã tìm thấy bản ghi ID: {input_id}")
            current_id = input_id
            # Gán dữ liệu cũ vào biến default
            # Record structure: id(0), huyen(1), xa(2), nam(3), trau(4), bo(5), lon(6), de(7), xc(8), sl(9)
            default_vals["huyen"] = record[1] if record[1] in DATA_BAC_KAN else list(DATA_BAC_KAN.keys())[0]
            default_vals["xa"] = record[2]
            default_vals["nam"] = record[3]
            default_vals["trau"] = record[4]
            default_vals["bo"] = record[5]
            default_vals["lon"] = record[6]
            default_vals["de"] = record[7]
            default_vals["xc"] = record[8]
            default_vals["sl"] = record[9]
        else:
            st.warning("Không tìm thấy ID này!")
            current_id = None

    st.markdown("---")
    st.write(f"### 📝 {mode}")

    # --- INPUT FIELDS (Không dùng st.form để Huyện/Xã nhảy số ngay lập tức) ---
    
    # 1. Chọn Huyện (Tác động ngay lập tức đến list Xã)
    # Lấy index của huyện cũ trong list để set default value
    try:
        huyen_index = list(DATA_BAC_KAN.keys()).index(default_vals["huyen"])
    except ValueError:
        huyen_index = 0
        
    huyen_opt = st.selectbox("Huyện", options=list(DATA_BAC_KAN.keys()), index=huyen_index)

    # 2. Chọn Xã (List xã thay đổi theo Huyện vừa chọn)
    xa_options = DATA_BAC_KAN[huyen_opt]
    
    # Cố gắng giữ lại giá trị xã cũ nếu nó nằm trong list huyện mới
    try:
        xa_index = xa_options.index(default_vals["xa"])
    except ValueError:
        xa_index = 0
        
    xa_opt = st.selectbox("Xã", options=xa_options, index=xa_index)

    # 3. Các thông tin số liệu
    nam = st.number_input("Năm", min_value=1990, max_value=2100, value=default_vals["nam"])
    
    c1, c2 = st.columns(2)
    with c1:
        trau = st.number_input("Trâu (con)", min_value=0, value=default_vals["trau"])
        bo = st.number_input("Bò (con)", min_value=0, value=default_vals["bo"])
    with c2:
        lon = st.number_input("Lợn (con)", min_value=0, value=default_vals["lon"])
        de = st.number_input("Dê (con)", min_value=0, value=default_vals["de"])
        
    xuat_chuong = st.number_input("Tổng xuất chuồng (con)", min_value=0, value=default_vals["xc"])
    san_luong = st.number_input("Sản lượng thịt (tấn)", min_value=0.0, step=0.1, format="%.2f", value=default_vals["sl"])

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Nút Lưu
    btn_label = "💾 Thêm Mới" if mode == "Thêm mới" else "💾 Cập Nhật Lưu"
    if st.button(btn_label, type="primary", use_container_width=True):
        # Validate cơ bản
        if trau < 0 or bo < 0 or lon < 0 or de < 0:
            st.error("Số lượng con không được âm!")
        else:
            data = (huyen_opt, xa_opt, nam, trau, bo, lon, de, xuat_chuong, san_luong)
            
            if mode == "Thêm mới":
                model.add_record(data)
                st.toast("✅ Đã thêm mới thành công!", icon="🎉")
            else:
                if current_id:
                    model.update_record(current_id, data)
                    st.toast(f"✅ Đã cập nhật bản ghi ID {current_id}!", icon="✏️")
                else:
                    st.error("Chưa chọn ID hợp lệ để sửa!")
            
            time.sleep(1)
            st.rerun()

# --- MAIN PAGE: HIỂN THỊ BẢNG ---
st.title("🐄 HỆ THỐNG QUẢN LÝ CHĂN NUÔI")
st.caption("Dữ liệu quản lý tổng đàn và sản lượng thịt hơi xuất chuồng")
st.markdown("---")

# Thanh tìm kiếm & Xóa nhanh
col_search, col_del = st.columns([3, 1])
with col_search:
    search_query = st.text_input("🔍 Tìm kiếm:", placeholder="Nhập tên Huyện hoặc Xã...")

# Load dữ liệu
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
        "ID": st.column_config.NumberColumn(width="small"),
        "Năm": st.column_config.NumberColumn(format="%d", width="small"),
        "Sản Lượng Thịt": st.column_config.NumberColumn(format="%.2f tấn"),
    }
)

# Chức năng xóa bên phải
with col_del:
    st.write("") # Spacer
    with st.popover("🗑️ Xóa bản ghi", help="Nhấn để mở công cụ xóa"):
        st.markdown("#### Xóa dữ liệu")
        del_id = st.number_input("Nhập ID cần xóa:", min_value=0, step=1)
        if st.button("Xác nhận xóa", type="secondary"):
            if del_id in df["ID"].values:
                model.delete_record(del_id)
                st.toast(f"Đã xóa bản ghi ID {del_id}", icon="🗑️")
                time.sleep(1)
                st.rerun()
            else:
                st.error("ID không tồn tại!")

st.divider()
st.info(f"Tổng số bản ghi: **{len(df)}**")
