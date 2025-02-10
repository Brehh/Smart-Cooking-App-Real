import streamlit as st
import google.generativeai as genai
import textwrap
import datetime
import os
import time
import uuid

# --- ตั้งค่า Page Configuration ---
st.set_page_config(
    page_title="🍽️ Smart Cooking App Version 1.0 😎",
    page_icon="🍳",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# --- File-based persistence สำหรับ Visitor Count และ Active Users ---
COUNTER_FILE = "visitor_count.txt"
ACTIVE_USERS_FILE = "active_users.txt"
ACTIVE_TIMEOUT = 20  # วินาทีที่ผู้ใช้ถูกนับเป็น active

def get_visitor_count():
    try:
        with open(COUNTER_FILE, "r") as f:
            content = f.read().strip()
            return int(content) if content else 0
    except FileNotFoundError:
        with open(COUNTER_FILE, "w") as f:
            f.write("0")
        return 0

def increment_visitor_count():
    count = get_visitor_count() + 1
    with open(COUNTER_FILE, "w") as f:
        f.write(str(count))
    return count

def get_active_users():
    current_time = time.time()
    active_users = {}
    try:
        with open(ACTIVE_USERS_FILE, "r") as f:
            for line in f:
                line = line.strip()
                if not line or "," not in line:
                    continue
                user_id, last_seen = line.split(",")
                if current_time - float(last_seen) <= ACTIVE_TIMEOUT:
                    active_users[user_id] = last_seen
    except FileNotFoundError:
        pass

    with open(ACTIVE_USERS_FILE, "w") as f:
        for user_id, last_seen in active_users.items():
            f.write(f"{user_id},{last_seen}\n")
    return len(active_users)

def update_active_user():
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    user_id = st.session_state.session_id
    current_time = time.time()
    active_users = {}
    try:
        with open(ACTIVE_USERS_FILE, "r") as f:
            for line in f:
                line = line.strip()
                if not line or "," not in line:
                    continue
                parts = line.split(",")
                if len(parts) != 2:
                    continue
                existing_user_id, last_seen = parts
                active_users[existing_user_id] = last_seen
    except FileNotFoundError:
        pass
    active_users[user_id] = str(current_time)
    with open(ACTIVE_USERS_FILE, "w") as f:
        for uid, last_seen in active_users.items():
            f.write(f"{uid},{last_seen}\n")

# --- API Key Setup ---
API_KEYS = st.secrets["API_KEYS"]

# --- Helper Functions ---
def call_gemini_api(prompt):
    for api_key in API_KEYS:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-2.0-flash")
            response = model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            error_message = str(e)
            if "insufficient_quota" in error_message or "Quota exceeded" in error_message:
                continue
            else:
                return f"❌ เกิดข้อผิดพลาด: {error_message}"
    return "⚠️ API ทั้งหมดหมดโควต้าแล้ว กรุณาตรวจสอบบัญชีของคุณ"

def process_menus(response_text):
    menu_list = []
    separators = ["🍽️ เมนูที่", "\n- ", "\n• ", "\n— ", "- ", "• "]
    for sep in separators:
        if sep in response_text:
            menu_list = response_text.split(sep)
            break
    else:
        return [response_text.strip()]
    menu_list = [menu.strip() for menu in menu_list if menu.strip()]
    return menu_list

def format_menu_text(menu):
    # แปลง **bold** หรือ *bold* เป็น HTML <b> tag
    menu = menu.replace("**", "<b>", 1).replace("**", "</b>", 1)
    menu = menu.replace("*", "<b>", 1).replace("*", "</b>", 1)
    menu = menu.replace("*", "<b>", 1).replace("*", "</b>", 1)
    return menu

# --- Custom CSS สำหรับโทนสีเขียวและดีไซน์ที่ทันสมัย ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Kanit:wght@300;400;600&display=swap');
body {
    font-family: 'Kanit', sans-serif;
    background-color: #f0f4f8;
    margin: 0;
    padding: 0;
}

/* Header แบบ Gradient สีเขียว */
.header {
    background: linear-gradient(90deg, #34d058, #28a745);
    padding: 20px;
    border-bottom: 2px solid #dee2e6;
    text-align: center;
    margin-bottom: 20px;
}
.header h1 {
    font-size: 3rem;
    margin: 0;
    color: #ffffff;
}
@media (max-width: 768px) {
    .header h1 {
        font-size: 2rem;
        margin: 0 10px;
        word-wrap: break-word;
    }
}
.visitor-info {
    font-size: 1.2rem;
    color: #fefefe;
}

/* Card styling สำหรับเนื้อหาต่างๆ */
.card, .menu-column {
    background-color: #ffffff;
    border: 1px solid #d1e0e0;
    border-radius: 8px;
    padding: 20px;
    margin-bottom: 20px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.1);
}

/* ปรับสีและ hover effect สำหรับเมนู */
.menu-column {
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}
.menu-column:hover {
    transform: translateY(-5px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}
.menu-column h4 {
    color: #28a745;
}

/* ปุ่มหลัก สีเขียว */
.button-primary {
    background-color: #28a745;
    color: #fff;
    border: none;
    border-radius: 25px;
    padding: 12px 28px;
    font-size: 1.2rem;
    cursor: pointer;
    transition: all 0.3s ease;
}
.button-primary:hover {
    background-color: #218838;
}
</style>
""", unsafe_allow_html=True)

# --- Update Visitor Count และ Active Users ---
visitor_count = increment_visitor_count()
update_active_user()
active_users = get_active_users()

# --- Header Section ---
st.markdown(f"""
<div class="header">
    <h1>🍽️ Smart Cooking App Version 1.0 😎</h1>
    <p class="visitor-info">Page Views: {visitor_count} | Active Users: {active_users}</p>
</div>
""", unsafe_allow_html=True)

# --- สร้าง Tab สำหรับแต่ละโหมด ---
tabs = st.tabs(["📝 สร้างเมนูอาหาร", "🔍 ค้นหาเมนูอาหาร", "📜 เกี่ยวกับผู้พัฒนา"])

# --- ฟังก์ชันสำหรับโหมดสร้างเมนูอาหาร ---
def create_menu_mode():
    st.subheader("✨ สร้างเมนูอาหารทำเอง")
    
    with st.expander("📝 กรอกวัตถุดิบหลัก", expanded=True):
        ingredients = st.text_area("วัตถุดิบหลัก (คั่นด้วยจุลภาค):",
                                   placeholder="เช่น ไข่, หมูสับ, ผักกาด...",
                                   height=120)
    with st.expander("⚙️ ปรับแต่งเมนู", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            category = st.selectbox("ประเภทอาหาร",
                                    ["อาหารทั่วไป", "มังสวิรัติ", "อาหารคลีน", "อาหารไทย", "อาหารญี่ปุ่น",
                                     "อาหารตะวันตก", "อาหารจีน", "อาหารอินเดีย", "อาหารเวียดนาม", "อาหารเกาหลี",
                                     "อาหารเม็กซิกัน", "อาหารอิตาเลียน", "อาหารฟาสต์ฟู้ด", "อาหารทะเล",
                                     "อาหารเจ", "อาหารอีสาน", "อาหารใต้", "อาหารเหนือ", "อาหารฟิวชั่น", "ขนม", "เครื่องดื่ม"])
            calories = st.slider("แคลอรี่ที่ต้องการ (kcal)", 100, 1500, 500, step=50)
        with col2:
            difficulty = st.radio("ระดับความยาก", ["ง่าย", "ปานกลาง", "ยาก", "ยากมาก", "นรก"], horizontal=True)
            cook_time = st.slider("เวลาทำอาหาร (นาที)", 5, 180, 30, step=5)
    
    if st.button("🍳 สร้างเมนู", key="create_menu"):
        if ingredients.strip():
            prompt = (f"ฉันมี: {ingredients} เป็นวัตถุดิบหลัก "
                      f"แนะนำเมนู {category} เวลาทำไม่เกิน {cook_time} นาที "
                      f"ประมาณ {calories} kcal ระดับความยาก {difficulty} "
                      f"พร้อมวิธีทำอย่างละเอียด เสนอ 3 ตัวเลือก คั่นด้วย '🍽️ เมนูที่' "
                      f"ไม่ต้องเกริ่นนำ ถ้าวัตถุดิบที่มีขาดอะไรไปให้บอกด้วย และบอกจำนวนที่ต้องใช้อย่างละเอียด")
            with st.spinner("กำลังสร้างสรรค์ไอเดียอร่อยๆ..."):
                menu_list = process_menus(call_gemini_api(prompt))
            if menu_list:
                st.markdown("<h3>🧑‍🍳 เมนูแนะนำ 3 เมนู:</h3>", unsafe_allow_html=True)
                cols = st.columns(3)
                for i, menu in enumerate(menu_list[:3]):
                    with cols[i]:
                        menu = format_menu_text(menu)
                        st.markdown(f"""
                        <div class="menu-column">
                            <h4>🍽️ เมนูที่ {i+1}</h4>
                            <p>{menu}</p>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.warning("⚠️ ไม่พบเมนูที่ตรงกับเกณฑ์ของคุณ โปรดลองปรับการตั้งค่า")
        else:
            st.warning("⚠️ กรุณากรอกวัตถุดิบของคุณ")

# --- ฟังก์ชันสำหรับโหมดค้นหาเมนูอาหาร ---
def search_menu_mode():
    st.subheader("✨ ค้นหาเมนูที่คุณน่าจะชอบ")
    
    with st.expander("⚙️ ตั้งค่าการค้นหา", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            country = st.selectbox("ประเทศที่คุณอยู่ในตอนนี้",
                                   ["ไทย", "ญี่ปุ่น", "เกาหลีใต้", "สหรัฐอเมริกา", "อังกฤษ", "ฝรั่งเศส", "เยอรมนี",
                                    "จีน", "อินเดีย", "รัสเซีย", "แคนาดา", "บราซิล", "ออสเตรเลีย", "อาร์เจนตินา",
                                    "เม็กซิโก", "อิตาลี", "สเปน", "เนเธอร์แลนด์", "สวิตเซอร์แลนด์", "เบลเยียม",
                                    "สวีเดน", "นอร์เวย์", "เดนมาร์ก", "ฟินแลนด์", "โปรตุเกส", "ออสเตรีย", "ไอร์แลนด์",
                                    "กรีซ", "ตุรกี", "แอฟริกาใต้", "อียิปต์", "ไนจีเรีย", "เคนยา", "โมร็อกโก",
                                    "แอลจีเรีย", "ซาอุดีอาระเบีย", "สหรัฐอาหรับเอมิเรตส์", "กาตาร์", "โอมาน", "คูเวต",
                                    "อิหร่าน", "อิรัก", "ปากีสถาน", "บังกลาเทศ", "อินโดนีเซีย", "มาเลเซีย", "สิงคโปร์",
                                    "ฟิลิปปินส์", "เวียดนาม", "พม่า", "กัมพูชา", "ลาว", "มองโกเลีย", "เกาหลีเหนือ",
                                    "ไต้หวัน", "ฮ่องกง", "มาเก๊า", "นิวซีแลนด์", "ฟิจิ", "ปาปัวนิวกินี",
                                    "หมู่เกาะโซโลมอน", "วานูอาตู", "นาอูรู", "ตูวาลู", "คิริบาส", "ไมโครนีเซีย",
                                    "หมู่เกาะมาร์แชลล์", "ปาเลา", "ซามัว", "ตองกา", "นีวเวย์", "หมู่เกาะคุก",
                                    "เฟรนช์โปลินีเซีย", "นิวแคลิโดเนีย", "วาลลิสและฟูตูนา",
                                    "เฟรนช์เซาเทิร์นและแอนตาร์กติกแลนดส์", "เซนต์เฮเลนา", "อัสเซนชัน และตริสตันดากูนยา",
                                    "หมู่เกาะฟอล์กแลนด์", "เซาท์จอร์เจียและหมู่เกาะเซาท์แซนด์วิช", "หมู่เกาะพิตแคร์น",
                                    "บริติชอินเดียนโอเชียนเทร์ริทอรี", "หมู่เกาะบริติชเวอร์จิน", "หมู่เกาะเคย์แมน",
                                    "มอนต์เซอร์รัต", "แองกวิลลา", "อารูบา", "กูราเซา", "ซินต์มาร์เติน", "โบแนร์",
                                    "เซนต์เอิสตาเชียสและเซนต์มาร์เติน", "กรีนแลนด์", "หมู่เกาะแฟโร", "ยิบรอลตาร์",
                                    "อากรีอาและบาร์บูดา", "แอนติกาและบาร์บูดา", "บาร์เบโดส", "ดอมินิกา", "เกรนาดา",
                                    "เซนต์คิตส์และเนวิส", "เซนต์ลูเซีย", "เซนต์วินเซนต์และเกรนาดีนส์",
                                    "ตรินิแดดและโตเบโก", "แองโกลา", "เบนิน", "บอตสวานา", "บูร์กินาฟาโซ", "บุรุนดี",
                                    "กาบูเวร์ดี", "แคเมอรูน", "สาธารณรัฐแอฟริกากลาง", "ชาด", "สาธารณรัฐคองโก",
                                    "สาธารณรัฐประชาธิปไตยคองโก", "โกตดิวัวร์", "จิบูตี", "อียิปต์", "อิเควทอเรียลกินี",
                                    "เอริเทรีย", "เอสวาตินี", "เอธิโอเปีย", "กาบอง", "แกมเบีย", "กานา", "กินี",
                                    "กินี-บิสเซา", "เคนยา", "เลโซโท", "ไลบีเรีย", "ลิเบีย", "มาดากัสการ์", "มาลาวี",
                                    "มาลี", "มอริเตเนีย", "มอริเชียส", "โมร็อกโก", "โมซัมบิก", "นามิเบีย", "ไนเจอร์",
                                    "ไนจีเรีย", "รวันดา", "เซาตูเมและปรินซิปี", "เซเนกัล", "เซเชลส์", "เซียร์ราลีโอน",
                                    "โซมาเลีย", "แอฟริกาใต้", "ซูดานใต้", "ซูดาน", "แทนซาเนีย", "โตโก", "ตูนิเซีย",
                                    "ยูกันดา", "แซมเบีย", "ซิมบับเว"])
            category = st.selectbox("ประเภทอาหาร",
                                    ["อาหารไทย", "อาหารญี่ปุ่น", "อาหารเกาหลี", "ฟาสต์ฟู้ด", "อาหารสุขภาพ",
                                     "อาหารจีน", "อาหารอินเดีย", "อาหารเวียดนาม", "อาหารเม็กซิกัน",
                                     "อาหารอิตาเลียน", "อาหารทะเล", "อาหารเจ", "อาหารอีสาน", "อาหารใต้",
                                     "อาหารเหนือ", "อาหารฟิวชั่น", "ขนม", "เครื่องดื่ม", "อาหารตะวันตก"])
        with col2:
            taste = st.radio("รสชาติ", ["เผ็ด", "หวาน", "เค็ม", "เปรี้ยว", "ขม", "อูมามิ", "มัน", "ฝาด", "จืด", "รสจัด", "กลมกล่อม", "กลางๆ"], horizontal=True)
            budget = st.radio("งบประมาณ", ["ต่ำกว่า 100 บาท", "100 - 300 บาท", "300 - 1000 บาท", "1000 - 10000 บาท", "ไม่จำกัดงบ(ระดับ MrBeast)"], horizontal=True)
    
    if st.button("🔎 ค้นหาเมนู", key="search_menu"):
        if budget == "ไม่จำกัดงบ(ระดับ MrBeast)":
            prompt = (f"ฉันต้องการซื้ออาหาร {category} รสชาติ {taste} ราคา 10000 - 10000000 บาท {budget} "
                      f"ที่มีขายใน {country} แนะนำ 3 ตัวเลือกเมนู {category} ที่มีขายใน {country} "
                      f"คั่นด้วย '🍽️ เมนูที่' ไม่ต้องเกริ่นนำ บอกราคาของอาหารด้วย และบอกว่าหาซื้อได้ที่ร้านไหน")
        else:
            prompt = (f"ฉันต้องการซื้ออาหาร {category} รสชาติ {taste} ราคา {budget} "
                      f"ที่มีขายใน {country} แนะนำ 3 ตัวเลือกเมนู {category} ที่มีขายใน {country} "
                      f"คั่นด้วย '🍽️ เมนูที่' ไม่ต้องเกริ่นนำ บอกราคาของอาหารด้วย และบอกว่าหาซื้อได้ที่ร้านไหน")
        with st.spinner("กำลังค้นหาตัวเลือกที่ดีที่สุด..."):
            menu_list = process_menus(call_gemini_api(prompt))
        if menu_list:
            st.markdown("<h3>🧑‍🍳 เมนูแนะนำ 3 เมนู:</h3>", unsafe_allow_html=True)
            cols = st.columns(3)
            for i, menu in enumerate(menu_list[:3]):
                with cols[i]:
                    menu = format_menu_text(menu)
                    st.markdown(f"""
                    <div class="menu-column">
                        <h4>🍽️ เมนูที่ {i+1}</h4>
                        <p>{menu}</p>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.warning("⚠️ ไม่พบเมนู โปรดลองอีกครั้ง")

# --- เรียกใช้งานแต่ละโหมดใน Tab ที่เหมาะสม ---
with tabs[0]:
    create_menu_mode()
with tabs[1]:
    search_menu_mode()
with tabs[2]:
    st.subheader("🤝 เกี่ยวกับผู้พัฒนา")
    st.markdown("""
    <div class='about-section'>
    <ul style='list-style: none; padding: 0; display: flex; flex-direction: column; align-items: center;'>

    <li style='font-size: 1.6rem; font-weight: bold; margin-top: 10px;'>1. นาย กัลปพฤกษ์ วิเชียรรัตน์ (คนแบกอิๆๆ😎)</li>
    <li style='font-size: 1.3rem;'><em>ชั้น 6/13 เลขที่ 3</em></li>
    <img src='https://media-hosting.imagekit.io//1b3ed8f3573a4e71/IMG_20241011_135949_649.webp?Expires=1833623214&Key-Pair-Id=K2ZIVPTIP2VGHC&Signature=XkV2~CAZ1JL5DLoYHTK43-DH1HSmbcpRfZqqgUbS~YZHNtsgvL-UkoVf9iDz8-pZKNYsLqdyFOahcMiuMR1ao1FQiu3I2iqWiSmsoBiHOfr3OxBObD32WF30wS6NTbMCg7MmWPKCratj29lGI0fhN~33HlEnQ50hMnDRnH9CKvwY3tOWxM2sTNcwZ5J1Q1nP5wCAUwCCFaeNxJwFxCWLBdR268qhrfTxu9-pgodzqM1~Jv0bj3UTjx2i7IMm7eLjfU14x4aE9HUjTKrgvzsadlHSzJgYIyhQvetbRsEVPeIiiIz9aMo3YzK-JCz3CPMnoU-7aBLe5yLmVOEeHvMTIQ__' width='250px' style='border-radius: 10%; margin-bottom: 20px;'>

    <li style='font-size: 1.6rem; font-weight: bold; margin-top: 10px;'>2. นาย ธีราธร มุกดาเพชรรัตน์ (ผู้ช่วย No.1)</li>
    <li style='font-size: 1.3rem;'><em>ชั้น 6/13 เลขที่ 13</em></li>
    <img src='https://media-hosting.imagekit.io//794cd2dd43b24aff/perth_tm2025_02_08_18_38_478aae62c6-a109-49ec-aef1-8152096b5149.jpg?Expires=1833622873&Key-Pair-Id=K2ZIVPTIP2VGHC&Signature=u9sNP10b88y78jCRRUyLwn3OeHhsL7C0QbvaOcjCmOSGCD69RWN6e08aV19Se-7mknqcTF~zU9~snvhpFExvNR9jMhDubAePljCWIhBzzbpsRsOQ5akdEMa9AXVUOuXIzFN-igpqs-g9t8y~TqJ6mOO7daYkGa~L6Pnp3~G47pI3yWS5DVZ5hXcSHK7GQmupabIkfaaM-67FPYu7wF96vGlfatkSqA5zzIUGeX0yc~3kzI7dlCzqzqaXRKng6upQ07299g0LwFv3LBRO22VffO1fZr82TxnXUdEPcfmci-esT9LH6JEKwRET2fRLklG~qBRLc8wnzS0RdyrYjXRhEA__' width='250px' style='border-radius: 50%; margin-bottom: 20px;'>

    <li style='font-size: 1.6rem; font-weight: bold; margin-top: 10px;'>3. นาย อภิวิชญ์ อดุลธรรมวิทย์ (ผู้ช่วย No.2)</li>
    <li style='font-size: 1.3rem;'><em>ชั้น 6/13 เลขที่ 28</em></li>
    <img src='https://media-hosting.imagekit.io//e3962c8e8fa84567/513%2028.jpg?Expires=1833636651&Key-Pair-Id=K2ZIVPTIP2VGHC&Signature=IApvPc310iSHh~zIvIWoOHb-ABMcnPIPUmVAfVKHMQAz66kE1hCxbPUEWQNAIiekpZ1oDq9Nf8rmJ18AlAFtxzRAEOVGCXV1UWgz79A7kCvHHMbV1MnsOD2ZfY60ApLE-FRccfbKP3nLjaGZkcR3YA2ynywJVFHHau6MMA6mTUvy41nTWtRi9EDNP2Pbkxpr7hemhzcbtanbqtASvUHfWHspP5WXgJOXxq-TgoMYJudxvJbUsyp1Kg0WV1TOmo91xMgs5DC14xVXaE9lJ6NwfIG3zvoLehDiIXpYrGaI~nG~KUGXQJK~1st7lCdnkoLrCQhXJ55pGIOeIspbRj0LDQ__' width='250px' style='border-radius: 50%; margin-bottom: 20px;'>

    <li style='font-size: 1.6rem; font-weight: bold; margin-top: 10px;'>4. นาย ปัณณวิชญ์ หลีกภัย (ผู้ช่วย No.3)</li>
    <li style='font-size: 1.3rem;'><em>ชั้น 6/13 เลขที่ 29</em></li>
    <img src='https://media-hosting.imagekit.io//a39b45568dc14fab/IMG_20250208_223334.jpg?Expires=1833637018&Key-Pair-Id=K2ZIVPTIP2VGHC&Signature=M2tJAPHXihMl1OUnwNiEBpEggLW-AZag9HFNkFb51KiIR6AGcdJkV0ovnL0DfgAx8WV7-vc65vXWLKNZWoB4vzXob5AYUfwmT9XcgJ1egfOuS3B95GNj-y3maPQ7nm2iW3Yv~Zd5HfeL~D2tZu8CdiJUdFj3bB4x22uceD6zVNP8FHAuMS5qcaDTwUQgoV9RQvKQFOLjsX9JX7ZQ6olCkXmdIXM31uDSwok1Vpru12aC3p16whyHG2iJ2s1iTROwcJurWM9F-R90NCjP63ZGEa0gdrKgHC6WvKeGSmkehKsqpQv7fL3i7dXpTSV-Z-mVVh72OcJfNr1W~WRZwIjMDQ__' width='250px' style='border-radius: 50%;'>
    </ul>
    </div>
    """, unsafe_allow_html=True)

# --- Admin Panel ใน Sidebar ---
with st.sidebar:
    st.markdown("### 🔧 Admin Panel")
    admin_password = st.text_input("Enter Admin Password:", type="password")
    if admin_password == st.secrets["ADMIN_PASSWORD"]:
        if st.button("Reset Visitor Count and Active Users"):
            with open(COUNTER_FILE, "w") as f:
                f.write("0")
            with open(ACTIVE_USERS_FILE, "w") as f:
                f.truncate(0)
            st.success("Visitor count and active users reset to 0.")
            st.experimental_rerun()
        
        st.markdown("#### 📂 View Stored Data")
        def read_file_content(file_path):
            try:
                with open(file_path, "r") as f:
                    content = f.read().strip()
                    return content if content else "(Empty File)"
            except FileNotFoundError:
                return "(File Not Found)"
        if st.button("View Visitor Count File"):
            st.text_area("Visitor Count File Content:", read_file_content(COUNTER_FILE), height=70)
        if st.button("View Active Users File"):
            st.text_area("Active Users File Content:", read_file_content(ACTIVE_USERS_FILE), height=100)
    else:
        if admin_password != "":
            st.warning("Incorrect password or unauthorized access.")
