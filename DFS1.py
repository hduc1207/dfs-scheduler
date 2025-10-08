import streamlit as st
from datetime import datetime, timedelta

# -----------------------------
# CẤU HÌNH CHUYÊN KHOA & BÁC SĨ
# -----------------------------
chuyen_khoa = {
    "Nội tổng quát": {"Bác sĩ An": ["Bác sĩ Bình"], "Bác sĩ Bình": []},
    "Tim mạch": {"Bác sĩ Chi": ["Bác sĩ Dũng"], "Bác sĩ Dũng": []},
    "Tai Mũi Họng": {"Bác sĩ Hạnh": ["Bác sĩ Khôi"], "Bác sĩ Khôi": []},
    "Da liễu": {"Bác sĩ Lan": ["Bác sĩ Minh"], "Bác sĩ Minh": []}
}

thoi_gian_kham = 30  # phút mỗi ca

# -----------------------------
# HÀM DFS TÌM BÁC SĨ RẢNH
# -----------------------------
def dfs_tim_bac_si_ranh(do_thi, bac_si, da_di_qua, lich_hien_tai, thoi_gian):
    if bac_si in da_di_qua:
        return None
    da_di_qua.add(bac_si)
    lich = lich_hien_tai.get(bac_si, [])

    if all(not (bd <= thoi_gian < kt) for bd, kt in lich):
        return bac_si

    for bac_si_phu in do_thi[bac_si]:
        ket_qua = dfs_tim_bac_si_ranh(do_thi, bac_si_phu, da_di_qua, lich_hien_tai, thoi_gian)
        if ket_qua:
            return ket_qua
    return None

# -----------------------------
# TÌM GIỜ RẢNH TIẾP THEO
# -----------------------------
def tim_gio_ranh_tiep_theo(bac_si, lich_hien_tai, thoi_gian):
    lich = sorted(lich_hien_tai.get(bac_si, []))
    for bd, kt in lich:
        if thoi_gian < bd:
            return thoi_gian
        elif bd <= thoi_gian < kt:
            thoi_gian = kt
    return thoi_gian

# -----------------------------
# HÀM XẾP LỊCH KHÁM
# -----------------------------
def dfs_xep_lich_quy_trinh(ten_benh_nhan, quy_trinh, thoi_gian_bat_dau, lich_hien_tai):
    ket_qua = []
    tg_hien_tai = thoi_gian_bat_dau

    for khoa in quy_trinh:
        bac_si_trong_khoa = chuyen_khoa[khoa]
        bac_si_bat_dau = list(bac_si_trong_khoa.keys())[0]
        bac_si_duoc_chon = dfs_tim_bac_si_ranh(bac_si_trong_khoa, bac_si_bat_dau, set(), lich_hien_tai, tg_hien_tai)

        if bac_si_duoc_chon:
            tg_hien_tai = tim_gio_ranh_tiep_theo(bac_si_duoc_chon, lich_hien_tai, tg_hien_tai)
            ket_thuc = tg_hien_tai + timedelta(minutes=thoi_gian_kham)
            lich_hien_tai[bac_si_duoc_chon].append((tg_hien_tai, ket_thuc))
            ket_qua.append((khoa, bac_si_duoc_chon, tg_hien_tai, ket_thuc))
            tg_hien_tai = ket_thuc
        else:
            ket_qua.append((khoa, "Không có bác sĩ trống", "", ""))
    return ket_qua


# -----------------------------
# GIAO DIỆN STREAMLIT
# -----------------------------
st.set_page_config(page_title="Xếp lịch khám bệnh (DFS)", page_icon="🩺", layout="centered")

st.title("🩺 Hệ thống xếp lịch khám bệnh")
st.markdown("Sử dụng **thuật toán DFS** để tìm bác sĩ rảnh và xếp quy trình khám tự động.")

quy_trinh_mau = [
    ["Nội tổng quát", "Tim mạch", "Tai Mũi Họng"],
    ["Tim mạch", "Nội tổng quát"],
    ["Tai Mũi Họng"],
    ["Da liễu", "Nội tổng quát"]
]

if "lich_hien_tai" not in st.session_state:
    st.session_state.lich_hien_tai = {bs: [] for ck in chuyen_khoa.values() for bs in ck.keys()}

with st.form("form_xep_lich"):
    ten = st.text_input("Họ tên bệnh nhân")
    quy_trinh_idx = st.selectbox("Chọn quy trình khám", range(len(quy_trinh_mau)), 
                                 format_func=lambda i: " → ".join(quy_trinh_mau[i]))
    bat_dau = st.datetime_input("Chọn thời gian bắt đầu", datetime.now())
    submit = st.form_submit_button("Xếp lịch")

if submit:
    ket_qua = dfs_xep_lich_quy_trinh(ten, quy_trinh_mau[quy_trinh_idx], bat_dau, st.session_state.lich_hien_tai)
    st.success(f"✅ Lịch khám cho **{ten}**")

    for khoa, bs, bd, kt in ket_qua:
        with st.container():
            st.markdown(
                f"""
                <div style="background-color:#e3f2fd;padding:10px 15px;border-left:6px solid #1565c0;border-radius:10px;margin:8px 0;">
                <strong>{khoa}</strong><br>
                👨‍⚕️ {bs if bs!='Không có bác sĩ trống' else '<span style="color:red">Không có bác sĩ trống</span>'}<br>
                🕓 {bd.strftime('%H:%M')} → {kt.strftime('%H:%M') if kt!='' else ''}
                </div>
                """,
                unsafe_allow_html=True
            )

st.markdown("---")
st.caption("💡 Mô phỏng thuật toán DFS trong việc phân bổ bác sĩ và khung giờ khám hợp lý.")
