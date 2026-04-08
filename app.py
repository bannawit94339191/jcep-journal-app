import streamlit as st
import pandas as pd
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import json


# ==========================================
# 1. ตั้งค่าการเชื่อมต่อ Google Sheets (ใช้ Secrets)
# ==========================================
@st.cache_resource
def init_sheets():
    # กำหนดสิทธิ์การเข้าถึง
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

    try:
        # ดึงรหัสผ่านจาก Streamlit Secrets (ต้องตั้งชื่อ GOOGLE_CREDENTIALS)
        creds_info = json.loads(st.secrets["GOOGLE_CREDENTIALS"])
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_info, scope)
        client = gspread.authorize(creds)

        # เชื่อมต่อกับไฟล์ Google Sheets ชื่อ JCEP_Database
        sheet = client.open("JCEP_Database").sheet1
        return sheet
    except Exception as e:
        st.error(f"การเชื่อมต่อ Google Sheets ล้มเหลว: {e}")
        return None


# เรียกใช้งานการเชื่อมต่อ
sheet = init_sheets()

# ถ้าเชื่อมต่อไม่ได้ ให้หยุดการทำงานและแจ้งเตือน
if sheet is None:
    st.warning("⚠️ ไม่สามารถเชื่อมต่อฐานข้อมูลได้ โปรดเช็คค่า Secrets ใน Streamlit Cloud")
    st.stop()

# ==========================================
# 2. การตั้งค่าหน้าเว็บ (Page Config)
# ==========================================
st.set_page_config(
    page_title="JCEP - Journal of Cooperative Education Progress",
    page_icon="logo-jcep.png",
    layout="wide"
)

# ==========================================
# 3. ตกแต่ง CSS (ปุ่มสีต่างๆ และ Footer)
# ==========================================
st.markdown("""
    <style>
    div[data-testid="stButton"] button {
        white-space: nowrap !important;
        padding: 5px 24px !important; 
        font-size: 16px !important;   
        font-weight: 600 !important;  
        border-radius: 6px !important;
        transition: all 0.3s ease !important; 
    }

    /* ปุ่ม ส่งข้อมูล (Send) - สีเขียว */
    div[data-testid="stButton"] button:has(p:contains("ส่งข้อมูล (Send)")) {
        background-color: #28a745 !important; 
        border: 1px solid #28a745 !important;              
    }
    div[data-testid="stButton"] button:has(p:contains("ส่งข้อมูล (Send)")) p { color: white !important; }

    /* ปุ่ม ยกเลิก (Cancel) - สีแดง */
    div[data-testid="stButton"] button:has(p:contains("ยกเลิก (Cancel)")) {
        background-color: #dc3545 !important;
        border: 1px solid #dc3545 !important; 
    }
    div[data-testid="stButton"] button:has(p:contains("ยกเลิก (Cancel)")) p { color: white !important; }

    .footer { 
        position: fixed; 
        left: 0; bottom: 0; width: 100%; 
        background-color: #f1f1f1; color: black; 
        text-align: center; padding: 10px; 
        font-size: 14px; z-index: 100;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 4. ระบบ Session และ Sidebar
# ==========================================
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

with st.sidebar:
    try:
        st.image("logo-jcep.png", use_container_width=True)
    except:
        st.warning("ไม่พบไฟล์โลโก้")
    st.title("เมนูหลัก")
    menu = st.radio("เลือกหน้าต่างทำงาน:", ["📝 หน้าส่งข้อมูลวารสาร (User)", "📊 หน้าสรุปข้อมูล (Admin)"])

# ==========================================
# 5. หน้า User: ฟอร์มกรอกข้อมูล
# ==========================================
if menu == "📝 หน้าส่งข้อมูลวารสาร (User)":
    st.header("ระบบจัดเก็บข้อมูลวารสารสหกิจศึกษาก้าวหน้า")
    st.subheader("Journal of Cooperative Education Progress")
    st.divider()

    all_values = sheet.get_all_values()
    current_id = len(all_values)

    st.text_input("1. ลำดับที่ (Auto-run)", value=str(current_id), disabled=True)

    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("2. ชื่อ - นามสกุล")
        university = st.text_input("3. มหาวิทยาลัย / สถาบัน")
        faculty = st.text_input("4. คณะ")
        major = st.text_input("5. สาขาวิชา")
    with col2:
        agency = st.text_input("6. สังกัด / หน่วยงาน")
        phone = st.text_input("8. ช่องทางการติดต่อกลับ (เบอร์โทร)")
        email = st.text_input("9. ช่องทางการติดต่อกลับ (E-mail)")

    address = st.text_area("7. ที่อยู่")

    st.write("10. ประเภทบทความ")
    c1, c2, c3 = st.columns(3)
    with c1:
        cb_research = st.checkbox("บทความวิจัย")
    with c2:
        cb_academic = st.checkbox("บทความวิชาการ")
    with c3:
        cb_other = st.checkbox("อื่นๆ")

    other_text = ""
    if cb_other:
        other_text = st.text_input("โปรดระบุประเภทบทความอื่นๆ")

    uploaded_file = st.file_uploader("11. แนบไฟล์วารสาร", type=['pdf', 'docx', 'doc', 'zip'])

    col_btn1, col_btn2, _ = st.columns([2, 2, 6])
    with col_btn1:
        send_btn = st.button("ส่งข้อมูล (Send)", use_container_width=True)
    with col_btn2:
        cancel_btn = st.button("ยกเลิก (Cancel)", use_container_width=True)

    if cancel_btn:
        st.rerun()

    if send_btn:
        if not name or not university:
            st.error("กรุณากรอกข้อมูลที่จำเป็นให้ครบถ้วน")
        else:
            article_types = []
            if cb_research: article_types.append("บทความวิจัย")
            if cb_academic: article_types.append("บทความวิชาการ")
            if cb_other and other_text: article_types.append(f"อื่นๆ ({other_text})")
            article_type_str = ", ".join(article_types)

            filename = "ไม่มีไฟล์แนบ"
            if uploaded_file is not None:
                filename = f"ID{current_id}_{uploaded_file.name}"

            row = [
                current_id, name, university, faculty, major, agency,
                address, phone, email, article_type_str, filename,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ]

            sheet.append_row(row)
            st.success(f"✅ บันทึกข้อมูลลำดับที่ {current_id} สำเร็จ!")

# ==========================================
# 6. หน้า Admin: Dashboard
# ==========================================
elif menu == "📊 หน้าสรุปข้อมูล (Admin)":
    if not st.session_state['logged_in']:
        st.header("Admin Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            if username == "bannawit.s" and password == "adminjcep":
                st.session_state['logged_in'] = True
                st.rerun()
            else:
                st.error("Username หรือ Password ไม่ถูกต้อง!")
    else:
        col_title, col_logout = st.columns([8, 2])
        with col_title:
            st.header("📊 Dashboard ข้อมูล")
        with col_logout:
            if st.button("Logout"):
                st.session_state['logged_in'] = False
                st.rerun()

        data = sheet.get_all_records()
        if data:
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True)
            csv = df.to_csv(index=False).encode('utf-8-sig')
            st.download_button("📥 Export CSV", data=csv, file_name="jcep_data.csv", mime="text/csv")
        else:
            st.info("ยังไม่มีข้อมูล")

st.markdown('<div class="footer">Update by Bannawit S. (OCE - RMUTK)</div>', unsafe_allow_html=True)