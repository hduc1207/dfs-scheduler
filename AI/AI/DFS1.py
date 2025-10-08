import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from io import BytesIO

# CẤU HÌNH CHUYÊN KHOA & BÁC SĨ
chuyen_khoa = {
    "Nội tổng quát": {"Bác sĩ An": ["Bác sĩ Bình"], "Bác sĩ Bình": []},
    "Tim mạch": {"Bác sĩ Chi": ["Bác sĩ Dũng"], "Bác sĩ Dũng": []},
    "Tai Mũi Họng": {"Bác sĩ Hạnh": ["Bác sĩ Khôi"], "Bác sĩ Khôi": []},
    "Da liễu": {"Bác sĩ Lan": ["Bác sĩ Minh"], "Bác sĩ Minh": []}
}
thoi_gian_kham = 30  # phút mỗi ca

# HÀM TÌM BÁC SĨ RẢNH (DFS)
def dfs_tim_bac_si_ranh(do_thi, bac_si, da_tham, lich_hien_tai, thoi_gian):
    if bac_si in da_tham:
        return None
    da_tham.add(bac_si)
    lich_bac_si = lich_hien_tai.get(bac_si, [])

    if all(not (s <= thoi_gian < e) for s, e in lich_bac_si):
        return bac_si

    for ke_tiep in do_thi[bac_si]:
        ket_qua = dfs_tim_bac_si_ranh(do_thi, ke_tiep, da_tham, lich_hien_tai, thoi_gian)
        if ket_qua:
            return ket_qua
    return None

# XẾP LỊCH THEO QUY TRÌNH KHÁM
def dfs_xep_lich_benh_nhan(ten_bn, quy_trinh, bat_dau, lich_hien_tai):
    ket_qua = []
    thoi_gian = bat_dau

    for khoa in quy_trinh:
        ds_bac_si = chuyen_khoa[khoa]
        bac_si_dau = list(ds_bac_si.keys())[0]
        bac_si_duoc_chon = dfs_tim_bac_si_ranh(ds_bac_si, bac_si_dau, set(), lich_hien_tai, thoi_gian)

        if bac_si_duoc_chon:
            ket_thuc = thoi_gian + timedelta(minutes=thoi_gian_kham)
            lich_hien_tai[bac_si_duoc_chon].append((thoi_gian, ket_thuc))
            ket_qua.append((khoa, bac_si_duoc_chon, thoi_gian, ket_thuc))
            thoi_gian = ket_thuc
        else:
            ket_qua.append((khoa, "Không có bác sĩ trống", "", ""))
    return ket_qua

# GIAO DIỆN STREAMLIT
st.set_page_config(page_title="Hệ thống đặt lịch khám DFS", layout="centered")
st.markdown("""
<h2 style='text-align:center;color:#007BFF;'>🏥 XẾP LỊCH KHÁM BỆNH </h2>
<p style='text-align:center;color:#444;'>Ứng dụng thuật toán tìm kiếm DFS trong xếp lịch khám bệnh.</p>
""", unsafe_allow_html=True)

st.divider()

# Lịch trong phiên
if "lich_hien_tai" not in st.session_state:
    st.session_state.lich_hien_tai = {bs: [] for ck in chuyen_khoa.values() for bs in ck.keys()}

# Quy trình khám mẫu
quy_trinh_mau = [
    ["Nội tổng quát", "Tim mạch", "Tai Mũi Họng"],
    ["Tim mạch", "Da liễu"],
    ["Tai Mũi Họng"],
    ["Da liễu", "Nội tổng quát"]
]

st.markdown("### 🧾 Nhập thông tin bệnh nhân")

ten = st.text_input("Họ tên bệnh nhân:")
chon = st.selectbox("Chọn quy trình khám:", range(len(quy_trinh_mau)),
                    format_func=lambda i: " → ".join(quy_trinh_mau[i]))
ngay = st.date_input("Ngày khám:", datetime.now().date())
gio = st.time_input("Giờ bắt đầu:", datetime.now().time())
bat_dau = datetime.combine(ngay, gio)

if st.button("📅 Xếp lịch"):
    lich = dfs_xep_lich_benh_nhan(ten, quy_trinh_mau[chon], bat_dau, st.session_state.lich_hien_tai)
    df = pd.DataFrame([
        {
            "Chuyên khoa": khoa,
            "Bác sĩ": bs,
            "Bắt đầu": bd.strftime("%H:%M") if bd else "",
            "Kết thúc": kt.strftime("%H:%M") if kt else ""
        }
        for khoa, bs, bd, kt in lich
    ])
    st.success(f"✅ Đã xếp lịch thành công cho **{ten}**")
    st.dataframe(df, use_container_width=True)

    # Xuất Excel bằng BytesIO (chuẩn web Streamlit Cloud)
    buffer = BytesIO()
    df.to_excel(buffer, index=False, engine='openpyxl')
    buffer.seek(0)
    st.download_button(
        "⬇️ Tải file Excel",
        buffer,
        file_name=f"Lich_kham_{ten.replace(' ', '_')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

st.divider()
st.caption("© 2025 - Ứng dụng xếp lịch DFS")
