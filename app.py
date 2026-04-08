import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# 1. เชื่อมต่อ Google Sheets (ดึงค่าทีละตัวจาก Secrets)
@st.cache_resource
def init_sheets():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    try:
        # ดึงค่าจาก Secrets แยกเป็นรายบรรทัดเพื่อลดความผิดพลาด
        creds_info = {
            "type": st.secrets["type"],
            "project_id": st.secrets["project_id"],
            "private_key_id": st.secrets["private_key_id"],
            "private_key": st.secrets["private_key"],
            "client_email": st.secrets["client_email"],
            "client_id": st.secrets["client_id"],
            "auth_uri": st.secrets["auth_uri"],
            "token_uri": st.secrets["token_uri"],
            "auth_provider_x509_cert_url": st.secrets["auth_provider_x509_cert_url"],
            "client_x509_cert_url": st.secrets["client_x509_cert_url"]
        }
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_info, scope)
        client = gspread.authorize(creds)
        sheet = client.open("JCEP_Database").sheet1
        return sheet
    except Exception as e:
        st.error(f"Error: {e}")
        return None

sheet = init_sheets()
if sheet is None:
    st.stop()

# 2. ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="JCEP Journal App", page_icon="logo-jcep.png", layout="wide")

# 3. เมนูและการทำงาน (User Form)
st.sidebar.image("logo-jcep.png", use_container_width=True)
menu = st.sidebar.radio("เมนู:", ["📝 ส่งข้อมูล (User)", "📊 สรุปผล (Admin)"])

if menu == "📝 ส่งข้อมูล (User)":
    st.header("ระบบจัดเก็บข้อมูลวารสาร JCEP")
    with st.form("my_form"):
        name = st.text_input("ชื่อ-นามสกุล")
        uni = st.text_input("มหาวิทยาลัย")
        submit = st.form_submit_button("ส่งข้อมูล")
        if submit and name and uni:
            all_values = sheet.get_all_values()
            row = [len(all_values), name, uni, datetime.now().strftime("%Y-%m-%d %H:%M")]
            sheet.append_row(row)
            st.success("บันทึกข้อมูลเรียบร้อย!")

elif menu == "📊 สรุปผล (Admin)":
    st.header("Admin Dashboard")
    df = pd.DataFrame(sheet.get_all_records())
    st.dataframe(df)
