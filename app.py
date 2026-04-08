import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import json

# 1. เชื่อมต่อ Google Sheets โดยใช้ค่าจาก Secrets
@st.cache_resource
def init_sheets():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    try:
        # ดึงข้อมูลจากช่อง Secrets ที่เราตั้งชื่อว่า GOOGLE_CREDENTIALS
        creds_json = st.secrets["GOOGLE_CREDENTIALS"]
        creds_info = json.loads(creds_json)
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_info, scope)
        client = gspread.authorize(creds)
        # ชื่อไฟล์ Google Sheets ของคุณ
        sheet = client.open("JCEP_Database").sheet1
        return sheet
    except Exception as e:
        st.error(f"การเชื่อมต่อล้มเหลว: {e}")
        return None

sheet = init_sheets()

if sheet is None:
    st.warning("⚠️ โปรดตรวจสอบการวาง Secrets ในหน้า Streamlit Cloud")
    st.stop()

# 2. ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="JCEP Journal", page_icon="logo-jcep.png")

with st.sidebar:
    try: st.image("logo-jcep.png")
    except: pass
    menu = st.radio("เมนู:", ["📝 ส่งข้อมูล (User)", "📊 ดูข้อมูล (Admin)"])

# 3. หน้าส่งข้อมูล (User)
if menu == "📝 ส่งข้อมูล (User)":
    st.header("ระบบส่งข้อมูลวารสาร JCEP")
    with st.form("input_form"):
        name = st.text_input("ชื่อ-นามสกุล")
        university = st.text_input("สถาบัน/มหาวิทยาลัย")
        submit = st.form_submit_button("ส่งข้อมูล")
        
    if submit:
        if name and university:
            all_data = sheet.get_all_values()
            row = [len(all_data), name, university, datetime.now().strftime("%Y-%m-%d %H:%M")]
            sheet.append_row(row)
            st.success("บันทึกข้อมูลเรียบร้อยแล้ว!")
        else:
            st.error("กรุณากรอกข้อมูลให้ครบถ้วน")

# 4. หน้าดูข้อมูล (Admin)
else:
    st.header("Admin Dashboard")
    pw = st.text_input("ใส่รหัสผ่านเพื่อดูข้อมูล", type="password")
    if pw == "adminjcep":
        data = sheet.get_all_records()
        st.dataframe(pd.DataFrame(data))
