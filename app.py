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
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    try:
        # ดึงข้อมูลกุญแจจาก Secrets ที่เราตั้งชื่อว่า GOOGLE_CREDENTIALS
        creds_dict = json.loads(st.secrets["GOOGLE_CREDENTIALS"])
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        sheet = client.open("JCEP_Database").sheet1
        return sheet
    except Exception as e:
        st.error(f"การเชื่อมต่อ Google Sheets ล้มเหลว: {e}")
        return None

sheet = init_sheets()

if sheet is None:
    st.warning("⚠️ โปรดตรวจสอบการวางรหัสในช่อง Secrets ใน Streamlit Cloud")
    st.stop()

# ==========================================
# 2. การตั้งค่าหน้าเว็บ (Page Config)
# ==========================================
st.set_page_config(
    page_title="JCEP - Journal Database",
    page_icon="logo-jcep.png",
    layout="wide"
)

# ส่วนโค้ดตกแต่งและฟอร์มอื่นๆ (เหมือนเดิม)
st.markdown("""
    <style>
    div[data-testid="stButton"] button { padding: 5px 24px !important; font-weight: 600 !important; border-radius: 6px !important; }
    .footer { position: fixed; left: 0; bottom: 0; width: 100%; background-color: #f1f1f1; text-align: center; padding: 10px; z-index: 100; }
    </style>
    """, unsafe_allow_html=True)

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

with st.sidebar:
    try: st.image("logo-jcep.png", use_container_width=True)
    except: pass
    st.title("เมนูหลัก")
    menu = st.radio("เลือกหน้าต่างทำงาน:", ["📝 หน้าส่งข้อมูลวารสาร (User)", "📊 หน้าสรุปข้อมูล (Admin)"])

if menu == "📝 หน้าส่งข้อมูลวารสาร (User)":
    st.header("ระบบจัดเก็บข้อมูลวารสาร JCEP")
    all_values = sheet.get_all_values()
    current_id = len(all_values)
    
    with st.form("user_form"):
        name = st.text_input("ชื่อ - นามสกุล")
        university = st.text_input("มหาวิทยาลัย / สถาบัน")
        phone = st.text_input("เบอร์โทร")
        email = st.text_input("E-mail")
        uploaded_file = st.file_uploader("แนบไฟล์", type=['pdf', 'docx', 'zip'])
        submit = st.form_submit_button("ส่งข้อมูล (Send)")
        
    if submit:
        if name and university:
            filename = uploaded_file.name if uploaded_file else "ไม่มีไฟล์แนบ"
            row = [current_id, name, university, phone, email, filename, datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
            sheet.append_row(row)
            st.success(f"✅ บันทึกข้อมูลลำดับที่ {current_id} สำเร็จ!")
        else:
            st.error("กรุณากรอกชื่อและมหาวิทยาลัย")

elif menu == "📊 หน้าสรุปข้อมูล (Admin)":
    if not st.session_state['logged_in']:
        user = st.text_input("Username")
        pw = st.text_input("Password", type="password")
        if st.button("Login"):
            if user == "bannawit.s" and pw == "adminjcep":
                st.session_state['logged_in'] = True
                st.rerun()
            else:
                st.error("รหัสผ่านไม่ถูกต้อง")
    else:
        if st.button("Logout"):
            st.session_state['logged_in'] = False
            st.rerun()
        data = sheet.get_all_records()
        if data:
            st.dataframe(pd.DataFrame(data))

st.markdown('<div class="footer">Update by Bannawit S. (OCE - RMUTK)</div>', unsafe_allow_html=True)
