import streamlit as st
import pandas as pd
from models.forestry_model import ForestryModel
import time

# 1. Cấu hình trang
st.set_page_config(
    page_title="Quản Lý Chăn Nuôi",
    page_icon="🐄",
    layout="wide"
)

# 2. Kết nối Model
# Sử dụng cache để không phải connect lại db liên tục
@st.cache_resource
def get_model():
    return ForestryModel('chan_nuoi.db')

model = get_model()

# 3. Sidebar - Khu vực nhập liệu (Thay cho Modal)
with st.sidebar:
    st.header("📝 Nhập Liệu / Cập Nhật")
    
    # Form nhập liệu
    with st.form("entry_form", clear_on_submit=True):
        st.write("Điền thông tin vật nuôi:")
        
        # Dữ liệu mẫu Huyện/Xã Bắc Kạn (Copy lại logic từ Modal cũ)
        DATA_BAC_KAN = {
            "Thành phố Bắc Kạn": ["Phường Phùng Chí Kiên", "Phường Sông Cầu", "Phường Đức Xuân", "Xã Dương Quang", "Xã Nông Thượng"],
            "Huyện Ba Bể": ["Thị trấn Chợ Rã", "Xã Nam Mẫu", "Xã Khang Ninh", "Xã Quảng Khê", "Xã Đồng Phúc"],
            # ... Bạn có thể copy nốt các huyện khác vào đây
        }
        
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
        
        submitted = st.form_submit_button("💾 Lưu Dữ Liệu")
        
        if submitted:
            # Gọi Model để thêm mới
            data = (huyen_opt, xa_opt, nam, trau, bo, lon, de, xuat_chuong, san_luong)
            model.add_record(data)
            st.success("Đã thêm dữ liệu thành công!")
            time.sleep(1)
            st.rerun() # Load lại trang

# 4. Giao diện chính - Hiển thị bảng
st.title("🐄 HỆ THỐNG QUẢN LÝ CHĂN NUÔI (WEB)")

# Thanh tìm kiếm
col_search, col_del = st.columns([3, 1])
with col_search:
    search_query = st.text_input("🔍 Tìm kiếm theo Huyện hoặc Xã:", "")

# Load dữ liệu từ Database
# Lưu ý: Hàm get_data cũ của bạn có phân trang, ở đây ta lấy hết hoặc lấy số lượng lớn
# Để đơn giản cho Web, mình lấy 1000 bản ghi mới nhất
all_data = model.get_data(page=1, page_size=1000, search_query=search_query)

# Chuyển sang Pandas DataFrame để hiển thị đẹp
columns = ["ID", "Huyện", "Xã", "Năm", "Trâu", "Bò", "Lợn", "Dê", "Xuất Chuồng", "Sản Lượng Thịt"]
df = pd.DataFrame(all_data, columns=columns)

# Hiển thị bảng dữ liệu
st.dataframe(
    df, 
    use_container_width=True,
    hide_index=True,
    height=600
)

# 5. Xử lý Xóa (Đơn giản hóa cho Web)
with col_del:
    st.write("") # Spacer
    st.write("") 
    # Nhập ID để xóa (Streamlit xử lý nút xóa trên từng dòng hơi phức tạp, đây là cách đơn giản nhất)
    with st.popover("🗑️ Xóa bản ghi"):
        id_to_delete = st.number_input("Nhập ID cần xóa:", min_value=0, step=1)
        if st.button("Xác nhận xóa", type="primary"):
            if id_to_delete > 0:
                model.delete_record(id_to_delete)
                st.toast(f"Đã xóa bản ghi ID {id_to_delete}")
                time.sleep(1)
                st.rerun()

# Footer thống kê nhanh
st.divider()
st.metric(label="Tổng số bản ghi", value=len(df))