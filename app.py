import streamlit as st
import json
import pandas as pd
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
import hashlib

# ══════════════════════════════════════════
#  PAGE CONFIG
# ══════════════════════════════════════════
st.set_page_config(
    page_title="Karim Maher | Data Analyst",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ══════════════════════════════════════════
#  GOOGLE SHEETS CONNECTION
# ══════════════════════════════════════════
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

@st.cache_resource
def get_gsheet_client():
    """اتصال بـ Google Sheets عبر secrets"""
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=SCOPES
    )
    return gspread.authorize(creds)

def get_sheet(sheet_name: str):
    client = get_gsheet_client()
    spreadsheet = client.open(st.secrets["spreadsheet_name"])
    return spreadsheet.worksheet(sheet_name)

# ── Projects ──
def load_projects() -> list:
    try:
        sh = get_sheet("projects")
        records = sh.get_all_records()
        return records
    except Exception as e:
        st.error(f"خطأ في تحميل المشاريع: {e}")
        return []

def save_project(proj: dict):
    sh = get_sheet("projects")
    row = [
        proj.get("id",""),
        proj.get("name",""),
        proj.get("type",""),
        proj.get("desc",""),
        proj.get("tools",""),
        proj.get("link",""),
        proj.get("emoji","📁"),
        proj.get("image_url",""),
        proj.get("date",""),
    ]
    sh.append_row(row)

def delete_project(project_id: str):
    sh = get_sheet("projects")
    records = sh.get_all_records()
    for i, r in enumerate(records, start=2):
        if str(r.get("id","")) == str(project_id):
            sh.delete_rows(i)
            break

# ── Profile ──
def load_profile() -> dict:
    try:
        sh = get_sheet("profile")
        records = sh.get_all_records()
        if records:
            return records[0]
        return {}
    except Exception as e:
        return {}

def save_profile(data: dict):
    sh = get_sheet("profile")
    sh.clear()
    sh.append_row(list(data.keys()))
    sh.append_row(list(data.values()))

# ══════════════════════════════════════════
#  AUTH
# ══════════════════════════════════════════
def hash_pw(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()

def check_password(entered: str, stored_hash: str) -> bool:
    return hash_pw(entered) == stored_hash

def is_logged_in() -> bool:
    return st.session_state.get("admin_logged_in", False)

# ══════════════════════════════════════════
#  CSS
# ══════════════════════════════════════════
def inject_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700;900&family=JetBrains+Mono:wght@400;700&display=swap');

    :root {
      --bg: #060810; --surface: #0d1117; --surface2: #161b27;
      --cyan: #00d4ff; --green: #00ff88; --orange: #ff8c42;
      --pink: #ff4d8d; --purple: #9b59ff;
      --text: #e2e8f8; --muted: #4a5580;
      --border: rgba(0,212,255,0.12);
    }

    html, body, [class*="css"] {
      font-family: 'Cairo', sans-serif !important;
      background-color: var(--bg) !important;
      color: var(--text) !important;
      direction: rtl;
    }

    /* Hide Streamlit default elements */
    #MainMenu, footer, header { visibility: hidden; }
    .block-container { padding: 2rem 3rem !important; max-width: 1200px; margin: 0 auto; }

    /* HERO */
    .hero-wrap {
      display: flex; align-items: center; justify-content: space-between;
      gap: 3rem; padding: 3rem 0 4rem; flex-wrap: wrap;
    }
    .hero-name {
      font-family: 'JetBrains Mono', monospace !important;
      font-size: 3.5rem; font-weight: 900; line-height: 1.1;
      background: linear-gradient(90deg, #00d4ff, #00ff88);
      -webkit-background-clip: text; -webkit-text-fill-color: transparent;
      margin-bottom: 0.5rem;
    }
    .hero-title { font-size: 1.1rem; color: var(--muted); font-weight: 700; margin-bottom: 1rem; }
    .hero-loc { color: var(--muted); font-size: 0.9rem; margin-bottom: 1.5rem; }

    .status-badge {
      display: inline-flex; align-items: center; gap: 0.5rem;
      background: rgba(0,212,255,0.06); border: 1px solid rgba(0,212,255,0.2);
      color: #00d4ff; border-radius: 6px; padding: 0.4rem 0.9rem;
      font-size: 0.78rem; font-weight: 700; margin-bottom: 1.5rem;
      font-family: 'JetBrains Mono', monospace;
    }

    /* AVATAR RING */
    .avatar-ring {
      width: 180px; height: 180px; border-radius: 50%; flex-shrink: 0;
      background: conic-gradient(#00d4ff, #00ff88, #9b59ff, #00d4ff);
      padding: 4px; animation: spin 4s linear infinite;
    }
    .avatar-inner {
      width: 100%; height: 100%; border-radius: 50%;
      background: #060810; display: flex; align-items: center; justify-content: center;
      font-size: 5rem; overflow: hidden;
    }
    .avatar-inner img { width: 100%; height: 100%; object-fit: cover; border-radius: 50%; }
    @keyframes spin { to { transform: rotate(360deg); } }

    /* SECTION */
    .sec-label {
      display: flex; align-items: center; gap: 0.8rem; margin-bottom: 0.5rem;
    }
    .sec-line { width: 35px; height: 2px; background: linear-gradient(90deg, #00d4ff, transparent); display: inline-block; }
    .sec-tag { font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: #00d4ff; font-weight: 700; letter-spacing: 2px; }
    .sec-title { font-size: 2rem; font-weight: 900; margin-bottom: 1.5rem; }
    .sec-title em { font-style: normal; color: #00d4ff; }

    /* CARDS */
    .card {
      background: #0d1117; border: 1px solid rgba(0,212,255,0.1);
      border-radius: 16px; padding: 1.5rem;
      transition: all 0.3s ease;
    }
    .card:hover { border-color: rgba(0,212,255,0.3); transform: translateY(-4px); box-shadow: 0 0 30px rgba(0,212,255,0.15); }

    /* PROJ CARD */
    .proj-card {
      background: #0d1117; border: 1px solid rgba(0,212,255,0.1);
      border-radius: 18px; overflow: hidden; transition: all 0.35s ease;
      height: 100%;
    }
    .proj-card:hover { border-color: rgba(0,212,255,0.3); transform: translateY(-6px); box-shadow: 0 20px 50px rgba(0,0,0,0.5), 0 0 25px rgba(0,212,255,0.12); }
    .proj-thumb {
      height: 160px; background: #161b27;
      display: flex; align-items: center; justify-content: center;
      font-size: 3.5rem; position: relative;
    }
    .proj-thumb img { width: 100%; height: 100%; object-fit: cover; }
    .proj-type-chip {
      display: inline-block; font-size: 0.62rem; font-weight: 700;
      padding: 0.2rem 0.6rem; border-radius: 6px;
      font-family: 'JetBrains Mono', monospace; margin-bottom: 0.5rem;
    }
    .type-dashboard { background: rgba(0,212,255,0.15); color: #00d4ff; }
    .type-streamlit  { background: rgba(255,77,141,0.15); color: #ff4d8d; }
    .type-notebook   { background: rgba(255,140,66,0.15); color: #ff8c42; }
    .type-pdf        { background: rgba(155,89,255,0.15); color: #9b59ff; }
    .type-video      { background: rgba(0,255,136,0.15);  color: #00ff88; }
    .type-link       { background: rgba(74,85,128,0.2);   color: #8899cc; }

    .proj-name { font-size: 1rem; font-weight: 900; margin-bottom: 0.4rem; }
    .proj-desc { font-size: 0.8rem; color: #4a5580; line-height: 1.6; margin-bottom: 0.8rem; }
    .tool-chip {
      display: inline-block; font-size: 0.6rem; font-weight: 700;
      padding: 0.15rem 0.45rem; background: #161b27;
      border: 1px solid rgba(0,212,255,0.1); border-radius: 5px;
      color: #4a5580; font-family: 'JetBrains Mono', monospace; margin: 0.1rem;
    }

    /* CERT ITEM */
    .cert-item {
      display: flex; align-items: center; gap: 1rem;
      background: #0d1117; border: 1px solid rgba(0,212,255,0.1);
      border-radius: 12px; padding: 1rem 1.2rem;
      margin-bottom: 0.8rem; transition: all 0.3s;
    }
    .cert-item:hover { border-color: rgba(0,255,136,0.3); transform: translateX(-4px); }

    /* SKILL TAG */
    .skill-tag {
      display: inline-block; background: #161b27;
      border: 1px solid rgba(0,212,255,0.1); border-radius: 8px;
      padding: 0.4rem 0.8rem; font-size: 0.8rem; font-weight: 700;
      margin: 0.2rem; transition: all 0.2s;
    }

    /* METRIC CARD */
    .metric-card {
      background: #0d1117; border: 1px solid rgba(0,212,255,0.1);
      border-radius: 16px; padding: 1.5rem; text-align: center;
      transition: all 0.3s;
    }
    .metric-card:hover { transform: translateY(-4px); border-color: rgba(0,212,255,0.2); }
    .metric-val { font-size: 2.2rem; font-weight: 900; font-family: 'JetBrains Mono', monospace; color: #00d4ff; }
    .metric-label { font-size: 0.8rem; color: #4a5580; font-weight: 700; margin-top: 0.3rem; }

    /* STREAMLIT CARD */
    .st-card {
      background: #0d1117; border: 1px solid rgba(255,77,141,0.15);
      border-radius: 16px; padding: 1.5rem; transition: all 0.3s;
    }
    .st-card:hover { border-color: rgba(255,77,141,0.4); transform: translateY(-5px); box-shadow: 0 0 25px rgba(255,77,141,0.12); }

    /* ADMIN */
    .admin-header {
      background: rgba(255,77,141,0.06); border: 1px solid rgba(255,77,141,0.15);
      border-radius: 12px; padding: 1rem 1.5rem;
      display: flex; align-items: center; justify-content: space-between;
      margin-bottom: 2rem;
    }

    /* PILLS */
    .pill {
      display: inline-flex; align-items: center; gap: 0.4rem;
      padding: 0.35rem 0.8rem; background: #161b27;
      border: 1px solid rgba(0,212,255,0.1); border-radius: 50px;
      font-size: 0.78rem; font-weight: 700; color: #4a5580; margin: 0.2rem;
    }

    /* CONTACT */
    .contact-card {
      background: #0d1117; border: 1px solid rgba(0,212,255,0.1);
      border-radius: 12px; padding: 1rem 1.5rem; margin-bottom: 0.8rem;
      transition: all 0.3s; text-decoration: none; display: block; color: #e2e8f8;
    }
    .contact-card:hover { border-color: #00d4ff; color: #00d4ff; transform: translateY(-2px); }

    /* FOOTER */
    .footer-wrap {
      border-top: 1px solid rgba(0,212,255,0.1); padding: 2rem 0;
      text-align: center; margin-top: 4rem;
    }
    .footer-logo { font-family: 'JetBrains Mono', monospace; font-size: 1rem; color: #00d4ff; }
    .footer-copy { font-size: 0.75rem; color: #4a5580; margin-top: 0.3rem; }

    /* Streamlit button overrides */
    .stButton > button {
      font-family: 'Cairo', sans-serif !important;
      font-weight: 700 !important; border-radius: 8px !important;
    }
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div {
      background: #161b27 !important; border-color: rgba(0,212,255,0.15) !important;
      color: #e2e8f8 !important; font-family: 'Cairo', sans-serif !important;
    }
    div[data-testid="stSidebar"] {
      background: #0d1117 !important;
      border-left: 1px solid rgba(0,212,255,0.1) !important;
    }

    /* BG */
    .stApp { background: #060810 !important; }
    </style>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════
#  DEFAULT PROFILE DATA
# ══════════════════════════════════════════
DEFAULT_PROFILE = {
    "name_en"   : "Karim Maher",
    "title"     : "📊 Data Analyst · محلل بيانات",
    "location"  : "Alexandria, Egypt",
    "phone"     : "01063872784",
    "email"     : "",
    "linkedin"  : "",
    "github"    : "",
    "edu"       : "دبلومة تحليل البيانات — أكاديمية Tech Trek",
    "bio"       : "محلل بيانات متخصص في بناء نماذج تحليلية وتطبيقات Streamlit ولوحات معلومات تفاعلية، شغوف بتحويل البيانات لقرارات ذكية.",
    "skills"    : "Python, SQL, Power BI, Streamlit, Pandas, Scikit-learn, Excel, Matplotlib",
    "photo_url" : "",
    "pw_hash"   : hashlib.sha256("karim2024".encode()).hexdigest(),
}

TYPE_LABELS = {
    "dashboard" : "📊 Dashboard",
    "streamlit" : "🚀 Streamlit App",
    "notebook"  : "📓 Jupyter Notebook",
    "pdf"       : "📄 PDF Report",
    "video"     : "🎬 Video",
    "link"      : "🔗 External Link",
}

TYPE_COLORS = {
    "dashboard" : "type-dashboard",
    "streamlit" : "type-streamlit",
    "notebook"  : "type-notebook",
    "pdf"       : "type-pdf",
    "video"     : "type-video",
    "link"      : "type-link",
}

SKILL_ICONS = {
    "python": "🐍", "sql": "🗄️", "power": "📊", "streamlit": "🚀",
    "pandas": "📈", "scikit": "🤖", "excel": "📋", "tableau": "📉",
    "matplotlib": "📉", "seaborn": "🎨", "numpy": "🔢", "r ": "📐",
}

# ══════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════
def get_profile_val(profile: dict, key: str) -> str:
    val = profile.get(key, "")
    if not val:
        val = DEFAULT_PROFILE.get(key, "")
    return str(val)

def render_skills(skills_str: str):
    html = ""
    for s in skills_str.split(","):
        s = s.strip()
        if not s:
            continue
        icon = "⚙️"
        for k, v in SKILL_ICONS.items():
            if k in s.lower():
                icon = v
                break
        html += f'<span class="skill-tag">{icon} {s}</span>'
    return html

# ══════════════════════════════════════════
#  PUBLIC: HERO
# ══════════════════════════════════════════
def render_hero(profile: dict):
    name     = get_profile_val(profile, "name_en")
    title    = get_profile_val(profile, "title")
    location = get_profile_val(profile, "location")
    phone    = get_profile_val(profile, "phone")
    photo    = get_profile_val(profile, "photo_url")

    col_text, col_avatar = st.columns([2, 1])

    with col_text:
        st.markdown('<div class="status-badge">● متاح للعمل · Available for Work</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="hero-name">{name}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="hero-title">{title}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="hero-loc">📍 {location} &nbsp;|&nbsp; 📞 {phone}</div>', unsafe_allow_html=True)
        st.markdown("""
            <div style="margin-top:1rem">
              <span class="pill">🐍 Python · SQL · Power BI</span>
              <span class="pill">🚀 Streamlit Developer</span>
              <span class="pill">🎓 Certified Analyst</span>
            </div>
        """, unsafe_allow_html=True)

    with col_avatar:
        if photo:
            st.markdown(f"""
                <div style="display:flex;justify-content:center;padding:1rem 0">
                  <div class="avatar-ring">
                    <div class="avatar-inner"><img src="{photo}" alt="{name}"></div>
                  </div>
                </div>""", unsafe_allow_html=True)
        else:
            st.markdown("""
                <div style="display:flex;justify-content:center;padding:1rem 0">
                  <div class="avatar-ring">
                    <div class="avatar-inner">👤</div>
                  </div>
                </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════
#  PUBLIC: ABOUT
# ══════════════════════════════════════════
def render_about(profile: dict):
    st.markdown('<div class="sec-label"><span class="sec-line"></span><span class="sec-tag">01 / ABOUT</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-title">التعليم و<em>الخبرة</em></div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        edu = get_profile_val(profile, "edu")
        st.markdown(f"""
            <div class="card">
              <div style="font-size:2rem;margin-bottom:.8rem">🎓</div>
              <div style="font-size:.9rem;font-weight:900;color:#00d4ff;margin-bottom:.4rem">الدبلومة المهنية</div>
              <div style="font-size:.82rem;color:#4a5580;line-height:1.7">{edu}</div>
            </div>""", unsafe_allow_html=True)
    with c2:
        bio = get_profile_val(profile, "bio")
        st.markdown(f"""
            <div class="card">
              <div style="font-size:2rem;margin-bottom:.8rem">💼</div>
              <div style="font-size:.9rem;font-weight:900;color:#00d4ff;margin-bottom:.4rem">نبذة مهنية</div>
              <div style="font-size:.82rem;color:#4a5580;line-height:1.7">{bio}</div>
            </div>""", unsafe_allow_html=True)

    c3, c4 = st.columns(2)
    with c3:
        skills_str  = get_profile_val(profile, "skills")
        skills_html = render_skills(skills_str)
        st.markdown(f"""
            <div class="card">
              <div style="font-size:2rem;margin-bottom:.8rem">🛠️</div>
              <div style="font-size:.9rem;font-weight:900;color:#00d4ff;margin-bottom:.8rem">المهارات التقنية</div>
              {skills_html}
            </div>""", unsafe_allow_html=True)
    with c4:
        st.markdown("""
            <div class="card">
              <div style="font-size:2rem;margin-bottom:.8rem">🚀</div>
              <div style="font-size:.9rem;font-weight:900;color:#00d4ff;margin-bottom:.4rem">Streamlit Developer</div>
              <div style="font-size:.82rem;color:#4a5580;line-height:1.7">
                أبني تطبيقات ويب تفاعلية بـ <strong style="color:#e2e8f8">Streamlit</strong> تحوّل نماذج البيانات لأدوات قابلة للاستخدام الفوري بدون خبرة برمجية من المستخدم
              </div>
            </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════
#  PUBLIC: CERTIFICATES
# ══════════════════════════════════════════
def render_certs():
    st.markdown('<div class="sec-label"><span class="sec-line"></span><span class="sec-tag">02 / CERTIFICATES</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-title">الشهادات <em>المهنية</em></div>', unsafe_allow_html=True)

    certs = [
        ("🏕️", "Data Analyst Track", "DataCamp — منصة دولية متخصصة في علوم البيانات", "rgba(255,140,66,.1)", "#ff8c42", "DataCamp"),
        ("🎓", "دبلومة تحليل البيانات", "أكاديمية Tech Trek — برنامج مكثف شامل", "rgba(0,212,255,.1)", "#00d4ff", "Tech Trek"),
        ("🏛️", "شهادة تحليل البيانات", "نقابة المهندسين المصريين — اعتماد رسمي معتمد", "rgba(155,89,255,.1)", "#9b59ff", "نقابة المهندسين"),
    ]
    for icon, name, issuer, bg, color, chip in certs:
        st.markdown(f"""
            <div class="cert-item">
              <div style="width:42px;height:42px;border-radius:10px;background:{bg};
                          display:flex;align-items:center;justify-content:center;font-size:1.3rem;flex-shrink:0">
                {icon}
              </div>
              <div style="flex:1">
                <div style="font-size:.88rem;font-weight:900">{name}</div>
                <div style="font-size:.73rem;color:#4a5580">{issuer}</div>
              </div>
              <span style="font-size:.65rem;font-weight:700;padding:.2rem .6rem;border-radius:6px;
                           background:{bg};color:{color};border:1px solid {color}40;
                           font-family:'JetBrains Mono',monospace">
                {chip}
              </span>
            </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════
#  PUBLIC: PROJECTS
# ══════════════════════════════════════════
def render_projects(projects: list):
    st.markdown('<div class="sec-label"><span class="sec-line"></span><span class="sec-tag">03 / PROJECTS</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-title">معرض <em>المشاريع</em></div>', unsafe_allow_html=True)

    if not projects:
        st.info("📭 لم تُضف مشاريع بعد — ادخل لوحة التحكم وأضف أول مشروع!")
        return

    # Filter tabs
    all_types = ["الكل"] + list(TYPE_LABELS.values())
    selected  = st.selectbox("🔍 فلتر حسب النوع", all_types, label_visibility="collapsed")

    filtered = projects
    if selected != "الكل":
        key = next((k for k, v in TYPE_LABELS.items() if v == selected), None)
        if key:
            filtered = [p for p in projects if p.get("type") == key]

    if not filtered:
        st.warning("لا توجد مشاريع من هذا النوع")
        return

    cols = st.columns(3)
    for i, proj in enumerate(filtered):
        with cols[i % 3]:
            ptype     = proj.get("type", "link")
            type_cls  = TYPE_COLORS.get(ptype, "type-link")
            type_lbl  = TYPE_LABELS.get(ptype, ptype)
            emoji     = proj.get("emoji", "📁")
            img_url   = proj.get("image_url", "")
            link      = proj.get("link", "")
            tools_str = proj.get("tools", "")
            tools_html= "".join([f'<span class="tool-chip">{t.strip()}</span>' for t in tools_str.split(",") if t.strip()])

            thumb_html = f'<img src="{img_url}" style="width:100%;height:160px;object-fit:cover">' if img_url else f'<span style="font-size:3.5rem">{emoji}</span>'

            open_btn = ""
            if link:
                open_btn = f'<a href="{link}" target="_blank" style="display:inline-block;margin-top:.8rem;padding:.4rem 1rem;background:linear-gradient(135deg,#00d4ff,#9b59ff);border-radius:8px;color:white;font-weight:700;font-size:.75rem;text-decoration:none">فتح ↗</a>'

            st.markdown(f"""
                <div class="proj-card" style="padding-bottom:1rem">
                  <div class="proj-thumb">{thumb_html}</div>
                  <div style="padding:.8rem 1rem">
                    <span class="proj-type-chip {type_cls}">{type_lbl}</span>
                    <div class="proj-name">{proj.get("name","")}</div>
                    <div class="proj-desc">{proj.get("desc","")}</div>
                    <div>{tools_html}</div>
                    {open_btn}
                  </div>
                </div>""", unsafe_allow_html=True)
            st.write("")

# ══════════════════════════════════════════
#  PUBLIC: STREAMLIT APPS
# ══════════════════════════════════════════
def render_streamlit_apps(projects: list):
    st_apps = [p for p in projects if p.get("type") == "streamlit"]
    if not st_apps:
        return

    st.markdown('<div class="sec-label"><span class="sec-line"></span><span class="sec-tag">04 / STREAMLIT APPS</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-title">تطبيقات <em>Streamlit</em></div>', unsafe_allow_html=True)

    cols = st.columns(3)
    for i, app in enumerate(st_apps):
        with cols[i % 3]:
            link = app.get("link", "")
            btn  = f'<a class="st-card" href="{link}" target="_blank" style="text-decoration:none;display:block">' if link else '<div class="st-card">'
            end  = '</a>' if link else '</div>'
            st.markdown(f"""
                {btn}
                  <div style="font-size:2.5rem;margin-bottom:.8rem">{app.get("emoji","🚀")}</div>
                  <div style="font-size:1rem;font-weight:900;margin-bottom:.4rem">{app.get("name","")}</div>
                  <div style="font-size:.78rem;color:#4a5580;line-height:1.6">{app.get("desc","تطبيق Streamlit تفاعلي")}</div>
                  {"<div style='margin-top:.8rem;color:#ff4d8d;font-size:.78rem;font-weight:700'>🚀 فتح التطبيق ↗</div>" if link else ""}
                {end}""", unsafe_allow_html=True)
            st.write("")

# ══════════════════════════════════════════
#  PUBLIC: CONTACT
# ══════════════════════════════════════════
def render_contact(profile: dict):
    st.markdown('<div class="sec-label"><span class="sec-line"></span><span class="sec-tag">05 / CONTACT</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-title" style="text-align:center">تواصل <em>معي</em></div>', unsafe_allow_html=True)

    phone    = get_profile_val(profile, "phone")
    email    = get_profile_val(profile, "email")
    linkedin = get_profile_val(profile, "linkedin")
    github   = get_profile_val(profile, "github")

    cols = st.columns(4)
    contacts = [
        (f"📞 {phone}",  f"tel:{phone}" if phone else "#"),
        (f"✉️ البريد",   f"mailto:{email}" if email else "#"),
        ("💼 LinkedIn",  linkedin or "#"),
        ("🐙 GitHub",    github or "#"),
    ]
    for col, (label, href) in zip(cols, contacts):
        with col:
            st.markdown(f'<a class="contact-card" href="{href}" target="_blank">{label}</a>', unsafe_allow_html=True)

# ══════════════════════════════════════════
#  ADMIN: LOGIN
# ══════════════════════════════════════════
def render_login(profile: dict):
    st.markdown("<br><br>", unsafe_allow_html=True)
    col = st.columns([1, 1, 1])[1]
    with col:
        st.markdown("""
            <div style="background:#0d1117;border:1px solid rgba(255,77,141,.2);border-radius:24px;padding:2.5rem;text-align:center">
              <div style="font-size:3rem;margin-bottom:.5rem">🔐</div>
              <div style="font-size:1.3rem;font-weight:900;margin-bottom:.3rem">لوحة التحكم</div>
              <div style="font-size:.8rem;color:#4a5580;margin-bottom:1.5rem">خاص بـ Karim Maher فقط</div>
            </div>""", unsafe_allow_html=True)
        st.write("")
        pw = st.text_input("الباسورد", type="password", placeholder="• • • • • • • •", label_visibility="collapsed")
        if st.button("دخول →", use_container_width=True):
            stored_hash = get_profile_val(profile, "pw_hash")
            if check_password(pw, stored_hash):
                st.session_state.admin_logged_in = True
                st.rerun()
            else:
                st.error("❌ باسورد غلط!")

# ══════════════════════════════════════════
#  ADMIN: DASHBOARD
# ══════════════════════════════════════════
def render_admin(profile: dict, projects: list):

    st.markdown("""
        <div class="admin-header">
          <div>
            <span style="font-size:.9rem;font-weight:900;color:#ff4d8d;font-family:'JetBrains Mono',monospace">⚙️ لوحة تحكم كريم ماهر</span>
            <div style="font-size:.72rem;color:#4a5580">أدر بروفايلك ومشاريعك — أي تغيير يظهر فوراً للكل</div>
          </div>
        </div>""", unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["👤 البروفايل والصورة", "🗂️ المشاريع"])

    # ── TAB 1: PROFILE ──
    with tab1:
        col_photo, col_form = st.columns([1, 2])

        with col_photo:
            st.markdown("#### 📷 صورتك الشخصية")
            photo_url = get_profile_val(profile, "photo_url")
            if photo_url:
                st.image(photo_url, width=200)
            else:
                st.markdown('<div style="width:200px;height:200px;background:#161b27;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:5rem;border:2px dashed rgba(0,212,255,.2)">👤</div>', unsafe_allow_html=True)
            st.write("")
            new_photo = st.text_input("🔗 رابط الصورة (URL)", value=photo_url, placeholder="https://i.imgur.com/yourphoto.jpg", help="ارفع صورتك على imgur.com أو imgbb.com وحط الرابط هنا")
            st.caption("💡 ارفع صورتك على [imgur.com](https://imgur.com) مجاناً واحضر الرابط المباشر")

        with col_form:
            st.markdown("#### ✏️ بياناتك الشخصية")
            c1, c2 = st.columns(2)
            with c1:
                new_name     = st.text_input("الاسم (إنجليزي)", value=get_profile_val(profile, "name_en"))
                new_loc      = st.text_input("الموقع", value=get_profile_val(profile, "location"))
                new_linkedin = st.text_input("رابط LinkedIn", value=get_profile_val(profile, "linkedin"))
                new_edu      = st.text_input("التعليم / الدبلومة", value=get_profile_val(profile, "edu"))
            with c2:
                new_title  = st.text_input("المسمى الوظيفي", value=get_profile_val(profile, "title"))
                new_phone  = st.text_input("رقم الهاتف", value=get_profile_val(profile, "phone"))
                new_github = st.text_input("رابط GitHub", value=get_profile_val(profile, "github"))
                new_email  = st.text_input("البريد الإلكتروني", value=get_profile_val(profile, "email"))

            new_bio    = st.text_area("نبذة شخصية", value=get_profile_val(profile, "bio"), height=80)
            new_skills = st.text_input("المهارات (افصل بفاصلة)", value=get_profile_val(profile, "skills"))

            st.markdown("#### 🔑 تغيير الباسورد")
            cp1, cp2 = st.columns(2)
            with cp1:
                new_pass = st.text_input("الباسورد الجديد", type="password", placeholder="اتركه فاضي لو مش عايز تغيره")
            with cp2:
                new_pass2 = st.text_input("تأكيد الباسورد", type="password", placeholder="كرره مرة تانية")

            if st.button("💾 حفظ كل التغييرات", use_container_width=True, type="primary"):
                pw_hash = get_profile_val(profile, "pw_hash")
                if new_pass:
                    if new_pass != new_pass2:
                        st.error("❌ الباسوردين مش متطابقين!")
                        return
                    if len(new_pass) < 4:
                        st.error("❌ الباسورد لازم 4 أحرف على الأقل")
                        return
                    pw_hash = hash_pw(new_pass)

                new_profile = {
                    "name_en"  : new_name,
                    "title"    : new_title,
                    "location" : new_loc,
                    "phone"    : new_phone,
                    "email"    : new_email,
                    "linkedin" : new_linkedin,
                    "github"   : new_github,
                    "edu"      : new_edu,
                    "bio"      : new_bio,
                    "skills"   : new_skills,
                    "photo_url": new_photo,
                    "pw_hash"  : pw_hash,
                }
                save_profile(new_profile)
                st.cache_data.clear()
                st.success("✅ تم حفظ البروفايل بنجاح! يظهر للكل دلوقتي 🎉")
                st.rerun()

        if st.button("🚪 تسجيل الخروج", use_container_width=False):
            st.session_state.admin_logged_in = False
            st.rerun()

    # ── TAB 2: PROJECTS ──
    with tab2:
        col_form, col_list = st.columns([1, 2])

        with col_form:
            st.markdown("#### ➕ إضافة مشروع جديد")
            proj_type  = st.selectbox("نوع المشروع", options=list(TYPE_LABELS.keys()), format_func=lambda x: TYPE_LABELS[x])
            proj_name  = st.text_input("اسم المشروع *")
            proj_desc  = st.text_area("وصف مختصر", height=80)
            proj_tools = st.text_input("التقنيات (افصل بفاصلة)", placeholder="Python, Pandas, Streamlit")
            proj_link  = st.text_input("رابط خارجي (URL)", placeholder="https://...")
            proj_img   = st.text_input("رابط صورة الغلاف", placeholder="https://i.imgur.com/...", help="ارفع صورة على imgur وحط الرابط")
            proj_emoji = st.text_input("إيموجي مميز", max_chars=2, placeholder="📊")

            if st.button("✅ إضافة للبورتفوليو", use_container_width=True, type="primary"):
                if not proj_name:
                    st.error("❌ أدخل اسم المشروع!")
                else:
                    new_proj = {
                        "id"        : str(int(datetime.now().timestamp())),
                        "name"      : proj_name,
                        "type"      : proj_type,
                        "desc"      : proj_desc,
                        "tools"     : proj_tools,
                        "link"      : proj_link,
                        "emoji"     : proj_emoji or {"dashboard":"📊","streamlit":"🚀","notebook":"📓","pdf":"📄","video":"🎬","link":"🔗"}.get(proj_type,"📁"),
                        "image_url" : proj_img,
                        "date"      : datetime.now().strftime("%Y-%m-%d"),
                    }
                    save_project(new_proj)
                    st.cache_data.clear()
                    st.success(f"✅ تم إضافة '{proj_name}' بنجاح!")
                    st.rerun()

        with col_list:
            st.markdown(f"#### المشاريع الحالية — {len(projects)} مشروع")
            if not projects:
                st.info("📭 لا توجد مشاريع بعد")
            else:
                for proj in projects:
                    c1, c2 = st.columns([5, 1])
                    with c1:
                        emoji = proj.get("emoji","📁")
                        ptype = TYPE_LABELS.get(proj.get("type","link"), proj.get("type",""))
                        st.markdown(f"""
                            <div style="background:#161b27;border:1px solid rgba(0,212,255,.08);
                                        border-radius:10px;padding:.8rem 1rem;margin-bottom:.5rem">
                              <div style="font-weight:900;font-size:.88rem">{emoji} {proj.get("name","")}</div>
                              <div style="font-size:.7rem;color:#4a5580">{ptype} · {proj.get("date","")} · {proj.get("tools","")}</div>
                            </div>""", unsafe_allow_html=True)
                    with c2:
                        if st.button("🗑️", key=f"del_{proj.get('id')}"):
                            delete_project(str(proj.get("id")))
                            st.cache_data.clear()
                            st.success("تم الحذف")
                            st.rerun()

# ══════════════════════════════════════════
#  MAIN APP
# ══════════════════════════════════════════
def main():
    inject_css()

    # Load data
    profile  = load_profile()
    projects = load_projects()

    # Sidebar nav
    with st.sidebar:
        st.markdown("### 📊 Karim Maher")
        page = st.radio(
            "التنقل",
            ["🏠 البورتفوليو", "🔐 لوحة التحكم"],
            label_visibility="collapsed"
        )
        st.markdown("---")
        st.caption("Karim Maher Portfolio v2.0")

    if page == "🏠 البورتفوليو":
        render_hero(profile)
        st.markdown("---")
        render_about(profile)
        st.markdown("---")
        render_certs()
        st.markdown("---")
        render_projects(projects)
        st.markdown("---")
        render_streamlit_apps(projects)
        st.markdown("---")
        render_contact(profile)
        st.markdown("""
            <div class="footer-wrap">
              <div class="footer-logo">Karim Maher · Data Analyst</div>
              <div class="footer-copy">Alexandria, Egypt 🇪🇬 · © 2026</div>
            </div>""", unsafe_allow_html=True)

    elif page == "🔐 لوحة التحكم":
        if not is_logged_in():
            render_login(profile)
        else:
            render_admin(profile, projects)

if __name__ == "__main__":
    main()
