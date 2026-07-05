import streamlit as st
import sys, os, hashlib, time, json, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from meta_evaluator import MetaEvaluator

# ═══════════════════════════════════════════════════════════════
# COREX CONFIGURATION
# ═══════════════════════════════════════════════════════════════
APP_NAME = "CoreX"
APP_ICON = "◈"
APP_TAGLINE = "Reality-Grade AI Verification"

FREE_DAILY_LIMIT = 10
PREMIUM_PRICE = "$5.99/month"

THEME_ENGINE = {
    "default": {
        "primary": "#0a0a0f", "accent": "#6366f1", "glow": "rgba(99,102,241,0.4)",
        "text": "#e2e8f0", "muted": "#94a3b8", "card": "rgba(15,15,25,0.85)",
        "border": "rgba(99,102,241,0.2)", "particle": "#6366f1",
        "gradient": "linear-gradient(135deg, #0a0a0f 0%, #1a1a2e 50%, #16213e 100%)",
        "accent_gradient": "linear-gradient(135deg, #6366f1, #8b5cf6)",
        "score_high": "#22d3ee", "score_mid": "#fbbf24", "score_low": "#f43f5e",
        "emoji": "◈", "image_keywords": "technology abstract futuristic"
    },
    "space": {
        "primary": "#020617", "accent": "#38bdf8", "glow": "rgba(56,189,248,0.4)",
        "text": "#e0f2fe", "muted": "#7dd3fc", "card": "rgba(2,6,23,0.9)",
        "border": "rgba(56,189,248,0.2)", "particle": "#38bdf8",
        "gradient": "linear-gradient(135deg, #020617 0%, #0c4a6e 50%, #1e3a5f 100%)",
        "accent_gradient": "linear-gradient(135deg, #38bdf8, #818cf8)",
        "score_high": "#7dd3fc", "score_mid": "#fcd34d", "score_low": "#fb7185",
        "emoji": "🪐", "image_keywords": "space galaxy stars planet cosmos nebula"
    },
    "nature": {
        "primary": "#052e16", "accent": "#4ade80", "glow": "rgba(74,222,128,0.4)",
        "text": "#dcfce7", "muted": "#86efac", "card": "rgba(5,46,22,0.9)",
        "border": "rgba(74,222,128,0.2)", "particle": "#4ade80",
        "gradient": "linear-gradient(135deg, #052e16 0%, #14532d 50%, #166534 100%)",
        "accent_gradient": "linear-gradient(135deg, #4ade80, #22d3ee)",
        "score_high": "#86efac", "score_mid": "#fde047", "score_low": "#fca5a5",
        "emoji": "🌿", "image_keywords": "nature forest green landscape trees"
    },
    "history": {
        "primary": "#451a03", "accent": "#f59e0b", "glow": "rgba(245,158,11,0.4)",
        "text": "#fef3c7", "muted": "#fcd34d", "card": "rgba(69,26,3,0.9)",
        "border": "rgba(245,158,11,0.2)", "particle": "#f59e0b",
        "gradient": "linear-gradient(135deg, #451a03 0%, #78350f 50%, #92400e 100%)",
        "accent_gradient": "linear-gradient(135deg, #f59e0b, #f97316)",
        "score_high": "#fcd34d", "score_mid": "#fdba74", "score_low": "#fca5a5",
        "emoji": "🏛", "image_keywords": "ancient history monument architecture ruins"
    },
    "tech": {
        "primary": "#0f172a", "accent": "#06b6d4", "glow": "rgba(6,182,212,0.4)",
        "text": "#cffafe", "muted": "#67e8f9", "card": "rgba(15,23,42,0.9)",
        "border": "rgba(6,182,212,0.2)", "particle": "#06b6d4",
        "gradient": "linear-gradient(135deg, #0f172a 0%, #164e63 50%, #155e75 100%)",
        "accent_gradient": "linear-gradient(135deg, #06b6d4, #3b82f6)",
        "score_high": "#67e8f9", "score_mid": "#fde047", "score_low": "#fda4af",
        "emoji": "⚡", "image_keywords": "technology circuit digital cyber computer"
    },
    "art": {
        "primary": "#4a044e", "accent": "#e879f9", "glow": "rgba(232,121,249,0.4)",
        "text": "#fae8ff", "muted": "#f0abfc", "card": "rgba(74,4,78,0.9)",
        "border": "rgba(232,121,249,0.2)", "particle": "#e879f9",
        "gradient": "linear-gradient(135deg, #4a044e 0%, #86198f 50%, #a21caf 100%)",
        "accent_gradient": "linear-gradient(135deg, #e879f9, #c084fc)",
        "score_high": "#f0abfc", "score_mid": "#fde68a", "score_low": "#fecdd3",
        "emoji": "🎨", "image_keywords": "art painting creative colorful abstract"
    }
}

TOPIC_KEYWORDS = {
    "space": ["moon", "planet", "star", "galaxy", "mars", "sun", "earth", "nasa", "space", "universe", "cosmos", "satellite", "orbit", "astronaut", "rocket"],
    "nature": ["tree", "plant", "animal", "forest", "ocean", "river", "mountain", "flower", "bird", "fish", "climate", "weather", "ecosystem", "biology", "photosynthesis"],
    "history": ["war", "empire", "king", "queen", "ancient", "century", "revolution", "civilization", "dynasty", "pharaoh", "roman", "world war", "battle", "treaty"],
    "tech": ["computer", "ai", "software", "code", "internet", "phone", "robot", "chip", "quantum", "algorithm", "data", "network", "cyber", "digital", "tech"],
    "art": ["paint", "music", "sculpture", "dance", "poem", "novel", "artist", "museum", "gallery", "symphony", "theater", "film", "cinema", "literature"]
}

def detect_theme(text):
    text_lower = text.lower()
    scores = {}
    for theme, keywords in TOPIC_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in text_lower)
        if score > 0:
            scores[theme] = score
    if not scores:
        return "default"
    return max(scores, key=scores.get)

# Simple user database
USER_DB = {
    "admin": {
        "password_hash": hashlib.sha256("admin123".encode()).hexdigest(),
        "is_premium": True,
        "usage_count": 0,
        "last_reset": time.time()
    }
}

def check_password(username, password):
    if username not in USER_DB:
        return False
    return USER_DB[username]["password_hash"] == hashlib.sha256(password.encode()).hexdigest()

def reset_daily_usage(username):
    user = USER_DB[username]
    if time.time() - user["last_reset"] > 86400:
        user["usage_count"] = 0
        user["last_reset"] = time.time()

def can_use_service(username):
    user = USER_DB[username]
    reset_daily_usage(username)
    if user["is_premium"]:
        return True, float('inf')
    remaining = FREE_DAILY_LIMIT - user["usage_count"]
    return remaining > 0, remaining

# ═══════════════════════════════════════════════════════════════
# PAGE CONFIG
# ═══════════════════════════════════════════════════════════════
st.set_page_config(
    page_title=f"{APP_NAME} — {APP_TAGLINE}",
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ═══════════════════════════════════════════════════════════════
# SESSION STATE (FIXED - use unique keys to avoid conflicts)
# ═══════════════════════════════════════════════════════════════
if "cx_logged_in" not in st.session_state:
    st.session_state.cx_logged_in = False
if "cx_username" not in st.session_state:
    st.session_state.cx_username = None
if "cx_theme" not in st.session_state:
    st.session_state.cx_theme = "default"
if "cx_last_question" not in st.session_state:
    st.session_state.cx_last_question = ""
if "cx_run_eval" not in st.session_state:
    st.session_state.cx_run_eval = False
if "cx_current_q" not in st.session_state:
    st.session_state.cx_current_q = ""
if "cx_current_r" not in st.session_state:
    st.session_state.cx_current_r = ""

# Detect theme
if st.session_state.cx_last_question:
    detected = detect_theme(st.session_state.cx_last_question)
    if detected != st.session_state.cx_theme:
        st.session_state.cx_theme = detected

theme = THEME_ENGINE[st.session_state.cx_theme]

# ═══════════════════════════════════════════════════════════════
# CSS
# ═══════════════════════════════════════════════════════════════
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=Inter:wght@300;400;500;600;700;800;900&display=swap');

    .stApp {{
        background: {theme['gradient']} !important;
        font-family: 'Inter', sans-serif;
    }}
    .main .block-container {{
        padding: 0 !important;
        max-width: 100% !important;
    }}

    .theme-hero {{
        position: relative;
        width: 100%;
        height: 320px;
        overflow: hidden;
        border-radius: 0 0 40px 40px;
        margin-bottom: 2rem;
    }}
    .theme-hero img {{
        width: 100%;
        height: 100%;
        object-fit: cover;
        filter: brightness(0.35) saturate(1.2);
    }}
    .theme-hero-overlay {{
        position: absolute;
        top: 0; left: 0; right: 0; bottom: 0;
        background: linear-gradient(180deg, 
            rgba(10,10,15,0.2) 0%, 
            rgba(10,10,15,0.5) 50%,
            {theme['primary']} 100%);
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 2rem;
    }}
    .theme-hero-logo {{
        font-family: 'Space Grotesk', sans-serif;
        font-size: 3.5rem;
        font-weight: 700;
        letter-spacing: -0.05em;
        background: linear-gradient(135deg, #fff, {theme['accent']});
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0 0 60px {theme['glow']};
        animation: float 6s ease-in-out infinite;
    }}
    @keyframes float {{
        0%, 100% {{ transform: translateY(0px); }}
        50% {{ transform: translateY(-10px); }}
    }}
    .theme-hero-tagline {{
        color: rgba(255,255,255,0.7);
        font-size: 1rem;
        font-weight: 300;
        letter-spacing: 0.2em;
        text-transform: uppercase;
        margin-top: 0.5rem;
    }}
    .theme-badge {{
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        margin-top: 1rem;
        padding: 8px 24px;
        background: rgba(255,255,255,0.1);
        border: 1px solid rgba(255,255,255,0.2);
        border-radius: 50px;
        color: {theme['accent']};
        font-size: 0.85rem;
        font-weight: 500;
        backdrop-filter: blur(10px);
    }}

    .glass-card {{
        background: {theme['card']};
        border: 1px solid {theme['border']};
        border-radius: 24px;
        padding: 2rem;
        backdrop-filter: blur(20px) saturate(180%);
        -webkit-backdrop-filter: blur(20px) saturate(180%);
        box-shadow: 
            0 8px 32px rgba(0,0,0,0.3),
            0 0 0 1px {theme['border']},
            inset 0 1px 0 rgba(255,255,255,0.05);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }}
    .glass-card::before {{
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 1px;
        background: linear-gradient(90deg, transparent, {theme['accent']}, transparent);
        opacity: 0.5;
    }}
    .glass-card:hover {{
        transform: translateY(-4px) scale(1.01);
        box-shadow: 
            0 20px 60px rgba(0,0,0,0.4),
            0 0 40px {theme['glow']},
            inset 0 1px 0 rgba(255,255,255,0.1);
    }}

    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {{
        background: {theme['card']} !important;
        border: 1px solid {theme['border']} !important;
        border-radius: 16px !important;
        color: {theme['text']} !important;
        font-family: 'Inter', sans-serif !important;
        padding: 1rem 1.25rem !important;
        font-size: 1rem !important;
        transition: all 0.3s ease !important;
        box-shadow: inset 0 2px 8px rgba(0,0,0,0.2) !important;
    }}
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {{
        border-color: {theme['accent']} !important;
        box-shadow: 0 0 20px {theme['glow']}, inset 0 2px 8px rgba(0,0,0,0.2) !important;
    }}
    .stTextInput > label,
    .stTextArea > label {{
        color: {theme['muted']} !important;
        font-weight: 500 !important;
        font-size: 0.85rem !important;
        text-transform: uppercase;
        letter-spacing: 0.1em;
    }}

    .stButton > button {{
        background: {theme['accent_gradient']} !important;
        color: #fff !important;
        border: none !important;
        border-radius: 16px !important;
        padding: 1rem 2rem !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 4px 20px {theme['glow']} !important;
    }}
    .stButton > button:hover {{
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 40px {theme['glow']} !important;
    }}

    .score-ring-container {{
        position: relative;
        width: 180px;
        height: 180px;
        margin: 0 auto;
    }}
    .score-ring-svg {{
        transform: rotate(-90deg);
        filter: drop-shadow(0 0 20px {theme['glow']});
    }}
    .score-ring-bg {{
        fill: none;
        stroke: rgba(255,255,255,0.05);
        stroke-width: 8;
    }}
    .score-ring-progress {{
        fill: none;
        stroke: url(#scoreGradient);
        stroke-width: 8;
        stroke-linecap: round;
        stroke-dasharray: 502.65;
        stroke-dashoffset: 502.65;
        animation: ringFill 1.5s cubic-bezier(0.4, 0, 0.2, 1) forwards;
    }}
    @keyframes ringFill {{
        to {{ stroke-dashoffset: var(--target-offset); }}
    }}
    .score-value {{
        position: absolute;
        top: 50%; left: 50%;
        transform: translate(-50%, -50%);
        font-family: 'Space Grotesk', sans-serif;
        font-size: 2.5rem;
        font-weight: 700;
        color: {theme['text']};
    }}
    .score-label {{
        position: absolute;
        top: 65%; left: 50%;
        transform: translateX(-50%);
        color: {theme['muted']};
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 0.15em;
    }}

    .dim-bar-container {{
        margin: 0.6rem 0;
    }}
    .dim-bar-label {{
        display: flex;
        justify-content: space-between;
        color: {theme['muted']};
        font-size: 0.8rem;
        margin-bottom: 0.3rem;
    }}
    .dim-bar-track {{
        height: 5px;
        background: rgba(255,255,255,0.05);
        border-radius: 3px;
        overflow: hidden;
    }}
    .dim-bar-fill {{
        height: 100%;
        border-radius: 3px;
        background: {theme['accent_gradient']};
        box-shadow: 0 0 10px {theme['glow']};
        animation: barGrow 1s cubic-bezier(0.4, 0, 0.2, 1) forwards;
        width: 0%;
    }}
    @keyframes barGrow {{
        to {{ width: var(--bar-width); }}
    }}

    .fact-card {{
        background: {theme['card']};
        border-left: 3px solid {theme['accent']};
        border-radius: 0 12px 12px 0;
        padding: 1rem 1.25rem;
        margin: 0.5rem 0;
        font-size: 0.9rem;
        color: {theme['text']};
        line-height: 1.6;
        transition: all 0.3s ease;
    }}
    .fact-card:hover {{
        transform: translateX(4px);
        box-shadow: -4px 0 20px {theme['glow']};
    }}
    .fact-source {{
        color: {theme['accent']};
        font-size: 0.7rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-bottom: 0.25rem;
    }}

    .correction-panel {{
        background: linear-gradient(135deg, rgba(34,211,238,0.1), rgba(99,102,241,0.1));
        border: 1px solid rgba(34,211,238,0.3);
        border-radius: 20px;
        padding: 1.5rem;
        margin-top: 1rem;
    }}
    .correction-panel h4 {{
        color: #22d3ee;
        margin: 0 0 0.75rem 0;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
    }}

    .login-orb {{
        width: 100px;
        height: 100px;
        margin: 0 auto 2rem;
        border-radius: 50%;
        background: {theme['accent_gradient']};
        box-shadow: 0 0 60px {theme['glow']}, inset 0 0 30px rgba(255,255,255,0.1);
        animation: orbPulse 3s ease-in-out infinite;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 2.5rem;
    }}
    @keyframes orbPulse {{
        0%, 100% {{ transform: scale(1); box-shadow: 0 0 60px {theme['glow']}; }}
        50% {{ transform: scale(1.05); box-shadow: 0 0 100px {theme['glow']}; }}
    }}

    .premium-card {{
        background: linear-gradient(135deg, rgba(255,215,0,0.08), rgba(255,237,78,0.05));
        border: 1px solid rgba(255,215,0,0.25);
        border-radius: 24px;
        padding: 2rem;
        text-align: center;
        position: relative;
        overflow: hidden;
    }}
    .premium-card::before {{
        content: '';
        position: absolute;
        top: -50%; left: -50%;
        width: 200%; height: 200%;
        background: radial-gradient(circle, rgba(255,215,0,0.1) 0%, transparent 60%);
        animation: goldShimmer 4s ease-in-out infinite;
    }}
    @keyframes goldShimmer {{
        0%, 100% {{ transform: translate(0,0); }}
        50% {{ transform: translate(10%, 10%); }}
    }}
    .premium-price {{
        font-family: 'Space Grotesk', sans-serif;
        font-size: 2.5rem;
        font-weight: 700;
        color: #ffd700;
        text-shadow: 0 0 30px rgba(255,215,0,0.5);
    }}

    .corex-footer {{
        text-align: center;
        padding: 3rem 2rem;
        margin-top: 4rem;
        border-top: 1px solid {theme['border']};
        position: relative;
    }}
    .corex-footer::before {{
        content: '';
        position: absolute;
        top: -1px; left: 50%;
        transform: translateX(-50%);
        width: 200px; height: 1px;
        background: {theme['accent_gradient']};
    }}
    .footer-logo {{
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.5rem;
        font-weight: 700;
        background: {theme['accent_gradient']};
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }}
    .footer-links {{
        display: flex;
        justify-content: center;
        gap: 2rem;
        margin: 1rem 0;
    }}
    .footer-links a {{
        color: {theme['muted']};
        text-decoration: none;
        font-size: 0.85rem;
        transition: color 0.3s;
    }}
    .footer-links a:hover {{
        color: {theme['accent']};
    }}
    .footer-copy {{
        color: rgba(255,255,255,0.3);
        font-size: 0.8rem;
        margin-top: 1rem;
    }}

    .image-grid {{
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 0.75rem;
        margin: 1.5rem 0;
    }}
    .image-grid-item {{
        position: relative;
        border-radius: 16px;
        overflow: hidden;
        aspect-ratio: 16/10;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        border: 1px solid {theme['border']};
    }}
    .image-grid-item:hover {{
        transform: scale(1.05) translateY(-4px);
        box-shadow: 0 20px 40px rgba(0,0,0,0.4), 0 0 30px {theme['glow']};
        z-index: 10;
    }}
    .image-grid-item img {{
        width: 100%;
        height: 100%;
        object-fit: cover;
    }}

    .css-1d391kg, .css-163ttbj {{
        background: {theme['primary']} !important;
    }}

    #MainMenu {{ visibility: hidden; }}
    footer {{ visibility: hidden; }}
    .stDeployButton {{ display: none; }}

    ::-webkit-scrollbar {{ width: 6px; }}
    ::-webkit-scrollbar-track {{ background: {theme['primary']}; }}
    ::-webkit-scrollbar-thumb {{ background: {theme['accent']}; border-radius: 3px; }}
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# LOGIN PAGE
# ═══════════════════════════════════════════════════════════════
if not st.session_state.cx_logged_in:
    st.markdown("""
    <div style="max-width: 420px; margin: 0 auto; padding-top: 3rem;">
        <div class="login-orb">◈</div>
        <div style="text-align: center; margin-bottom: 2.5rem;">
            <h1 style="font-family: 'Space Grotesk', sans-serif; font-size: 2.2rem; font-weight: 700; background: linear-gradient(135deg, #6366f1, #8b5cf6); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 0.5rem;">CoreX</h1>
            <p style="color: #94a3b8; font-size: 0.95rem; letter-spacing: 0.1em; text-transform: uppercase;">Reality-Grade AI Verification</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        with st.container():
            st.markdown('<div class="glass-card" style="padding: 2rem;">', unsafe_allow_html=True)

            tab_login, tab_create = st.tabs(["Sign In", "Create Account"])

            with tab_login:
                username = st.text_input("Username", key="cx_login_user")
                password = st.text_input("Password", type="password", key="cx_login_pass")
                if st.button("Enter CoreX →", use_container_width=True, key="cx_login_btn"):
                    if check_password(username, password):
                        st.session_state.cx_logged_in = True
                        st.session_state.cx_username = username
                        st.rerun()
                    else:
                        st.error("Invalid credentials")

            with tab_create:
                new_user = st.text_input("Choose Username", key="cx_new_user")
                new_pass = st.text_input("Choose Password", type="password", key="cx_new_pass")
                if st.button("Create Free Account", use_container_width=True, key="cx_create_btn"):
                    if new_user and new_pass:
                        if new_user not in USER_DB:
                            USER_DB[new_user] = {
                                "password_hash": hashlib.sha256(new_pass.encode()).hexdigest(),
                                "is_premium": False,
                                "usage_count": 0,
                                "last_reset": time.time()
                            }
                            st.success("Account created! Sign in above.")
                        else:
                            st.error("Username taken")
                    else:
                        st.error("Fill all fields")

            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown("""
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-top: 1.5rem;">
                <div class="glass-card" style="text-align: center; padding: 1.25rem;">
                    <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">🆓</div>
                    <div style="font-weight: 600; color: #e2e8f0; margin-bottom: 0.25rem;">Free</div>
                    <div style="font-size: 0.8rem; color: #94a3b8;">10 checks/day</div>
                </div>
                <div class="glass-card" style="text-align: center; padding: 1.25rem; border-color: rgba(255,215,0,0.3);">
                    <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">⭐</div>
                    <div style="font-weight: 600; color: #ffd700; margin-bottom: 0.25rem;">Premium</div>
                    <div style="font-size: 0.8rem; color: #94a3b8;">Unlimited</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.stop()

# ═══════════════════════════════════════════════════════════════
# MAIN APP
# ═══════════════════════════════════════════════════════════════
username = st.session_state.cx_username
user = USER_DB[username]
can_use, remaining = can_use_service(username)

# Sidebar
with st.sidebar:
    st.markdown(f"""
    <div style="text-align: center; margin-bottom: 1.5rem;">
        <div style="font-family: 'Space Grotesk', sans-serif; font-size: 1.8rem; font-weight: 700; background: linear-gradient(135deg, #6366f1, #8b5cf6); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">◈ CoreX</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1rem;">
        <div style="width: 36px; height: 36px; border-radius: 50%; background: linear-gradient(135deg, #6366f1, #8b5cf6); display: flex; align-items: center; justify-content: center; font-weight: 700; color: white;">{username[0].upper()}</div>
        <div>
            <div style="font-weight: 600; color: #e2e8f0; font-size: 0.9rem;">{username}</div>
            <div style="font-size: 0.75rem; color: {'#ffd700' if user['is_premium'] else '#94a3b8'};">{'⭐ PREMIUM' if user['is_premium'] else f'🆓 FREE — {remaining} left'}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 📊 Session")
    st.markdown(f"**Checks:** {user['usage_count']}")
    st.markdown(f"**Theme:** {st.session_state.cx_theme.title()}")

    if not user["is_premium"]:
        st.markdown("---")
        st.markdown(f"""
        <div class="premium-card">
            <div style="position: relative; z-index: 1;">
                <div style="font-size: 1.2rem; margin-bottom: 0.5rem;">⭐</div>
                <div style="font-weight: 700; color: #ffd700; margin-bottom: 0.5rem;">Go Premium</div>
                <div class="premium-price">{PREMIUM_PRICE}</div>
                <div style="color: #94a3b8; font-size: 0.8rem; margin: 0.75rem 0;">
                    • Unlimited checks<br>
                    • Multi-AI engine<br>
                    • API access<br>
                    • Priority support
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.button("💳 Upgrade", use_container_width=True, key="cx_upgrade_btn")

    st.markdown("---")
    if st.button("🚪 Sign Out", use_container_width=True, key="cx_logout_btn"):
        st.session_state.cx_logged_in = False
        st.session_state.cx_username = None
        st.rerun()

# Hero with image
unsplash_keywords = theme["image_keywords"].replace(" ", ",")
hero_image_url = f"https://source.unsplash.com/1200x350/?{unsplash_keywords}"

st.markdown(f"""
<div class="theme-hero">
    <img src="{hero_image_url}" alt="{st.session_state.cx_theme.title()} theme" />
    <div class="theme-hero-overlay">
        <div class="theme-hero-logo">◈ CoreX</div>
        <div class="theme-hero-tagline">Reality-Grade AI Verification</div>
        <div class="theme-badge">{theme['emoji']} {st.session_state.cx_theme.title()} Theme Active</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Check limit
if not can_use and not user["is_premium"]:
    st.markdown("""
    <div class="glass-card" style="text-align: center; padding: 3rem; margin: 2rem 0;">
        <div style="font-size: 3rem; margin-bottom: 1rem;">🚫</div>
        <h2 style="color: #f43f5e; margin-bottom: 0.5rem;">Daily Limit Reached</h2>
        <p style="color: #94a3b8; margin-bottom: 1.5rem;">You have used all 10 free checks today.</p>
        <div class="premium-card" style="max-width: 400px; margin: 0 auto;">
            <div style="position: relative; z-index: 1;">
                <div style="font-weight: 700; color: #ffd700; margin-bottom: 0.5rem;">Upgrade to Premium</div>
                <div class="premium-price">$5.99/month</div>
                <p style="color: #94a3b8; font-size: 0.9rem; margin-top: 0.75rem;">Unlimited fact-checking. Zero limits.</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# Main interface
evaluator = MetaEvaluator()

col_input, col_result = st.columns([1, 1])

with col_input:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### 🎯 Verify Anything")

    question = st.text_input("Question", "When was the Eiffel Tower built and who designed it?", key="cx_question_input")
    response = st.text_area("AI Response to Evaluate", "The Eiffel Tower was built in 1850 by Leonardo da Vinci. It is 500 meters tall and made of solid gold.", key="cx_response_input")

    if st.button("◈ Verify Reality", use_container_width=True, key="cx_verify_btn"):
        if not can_use and not user["is_premium"]:
            st.error("Daily limit reached!")
            st.stop()

        st.session_state.cx_last_question = question
        st.session_state.cx_current_q = question
        st.session_state.cx_current_r = response
        st.session_state.cx_run_eval = True
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

# Evaluation
if st.session_state.cx_run_eval:
    question = st.session_state.cx_current_q
    response = st.session_state.cx_current_r

    with col_result:
        with st.spinner("🔍 Scanning reality..."):
            report = evaluator.evaluate_and_correct(question, response if response else None)
            user["usage_count"] += 1

        eval_data = report["evaluation"]
        score = eval_data["overall_score"]
        score_pct = (score / 5.0) * 100

        if score >= 4:
            score_color = theme["score_high"]
            score_word = "Verified"
        elif score >= 2.5:
            score_color = theme["score_mid"]
            score_word = "Questionable"
        else:
            score_color = theme["score_low"]
            score_word = "Unreliable"

        ring_offset = 502.65 * (1 - score_pct / 100)

        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### 📊 Reality Score")

        st.markdown(f"""
        <div class="score-ring-container">
            <svg class="score-ring-svg" width="180" height="180" viewBox="0 0 180 180">
                <defs>
                    <linearGradient id="scoreGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" style="stop-color:{score_color};stop-opacity:1" />
                        <stop offset="100%" style="stop-color:{theme['accent']};stop-opacity:1" />
                    </linearGradient>
                </defs>
                <circle class="score-ring-bg" cx="90" cy="90" r="80"/>
                <circle class="score-ring-progress" cx="90" cy="90" r="80" 
                    style="--target-offset: {ring_offset:.2f};"/>
            </svg>
            <div class="score-value" style="color: {score_color};">{score:.2f}</div>
            <div class="score-label">{score_word}</div>
        </div>
        """, unsafe_allow_html=True)

        dims = [
            ("Accuracy", eval_data["accuracy"]),
            ("Relevance", eval_data["relevance"]),
            ("Hallucination", eval_data["hallucination"]),
            ("Completeness", eval_data["completeness"])
        ]

        for name, val in dims:
            bar_width = (val / 5.0) * 100
            st.markdown(f"""
            <div class="dim-bar-container">
                <div class="dim-bar-label">
                    <span>{name}</span>
                    <span>{val}/5</span>
                </div>
                <div class="dim-bar-track">
                    <div class="dim-bar-fill" style="--bar-width: {bar_width}%;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown(f"""
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem; margin-top: 1rem;">
            <div style="text-align: center; padding: 0.75rem; background: rgba(255,255,255,0.03); border-radius: 12px;">
                <div style="font-size: 1.3rem; font-weight: 700; color: {theme['accent']};">{eval_data['facts_found']}</div>
                <div style="font-size: 0.7rem; color: {theme['muted']}; text-transform: uppercase; letter-spacing: 0.1em;">Facts Found</div>
            </div>
            <div style="text-align: center; padding: 0.75rem; background: rgba(255,255,255,0.03); border-radius: 12px;">
                <div style="font-size: 1.3rem; font-weight: 700; color: {theme['accent']};">{eval_data['fact_coverage']:.0f}%</div>
                <div style="font-size: 0.7rem; color: {theme['muted']}; text-transform: uppercase; letter-spacing: 0.1em;">Coverage</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    # Image Grid
    st.markdown("### 🖼️ Visual Context")
    search_query = question.replace(" ", ",")
    st.markdown(f"""
    <div class="image-grid">
        <div class="image-grid-item">
            <img src="https://source.unsplash.com/400x300/?{search_query}" alt="Related 1" />
        </div>
        <div class="image-grid-item">
            <img src="https://source.unsplash.com/400x300/?{search_query},detail" alt="Related 2" />
        </div>
        <div class="image-grid-item">
            <img src="https://source.unsplash.com/400x300/?{search_query},closeup" alt="Related 3" />
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Facts Section
    st.markdown("### 📚 Verified Sources")
    cols = st.columns(2)
    for i, fact in enumerate(report["reference_facts"][:6]):
        with cols[i % 2]:
            source_match = re.match(r'\[(.*?)\]\s*(.*)', fact)
            if source_match:
                source, content = source_match.groups()
            else:
                source, content = "Source", fact
            st.markdown(f"""
            <div class="fact-card">
                <div class="fact-source">{source}</div>
                <div>{content[:200]}{'...' if len(content) > 200 else ''}</div>
            </div>
            """, unsafe_allow_html=True)

    # Correction
    if report["corrected_answer"] != report["original_response"]:
        st.markdown("""
        <div class="correction-panel">
            <h4>✅ Reality-Corrected Answer</h4>
        """, unsafe_allow_html=True)
        st.markdown(report["corrected_answer"])
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="glass-card" style="border-color: rgba(34,211,238,0.3); background: linear-gradient(135deg, rgba(34,211,238,0.05), rgba(99,102,241,0.05));">
            <div style="display: flex; align-items: center; gap: 0.75rem;">
                <div style="font-size: 1.5rem;">✅</div>
                <div>
                    <div style="font-weight: 600; color: #22d3ee;">Verified Accurate</div>
                    <div style="color: #94a3b8; font-size: 0.85rem;">No corrections needed. This answer aligns with verified sources.</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.session_state.cx_run_eval = False

# Footer
st.markdown(f"""
<div class="corex-footer">
    <div class="footer-logo">◈ CoreX</div>
    <p style="color: {theme['muted']}; font-size: 0.9rem; margin-bottom: 1rem;">Reality-Grade AI Verification</p>
    <div class="footer-links">
        <a href="#">Privacy</a>
        <a href="#">Terms</a>
        <a href="#">API</a>
        <a href="#">Contact</a>
    </div>
    <div class="footer-copy">
        © 2026 CoreX Systems. All rights reserved.<br>
        Powered by Wikipedia, Wikidata & Live Web Intelligence
    </div>
</div>
""", unsafe_allow_html=True)
