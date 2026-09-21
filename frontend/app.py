import html as _html
from datetime import datetime

import streamlit as st

from api_client import (
    register,
    login,
    get_videos,
    create_video,
    ask_question,
    get_questions
)


# ============================================================
# Page Configuration
# ============================================================

st.set_page_config(
    page_title="AI Video Assistant",
    page_icon="🎥",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# Helpers
# ============================================================

def h(s):
    """Flatten HTML so Markdown never treats indentation as a code block."""
    return "".join(line.strip() for line in s.strip().splitlines())


def esc(value):
    return _html.escape(str(value if value is not None else ""))


def fmt_date(video):
    raw = video.get("created_at") or video.get("uploaded_at")
    if not raw:
        return ""
    try:
        return datetime.fromisoformat(
            str(raw).replace("Z", "+00:00")
        ).strftime("%b %d, %Y")
    except Exception:
        return str(raw)[:10]


def fmt_datetime(raw):
    if not raw:
        return "—"
    try:
        return datetime.fromisoformat(
            str(raw).replace("Z", "+00:00")
        ).strftime("%b %d, %Y, %I:%M %p")
    except Exception:
        return str(raw)


def badge(status):
    status = str(status or "").lower()
    return (
        f'<span class="badge badge-{esc(status)}">'
        f'{esc(status.capitalize())}</span>'
    )


def thumb_class(video):
    """Pick one of five gradients from the video id so rows look distinct."""
    return f"g{sum(ord(c) for c in str(video.get('id'))) % 5}"


PLAY_SVG = h("""
<svg viewBox="0 0 24 24" width="22" height="22" fill="none" style="display:block">
<path d="M8 5v14l11-7z" fill="#fff"/>
</svg>
""")

PLAY_SVG_BIG = PLAY_SVG.replace('width="22" height="22"', 'width="56" height="56"')


def logo_block(compact=False):
    if compact:
        return h(f"""
        <div class="logo compact">
            <div class="logo-icon">{PLAY_SVG}</div>
            <div class="logo-title">AI Video Assistant</div>
        </div>
        """)
    return h(f"""
    <div class="logo">
        <div class="logo-icon">{PLAY_SVG}</div>
        <div>
            <div class="logo-title">AI Video Assistant</div>
            <div class="logo-sub">Your Personal Video Learning Companion</div>
        </div>
    </div>
    """)


ROBOT_SVG = h("""
<svg viewBox="0 0 260 200" width="260" height="200" xmlns="http://www.w3.org/2000/svg">
<defs>
<linearGradient id="g1" x1="0" y1="0" x2="1" y2="1">
<stop offset="0" stop-color="#6D5CFF"/><stop offset="1" stop-color="#3B3FD8"/>
</linearGradient>
</defs>
<rect x="18" y="36" width="150" height="104" rx="12" fill="url(#g1)"/>
<rect x="28" y="46" width="130" height="84" rx="8" fill="#1B2A6B"/>
<circle cx="93" cy="88" r="24" fill="#3E7BFF"/>
<path d="M85 76v24l22-12z" fill="#fff"/>
<rect x="72" y="146" width="42" height="8" rx="4" fill="#4B4EF0"/>
<rect x="150" y="18" width="70" height="34" rx="12" fill="#5B6BFF"/>
<rect x="162" y="30" width="30" height="4" rx="2" fill="#fff"/>
<rect x="162" y="38" width="20" height="4" rx="2" fill="#C9D0FF"/>
<rect x="150" y="70" width="80" height="66" rx="30" fill="#EEF0FF"/>
<rect x="158" y="80" width="64" height="40" rx="18" fill="#141B4D"/>
<circle cx="175" cy="100" r="6" fill="#4DD4FF"/>
<circle cx="205" cy="100" r="6" fill="#4DD4FF"/>
<rect x="186" y="56" width="8" height="16" rx="4" fill="#B7BEFF"/>
<circle cx="190" cy="54" r="5" fill="#6D5CFF"/>
<rect x="160" y="138" width="60" height="42" rx="20" fill="#EEF0FF"/>
</svg>
""")


# ============================================================
# Styling
# ============================================================

BASE_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, .stApp, button, input, textarea, select {
    font-family: 'Inter', sans-serif !important;
}

/* hide Streamlit chrome */
#MainMenu, footer { visibility: hidden; }
[data-testid="stAppDeployButton"], .stDeployButton,
[data-testid="stMainMenu"] { display: none !important; }
header[data-testid="stHeader"] { background: transparent; }

/* ---------- Inputs ---------- */
[data-baseweb="input"], [data-baseweb="base-input"], [data-baseweb="textarea"] {
    background: #FFFFFF !important;
    border-radius: 10px !important;
}
[data-baseweb="input"], [data-baseweb="textarea"] {
    border: 1px solid #DCE0F2 !important;
}
[data-baseweb="input"]:focus-within, [data-baseweb="textarea"]:focus-within {
    border-color: #4B4EF0 !important;
    box-shadow: 0 0 0 3px rgba(75,78,240,.15) !important;
}
[data-baseweb="input"] input, [data-baseweb="textarea"] textarea {
    background: transparent !important;
    color: #1B1F3B !important;
    padding: .7rem .9rem !important;
}
.stTextInput label, .stTextArea label, .stFileUploader label {
    font-weight: 600; color: #2A2F55;
}

/* ---------- Buttons ---------- */
button[kind="primary"], button[data-testid="stBaseButton-primary"] {
    background: linear-gradient(180deg, #5558F5, #4245E6) !important;
    border: none !important;
    color: #fff !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    min-height: 2.8rem;
    box-shadow: 0 6px 16px rgba(75,78,240,.28);
}
button[kind="primary"] p, button[data-testid="stBaseButton-primary"] p { color: #fff !important; }
button[kind="primary"]:hover, button[data-testid="stBaseButton-primary"]:hover {
    filter: brightness(1.08);
}
button[kind="secondary"], button[data-testid="stBaseButton-secondary"] {
    border-radius: 10px !important;
    font-weight: 600 !important;
    border: 1px solid #DCE0F2 !important;
    background: #fff !important;
    color: #3B3FD8 !important;
    min-height: 2.6rem;
}
button[kind="secondary"]:hover, button[data-testid="stBaseButton-secondary"]:hover {
    border-color: #4B4EF0 !important; background: #F3F4FF !important;
}

/* ---------- Logo (fixed alignment: flex-centered, block SVG) ---------- */
.logo { display: flex; align-items: center; gap: .75rem; }
.logo-icon {
    width: 40px; height: 40px; border-radius: 11px;
    display: flex; align-items: center; justify-content: center;
    background: linear-gradient(135deg, #6D5CFF, #3B6CFF);
    box-shadow: 0 6px 14px rgba(75,78,240,.35);
    flex-shrink: 0;
}
.logo-icon svg { display: block; margin-left: 2px; }
.logo-title { font-weight: 700; font-size: 1.15rem; color: #1B1F5E; line-height: 1.2; }
.logo-sub { font-size: .72rem; color: #6B7194; }
.logo.compact { gap: .65rem; padding-left: .3rem; }
.logo.compact .logo-icon { width: 34px; height: 34px; border-radius: 9px; }
.logo.compact .logo-icon svg { width: 18px; height: 18px; }
.logo.compact .logo-title { font-size: .92rem; color: #fff; }

/* ---------- Badges ---------- */
.badge {
    display: inline-block; padding: .28rem .8rem; border-radius: 999px;
    font-size: .74rem; font-weight: 600; border: 1px solid transparent;
}
.badge-completed { background: #E4F8EC; color: #16925A; border-color: #BDEBD0; }
.badge-processing { background: #FFF3DC; color: #C77A0A; border-color: #FBDDA0; }
.badge-failed { background: #FFE6E9; color: #D8384E; border-color: #F8BCC5; }

/* ---------- Page header ---------- */
.page-title { font-size: 1.7rem; font-weight: 800; color: #14184A; margin: 0; }
.page-sub { color: #6B7194; font-size: .9rem; margin-top: .2rem; }
.user-chip { display: flex; justify-content: flex-end; align-items: center; gap: .55rem; }
.user-chip .avatar {
    width: 34px; height: 34px; border-radius: 50%;
    background: linear-gradient(135deg, #6D5CFF, #3B3FD8);
    color: #fff; font-weight: 700; display: flex;
    align-items: center; justify-content: center; font-size: .9rem;
}
.user-chip .name { font-weight: 600; color: #2A2F55; font-size: .88rem; }

/* ---------- Stat cards ---------- */
.stat-card {
    position: relative; overflow: hidden;
    border-radius: 14px; padding: 1rem 1.2rem; border: 1px solid transparent;
}
.stat-card .num { font-size: 1.8rem; font-weight: 800; line-height: 1.1; }
.stat-card .lbl { font-size: .82rem; font-weight: 500; margin-top: .15rem; }
.stat-card .ico {
    position: absolute; right: 1rem; top: 50%; transform: translateY(-50%);
    font-size: 1.9rem; opacity: .35;
}
.stat-total { background: #E6F0FF; border-color: #CFE0FF; color: #2358C9; }
.stat-done { background: #DFF7E9; border-color: #BFEBD2; color: #15925A; }
.stat-proc { background: #FFF1D6; border-color: #F9DCA0; color: #C77A0A; }
.stat-fail { background: #FFE3E7; border-color: #F8BCC5; color: #D8384E; }

.section-title { font-size: 1.1rem; font-weight: 700; color: #14184A; margin: 0; }
.section-gap { height: 1.3rem; }

/* View All link-style button */
.st-key-viewall button {
    min-height: 2.2rem !important; border-radius: 999px !important;
    font-size: .85rem;
}

/* ---------- Video rows ---------- */
[class*="st-key-vrow_"] {
    background: #fff; border: 1px solid #E7E9F5; border-radius: 14px;
    padding: .8rem 1rem !important; margin-bottom: .6rem;
    box-shadow: 0 2px 8px rgba(30,35,90,.04);
    transition: box-shadow .15s ease, border-color .15s ease;
}
[class*="st-key-vrow_"]:hover {
    box-shadow: 0 8px 22px rgba(60,65,170,.12); border-color: #CFD3F7;
}
[class*="st-key-vrow_"] [data-testid="stHorizontalBlock"] {
    align-items: center !important;
    min-height: 58px;
}
.vinfo { display: flex; align-items: center; gap: 1rem; min-height: 58px; }
.thumb {
    width: 88px; height: 56px; border-radius: 10px; flex-shrink: 0;
    display: flex; align-items: center; justify-content: center;
    background: linear-gradient(135deg, #222B70, #4B4EF0);
}
.thumb svg { display: block; margin-left: 2px; }
.thumb.g0 { background: linear-gradient(135deg, #222B70, #4B4EF0); }
.thumb.g1 { background: linear-gradient(135deg, #4A2A86, #8B5CF6); }
.thumb.g2 { background: linear-gradient(135deg, #0E4D6B, #22A6D9); }
.thumb.g3 { background: linear-gradient(135deg, #12604A, #2FB67C); }
.thumb.g4 { background: linear-gradient(135deg, #7A2A5C, #E0567F); }
.thumb.big { width: 100%; height: 200px; border-radius: 14px; }
.v-title { font-weight: 600; color: #1B1F3B; font-size: .95rem; line-height: 1.3; }
.v-meta { color: #7A80A3; font-size: .78rem; margin-top: .2rem; }

/* ---------- Detail card ---------- */
.detail-card {
    background: #fff; border: 1px solid #E7E9F5; border-radius: 14px; padding: 1rem 1.2rem;
}
.detail-row { display: flex; justify-content: space-between; gap: 1rem; padding: .5rem 0;
    border-bottom: 1px solid #F0F1FA; font-size: .86rem; }
.detail-row:last-child { border-bottom: none; }
.detail-row .k { color: #7A80A3; }
.detail-row .v { color: #1B1F3B; font-weight: 500; text-align: right; }
.tip-box {
    background: #E9F0FF; border: 1px solid #CADBFF; border-radius: 12px;
    padding: .9rem 1.1rem; color: #23408F; margin-top: 1rem; font-size: .9rem;
}
.tip-box b { display: block; margin-bottom: .1rem; }

.empty-state {
    background: #fff; border: 1px dashed #CFD3F7; border-radius: 14px;
    padding: 2.2rem 1rem; text-align: center; color: #6B7194;
}
.empty-state .big { font-size: 2rem; }

/* ---------- Pill / segmented buttons (filters, upload toggle) ---------- */
.st-key-filters button, .st-key-method_toggle button {
    border-radius: 999px !important; min-height: 2.5rem;
}
.st-key-method_toggle button { min-height: 2.9rem; }

/* ---------- File uploader ---------- */
[data-testid="stFileUploaderDropzone"] {
    background: #F7F8FF; border: 2px dashed #C5CBF5; border-radius: 14px; padding: 1.6rem;
}

/* ---------- Tabs ---------- */
button[data-baseweb="tab"] { font-weight: 600; }
[data-baseweb="tab-highlight"] { background-color: #4B4EF0 !important; }

/* ---------- Expanders ---------- */
[data-testid="stExpander"] {
    background: #fff; border: 1px solid #E7E9F5 !important; border-radius: 12px;
}
</style>
"""


APP_CSS = """
<style>
.stApp { background: #F5F6FF; }
.block-container { padding-top: 2rem; max-width: 1100px; }

/* ---------- Sidebar ---------- */
[data-testid="stSidebar"] { background: #0B1230; }
[data-testid="stSidebar"] [data-testid="stSidebarContent"] { padding: 1.2rem .8rem; }
[data-testid="stSidebar"] [data-testid="stVerticalBlock"] { gap: .35rem; }

/* nav buttons: left aligned, icon + label */
[class*="st-key-nav_"] button, [class*="st-key-navact_"] button,
.st-key-logout_wrap button {
    width: 100%; min-height: 2.8rem;
    justify-content: flex-start !important;
    border: none !important; box-shadow: none !important;
    border-radius: 10px !important; padding: .55rem .9rem !important;
}
[class*="st-key-nav_"] button > div, [class*="st-key-navact_"] button > div,
.st-key-logout_wrap button > div {
    justify-content: flex-start !important; width: 100%; gap: .7rem;
}
[class*="st-key-nav_"] button p, [class*="st-key-navact_"] button p,
.st-key-logout_wrap button p {
    color: inherit !important; font-size: .92rem; font-weight: 500;
    text-align: left !important;
}
[class*="st-key-nav_"] button [data-testid="stIconMaterial"],
[class*="st-key-navact_"] button [data-testid="stIconMaterial"],
.st-key-logout_wrap button [data-testid="stIconMaterial"] {
    color: inherit !important; font-size: 1.3rem;
}

[class*="st-key-nav_"] button {
    background: transparent !important; color: #B9BFE0 !important;
}
[class*="st-key-nav_"] button:hover {
    background: rgba(255,255,255,.07) !important; color: #fff !important;
}
[class*="st-key-navact_"] button {
    background: #2B3196 !important; color: #fff !important;
    box-shadow: inset 3px 0 0 #8E94FF !important;
}

.st-key-logout_wrap button {
    background: transparent !important; color: #FF7A8A !important;
}
.st-key-logout_wrap button:hover { background: rgba(255,90,110,.12) !important; }

.sidebar-spacer { height: 34vh; }
.sidebar-divider { height: 1px; background: rgba(255,255,255,.08); margin: .6rem 0; }
</style>
"""


AUTH_CSS = """
<style>
.stApp {
    background: radial-gradient(circle at 15% 10%, #3A2A86 0%, #12163F 45%, #0A0D2A 100%);
}
[data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"] { display: none; }
.block-container { padding-top: 2.5rem; max-width: 1080px; }

[class*="st-key-authcard_"] {
    border-radius: 22px; overflow: hidden;
    box-shadow: 0 30px 80px rgba(0,0,0,.45);
    background: #fff;
}
[class*="st-key-authcard_"] [data-testid="stHorizontalBlock"] {
    gap: 0 !important; align-items: stretch;
}
[class*="st-key-authcard_"] [data-testid="stColumn"],
[class*="st-key-authcard_"] [data-testid="column"] { min-width: 0; }
[class*="st-key-authcard_"] [data-testid="stColumn"]:first-child,
[class*="st-key-authcard_"] [data-testid="column"]:first-child {
    background: #F8F9FF; padding: 2.4rem 2.6rem;
}
.st-key-authcard_login [data-testid="stColumn"]:last-child,
.st-key-authcard_login [data-testid="column"]:last-child {
    background: linear-gradient(160deg, #0B1030, #1B1552);
}
.st-key-authcard_register [data-testid="stColumn"]:last-child,
.st-key-authcard_register [data-testid="column"]:last-child {
    background: linear-gradient(160deg, #ECEEFF, #DDE0FF);
}

.auth-heading { font-size: 2rem; font-weight: 800; color: #14184A; margin: 2.2rem 0 .2rem; }
.auth-sub { color: #6B7194; font-size: .92rem; margin-bottom: 1.4rem; }

.auth-right { padding: 2.2rem 2.2rem; min-height: 620px; display: flex;
    flex-direction: column; justify-content: center; }
.auth-right .illus { display: flex; justify-content: center; margin-bottom: 1.2rem; }
.auth-right h2 { font-size: 1.6rem; font-weight: 800; line-height: 1.25; margin: 0 0 .7rem; }
.auth-right p { font-size: .82rem; line-height: 1.5; margin-bottom: 1.2rem; }
.auth-right ul { list-style: none; padding: 0; margin: 0; }
.auth-right li { display: flex; align-items: center; gap: .7rem;
    font-size: .88rem; padding: .4rem 0; }
.auth-right.dark { color: #fff; }
.auth-right.dark p { color: #C9CDF0; }
.auth-right.dark .ic {
    width: 26px; height: 26px; border-radius: 8px; background: #2FB67C;
    display: flex; align-items: center; justify-content: center;
    font-size: .8rem; color: #fff;
}
.auth-right.light { color: #14184A; }
.auth-right.light p, .auth-right.light li { color: #3A4070; }
.auth-right.light .ic { color: #3B3FD8; font-weight: 800; }

.st-key-auth_switch button {
    background: transparent !important; border: none !important;
    box-shadow: none !important; color: #4B4EF0 !important;
    font-weight: 600 !important;
}
</style>
"""


# ============================================================
# Reusable UI pieces
# ============================================================

def page_header(title, subtitle):
    left, right = st.columns([4, 1], vertical_alignment="center")
    with left:
        st.markdown(
            h(f"""
            <div class="page-title">{title}</div>
            <div class="page-sub">{subtitle}</div>
            """),
            unsafe_allow_html=True
        )
    with right:
        username = st.session_state.get("username") or "user"
        st.markdown(
            h(f"""
            <div class="user-chip">
                <div class="avatar">{esc(username[:1].upper())}</div>
                <div class="name">{esc(username)}</div>
            </div>
            """),
            unsafe_allow_html=True
        )


def open_video(video_id):
    st.session_state["page"] = "My Videos"
    st.session_state["selected_video"] = video_id


def close_video():
    st.session_state.pop("selected_video", None)


def go(page_name):
    st.session_state["page"] = page_name
    st.session_state.pop("selected_video", None)


def set_state(key, value):
    st.session_state[key] = value


def video_row(video, prefix):
    with st.container(key=f"vrow_{prefix}_{video['id']}"):
        c_info, c_badge, c_btn = st.columns(
            [6, 1.8, 1.2],
            vertical_alignment="center"
        )

        with c_info:
            st.markdown(
                h(f"""
                <div class="vinfo">
                    <div class="thumb {thumb_class(video)}">{PLAY_SVG}</div>
                    <div>
                        <div class="v-title">{esc(video['title'])}</div>
                        <div class="v-meta">{esc(fmt_date(video))}</div>
                    </div>
                </div>
                """),
                unsafe_allow_html=True
            )

        with c_badge:
            st.markdown(badge(video["status"]), unsafe_allow_html=True)

        with c_btn:
            st.button(
                "Open",
                key=f"open_{prefix}_{video['id']}",
                on_click=open_video,
                args=(video["id"],),
                use_container_width=True
            )


def empty_state(message):
    st.markdown(
        h(f"""
        <div class="empty-state">
            <div class="big">📹</div>
            <div>{esc(message)}</div>
        </div>
        """),
        unsafe_allow_html=True
    )


def render_ask(token, video):
    """Ask a question about a completed video."""

    question = st.text_input(
        "Ask a question about this video",
        key=f"question_{video['id']}"
    )

    if st.button(
        "🤖 Ask AI",
        key=f"ask_{video['id']}",
        type="primary"
    ):

        if not question:

            st.warning(
                "Please enter a question."
            )

        else:

            with st.spinner(
                "Thinking..."
            ):

                response = ask_question(
                    token,
                    video["id"],
                    question
                )

            if response.status_code == 201:

                result = response.json()

                st.success("Answer")

                st.write(
                    result["answer"]
                )

            else:

                try:
                    error = response.json()

                except Exception:
                    error = (
                        "Could not get an answer."
                    )

                st.error(error)


def render_history(token, video):
    """Question history for a completed video."""

    st.subheader(
        "📚 Question History"
    )

    history_response = get_questions(
        token,
        video["id"]
    )

    if history_response.status_code == 200:

        history_data = history_response.json()

        if not history_data:

            st.info("No questions asked yet.")

        else:

            for item in history_data:

                with st.expander(
                    f"❓ {item['question']}"
                ):

                    st.write(item["answer"])

    else:

        st.error(
            "Could not load question history."
        )


# ============================================================
# LOGGED-IN PAGES
# ============================================================

def sidebar_nav():
    current = st.session_state.get("page", "Dashboard")

    nav_items = [
        ("Dashboard", ":material/home:"),
        ("Upload Video", ":material/cloud_upload:"),
        ("My Videos", ":material/video_library:"),
        ("Settings", ":material/settings:"),
    ]

    with st.sidebar:
        st.markdown(logo_block(compact=True), unsafe_allow_html=True)
        st.markdown("<div style='height:1.4rem'></div>", unsafe_allow_html=True)

        for name, icon in nav_items:
            active = (current == name)
            prefix = "navact_" if active else "nav_"

            with st.container(key=f"{prefix}{name.replace(' ', '_')}"):
                st.button(
                    name,
                    icon=icon,
                    key=f"b_{name}",
                    on_click=go,
                    args=(name,),
                    use_container_width=True
                )

        st.markdown('<div class="sidebar-spacer"></div>', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)

        # ---------------- Logout ----------------
        with st.container(key="logout_wrap"):
            if st.button(
                "Logout",
                icon=":material/logout:",
                key="logout_btn",
                use_container_width=True
            ):
                st.session_state.clear()
                st.rerun()


# -----------------------------
# Dashboard
# -----------------------------

def page_dashboard(token):
    username = st.session_state.get("username")

    page_header(
        f"Welcome back, {esc(username)}! 👋",
        "Keep learning, keep growing."
    )

    response = get_videos(token)

    if response.status_code == 200:

        data = response.json()
        results = data["results"]

        completed = sum(1 for v in results if v["status"] == "completed")
        processing = sum(1 for v in results if v["status"] == "processing")
        failed = sum(1 for v in results if v["status"] == "failed")

        st.markdown("<div style='height:.6rem'></div>", unsafe_allow_html=True)

        c1, c2, c3, c4 = st.columns(4)
        cards = [
            (c1, "stat-total", data["count"], "Total Videos", "🎬"),
            (c2, "stat-done", completed, "Completed", "✅"),
            (c3, "stat-proc", processing, "Processing", "⏳"),
            (c4, "stat-fail", failed, "Failed", "⚠️"),
        ]
        for col, cls, num, label, emoji in cards:
            with col:
                st.markdown(
                    h(f"""
                    <div class="stat-card {cls}">
                        <div class="num">{num}</div>
                        <div class="lbl">{label}</div>
                        <div class="ico">{emoji}</div>
                    </div>
                    """),
                    unsafe_allow_html=True
                )

        st.markdown('<div class="section-gap"></div>', unsafe_allow_html=True)

        t_left, t_right = st.columns([6, 1.3], vertical_alignment="center")
        with t_left:
            st.markdown(
                '<div class="section-title">Recent Videos</div>',
                unsafe_allow_html=True
            )
        with t_right:
            with st.container(key="viewall"):
                st.button(
                    "View All",
                    icon=":material/arrow_forward:",
                    key="view_all",
                    on_click=go,
                    args=("My Videos",),
                    use_container_width=True
                )

        st.markdown("<div style='height:.5rem'></div>", unsafe_allow_html=True)

        if data["count"] == 0:

            empty_state("No videos yet. Upload your first video to get started.")

        else:

            for video in results[:5]:
                video_row(video, "dash")

    else:

        st.error(
            "Could not load your videos."
        )


# -----------------------------
# Upload Video
# -----------------------------

def page_upload(token):
    page_header(
        "Upload Video",
        "Upload a video file or paste a YouTube link to get started."
    )

    st.markdown("<div style='height:.8rem'></div>", unsafe_allow_html=True)

    if "upload_method" not in st.session_state:
        st.session_state["upload_method"] = "Local Video"

    upload_method = st.session_state["upload_method"]

    with st.container(key="method_toggle"):
        m1, m2 = st.columns(2)
        with m1:
            st.button(
                "Upload File",
                icon=":material/upload_file:",
                key="m_local",
                type="primary" if upload_method == "Local Video" else "secondary",
                on_click=set_state,
                args=("upload_method", "Local Video"),
                use_container_width=True
            )
        with m2:
            st.button(
                "YouTube Link",
                icon=":material/smart_display:",
                key="m_youtube",
                type="primary" if upload_method == "YouTube URL" else "secondary",
                on_click=set_state,
                args=("upload_method", "YouTube URL"),
                use_container_width=True
            )

    st.markdown("<div style='height:.6rem'></div>", unsafe_allow_html=True)

    title = st.text_input(
        "Video Title",
        placeholder="Enter a title for your video"
    )

    # -----------------------------
    # YouTube URL
    # -----------------------------

    if upload_method == "YouTube URL":

        source = st.text_input(
            "YouTube URL",
            placeholder="https://www.youtube.com/watch?v=..."
        )

        if st.button(
            "🚀 Process Video",
            type="primary",
            use_container_width=True
        ):

            if not title or not source:

                st.warning(
                    "Please provide a title and YouTube URL."
                )

            else:

                with st.spinner(
                    "Processing video... This may take some time."
                ):

                    response = create_video(
                        token=token,
                        title=title,
                        source=source
                    )

                if response.status_code == 201:

                    st.success(
                        "Video processed successfully!"
                    )

                    st.session_state["flash"] = (
                        "Video processed successfully!"
                    )

                    st.rerun()

                else:

                    try:
                        error = response.json()

                    except Exception:
                        error = "Video processing failed."

                    st.error(error)

    # -----------------------------
    # Local Video
    # -----------------------------

    else:

        video_file = st.file_uploader(
            "Choose a video file",
            type=[
                "mp4",
                "mov",
                "avi",
                "mkv",
                "webm"
            ]
        )

        if st.button(
            "🚀 Process Video",
            type="primary",
            use_container_width=True
        ):

            if not title or not video_file:

                st.warning(
                    "Please provide a title and select a video."
                )

            else:

                with st.spinner(
                    "Processing video... This may take some time."
                ):

                    response = create_video(
                        token=token,
                        title=title,
                        video_file=video_file
                    )

                if response.status_code == 201:

                    st.success(
                        "Video processed successfully!"
                    )

                    st.session_state["flash"] = (
                        "Video processed successfully!"
                    )

                    st.rerun()

                else:

                    try:
                        error = response.json()

                    except Exception:
                        error = "Video processing failed."

                    st.error(error)


# -----------------------------
# My Videos
# -----------------------------

def page_my_videos(token):
    page_header(
        "My Videos",
        "View and manage all your uploaded videos."
    )

    st.markdown("<div style='height:.6rem'></div>", unsafe_allow_html=True)

    if "video_filter" not in st.session_state:
        st.session_state["video_filter"] = "All"

    status_filter = st.session_state["video_filter"]

    with st.container(key="filters"):
        cols = st.columns(
            [1, 1.7, 1.8, 1.3, 0.3, 3.6],
            vertical_alignment="center"
        )

        for col, name in zip(cols[:4], ["All", "Completed", "Processing", "Failed"]):
            with col:
                st.button(
                    name,
                    key=f"flt_{name}",
                    type="primary" if status_filter == name else "secondary",
                    on_click=set_state,
                    args=("video_filter", name),
                    use_container_width=True
                )

        with cols[5]:
            search = st.text_input(
                "Search",
                placeholder="Search videos...",
                label_visibility="collapsed"
            )

    st.markdown("<div style='height:.6rem'></div>", unsafe_allow_html=True)

    response = get_videos(token)

    if response.status_code == 200:

        data = response.json()

        if data["count"] == 0:

            empty_state("No videos yet. Upload your first video to get started.")

        else:

            shown = 0

            for video in data["results"]:

                if (
                    status_filter != "All"
                    and video["status"] != status_filter.lower()
                ):
                    continue

                if search and search.lower() not in video["title"].lower():
                    continue

                video_row(video, "list")
                shown += 1

            if shown == 0:
                empty_state("No videos match your filters.")

    else:

        st.error(
            "Could not load your videos."
        )


# -----------------------------
# Video Detail
# -----------------------------

def page_video_detail(token, video_id):
    st.button(
        "Back to Videos",
        icon=":material/arrow_back:",
        key="back_btn",
        on_click=close_video
    )

    response = get_videos(token)

    if response.status_code != 200:
        st.error("Could not load your videos.")
        return

    video = next(
        (v for v in response.json()["results"] if v["id"] == video_id),
        None
    )

    if video is None:
        st.warning("Video not found.")
        return

    left, right = st.columns([5, 1], vertical_alignment="center")
    with left:
        st.markdown(
            h(f"""
            <div class="page-title">{esc(video['title'])}</div>
            <div class="page-sub">Uploaded on {esc(fmt_date(video))}</div>
            """),
            unsafe_allow_html=True
        )
    with right:
        st.markdown(badge(video["status"]), unsafe_allow_html=True)

    st.markdown("<div style='height:.6rem'></div>", unsafe_allow_html=True)

    # ==================================================
    # COMPLETED VIDEO
    # ==================================================

    if video["status"] == "completed":

        tab_overview, tab_ask, tab_history = st.tabs(
            ["Overview", "Ask Questions", "History"]
        )

        with tab_overview:
            c1, c2 = st.columns([1.3, 1])
            with c1:
                st.markdown(
                    f'<div class="thumb big {thumb_class(video)}">{PLAY_SVG_BIG}</div>',
                    unsafe_allow_html=True
                )
            with c2:
                st.markdown(
                    h(f"""
                    <div class="detail-card">
                        <div class="detail-row"><span class="k">Title</span>
                            <span class="v">{esc(video['title'])}</span></div>
                        <div class="detail-row"><span class="k">Status</span>
                            <span class="v">{esc(video['status'])}</span></div>
                        <div class="detail-row"><span class="k">Created At</span>
                            <span class="v">{esc(fmt_datetime(video.get('created_at')))}</span></div>
                        <div class="detail-row"><span class="k">Updated At</span>
                            <span class="v">{esc(fmt_datetime(video.get('updated_at')))}</span></div>
                    </div>
                    """),
                    unsafe_allow_html=True
                )

            st.markdown(
                h("""
                <div class="tip-box">
                    <b>💡 Now you can ask questions about this video!</b>
                    Go to the Ask Questions tab to start chatting with your video content.
                </div>
                """),
                unsafe_allow_html=True
            )

        with tab_ask:
            render_ask(token, video)

        with tab_history:
            render_history(token, video)

    # ==================================================
    # FAILED VIDEO
    # ==================================================

    elif video["status"] == "failed":

        if video.get("error_message"):

            st.error(
                video["error_message"]
            )

    # ==================================================
    # PROCESSING VIDEO
    # ==================================================

    elif video["status"] == "processing":

        st.info(
            "⏳ Video is currently being processed."
        )


# -----------------------------
# Settings
# -----------------------------

def page_settings():
    page_header("Settings", "Your account details.")

    st.markdown("<div style='height:.8rem'></div>", unsafe_allow_html=True)

    st.markdown(
        h(f"""
        <div class="detail-card">
            <div class="detail-row"><span class="k">Username</span>
                <span class="v">{esc(st.session_state.get('username'))}</span></div>
        </div>
        """),
        unsafe_allow_html=True
    )


# ============================================================
# LOGGED-IN USER
# ============================================================

if st.session_state.get("logged_in", False):

    st.markdown(BASE_CSS, unsafe_allow_html=True)
    st.markdown(APP_CSS, unsafe_allow_html=True)

    token = st.session_state["token"]

    sidebar_nav()

    if st.session_state.pop("login_success", False):
        st.success("Login successful!")

    flash = st.session_state.pop("flash", None)
    if flash:
        st.success(flash)

    selected = st.session_state.get("selected_video")
    page = st.session_state.get("page", "Dashboard")

    if selected is not None:
        page_video_detail(token, selected)

    elif page == "Dashboard":
        page_dashboard(token)

    elif page == "Upload Video":
        page_upload(token)

    elif page == "My Videos":
        page_my_videos(token)

    else:
        page_settings()

    st.stop()


# ============================================================
# LOGIN / REGISTER PAGE
# ============================================================

st.markdown(BASE_CSS, unsafe_allow_html=True)
st.markdown(AUTH_CSS, unsafe_allow_html=True)

if "auth_mode" not in st.session_state:
    st.session_state["auth_mode"] = "login"


def set_auth_mode(mode):
    st.session_state["auth_mode"] = mode


mode = st.session_state["auth_mode"]


with st.container(key=f"authcard_{mode}"):

    left, right = st.columns(2)

    # ---------------- Right (decorative) panel ----------------

    with right:

        if mode == "login":

            st.markdown(
                h(f"""
                <div class="auth-right dark">
                    <div class="illus">{ROBOT_SVG}</div>
                    <h2>Turn Any Video<br>Into Knowledge</h2>
                    <p>Upload your videos or paste a YouTube link. Get
                    transcripts, ask questions, and learn faster with AI.</p>
                    <ul>
                        <li><span class="ic">✓</span>AI-Powered Transcripts</li>
                        <li><span class="ic">✓</span>Ask Anything About Your Video</li>
                        <li><span class="ic">✓</span>Save and Manage Your Learning</li>
                        <li><span class="ic">✓</span>Support for Multiple Languages</li>
                    </ul>
                </div>
                """),
                unsafe_allow_html=True
            )

        else:

            st.markdown(
                h(f"""
                <div class="auth-right light">
                    <div class="illus">{ROBOT_SVG}</div>
                    <h2>Learn Smarter<br>With AI</h2>
                    <ul>
                        <li><span class="ic">✓</span>Upload or paste YouTube links</li>
                        <li><span class="ic">✓</span>Get accurate transcripts</li>
                        <li><span class="ic">✓</span>Ask questions and get answers</li>
                        <li><span class="ic">✓</span>Build your personal knowledge library</li>
                    </ul>
                </div>
                """),
                unsafe_allow_html=True
            )

    # ---------------- Left (form) panel ----------------

    with left:

        st.markdown(logo_block(), unsafe_allow_html=True)

        # ====================================================
        # LOGIN
        # ====================================================

        if mode == "login":

            st.markdown(
                h("""
                <div class="auth-heading">Welcome Back 👋</div>
                <div class="auth-sub">Login to continue your learning journey</div>
                """),
                unsafe_allow_html=True
            )

            username = st.text_input(
                "Username",
                placeholder="Username",
                label_visibility="collapsed",
                key="login_username"
            )

            password = st.text_input(
                "Password",
                type="password",
                placeholder="Password",
                label_visibility="collapsed",
                key="login_password"
            )

            if st.button(
                "Login",
                type="primary",
                use_container_width=True
            ):

                if not username or not password:

                    st.warning(
                        "Please enter username and password."
                    )

                else:

                    response = login(
                        username,
                        password
                    )

                    if response.status_code == 200:

                        data = response.json()

                        st.session_state["token"] = (
                            data["token"]
                        )

                        st.session_state["username"] = (
                            username
                        )

                        st.session_state["logged_in"] = True

                        st.session_state["login_success"] = True

                        st.rerun()

                    else:

                        try:
                            error = response.json()

                        except Exception:
                            error = (
                                "Invalid username or password."
                            )

                        st.error(error)

            with st.container(key="auth_switch"):
                st.button(
                    "Don't have an account? Register",
                    key="to_register",
                    on_click=set_auth_mode,
                    args=("register",),
                    use_container_width=True
                )

        # ====================================================
        # REGISTER
        # ====================================================

        else:

            st.markdown(
                h("""
                <div class="auth-heading">Create Your Account</div>
                <div class="auth-sub">Start your AI learning journey today</div>
                """),
                unsafe_allow_html=True
            )

            new_username = st.text_input(
                "Username",
                placeholder="Username",
                label_visibility="collapsed",
                key="register_username"
            )

            new_password = st.text_input(
                "Password",
                type="password",
                placeholder="Password",
                label_visibility="collapsed",
                key="register_password"
            )

            confirm_password = st.text_input(
                "Confirm Password",
                type="password",
                placeholder="Confirm Password",
                label_visibility="collapsed",
                key="confirm_password"
            )

            if st.button(
                "Register",
                type="primary",
                use_container_width=True
            ):

                if not new_username or not new_password:

                    st.warning(
                        "Please fill in all fields."
                    )

                elif new_password != confirm_password:

                    st.error(
                        "Passwords do not match."
                    )

                else:

                    response = register(
                        new_username,
                        new_password
                    )

                    if response.status_code == 201:

                        st.success(
                            "Account created successfully! "
                            "You can now login."
                        )

                    else:

                        try:
                            error = response.json()

                        except Exception:
                            error = "Registration failed."

                        st.error(error)

            with st.container(key="auth_switch"):
                st.button(
                    "Already have an account? Login",
                    key="to_login",
                    on_click=set_auth_mode,
                    args=("login",),
                    use_container_width=True
                )