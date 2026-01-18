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

# --- 2. LOGIC DATABASE (MODEL) ---
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

    def get_data(self, search_query=""):
        conn = self.connect()
        # Lấy dữ liệu vào Pandas DataFrame luôn cho tiện xử lý
        query = "SELECT * FROM du_lieu_chan_nuoi WHERE 1=1"
        params = []
        if search_query:
            query += " AND (huyen LIKE ? OR xa LIKE ?)"
            params.extend([f"%{search_query}%", f"%{search_query}%"])
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

# --- 3. DỮ LIỆU HÀNH CHÍNH BẮC KẠN ---
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

# --- 4. GIAO DIỆN CHÍNH (VIEW) ---
def main():
    st.title("🐄 HỆ THỐNG QUẢN LÝ CHĂN NUÔI")
    
    # Khởi tạo Model
    model = ForestryModel()
    
    # Tạo 4 Tab chức năng rõ ràng
    tab1, tab2, tab3, tab4 = st.tabs(["📋 XEM DỮ LIỆU", "➕ THÊM MỚI", "✏️ CHỈNH SỬA", "🗑️ XÓA BỎ"])

    # --- TAB 1: XEM DỮ LIỆU ---
    with tab1:
        col_search, _ = st.columns([1, 2])
        search_txt = col_search.text_input("🔍 Tìm kiếm Huyện/Xã:", placeholder="Nhập từ khóa...")
        
        # Load data
        df = model.get_data(search_query=search_txt)
        
        # Hiển thị Metrics (Thống kê nhanh)
        m1, m2, m3 = st.columns(3)
        m1.metric("Tổng số bản ghi", len(df))
        m2.metric("Tổng sản lượng thịt", f"{df['san_luong_thit'].sum():,.2f} tấn")
        m3.metric("Tổng xuất chuồng", f"{df['tong_xuat_chuong'].sum():,} con")
        
        # Hiển thị bảng
        st.dataframe(
            df,
            use_container_width=True,
            height=500,
            hide_index=True,
            column_config={
                "id": st.column_config.NumberColumn("ID", width="small"),
                "nam": st.column_config.NumberColumn("Năm", format="%d"),
                "san_luong_thit": st.column_config.NumberColumn("SL Thịt (Tấn)", format="%.2f"),
                "tong_xuat_chuong": st.column_config.NumberColumn("Xuất Chuồng (Con)"),
                "con_trau": "Trâu", "con_bo": "Bò", "con_lon": "Lợn", "con_de": "Dê"
            }
        )

    # --- TAB 2: THÊM MỚI ---
    with tab2:
        st.subheader("Thêm mới vật nuôi")
        
        # Chọn Huyện/Xã (Tự động lọc)
        col_h, col_x, col_n = st.columns(3)
        huyen_new = col_h.selectbox("Chọn Huyện:", list(DATA_BAC_KAN.keys()), key="add_huyen")
        xa_new = col_x.selectbox("Chọn Xã:", DATA_BAC_KAN[huyen_new], key="add_xa")
        nam_new = col_n.number_input("Năm:", 2000, 2100, 2024, key="add_nam")
        
        st.write("Số lượng vật nuôi:")
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

    # --- TAB 3: CHỈNH SỬA ---
    with tab3:
        st.subheader("Cập nhật thông tin")
        col_id, col_btn = st.columns([1, 3])
        edit_id = col_id.number_input("Nhập ID bản ghi cần sửa:", min_value=1, step=1)
        
        record = model.get_record_by_id(edit_id)
        
        if record:
            st.info(f"Đang sửa bản ghi: {record[1]} - {record[2]} (Năm {record[3]})")
            
            # Form sửa (Pre-fill dữ liệu cũ)
            col_eh, col_ex, col_en = st.columns(3)
            
            # Xử lý Huyện cũ
            default_huyen = record[1] if record[1] in DATA_BAC_KAN else list(DATA_BAC_KAN.keys())[0]
            # Key phải khác Tab 2 để không bị conflict
            huyen_edit = col_eh.selectbox("Huyện:", list(DATA_BAC_KAN.keys()), index=list(DATA_BAC_KAN.keys()).index(default_huyen), key="edit_huyen")
            
            # Xử lý Xã cũ
            xa_list = DATA_BAC_KAN[huyen_edit]
            default_xa = record[2] if record[2] in xa_list else xa_list[0]
            xa_edit = col_ex.selectbox("Xã:", xa_list, index=xa_list.index(default_xa), key="edit_xa")
            
            nam_edit = col_en.number_input("Năm:", 2000, 2100, record[3], key="edit_nam")
            
            ec1, ec2, ec3, ec4 = st.columns(4)
            trau_e = ec1.number_input("Trâu:", 0, value=record[4], key="edit_trau")
            bo_e = ec2.number_input("Bò:", 0, value=record[5], key="edit_bo")
            lon_e = ec3.number_input("Lợn:", 0, value=record[6], key="edit_lon")
            de_e = ec4.number_input("Dê:", 0, value=record[7], key="edit_de")
            
            ec5, ec6 = st.columns(2)
            xc_e = ec5.number_input("Xuất chuồng:", 0, value=record[8], key="edit_xc")
            sl_e = ec6.number_input("Sản lượng (tấn):", 0.0, value=record[9], format="%.2f", key="edit_sl")
            
            if st.button("Cập Nhật Thay Đổi", type="primary"):
                data = (huyen_edit, xa_edit, nam_edit, trau_e, bo_e, lon_e, de_e, xc_e, sl_e)
                model.update_record(edit_id, data)
                st.toast(f"Đã cập nhật ID {edit_id}!", icon="💾")
                time.sleep(1)
                st.rerun()
                
        else:
            st.warning("Không tìm thấy ID này. Vui lòng kiểm tra lại bên Tab 'Xem Dữ Liệu'.")

    # --- TAB 4: XÓA ---
    with tab4:
        st.subheader("Xóa dữ liệu")
        st.warning("Lưu ý: Hành động này không thể hoàn tác!")
        
        col_del_id, _ = st.columns([1, 3])
        del_id = col_del_id.number_input("Nhập ID cần xóa:", min_value=1, step=1, key="del_id_input")
        
        # Hiển thị thông tin trước khi xóa để chắc chắn
        if del_id:
            rec = model.get_record_by_id(del_id)
            if rec:
                st.write(f"Bạn đang chọn xóa: **{rec[1]} - {rec[2]} (ID: {rec[0]})**")
                if st.button("🔴 Xác Nhận Xóa Vĩnh Viễn"):
                    model.delete_record(del_id)
                    st.toast(f"Đã xóa bản ghi ID {del_id}", icon="🗑️")
                    time.sleep(1)
                    st.rerun()
            else:
                st.caption("Chưa tìm thấy bản ghi phù hợp.")

if __name__ == "__main__":
    main()
