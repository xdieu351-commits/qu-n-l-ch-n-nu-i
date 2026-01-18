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

# --- 2. DỮ LIỆU HÀNH CHÍNH (BẮC KẠN) ---
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

# --- 3. MODEL (DATABASE) ---
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

    def get_data(self, search_text="", huyen_filter="Tất cả", xa_filter="Tất cả"):
        conn = self.connect()
        query = "SELECT * FROM du_lieu_chan_nuoi WHERE 1=1"
        params = []

        if huyen_filter and huyen_filter != "Tất cả":
            query += " AND huyen = ?"
            params.append(huyen_filter)

        if xa_filter and xa_filter != "Tất cả":
            query += " AND xa = ?"
            params.append(xa_filter)

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
    
    tab1, tab2, tab3, tab4 = st.tabs(["📋 XEM DỮ LIỆU", "➕ THÊM MỚI", "✏️ CHỈNH SỬA", "🗑️ XÓA BỎ"])

    # --- TAB 1: XEM DỮ LIỆU ---
    with tab1:
        with st.container(border=True):
            col_f1, col_f2, col_f3 = st.columns(3)
            list_huyen = ["Tất cả"] + list(DATA_BAC_KAN.keys())
            f_huyen = col_f1.selectbox("Lọc Huyện:", list_huyen, key="filter_huyen")
            
            if f_huyen != "Tất cả":
                list_xa = ["Tất cả"] + DATA_BAC_KAN[f_huyen]
            else:
                list_xa = ["Tất cả"]
            f_xa = col_f2.selectbox("Lọc Xã:", list_xa, key="filter_xa")
            f_search = col_f3.text_input("Tìm kiếm:", placeholder="Từ khóa...", key="filter_search")

        df = model.get_data(search_text=f_search, huyen_filter=f_huyen, xa_filter=f_xa)
        
        if not df.empty:
            st.dataframe(
                df, use_container_width=True, height=500, hide_index=True,
                column_config={
                    "id": st.column_config.NumberColumn("ID", width="small"),
                    "nam": st.column_config.NumberColumn("Năm", format="%d"),
                    "san_luong_thit": st.column_config.NumberColumn("SL Thịt (Tấn)", format="%.2f"),
                }
            )
        else:
            st.warning("Không có dữ liệu.")

    # --- TAB 2: THÊM MỚI ---
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
        
        if st.button("Lưu Mới", type="primary"):
            data = (huyen_new, xa_new, nam_new, trau, bo, lon, de, xc, sl)
            model.add_record(data)
            st.toast("Thêm thành công!", icon="✅")
            time.sleep(1)
            st.rerun()

    # --- TAB 3: CHỈNH SỬA (LOGIC RÀNG BUỘC THÔNG MINH) ---
    with tab3:
        st.subheader("Cập nhật thông tin")
        
        # 1. Chọn vùng để lọc
        ce1, ce2 = st.columns(2)
        edit_huyen_filter = ce1.selectbox("Lọc Huyện (Tìm kiếm):", list(DATA_BAC_KAN.keys()), key="edit_filter_huyen")
        edit_xa_filter = ce2.selectbox("Lọc Xã (Tìm kiếm):", DATA_BAC_KAN[edit_huyen_filter], key="edit_filter_xa")
        
        # 2. Lấy danh sách bản ghi
        records_df = model.get_data(huyen_filter=edit_huyen_filter, xa_filter=edit_xa_filter)
        
        if not records_df.empty:
            record_options = {f"ID {row['id']} | Năm {row['nam']}": row['id'] for i, row in records_df.iterrows()}
            selected_option = st.selectbox("👉 Chọn bản ghi cần sửa:", list(record_options.keys()), key="edit_select_record")
            selected_id = record_options[selected_option]
            
            st.markdown("---")
            rec = model.get_record_by_id(selected_id)
            
            # --- FORM SỬA (Dynamic Update) ---
            # Lưu ý: Ta dùng key=f"name_{selected_id}" để tạo widget mới mỗi khi đổi bản ghi.
            # Điều này giúp reset form về giá trị của bản ghi mới chọn.
            
            col_eh, col_ex, col_en = st.columns(3)
            
            # A. Chọn Huyện (Lấy giá trị DB làm mặc định)
            curr_huyen_db = rec[1] if rec[1] in DATA_BAC_KAN else list(DATA_BAC_KAN.keys())[0]
            try:
                idx_h = list(DATA_BAC_KAN.keys()).index(curr_huyen_db)
            except ValueError: idx_h = 0
            
            # Widget Huyện (User có thể thay đổi)
            h_val = col_eh.selectbox("Huyện:", list(DATA_BAC_KAN.keys()), index=idx_h, key=f"e_h_{selected_id}")
            
            # B. Chọn Xã (List xã phụ thuộc vào h_val vừa chọn bên trên, KHÔNG phụ thuộc DB nữa)
            xa_list_dynamic = DATA_BAC_KAN[h_val]
            
            # Logic mặc định cho Xã:
            # - Nếu Huyện user chọn == Huyện trong DB -> Mặc định là Xã trong DB.
            # - Nếu Huyện user chọn != Huyện trong DB (User vừa đổi huyện) -> Mặc định là xã đầu tiên của huyện mới.
            curr_xa_db = rec[2]
            if curr_xa_db in xa_list_dynamic:
                idx_x = xa_list_dynamic.index(curr_xa_db)
            else:
                idx_x = 0 # Reset về 0 nếu xã cũ không khớp với huyện mới
                
            x_val = col_ex.selectbox("Xã:", xa_list_dynamic, index=idx_x, key=f"e_x_{selected_id}")
            
            # C. Các trường khác
            n_val = col_en.number_input("Năm:", 2000, 2100, rec[3], key=f"e_n_{selected_id}")
            
            ec1, ec2, ec3, ec4 = st.columns(4)
            t_val = ec1.number_input("Trâu:", 0, value=rec[4], key=f"e_t_{selected_id}")
            b_val = ec2.number_input("Bò:", 0, value=rec[5], key=f"e_b_{selected_id}")
            l_val = ec3.number_input("Lợn:", 0, value=rec[6], key=f"e_l_{selected_id}")
            d_val = ec4.number_input("Dê:", 0, value=rec[7], key=f"e_d_{selected_id}")
            
            ec5, ec6 = st.columns(2)
            xc_val = ec5.number_input("Xuất chuồng:", 0, value=rec[8], key=f"e_xc_{selected_id}")
            sl_val = ec6.number_input("Sản lượng:", 0.0, value=rec[9], format="%.2f", key=f"e_sl_{selected_id}")
            
            if st.button("💾 Lưu Thay Đổi", type="primary", key=f"btn_save_{selected_id}"):
                data = (h_val, x_val, n_val, t_val, b_val, l_val, d_val, xc_val, sl_val)
                model.update_record(selected_id, data)
                st.toast("Cập nhật thành công!", icon="✅")
                time.sleep(1)
                st.rerun()
        else:
            st.info("Chưa có dữ liệu tại khu vực này.")

    # --- TAB 4: XÓA ---
    with tab4:
        st.subheader("Xóa dữ liệu")
        cd1, cd2 = st.columns(2)
        del_h_f = cd1.selectbox("Huyện:", list(DATA_BAC_KAN.keys()), key="del_h_f")
        del_x_f = cd2.selectbox("Xã:", DATA_BAC_KAN[del_h_f], key="del_x_f")
        
        del_df = model.get_data(huyen_filter=del_h_f, xa_filter=del_x_f)
        
        if not del_df.empty:
            del_opts = {f"ID {row['id']} | Năm {row['nam']}": row['id'] for i, row in del_df.iterrows()}
            del_sel = st.selectbox("Chọn bản ghi xóa:", list(del_opts.keys()), key="del_sel")
            id_del = del_opts[del_sel]
            
            if st.button("🔴 Xóa Vĩnh Viễn", type="secondary"):
                model.delete_record(id_del)
                st.toast("Đã xóa xong!", icon="🗑️")
                time.sleep(1)
                st.rerun()
        else:
            st.caption("Không có dữ liệu.")

if __name__ == "__main__":
    main()import streamlit as st
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

# --- 2. DỮ LIỆU HÀNH CHÍNH (BẮC KẠN) ---
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

# --- 3. MODEL (DATABASE) ---
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

    def get_data(self, search_text="", huyen_filter="Tất cả", xa_filter="Tất cả"):
        conn = self.connect()
        query = "SELECT * FROM du_lieu_chan_nuoi WHERE 1=1"
        params = []

        if huyen_filter and huyen_filter != "Tất cả":
            query += " AND huyen = ?"
            params.append(huyen_filter)

        if xa_filter and xa_filter != "Tất cả":
            query += " AND xa = ?"
            params.append(xa_filter)

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
    
    tab1, tab2, tab3, tab4 = st.tabs(["📋 XEM DỮ LIỆU", "➕ THÊM MỚI", "✏️ CHỈNH SỬA", "🗑️ XÓA BỎ"])

    # --- TAB 1: XEM DỮ LIỆU ---
    with tab1:
        with st.container(border=True):
            col_f1, col_f2, col_f3 = st.columns(3)
            list_huyen = ["Tất cả"] + list(DATA_BAC_KAN.keys())
            f_huyen = col_f1.selectbox("Lọc Huyện:", list_huyen, key="filter_huyen")
            
            if f_huyen != "Tất cả":
                list_xa = ["Tất cả"] + DATA_BAC_KAN[f_huyen]
            else:
                list_xa = ["Tất cả"]
            f_xa = col_f2.selectbox("Lọc Xã:", list_xa, key="filter_xa")
            f_search = col_f3.text_input("Tìm kiếm:", placeholder="Từ khóa...", key="filter_search")

        df = model.get_data(search_text=f_search, huyen_filter=f_huyen, xa_filter=f_xa)
        
        if not df.empty:
            st.dataframe(
                df, use_container_width=True, height=500, hide_index=True,
                column_config={
                    "id": st.column_config.NumberColumn("ID", width="small"),
                    "nam": st.column_config.NumberColumn("Năm", format="%d"),
                    "san_luong_thit": st.column_config.NumberColumn("SL Thịt (Tấn)", format="%.2f"),
                }
            )
        else:
            st.warning("Không có dữ liệu.")

    # --- TAB 2: THÊM MỚI ---
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
        
        if st.button("Lưu Mới", type="primary"):
            data = (huyen_new, xa_new, nam_new, trau, bo, lon, de, xc, sl)
            model.add_record(data)
            st.toast("Thêm thành công!", icon="✅")
            time.sleep(1)
            st.rerun()

    # --- TAB 3: CHỈNH SỬA (LOGIC RÀNG BUỘC THÔNG MINH) ---
    with tab3:
        st.subheader("Cập nhật thông tin")
        
        # 1. Chọn vùng để lọc
        ce1, ce2 = st.columns(2)
        edit_huyen_filter = ce1.selectbox("Lọc Huyện (Tìm kiếm):", list(DATA_BAC_KAN.keys()), key="edit_filter_huyen")
        edit_xa_filter = ce2.selectbox("Lọc Xã (Tìm kiếm):", DATA_BAC_KAN[edit_huyen_filter], key="edit_filter_xa")
        
        # 2. Lấy danh sách bản ghi
        records_df = model.get_data(huyen_filter=edit_huyen_filter, xa_filter=edit_xa_filter)
        
        if not records_df.empty:
            record_options = {f"ID {row['id']} | Năm {row['nam']}": row['id'] for i, row in records_df.iterrows()}
            selected_option = st.selectbox("👉 Chọn bản ghi cần sửa:", list(record_options.keys()), key="edit_select_record")
            selected_id = record_options[selected_option]
            
            st.markdown("---")
            rec = model.get_record_by_id(selected_id)
            
            # --- FORM SỬA (Dynamic Update) ---
            # Lưu ý: Ta dùng key=f"name_{selected_id}" để tạo widget mới mỗi khi đổi bản ghi.
            # Điều này giúp reset form về giá trị của bản ghi mới chọn.
            
            col_eh, col_ex, col_en = st.columns(3)
            
            # A. Chọn Huyện (Lấy giá trị DB làm mặc định)
            curr_huyen_db = rec[1] if rec[1] in DATA_BAC_KAN else list(DATA_BAC_KAN.keys())[0]
            try:
                idx_h = list(DATA_BAC_KAN.keys()).index(curr_huyen_db)
            except ValueError: idx_h = 0
            
            # Widget Huyện (User có thể thay đổi)
            h_val = col_eh.selectbox("Huyện:", list(DATA_BAC_KAN.keys()), index=idx_h, key=f"e_h_{selected_id}")
            
            # B. Chọn Xã (List xã phụ thuộc vào h_val vừa chọn bên trên, KHÔNG phụ thuộc DB nữa)
            xa_list_dynamic = DATA_BAC_KAN[h_val]
            
            # Logic mặc định cho Xã:
            # - Nếu Huyện user chọn == Huyện trong DB -> Mặc định là Xã trong DB.
            # - Nếu Huyện user chọn != Huyện trong DB (User vừa đổi huyện) -> Mặc định là xã đầu tiên của huyện mới.
            curr_xa_db = rec[2]
            if curr_xa_db in xa_list_dynamic:
                idx_x = xa_list_dynamic.index(curr_xa_db)
            else:
                idx_x = 0 # Reset về 0 nếu xã cũ không khớp với huyện mới
                
            x_val = col_ex.selectbox("Xã:", xa_list_dynamic, index=idx_x, key=f"e_x_{selected_id}")
            
            # C. Các trường khác
            n_val = col_en.number_input("Năm:", 2000, 2100, rec[3], key=f"e_n_{selected_id}")
            
            ec1, ec2, ec3, ec4 = st.columns(4)
            t_val = ec1.number_input("Trâu:", 0, value=rec[4], key=f"e_t_{selected_id}")
            b_val = ec2.number_input("Bò:", 0, value=rec[5], key=f"e_b_{selected_id}")
            l_val = ec3.number_input("Lợn:", 0, value=rec[6], key=f"e_l_{selected_id}")
            d_val = ec4.number_input("Dê:", 0, value=rec[7], key=f"e_d_{selected_id}")
            
            ec5, ec6 = st.columns(2)
            xc_val = ec5.number_input("Xuất chuồng:", 0, value=rec[8], key=f"e_xc_{selected_id}")
            sl_val = ec6.number_input("Sản lượng:", 0.0, value=rec[9], format="%.2f", key=f"e_sl_{selected_id}")
            
            if st.button("💾 Lưu Thay Đổi", type="primary", key=f"btn_save_{selected_id}"):
                data = (h_val, x_val, n_val, t_val, b_val, l_val, d_val, xc_val, sl_val)
                model.update_record(selected_id, data)
                st.toast("Cập nhật thành công!", icon="✅")
                time.sleep(1)
                st.rerun()
        else:
            st.info("Chưa có dữ liệu tại khu vực này.")

    # --- TAB 4: XÓA ---
    with tab4:
        st.subheader("Xóa dữ liệu")
        cd1, cd2 = st.columns(2)
        del_h_f = cd1.selectbox("Huyện:", list(DATA_BAC_KAN.keys()), key="del_h_f")
        del_x_f = cd2.selectbox("Xã:", DATA_BAC_KAN[del_h_f], key="del_x_f")
        
        del_df = model.get_data(huyen_filter=del_h_f, xa_filter=del_x_f)
        
        if not del_df.empty:
            del_opts = {f"ID {row['id']} | Năm {row['nam']}": row['id'] for i, row in del_df.iterrows()}
            del_sel = st.selectbox("Chọn bản ghi xóa:", list(del_opts.keys()), key="del_sel")
            id_del = del_opts[del_sel]
            
            if st.button("🔴 Xóa Vĩnh Viễn", type="secondary"):
                model.delete_record(id_del)
                st.toast("Đã xóa xong!", icon="🗑️")
                time.sleep(1)
                st.rerun()
        else:
            st.caption("Không có dữ liệu.")

if __name__ == "__main__":
    main()
