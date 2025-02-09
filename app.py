import streamlit as st
import google.generativeai as genai
import textwrap
import datetime
import os
import time
import uuid

# --- Page Configuration ---
st.set_page_config(
    page_title="🍽️ Smart Cooking App 😎",
    page_icon="🍳",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Custom CSS (Light Theme & Responsive) ---
st.markdown("""
<style>
/* Global Styles (Light Theme) */
body {
    font-family: 'Kanit', sans-serif;
    color: #333; /* Dark text for light theme */
    background-color: #f8f9fa; /* Light background */
}

.stApp {
    background-color: #f8f9fa; /* Consistent background */
}

/* Main Container Styles */
.main-container {
    border-radius: 15px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05); /* Subtle shadow */
    padding: 30px;
    margin-bottom: 20px;
    border: 1px solid #e0e0e0; /* Lighter border */
    background-color: white; /* White container background */
}

/* Header - Title at the Top */
.title {
    color: #343a40;
    text-align: center;
    padding: 1rem 0;
    font-size: 2.5rem; /* Slightly smaller for responsiveness */
    font-weight: 700;
    margin-bottom: 1rem;
    position: relative; /* For positioning visitor counts */
    width: 100%;
}

/* Visitor Count Styles - Positioned within the Title */
.visitor-info {
    position: absolute;
    top: -20px; /* Adjusted positioning */
    width: 100%;
    display: flex;
    justify-content: space-between;
    padding: 0 20px;
    font-size: 1.2rem; /* Smaller font size */
    color: #6c757d; /* Gray text */
}


/* Mode Selection Buttons - Using st.buttons */
.mode-buttons {
    display: flex;
    justify-content: center;
    flex-wrap: wrap; /* Allow wrapping on smaller screens */
    gap: 10px; /* Smaller gap */
    margin-bottom: 20px;
}

.mode-button {
    background-color: #007bff;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 10px 20px; /* Smaller padding */
    font-size: 1.2rem; /* Smaller font */
    font-weight: bold;
    cursor: pointer;
    transition: all 0.3s ease;
    box-shadow: 0 2px 5px rgba(0,0,0,0.2);
}

.mode-button:hover {
    background-color: #0056b3;
}

.mode-button-selected {
    background-color: #28a745; /* Green - for the selected mode */
    color: white;
    border: none;
    border-radius: 8px;
    padding: 10px 20px;
    font-size: 1.2rem;
    font-weight: bold;
    cursor: pointer;
    transition: all 0.3s ease;
    box-shadow: 0 2px 5px rgba(0,0,0,0.2);
}
.mode-button-selected:hover {
    background-color: #218838;
}

/* Subheaders */
.st-expanderHeader {
    font-size: 1.4rem; /* Smaller expander header */
    font-weight: 600; /* Slightly less bold */
    margin-bottom: 0.5rem;
}

/* Input Sections */
.input-section {
    margin-bottom: 0.8rem;
}

/* Input Fields - Streamlit Native Styling Adjustments */
.stTextInput, .stSelectbox, .stSlider, .stRadio, .stNumberInput {
    margin-bottom: 0.6rem;
}
.stTextInput>div>div>input, .stSelectbox>div>div>select,
.stSlider>div>div>div[role="slider"], .stRadio>div>label, .stNumberInput>div>div>input {
    border: 1px solid #ced4da; /* Lighter border */
    border-radius: 4px;
    padding: 8px 12px;
    font-size: 1rem;
    color: #495057; /* Darker text */
}

/* Text Area */
.stTextArea>div>div>textarea{
    border-color:#ced4da;  /* Consistent border color */
    border-radius: 8px;
    font-size: 1rem; /* Keep consistent font size */
}


/* Buttons */
.stButton>button {
    background-color: #28a745;
    color: white;
    border: none;
    border-radius: 20px; /* Slightly smaller radius */
    padding: 10px 24px;  /* Smaller padding */
    font-size: 1.1rem; /* Slightly smaller font */
    transition: all 0.3s ease;
    box-shadow: 0 3px 6px rgba(0, 0, 0, 0.1); /* Subtle shadow */
    width: 100%;
}

.stButton>button:hover {
    background-color: #218838;
    transform: translateY(-2px); /* Slightly less lift */
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15); /* Slightly larger shadow */
}

.stButton>button:active {
    transform: translateY(0);
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1); /* Smaller shadow */
}

/* Menu Columns */
.menu-column {
    border-radius: 12px;
    padding: 20px;  /* Slightly smaller padding */
    margin-bottom: 10px; /* Smaller margin */
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05); /* Lighter shadow */
    transition: transform 0.25s ease, box-shadow: 0.25s ease;
    border: 1px solid #dee2e6;
}

.menu-column:hover {
    transform: scale(1.01); /* Smaller scale */
    box-shadow: 0 3px 10px rgba(0, 0, 0, 0.1); /* Slightly smaller shadow */
}

.menu-column h3 {
    color: #28a745;
    margin-bottom: 10px;
    font-size: 1.3rem; /* Slightly smaller font */
    font-weight: 600;
}

.menu-item {
    font-size: 1rem; /* Slightly smaller font */
    line-height: 1.6;
}

/* About Section */
.about-section {
    border-radius: 12px;
    padding: 20px; /* Slightly smaller padding */
    margin-top: 20px; /* Smaller margin */
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05); /* Lighter shadow */
    border: 1px solid #dee2e6;
}
.about-section ul {
    list-style: none;
    padding: 0;
}

.about-section li {
    margin-bottom: 0.5rem;
}
.about-section img{
        border-radius: 50% !important;
        margin-bottom: 20px !important;
}

/* Spinners */
.st-cf {
    color: #28a745 !important;
}

/* Larger and Bolder Expander Text */
.st-expander button[data-baseweb="button"] {
    font-size: 1.2rem !important; /* Larger font */
    font-weight: bold !important;  /* Bold text */
}

/* Change expander icons */
.st-expander svg {
    color: #007bff; /* Blue expander icon */
}

/* Responsive adjustments */
@media (max-width: 768px) {
    .title {
        font-size: 2rem; /* Smaller title on small screens */
    }
    .visitor-info {
        top: -15px;
        font-size: 0.9rem; /* Smaller visitor info */
    }
    .mode-buttons {
        flex-direction: column; /* Stack on small screens */
    }
    .menu-column {
        padding: 15px;
    }
     /* Adjust image size on smaller screens */
    .about-section img {
        width: 150px !important; /* Smaller image */
        height: auto !important;
    }
}
</style>
""", unsafe_allow_html=True)


# --- Visitor Counter (File-based persistence) ---
COUNTER_FILE = "visitor_count.txt"
ACTIVE_USERS_FILE = "active_users.txt"
ACTIVE_TIMEOUT = 20  # Consider users active if they interacted within 10 seconds
PING_INTERVAL = 5  # Ping every 5 seconds to keep users active


def get_visitor_count():
    """Gets the current visitor count from a file."""
    try:
        with open(COUNTER_FILE, "r") as f:
            content = f.read().strip()
            return int(content) if content else 0  # Handle empty file
    except FileNotFoundError:
        with open(COUNTER_FILE, "w") as f:
            f.write("0")
        return 0


def increment_visitor_count():
    """Increments the visitor count every time the page is accessed."""
    count = get_visitor_count() + 1
    with open(COUNTER_FILE, "w") as f:
        f.write(str(count))
    return count


def get_active_users():
    """Counts the number of active users in the last ACTIVE_TIMEOUT seconds and removes inactive ones."""
    current_time = time.time()
    active_users = {}
    try:
        with open(ACTIVE_USERS_FILE, "r") as f:
            for line in f:
                line = line.strip()
                if not line or "," not in line:
                    continue  # Skip empty or malformed lines
                user_id, last_seen = line.split(",")
                if current_time - float(last_seen) <= ACTIVE_TIMEOUT:
                    active_users[user_id] = last_seen
    except FileNotFoundError:
        pass

    # Update the file with only currently active users
    with open(ACTIVE_USERS_FILE, "w") as f:
        for user_id, last_seen in active_users.items():
            f.write(f"{user_id},{last_seen}\n")

    return len(active_users)


def update_active_user():
    """Keeps updating the user's active status while the page is open."""
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

    # Update the current user's last seen time
    active_users[user_id] = str(current_time)
    with open(ACTIVE_USERS_FILE, "w") as f:
        for uid, last_seen in active_users.items():
            f.write(f"{uid},{last_seen}\n")


# --- API Key Setup (From Streamlit Secrets) ---
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



# --- Increment Visitor Count and Update Active Users ---
visitor_count = increment_visitor_count()
update_active_user()
active_users = get_active_users()

# --- App UI ---
st.markdown("<div class='title'>🍽️ Smart Cooking App Demo 0.2 😎</h1>", unsafe_allow_html=True)
# --- Display Visitor Count and Active Users ---
st.markdown(f"<div class='visitor-info'><span>Page Views: {visitor_count}</span> <span>Active Users: {active_users}</span></div>", unsafe_allow_html=True)


# --- Mode Selection (Using Buttons and Session State) ---
# Initialize mode if not in session state.  Keep it closed initially.
if 'mode' not in st.session_state:
    st.session_state.mode = None  # No mode selected initially

with st.container(border=True):
    with st.expander("🔄 เลือกโหมดการทำงาน", expanded = not st.session_state.mode is not None):
        col1, col2 = st.columns(2)

        with col1:
            if st.button("📝 สร้างเมนูอาหาร", key="create_mode", type="primary" if st.session_state.mode == "create" else "secondary", use_container_width=True):
                st.session_state.mode = "create"

        with col2:
            if st.button("🔍 ค้นหารายการอาหาร", key="search_mode",  type="primary" if st.session_state.mode == "search" else "secondary", use_container_width=True):
                st.session_state.mode = "search"



# --- Function Definitions for Each Mode ---
def create_menu_mode():
    st.subheader("✨ สร้างเมนูอาหารทำเอง 🤩")

    with st.expander("📝 กรอกวัตถุดิบหลัก (คั่นด้วยจุลภาคด้วย)", expanded=True):
        ingredients = st.text_area("วัตถุดิบหลัก (คั่นด้วยจุลภาค):",
                                    placeholder="เช่น ไข่, หมูสับ, ผักกาด...",
                                    height=120, label_visibility="collapsed")

    with st.expander("⚙️ ปรับแต่งเมนู", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            category = st.selectbox("ประเภทอาหาร",
                                    ["อาหารทั่วไป", "มังสวิรัติ", "อาหารคลีน", "อาหารไทย", "อาหารญี่ปุ่น",
                                    "อาหารตะวันตก", "อาหารจีน", "อาหารอินเดีย", "อาหารเวียดนาม", "อาหารเกาหลี",
                                    "อาหารเม็กซิกัน", "อาหารอิตาเลียน", "อาหารฟาสต์ฟู้ด", "อาหารทะเล",
                                    "อาหารมังสวิรัติ", "อาหารเจ", "อาหารอีสาน", "อาหารใต้", "อาหารเหนือ",
                                    "อาหารฟิวชั่น", "ขนม", "เครื่องดื่ม"])
            calories = st.slider("แคลอรี่ที่ต้องการ (kcal)", 100, 1500, 500, step=50)

        with col2:
            difficulty = st.radio("ระดับความยาก", ["ง่าย", "ปานกลาง", "ยาก", 'ยากมาก', 'นรก'], horizontal=True)
            cook_time = st.slider("เวลาทำอาหาร (นาที)", 5, 180, 30, step=5)

    if st.button("🍳 สร้างเมนู", use_container_width=True):
        if ingredients:
            prompt = (f"ฉันมี: {ingredients} เป็นวัตถุดิบหลัก "
                      f"แนะนำเมนู {category} เวลาทำไม่เกิน {cook_time} นาที "
                      f"ประมาณ {calories} kcal ระดับความยาก ระดับ{difficulty} "
                      f"พร้อมวิธีทำอย่างละเอียด เสนอ 3 ตัวเลือก คั่นด้วย '🍽️ เมนูที่' ไม่ต้องเกริ่นนำ ถ้าวัตถุดิบที่มีขาดอะไรไปให้บอกด้วย และบอกจำนวนที่ต้องใช้อย่างละเอียด")
            with st.spinner("กำลังสร้างสรรค์ไอเดียอร่อยๆ... 3 เมนู"):
                menu_list = process_menus(call_gemini_api(prompt))

            if menu_list:
                st.subheader("🧑‍🍳 เมนูแนะนำ 3 เมนู:")
                cols = st.columns(3)
                for i, menu in enumerate(menu_list[:3]):
                    with cols[i]:
                        # Convert Markdown **bold** to HTML <b> tags
                        menu = menu.replace("**", "<b>").replace("**", "</b>")
                        st.markdown(
                            f"<div class='menu-column'><h3>🍽️ เมนูที่ {i + 1}</h3><p class='menu-item'>{menu}</p></div>",
                            unsafe_allow_html=True
                            )
            else:
                st.warning("⚠️ ไม่พบเมนูที่ตรงกับเกณฑ์ของคุณ โปรดลองปรับการตั้งค่า")
        else:
            st.warning("⚠️ กรุณากรอกวัตถุดิบของคุณ")


def search_menu_mode():
    st.subheader("✨ ค้นหาเมนูที่คุณน่าจะชอบ 3 เมนู")

    with st.expander("⚙️ ตั้งค่าการค้นหา", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            country = st.selectbox('ประเทศที่คุณอยู่ในตอนนี้',
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
                                    "มอนต์เซอร์รัต", "อังGuilla", "อารูบา", "กูราเซา", "ซินต์มาร์เติน", "โบแนร์",
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
                                    ["อาหารไทย", "อาหารญี่ปุ่น", "อาหารเกาหลี", "ฟาสต์ฟู้ด", "อาหารสุขภาพ", "อาหารจีน",
                                    "อาหารอินเดีย", "อาหารเวียดนาม", "อาหารเม็กซิกัน", "อาหารอิตาเลียน", "อาหารทะเล",
                                    "อาหารมังสวิรัติ", "อาหารเจ", "อาหารอีสาน", "อาหารใต้", "อาหารเหนือ",
                                    "อาหารฟิวชั่น", "ขนม", "เครื่องดื่ม", "อาหารตะวันตก", "อาหารนานาชาติ"])
        with col2:
            taste = st.radio("รสชาติ", ["เผ็ด", "หวาน", "เค็ม", "เปรี้ยว", "ขม", "อูมามิ", "มัน", "ฝาด", "จืด", 'รสจัด',
                                            'กลมกล่อม', 'กลางๆ'], horizontal=True)
            budget = st.radio("งบประมาณ", ['ต่ำกว่า 100 บาท', '100 - 300 บาท', '300 - 1000 บาท', '1000 - 10000 บาท',
                                            'ไม่จำกัดงบ(ระดับ MrBeast)'], horizontal=True)

    if st.button("🔎 ค้นหาเมนู", use_container_width=True):
        if budget == 'ไม่จำกัดงบ(ระดับ MrBeast)':
            prompt = (f"ฉันต้องการซื้ออาหาร {category} รสชาติ {taste} ราคา 10000 -10000000 บาท {budget} ทีมีขายใน {country} "
                      f"แนะนำ 3 ตัวเลือกเมนู {category} ที่มีขายใน {country} คั่นด้วย '🍽️ เมนูที่' ไม่ต้องเกริ่นนำ บอกราคาของอาหารด้วย บอกด้วยว่าหาซื้อได้ที่ร้านไหน")
            print('MrBeast') # Debugging line
        else:
            prompt = (f"ฉันต้องการซื้ออาหาร {category} รสชาติ {taste} ราคา {budget} ทีมีขายใน {country} "
                      f"แนะนำ 3 ตัวเลือกเมนู {category} ที่มีขายใน {country} คั่นด้วย '🍽️ เมนูที่' ไม่ต้องเกริ่นนำ บอกราคาของอาหารด้วย บอกด้วยว่าหาซื้อได้ที่ร้านไหน")
        with st.spinner("กำลังค้นหาตัวเลือกที่ดีที่สุด... 3 เมนู"):
            menu_list = process_menus(call_gemini_api(prompt))

        if menu_list:
            st.subheader("🧑‍🍳 เมนูแนะนำ 3 เมนู:")
            cols = st.columns(3)
            for i, menu in enumerate(menu_list[:3]):
                with cols[i]:
                    menu = menu.replace("**", "<b>").replace("**", "</b>")
                    menu = menu.replace("*", "<b>").replace("*", "</b>")# Convert **text** to <b>text</b>
                    st.markdown(
                        f"<div class='menu-column'><h3>🍽️ เมนูที่ {i + 1}</h3><p class='menu-item'>{menu}</p></div>",
                        unsafe_allow_html=True
                        )
        else:
            st.warning("⚠️ ไม่พบเมนู โปรดลองอีกครั้ง")



# --- Conditional Display based on Selected Mode ---
if st.session_state.mode == "create":
    create_menu_mode()
elif st.session_state.mode == "search":
    search_menu_mode()


# --- About Section ---
st.markdown("---")
if st.button("📜 เกี่ยวกับผู้พัฒนา", use_container_width=True):
    with st.expander("🤝 พบกับทีมงาน", expanded=False):
        st.markdown("""
        <div class='about-section'>
        <ul style='list-style: none; padding: 0; display: flex; flex-direction: column; align-items: center;'>

        <li style='font-size: 1.4rem; font-weight: bold; margin-top: 10px;'>นาย กัลปพฤกษ์ วิเชียรรัตน์ (คนแบกอิๆๆ😎)</li>
        <li style='font-size: 1.1rem;'><em>ชั้น 6/13 เลขที่ 3</em></li>
        <img src='https://media-hosting.imagekit.io//1b3ed8f3573a4e71/IMG_20241011_135949_649.webp?Expires=1833623214&Key-Pair-Id=K2ZIVPTIP2VGHC&Signature=XkV2~CAZ1JL5DLoYHTK43-DH1HSmbcpRfZqqgUbS~YZHNtsgvL-UkoVf9iDz8-pZKNYsLqdyFOahcMiuMR1ao1FQiu3I2iqWiSmsoBiHOfr3OxBObD32WF30wS6NTbMCg7MmWPKCratj29lGI0fhN~33HlEnQ50hMnDRnH9CKvwY3tOWxM2sTNcwZ5J1Q1nP5wCAUwCCFaeNxJwFxCWLBdR268qhrfTxu9-pgodzqM1~Jv0bj3UTjx2i7IMm7eLjfU14x4aE9HUjTKrgvzsadlHSzJgYIyhQvetbRsEVPeIiiIz9aMo3YzK-JCz3CPMnoU-7aBLe5yLmVOEeHvMTIQ__' width='250px'>

        <li style='font-size: 1.4rem; font-weight: bold; margin-top: 10px;'>นาย ธีราธร มุกดาเพชรรัตน์ (ผู้ช่วย No.1)</li>
        <li style='font-size: 1.1rem;'><em>ชั้น 6/13 เลขที่ 13</em></li>
        <img src='https://media-hosting.imagekit.io//794cd2dd43b24aff/perth_tm2025_02_08_18_38_478aae62c6-a109-49ec-aef1-8152096b5149.jpg?Expires=1833622873&Key-Pair-Id=K2ZIVPTIP2VGHC&Signature=u9sNP10b88y78jCRRUyLwn3OeHhsL7C0QbvaOcjCmOSGCD69RWN6e08aV19Se-7mknqcTF~zU9~snvhpFExvNR9jMhDubAePljCWIhBzzbpsRsOQ5akdEMa9AXVUOuXIzFN-igpqs-g9t8y~TqJ6mOO7daYkGa~L6Pnp3~G47pI3yWS5DVZ5hXcSHK7GQmupabIkfaaM-67FPYu7wF96vGlfatkSqA5zzIUGeX0yc~3kzI7dlCzqzqaXRKng6upQ07299g0LwFv3LBRO22VffO1fZr82TxnXUdEPcfmci-esT9LH6JEKwRET2fRLklG~qBRLc8wnzS0RdyrYjXRhEA__' width='250px'>

        <li style='font-size: 1.4rem; font-weight: bold; margin-top: 10px;'>นาย อภิวิชญ์ อดุลธรรมวิทย์ (ผู้ช่วย No.2)</li>
        <li style='font-size: 1.1rem;'><em>ชั้น 6/13 เลขที่ 28</em></li>
        <img src='https://media-hosting.imagekit.io//e3962c8e8fa84567/513%2028.jpg?Expires=1833636651&Key-Pair-Id=K2ZIVPTIP2VGHC&Signature=IApvPc310iSHh~zIvIWoOHb-ABMcnPIPUmVAfVKHMQAz66kE1hCxbPUEWQNAIiekpZ1oDq9Nf8rmJ18AlAFtxzRAEOVGCXV1UWgz79A7kCvHHMbV1MnsOD2ZfY60ApLE-FRccfbKP3nLjaGZkcR3YA2ynywJVFHHau6MMA6mTUvy41nTWtRi9EDNP2Pbkxpr7hemhzcbtanbqtASvUHfWHspP5WXgJOXxq-TgoMYJudxvJbUsyp1Kg0WV1TOmo91xMgs5DC14xVXaE9lJ6NwfIG3zvoLehDiIXpYrGaI~nG~KUGXQJK~1st7lCdnkoLrCQhXJ55pGIOeIspbRj0LDQ__' width='250px'>

        <li style='font-size: 1.4rem; font-weight: bold; margin-top: 10px;'>นาย ปัณณวิชญ์ หลีกภัย</li>
        <li style='font-size: 1.1rem;'><em>ชั้น 6/13 เลขที่ 29</em></li>
        <img src='https://media-hosting.imagekit.io//a39b45568dc14fab/IMG_20250208_223334.jpg?Expires=1833637018&Key-Pair-Id=K2ZIVPTIP2VGHC&Signature=M2tJAPHXihMl1OUnwNiEBpEggLW-AZag9HFNkFb51KiIR6AGcdJkV0ovnL0DfgAx8WV7-vc65vXWLKNZWoB4vzXob5AYUfwmT9XcgJ1egfOuS3B95GNj-y3maPQ7nm2iW3Yv~Zd5HfeL~D2tZu8CdiJUdFj3bB4x22uceD6zVNP8FHAuMS5qcaDTwUQgoV9RQvKQFOLjsX9JX7ZQ6olCkXmdIXM31uDSwok1Vpru12aC3p16whyHG2iJ2s1iTROwcJurWM9F-R90NCjP63ZGEa0gdrKgHC6WvKeGSmkehKsqpQv7fL3i7dXpTSV-Z-mVVh72OcJfNr1W~WRZwIjMDQ__' width='250px'>
        </ul>
        </div>
        """, unsafe_allow_html=True)

# --- Admin Panel to Reset Visitor Count ---
st.markdown("---")
st.subheader("🔧 Admin Panel (เดาไปก็เท่านั้น)")
admin_password = st.text_input("Enter Admin Password:", type="password")
if admin_password == st.secrets["ADMIN_PASSWORD"]:
    if st.button("Reset Visitor Count and Active Users"):
        with open(COUNTER_FILE, "w") as f:
            f.write("0")
        with open(ACTIVE_USERS_FILE, "w") as f:
            f.truncate(0)
        st.success("Visitor count and active users reset to 0.")
        st.rerun()  # Force a page reload to reflect the changes immediately
        
    # --- View File Contents ---
    st.subheader("📂 View Stored Data")
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
  if admin_password != "":  # Only show the warning if the user *tried* to enter a password
       st.warning("Incorrect password or unauthorized access.")
