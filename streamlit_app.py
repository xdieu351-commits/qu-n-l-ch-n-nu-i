import streamlit as st
import pandas as pd
import sqlite3
import time
import os

# --- 1. CẤU HÌNH TRANG ---
st.set_page_config(
    page_title="Quản Lý Chăn Nuôi",
    page_icon="🐄",
    layout="wide"
)

# --- 2. DỮ LIỆU HÀNH CHÍNH (Dùng chung cho cả app) ---
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

# --- 3. MODEL (LOGIC DATABASE) ---
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

    # Hàm lấy dữ liệu có hỗ trợ lọc nâng cao
    def get_data(self, search_text="", huyen_filter="Tất cả", xa_filter="Tất cả"):
        conn = self.connect()
        query = "SELECT * FROM du_lieu_chan_nuoi WHERE 1=1"
        params = []

        # Lọc theo Huyện
        if huyen_filter and huyen_filter != "Tất cả":
            query += " AND huyen = ?"
            params.append(huyen_filter)

        # Lọc theo Xã
        if xa_filter and xa_filter != "Tất cả":
            query += " AND xa = ?"
            params.append(xa_filter)

        # Tìm kiếm từ khóa (nếu có)
        if search_text:
            query += " AND (huyen LIKE ? OR xa LIKE ?)"
            params.extend([f"%{search_text}%", f"%{search_text}%"])

        query += " ORDER BY id DESC"
        
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        return df

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
        sql = '''UPDATE du_lieu_chan_nuoi SET
                 huyen=?, xa=?, nam=?, con_trau=?, con_bo=?, con_lon=?, con_de=?, 
                 tong_xuat_chuong=?, san_luong_thit=?
                 WHERE id=?'''
        cursor.execute(sql, data + (record_id,))
        conn.commit()
        conn.close()

    def delete_record(self, record_id):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM du_lieu_chan_nuoi WHERE id=?", (record_id,))
        conn.commit()
        conn.close()

# --- 4. GIAO DIỆN CHÍNH (VIEW) ---
def main():
    st.title("🐄 HỆ THỐNG QUẢN LÝ CHĂN NUÔI")
    model = ForestryModel()
    
    tab1, tab2, tab3, tab4 = st.tabs(["📋 XEM & LỌC DỮ LIỆU", "➕ THÊM MỚI", "✏️ CHỈNH SỬA", "🗑️ XÓA BỎ"])

    # ==========================
    # TAB 1: XEM DỮ LIỆU (Có bộ lọc vùng)
    # ==========================
    with tab1:
        # Bộ lọc
        with st.container(border=True):
            st.write("🔍 **Bộ lọc dữ liệu:**")
            col_f1, col_f2, col_f3 = st.columns(3)
            
            # Dropdown Huyện (Thêm option "Tất cả")
            list_huyen = ["Tất cả"] + list(DATA_BAC_KAN.keys())
            f_huyen = col_f1.selectbox("Chọn Huyện:", list_huyen, key="filter_huyen")
            
            # Dropdown Xã (Phụ thuộc Huyện)
            if f_huyen != "Tất cả":
                list_xa = ["Tất cả"] + DATA_BAC_KAN[f_huyen]
            else:
                list_xa = ["Tất cả"]
            f_xa = col_f2.selectbox("Chọn Xã:", list_xa, key="filter_xa")
            
            # Ô tìm kiếm từ khóa
            f_search = col_f3.text_input("Từ khóa khác:", placeholder="Tìm...", key="filter_search")

        # Load dữ liệu dựa trên bộ lọc
        df = model.get_data(search_text=f_search, huyen_filter=f_huyen, xa_filter=f_xa)
        
        # Thống kê nhanh
        if not df.empty:
            st.caption(f"Tìm thấy **{len(df)}** bản ghi phù hợp.")
            st.dataframe(
                df,
                use_container_width=True,
                height=500,
                hide_index=True,
                column_config={
                    "id": st.column_config.NumberColumn("ID", width="small"),
                    "nam": st.column_config.NumberColumn("Năm", format="%d"),
                    "san_luong_thit": st.column_config.NumberColumn("SL Thịt (Tấn)", format="%.2f"),
                    "tong_xuat_chuong": st.column_config.NumberColumn("Xuất Chuồng"),
                }
            )
        else:
            st.warning("Không tìm thấy dữ liệu nào với bộ lọc này.")

    # ==========================
    # TAB 2: THÊM MỚI (Giữ nguyên, chỉ đổi key để tránh trùng lặp)
    # ==========================
    with tab2:
        st.subheader("Thêm mới vật nuôi")
        col_h, col_x, col_n = st.columns(3)
        huyen_new = col_h.selectbox("Huyện:", list(DATA_BAC_KAN.keys()), key="add_huyen")
        xa_new = col_x.selectbox("Xã:", DATA_BAC_KAN[huyen_new], key="add_xa")
        nam_new = col_n.number_input("Năm:", 2000, 2100, 2024, key="add_nam")
        
        c1, c2, c3, c4 = st.columns(4)
        trau = c1.number_input("Trâu:", 0, key="add_trau")
        bo = c2.number_input("Bò:", 0, key="add_bo")
        lon = c3.number_input("Lợn:", 0, key="add_lon")
        de = c4.number_input("Dê:", 0, key="add_de")
        
        c5, c6 = st.columns(2)
        xc = c5.number_input("Tổng xuất chuồng:", 0, key="add_xc")
        sl = c6.number_input("Sản lượng thịt (tấn):", 0.0, format="%.2f", key="add_sl")
        
        if st.button("Lưu Dữ Liệu Mới", type="primary"):
            data = (huyen_new, xa_new, nam_new, trau, bo, lon, de, xc, sl)
            model.add_record(data)
            st.toast("Đã thêm thành công!", icon="✅")
            time.sleep(1)
            st.rerun()

    # ==========================
    # TAB 3: CHỈNH SỬA (Chọn vùng -> Chọn bản ghi)
    # ==========================
    with tab3:
        st.subheader("Cập nhật thông tin")
        st.info("Bước 1: Chọn vùng để tìm bản ghi cần sửa")
        
        # 1. Chọn vùng để lọc bản ghi
        ce1, ce2 = st.columns(2)
        edit_huyen_filter = ce1.selectbox("Chọn Huyện (Lọc):", list(DATA_BAC_KAN.keys()), key="edit_filter_huyen")
        edit_xa_filter = ce2.selectbox("Chọn Xã (Lọc):", DATA_BAC_KAN[edit_huyen_filter], key="edit_filter_xa")
        
        # 2. Lấy danh sách bản ghi thuộc xã đó
        records_df = model.get_data(huyen_filter=edit_huyen_filter, xa_filter=edit_xa_filter)
        
        if not records_df.empty:
            # Tạo list hiển thị dạng: "ID - Năm ... (Số lượng ...)" để dễ chọn
            record_options = {
                f"ID {row['id']} | Năm {row['nam']} | Tổng XC: {row['tong_xuat_chuong']}": row['id'] 
                for index, row in records_df.iterrows()
            }
            
            st.write("Bước 2: Chọn bản ghi cụ thể")
            selected_option = st.selectbox("Chọn bản ghi:", list(record_options.keys()), key="edit_select_record")
            selected_id = record_options[selected_option] # Lấy ID thực
            
            # 3. Hiện Form sửa
            st.markdown("---")
            st.write(f"**Đang sửa bản ghi ID: {selected_id}**")
            rec = model.get_record_by_id(selected_id)
            
            # Form điền sẵn dữ liệu cũ
            col_eh, col_ex, col_en = st.columns(3)
            # Logic: Giữ nguyên Huyện/Xã cũ của bản ghi (có thể khác bộ lọc nếu muốn đổi xã)
            curr_huyen_idx = list(DATA_BAC_KAN.keys()).index(rec[1])
            h_val = col_eh.selectbox("Huyện:", list(DATA_BAC_KAN.keys()), index=curr_huyen_idx, key="e_form_h")
            
            xa_list = DATA_BAC_KAN[h_val]
            curr_xa_idx = xa_list.index(rec[2]) if rec[2] in xa_list else 0
            x_val = col_ex.selectbox("Xã:", xa_list, index=curr_xa_idx, key="e_form_x")
            
            n_val = col_en.number_input("Năm:", 2000, 2100, rec[3], key="e_form_n")
            
            ec1, ec2, ec3, ec4 = st.columns(4)
            t_val = ec1.number_input("Trâu:", 0, value=rec[4], key="e_form_t")
            b_val = ec2.number_input("Bò:", 0, value=rec[5], key="e_form_b")
            l_val = ec3.number_input("Lợn:", 0, value=rec[6], key="e_form_l")
            d_val = ec4.number_input("Dê:", 0, value=rec[7], key="e_form_d")
            
            ec5, ec6 = st.columns(2)
            xc_val = ec5.number_input("Xuất chuồng:", 0, value=rec[8], key="e_form_xc")
            sl_val = ec6.number_input("Sản lượng:", 0.0, value=rec[9], format="%.
