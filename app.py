import re
from datetime import date

import streamlit as st
from dateutil.relativedelta import relativedelta
import pandas as pd
import plotly.graph_objects as go

# ============================================================
# CẤU HÌNH TRANG
# ============================================================

st.set_page_config(
    page_title="Tính tiền gửi tiết kiệm",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ============================================================
# THEME SYSTEM — Light / Dark qua CSS custom properties
# ============================================================

if "theme" not in st.session_state:
    st.session_state.theme = "light"

THEMES = {
    "light": dict(
        app_bg="linear-gradient(135deg, #F8FAFC 0%, #E2E8F0 100%)",
        text="#0F172A", muted="#64748B", heading="#0B192C",
        navy="#0B192C", sapphire="#1E3E62", emerald="#00D26A",
        crimson="#FF4D4D", amber="#FFB020",
        panel_bg="rgba(255,255,255,0.68)", panel_border="rgba(255,255,255,0.6)",
        panel_shadow1="rgba(163,177,198,0.35)", panel_shadow2="rgba(255,255,255,0.65)",
        card_bg="rgba(255,255,255,0.78)",
        input_bg="#FFFFFF", input_text="#0F172A", input_border="rgba(15,23,42,0.16)",
        placeholder="#94A3B8",
        table_bg="#FFFFFF", table_border="rgba(15,23,42,0.08)", table_head_bg="#F1F5F9",
        table_row_alt="#F8FAFC",
        grid_line="rgba(11,25,44,0.08)",
        slider_track="rgba(30,62,98,0.14)",
        chip_bg="rgba(255,255,255,0.8)",
        expander_bg="rgba(255,255,255,0.65)",
        color_scheme="light",
    ),
    "dark": dict(
        app_bg="linear-gradient(135deg, #0A0F1C 0%, #111A2E 100%)",
        text="#E2E8F0", muted="#94A3B8", heading="#F1F5F9",
        navy="#0B192C", sapphire="#4C86C6", emerald="#22E88A",
        crimson="#FF6B6B", amber="#FFC24B",
        panel_bg="rgba(19,26,46,0.72)", panel_border="rgba(255,255,255,0.08)",
        panel_shadow1="rgba(0,0,0,0.5)", panel_shadow2="rgba(255,255,255,0.03)",
        card_bg="rgba(24,32,54,0.85)",
        input_bg="#1B2438", input_text="#E2E8F0", input_border="rgba(255,255,255,0.14)",
        placeholder="#64748B",
        table_bg="#151E33", table_border="rgba(255,255,255,0.08)", table_head_bg="#1E2A45",
        table_row_alt="#1A2438",
        grid_line="rgba(255,255,255,0.08)",
        slider_track="rgba(255,255,255,0.12)",
        chip_bg="rgba(27,36,56,0.85)",
        expander_bg="rgba(19,26,46,0.6)",
        color_scheme="dark",
    ),
}

TH = THEMES[st.session_state.theme]

ICONS = {
    "wallet": '<path d="M21 12V7H5a2 2 0 0 1 0-4h14v4"/><path d="M3 5v14a2 2 0 0 0 2 2h16v-5"/><path d="M18 12a2 2 0 0 0 0 4h4v-4Z"/>',
    "calendar": '<rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/>',
    "trending": '<polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/>',
    "banknote": '<rect x="2" y="6" width="20" height="12" rx="2"/><circle cx="12" cy="12" r="2"/><path d="M6 12h.01M18 12h.01"/>',
    "repeat": '<polyline points="17 1 21 5 17 9"/><path d="M3 11V9a4 4 0 0 1 4-4h14"/><polyline points="7 23 3 19 7 15"/><path d="M21 13v2a4 4 0 0 1-4 4H3"/>',
    "check": '<path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/>',
}


def svg_icon(name, size=20):
    return f'<svg viewBox="0 0 24 24" width="{size}" height="{size}" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">{ICONS[name]}</svg>'


def build_css(th: dict) -> str:
    return f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"], .stApp, p, span, div, label {{
        font-family: 'Plus Jakarta Sans', 'Inter', -apple-system, sans-serif !important;
    }}
    [data-testid="stIconMaterial"], span[data-testid="stIconMaterial"],
    .material-symbols-rounded, .material-symbols-outlined, .material-icons,
    [class*="material-symbols"] {{
        font-family: 'Material Symbols Rounded', 'Material Symbols Outlined', 'Material Icons' !important;
    }}

    .stApp {{ background: {th['app_bg']}; color: {th['text']}; }}
    #MainMenu, footer {{ visibility: hidden; }}

    /* ---- Chữ mặc định toàn app ---- */
    .stApp, .stApp p, .stApp span, .stApp label, .stApp li,
    .stMarkdown, .stCaption, [data-testid="stMarkdownContainer"] {{
        color: {th['text']};
    }}
    h1, h2, h3, h4, h5, h6 {{ color: {th['heading']} !important; }}
    .stCaption, [data-testid="stCaptionContainer"] {{ color: {th['muted']} !important; }}

    /* ---- Panels (container border=True) ---- */
    div[data-testid="stVerticalBlockBorderWrapper"] {{
        border-radius: 22px !important;
        border: 1px solid {th['panel_border']} !important;
        background: {th['panel_bg']} !important;
        backdrop-filter: blur(14px);
        box-shadow: 10px 10px 26px {th['panel_shadow1']}, -10px -10px 26px {th['panel_shadow2']};
    }}

    .panel-title {{
        font-size: 15.5px; font-weight: 800; color: {th['heading']};
        display: flex; align-items: center; gap: 8px;
        margin-bottom: 10px; text-transform: uppercase; letter-spacing: 0.4px;
    }}
    .panel-title .pt-icon {{
        width: 26px; height: 26px; border-radius: 8px;
        background: linear-gradient(135deg, {th['sapphire']}, {th['navy']});
        color: white; display: flex; align-items: center; justify-content: center;
    }}

    /* ---- Inputs: text_input, number_input, date_input, selectbox, textarea ---- */
    .stTextInput input, .stNumberInput input, .stDateInput input,
    .stSelectbox div[data-baseweb="select"] > div, textarea {{
        background: {th['input_bg']} !important;
        color: {th['input_text']} !important;
        border: 1px solid {th['input_border']} !important;
        border-radius: 10px !important;
    }}
    .stTextInput input::placeholder, .stNumberInput input::placeholder,
    .stDateInput input::placeholder {{ color: {th['placeholder']} !important; }}
    .stSelectbox div[data-baseweb="select"] span {{ color: {th['input_text']} !important; }}
    ul[data-baseweb="menu"] {{ background: {th['input_bg']} !important; }}
    ul[data-baseweb="menu"] li {{ color: {th['input_text']} !important; }}
    ul[data-baseweb="menu"] li:hover {{ background: {th['slider_track']} !important; }}

    /* ---- Slider ---- */
    div[data-testid="stSlider"] [data-baseweb="slider"] > div > div {{
        background: {th['slider_track']} !important;
    }}
    div[data-testid="stSlider"] [role="slider"] {{
        background-color: {th['emerald']} !important;
        border-color: {th['emerald']} !important;
    }}
    div[data-testid="stSliderTickBarMin"], div[data-testid="stSliderTickBarMax"],
    div[data-testid="stThumbValue"] {{ color: {th['muted']} !important; }}

    /* ---- Radio (segmented control) ---- */
    div[role="radiogroup"] label {{ color: {th['text']} !important; }}
    .st-key-toggle_method div[role="radiogroup"] {{
        background: {th['slider_track']}; padding: 5px; border-radius: 14px; gap: 4px;
    }}
    .st-key-toggle_method label {{ border-radius: 10px !important; padding: 6px 10px !important; font-weight: 600 !important; }}

    /* ---- Quick-select chips ---- */
    .st-key-quick_chips .stButton>button, .st-key-adj_chips .stButton>button {{
        border-radius: 999px !important;
        border: 1px solid {th['input_border']} !important;
        background: {th['chip_bg']} !important;
        color: {th['sapphire']} !important; font-weight: 700 !important; font-size: 12.5px !important;
        box-shadow: 3px 3px 8px {th['panel_shadow1']}, -3px -3px 8px {th['panel_shadow2']} !important;
        padding: 2px 4px !important;
    }}
    .st-key-quick_chips .stButton>button:hover, .st-key-adj_chips .stButton>button:hover {{
        border-color: {th['emerald']} !important; color: {th['emerald']} !important;
    }}

    /* ---- Nút chính ---- */
    .st-key-calc_btn .stButton>button {{
        background: linear-gradient(135deg, {th['navy']} 0%, {th['sapphire']} 50%, #146356 100%) !important;
        background-size: 200% 200% !important;
        color: white !important; border: none !important; font-weight: 800 !important;
        border-radius: 14px !important; padding: 12px !important; font-size: 15px !important;
        box-shadow: 0 10px 24px rgba(11,25,44,0.3) !important;
        transition: background-position 0.5s ease, transform 0.2s ease !important;
    }}
    .st-key-calc_btn .stButton>button:hover {{ background-position: 100% 50% !important; transform: translateY(-2px) !important; }}
    .st-key-reset_btn .stButton>button, .st-key-theme_btn .stButton>button {{
        border-radius: 14px !important; font-weight: 700 !important;
        background: {th['chip_bg']} !important; color: {th['sapphire']} !important;
        border: 1px solid {th['input_border']} !important;
    }}
    .stButton>button {{ color: {th['sapphire']}; }}
    .st-key-calc_btn .stButton>button p {{ color: white !important; }}

    /* ---- Tabs ---- */
    div[data-testid="stTabs"] button p {{ color: {th['muted']}; font-weight: 600; }}
    div[data-testid="stTabs"] button[aria-selected="true"] p {{ color: {th['sapphire']}; font-weight: 800; }}
    div[data-testid="stTabs"] div[data-baseweb="tab-highlight"] {{ background-color: {th['emerald']} !important; }}
    div[data-testid="stTabs"] div[data-baseweb="tab-border"] {{ background-color: {th['input_border']} !important; }}

    /* ---- Expander ---- */
    div[data-testid="stExpander"] {{
        background: {th['expander_bg']} !important; border-radius: 16px !important;
        border: 1px solid {th['panel_border']} !important;
    }}
    div[data-testid="stExpander"] summary {{ color: {th['heading']} !important; font-weight: 700; }}
    div[data-testid="stExpander"] p, div[data-testid="stExpander"] li {{ color: {th['text']} !important; }}

    /* ---- Alert boxes (info/success/warning/error) ---- */
    div[data-testid="stAlert"] {{ border-radius: 14px !important; }}
    div[data-testid="stAlert"] p {{ color: {th['text']} !important; }}

    hr {{ opacity: 0.15; border-color: {th['input_border']}; }}

    /* ================= HERO BANNER ================= */
    .hero-banner {{
        position: relative;
        background: linear-gradient(120deg, {th['navy']} 0%, {th['sapphire']} 60%, #24507F 100%);
        border-radius: 24px; padding: 22px 30px 18px 30px; margin-bottom: 20px;
        overflow: hidden; box-shadow: 0 20px 45px rgba(11, 25, 44, 0.35);
    }}
    .hero-top {{ display: flex; align-items: center; justify-content: space-between; position: relative; z-index: 2; }}
    .hero-badge {{
        display: inline-flex; align-items: center; gap: 6px;
        background: rgba(0, 210, 106, 0.15); border: 1px solid rgba(0,210,106,0.4);
        color: {th['emerald']}; padding: 5px 14px; border-radius: 999px;
        font-size: 12.5px; font-weight: 700; letter-spacing: 0.3px;
    }}
    .hero-glow-icon {{
        width: 48px; height: 48px; border-radius: 16px;
        background: radial-gradient(circle at 30% 30%, rgba(0,210,106,0.35), rgba(30,62,98,0.6));
        display: flex; align-items: center; justify-content: center;
        box-shadow: 0 0 24px rgba(0,210,106,0.45), inset 0 0 12px rgba(255,255,255,0.15);
        color: {th['emerald']};
    }}
    .hero-title {{ font-size: 26px; font-weight: 800; color: #FFFFFF !important; margin: 12px 0 2px 0; position: relative; z-index: 2; letter-spacing: -0.3px; }}
    .hero-sub {{ color: rgba(255,255,255,0.68) !important; font-size: 13.5px; position: relative; z-index: 2; }}
    .ticker-wrap {{ margin-top: 14px; overflow: hidden; position: relative; z-index: 2; border-top: 1px solid rgba(255,255,255,0.12); padding-top: 10px; }}
    .ticker-track {{ display: flex; gap: 34px; white-space: nowrap; animation: ticker-scroll 18s linear infinite; }}
    @keyframes ticker-scroll {{ 0% {{ transform: translateX(0); }} 100% {{ transform: translateX(-50%); }} }}
    .ticker-item {{ color: rgba(255,255,255,0.85) !important; font-size: 12.5px; font-weight: 600; display: inline-flex; align-items: center; gap: 6px; }}
    .ticker-item .dot {{ width: 6px; height: 6px; border-radius: 50%; background: {th['emerald']}; box-shadow: 0 0 8px {th['emerald']}; }}
    .ticker-item.warn .dot {{ background: {th['crimson']}; box-shadow: 0 0 8px {th['crimson']}; }}
    .ticker-item.info .dot {{ background: {th['amber']}; box-shadow: 0 0 8px {th['amber']}; }}

    /* ================= KPI CARDS ================= */
    .kpi-card {{
        position: relative; overflow: hidden; border-radius: 20px; padding: 18px 18px 16px 18px;
        background: {th['card_bg']}; border: 1px solid {th['panel_border']};
        box-shadow: 8px 8px 18px {th['panel_shadow1']}, -8px -8px 18px {th['panel_shadow2']};
        transition: transform 0.25s ease; --accent: {th['navy']}; height: 100%;
    }}
    .kpi-card:hover {{ transform: translateY(-4px); }}
    .kpi-card .kpi-bg-icon {{ position: absolute; top: -10px; right: -6px; opacity: 0.10; color: var(--accent); transform: scale(2.6); }}
    .kpi-card .kpi-label {{
        font-size: 12px; font-weight: 700; color: {th['muted']} !important;
        text-transform: uppercase; letter-spacing: 0.4px; margin-bottom: 8px; display: flex; align-items: center; gap: 6px;
    }}
    .kpi-card .kpi-label .ic {{ color: var(--accent); }}
    .kpi-card .kpi-value {{ font-size: 22px; font-weight: 800; color: {th['heading']} !important; line-height: 1.15; position: relative; z-index: 2; }}
    .kpi-card .kpi-note {{ margin-top: 9px; position: relative; z-index: 2; }}
    .kpi-chip {{ display: inline-flex; align-items: center; gap: 5px; font-size: 11.5px; font-weight: 700; padding: 3px 10px; border-radius: 999px; }}
    .kpi-chip.pos {{ background: rgba(0,210,106,0.16); color: {th['emerald']}; }}
    .kpi-chip.neg {{ background: rgba(255,77,77,0.16); color: {th['crimson']}; }}
    .kpi-chip.warn {{ background: rgba(255,176,32,0.18); color: {th['amber']}; }}
    .kpi-navy {{ --accent: {th['sapphire']}; }}
    .kpi-emerald {{ --accent: {th['emerald']}; }}
    .kpi-crimson {{ --accent: {th['crimson']}; }}
    .kpi-amber {{ --accent: {th['amber']}; }}

    /* ================= RESULT HERO ================= */
    .result-hero {{
        border-radius: 22px; padding: 24px 26px; color: white !important; position: relative; overflow: hidden;
        background: linear-gradient(135deg, {th['navy']} 0%, {th['sapphire']} 100%);
        box-shadow: 0 18px 34px rgba(11,25,44,0.3);
    }}
    .result-hero.crimson {{ background: linear-gradient(135deg, #7A1414 0%, {th['crimson']} 100%); }}
    .result-hero.amber {{ background: linear-gradient(135deg, #7A4B00 0%, {th['amber']} 100%); }}
    .result-hero * {{ color: white !important; }}
    .result-hero .rh-label {{ font-size: 13px; letter-spacing: 0.4px; opacity: 0.85; font-weight: 700; text-transform: uppercase; }}
    .result-hero .rh-value {{ font-size: 32px; font-weight: 800; margin: 6px 0 12px 0; }}
    .result-hero .rh-detail {{ font-size: 13.5px; opacity: 0.92; line-height: 1.8; }}

    /* ================= PROGRESS BAR ================= */
    .progress-labels {{ display: flex; justify-content: space-between; font-size: 12.5px; font-weight: 700; color: {th['muted']} !important; margin-bottom: 6px; }}
    .progress-track {{
        height: 12px; border-radius: 999px; background: {th['slider_track']};
        box-shadow: inset 3px 3px 6px {th['panel_shadow1']}, inset -3px -3px 6px {th['panel_shadow2']}; overflow: hidden;
    }}
    .progress-fill {{
        height: 100%; border-radius: 999px;
        background: linear-gradient(90deg, {th['sapphire']}, {th['emerald']});
        box-shadow: 0 0 10px rgba(0,210,106,0.5); transition: width 0.4s ease;
    }}

    /* ================= BATTLE CARDS ================= */
    .battle-wrap {{ display: flex; align-items: stretch; gap: 14px; }}
    .battle-card {{
        flex: 1; border-radius: 20px; padding: 20px; position: relative;
        background: {th['card_bg']}; border: 1.5px solid {th['panel_border']};
        box-shadow: 8px 8px 18px {th['panel_shadow1']}, -8px -8px 18px {th['panel_shadow2']};
    }}
    .battle-card.winner {{ border-color: {th['emerald']}; box-shadow: 0 0 0 3px rgba(0,210,106,0.18); }}
    .battle-card .bc-tag {{ font-size: 11.5px; font-weight: 800; text-transform: uppercase; color: {th['muted']} !important; }}
    .battle-card .bc-title {{ font-size: 15.5px; font-weight: 800; color: {th['heading']} !important; margin: 4px 0 12px 0; }}
    .battle-card .bc-value {{ font-size: 23px; font-weight: 800; color: {th['heading']} !important; }}
    .battle-card .bc-line {{ font-size: 12.5px; color: {th['muted']} !important; margin-top: 4px; }}
    .battle-vs {{
        display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 13px; color: white !important;
        background: linear-gradient(135deg, {th['navy']}, {th['sapphire']}); width: 40px; height: 40px; border-radius: 50%;
        box-shadow: 0 6px 14px rgba(11,25,44,0.3); align-self: center; flex-shrink: 0;
    }}
    .winner-crown {{ position: absolute; top: -10px; right: 16px; font-size: 20px; }}
    .verdict-box {{
        margin-top: 14px; padding: 14px 16px; border-radius: 14px;
        background: rgba(0,210,106,0.10); border: 1px solid rgba(0,210,106,0.3);
        color: {th['emerald']} !important; font-size: 13.5px; font-weight: 600; line-height: 1.6;
    }}
    .verdict-box.neg {{ background: rgba(255,77,77,0.10); border-color: rgba(255,77,77,0.3); color: {th['crimson']} !important; }}
    .verdict-box b {{ color: inherit !important; }}

    /* ================= BADGES ================= */
    .badge-pill {{ display: inline-flex; align-items: center; gap: 6px; padding: 5px 14px; border-radius: 999px; font-size: 12.5px; font-weight: 700; margin-bottom: 10px; }}
    .badge-pill.emerald {{ background: rgba(0,210,106,0.16); color: {th['emerald']} !important; }}
    .badge-pill.crimson {{ background: rgba(255,77,77,0.16); color: {th['crimson']} !important; }}
    .badge-pill.amber {{ background: rgba(255,176,32,0.2); color: {th['amber']} !important; }}

    /* ================= BẢNG DỮ LIỆU DẠNG HTML TỰ VẼ ================= */
    .bank-table-wrap {{ overflow-x: auto; border-radius: 14px; border: 1px solid {th['table_border']}; }}
    table.bank-table {{ width: 100%; border-collapse: collapse; background: {th['table_bg']}; font-size: 13px; }}
    table.bank-table thead th {{
        background: {th['table_head_bg']}; color: {th['heading']} !important; font-weight: 700;
        text-align: left; padding: 10px 14px; border-bottom: 2px solid {th['table_border']}; white-space: nowrap;
    }}
    table.bank-table tbody td {{ padding: 9px 14px; color: {th['text']} !important; border-bottom: 1px solid {th['table_border']}; white-space: nowrap; }}
    table.bank-table tbody tr:nth-child(even) {{ background: {th['table_row_alt']}; }}
    table.bank-table tbody tr:hover {{ background: {th['slider_track']}; }}

    @media (min-width: 1000px) {{
        div[data-testid="column"]:first-child > div {{ position: sticky; top: 14px; }}
    }}
    /* ========================================================
       FIX UI LIGHT / DARK — Streamlit native widgets
       Đặc biệt: DateInput, Selectbox, Slider, Button, bảng
       ======================================================== */

    /* Native browser color scheme: tránh trình duyệt tự đổi màu chữ
       của input[type=date] khi app đang ở Dark Mode. */
    :root {{ color-scheme: {th['color_scheme']}; }}
    html {{ color-scheme: {th['color_scheme']} !important; }}

    /* ---------- DATE INPUT ---------- */
    .stDateInput,
    .stDateInput > div,
    .stDateInput [data-baseweb="input"],
    .stDateInput [data-baseweb="input"] > div {{
        background: {th['input_bg']} !important;
    }}

    .stDateInput input,
    .stDateInput input[type="date"],
    .stDateInput input[aria-label] {{
        background-color: {th['input_bg']} !important;
        color: {th['input_text']} !important;
        -webkit-text-fill-color: {th['input_text']} !important;
        caret-color: {th['input_text']} !important;
        opacity: 1 !important;
        text-shadow: none !important;
        color-scheme: {th['color_scheme']} !important;
    }}

    .stDateInput input::placeholder {{
        color: {th['placeholder']} !important;
        -webkit-text-fill-color: {th['placeholder']} !important;
        opacity: 1 !important;
    }}

    /* Nút xoá và icon lịch của DateInput */
    .stDateInput button,
    .stDateInput button svg {{
        color: {th['muted']} !important;
        fill: currentColor !important;
        opacity: 1 !important;
    }}
    .stDateInput button:hover {{
        background: {th['slider_track']} !important;
    }}
    .stDateInput input[type="date"]::-webkit-calendar-picker-indicator {{
        opacity: 1 !important;
        cursor: pointer;
        filter: {('invert(1) brightness(1.7)' if False else 'none')};
    }}

    /* Popover / calendar của DateInput */
    div[data-baseweb="popover"],
    div[data-baseweb="calendar"],
    div[role="dialog"] {{
        color-scheme: {th['color_scheme']} !important;
    }}
    div[data-baseweb="popover"] [data-baseweb="calendar"],
    div[data-baseweb="calendar"] {{
        background: {th['input_bg']} !important;
        color: {th['input_text']} !important;
        border-color: {th['input_border']} !important;
    }}
    div[data-baseweb="calendar"] *,
    div[data-baseweb="calendar"] button {{
        color: {th['input_text']} !important;
    }}
    div[data-baseweb="calendar"] button:hover {{
        background: {th['slider_track']} !important;
    }}

    /* ========================================================
       DATE INPUT — FINAL OVERRIDE
       BaseWeb/Streamlit có thể đặt nền ở wrapper thay vì input.
       Vì vậy ép nền + màu trên toàn bộ cấu trúc của DateInput.
       Mục tiêu Dark Mode: ô ngày tháng dùng cùng nền xanh đen
       #1B2438 như ô lãi suất/số tiền.
       ======================================================== */
    [data-testid="stDateInput"] [data-baseweb="input"],
    [data-testid="stDateInput"] [data-baseweb="input"] > div,
    [data-testid="stDateInput"] [data-baseweb="base-input"],
    [data-testid="stDateInput"] [data-baseweb="base-input"] > div,
    [data-testid="stDateInput"] input,
    [data-testid="stDateInput"] input:hover,
    [data-testid="stDateInput"] input:focus {{
        background: {th['input_bg']} !important;
        background-color: {th['input_bg']} !important;
        color: {th['input_text']} !important;
        -webkit-text-fill-color: {th['input_text']} !important;
        opacity: 1 !important;
        text-shadow: none !important;
        caret-color: {th['input_text']} !important;
        color-scheme: {th['color_scheme']} !important;
    }}

    /* Ép các lớp con của BaseWeb không quay về nền trắng mặc định. */
    [data-testid="stDateInput"] [data-baseweb="input"] > div > div,
    [data-testid="stDateInput"] [data-baseweb="input"] > div > div > div,
    [data-testid="stDateInput"] [data-baseweb="base-input"] > div > div {{
        background: {th['input_bg']} !important;
        background-color: {th['input_bg']} !important;
    }}

    [data-testid="stDateInput"] input::placeholder,
    [data-testid="stDateInput"] input::-webkit-input-placeholder {{
        color: {th['placeholder']} !important;
        -webkit-text-fill-color: {th['placeholder']} !important;
        opacity: 1 !important;
    }}

    [data-testid="stDateInput"] [data-baseweb="input"] *,
    [data-testid="stDateInput"] [data-baseweb="base-input"] * {{
        color: {th['input_text']} !important;
        -webkit-text-fill-color: {th['input_text']} !important;
    }}

    [data-testid="stDateInput"] [data-baseweb="input"],
    [data-testid="stDateInput"] [data-baseweb="base-input"] {{
        border: 1px solid {th['input_border']} !important;
        border-radius: 10px !important;
        box-shadow: none !important;
    }}

    [data-testid="stDateInput"] button,
    [data-testid="stDateInput"] button svg {{
        color: {th['muted']} !important;
        fill: currentColor !important;
        stroke: currentColor !important;
        opacity: 1 !important;
    }}

    [data-testid="stDateInput"] button:hover {{
        background: {th['slider_track']} !important;
    }}
    /* ---- ÉP MÀU TOÀN BỘ CON CỦA DATE INPUT (fix mất chữ ở dark mode) ---- */
    [data-testid="stDateInput"] * {{
        background-color: {th['input_bg']} !important;
        color: {th['input_text']} !important;
        -webkit-text-fill-color: {th['input_text']} !important;
    }}

    /* Placeholder rỗng (dd/mm/yyyy) khi chưa chọn ngày */
    [data-testid="stDateInput"] input::placeholder,
    [data-testid="stDateInput"] [aria-placeholder] {{
        color: {th['placeholder']} !important;
        -webkit-text-fill-color: {th['placeholder']} !important;
        opacity: 1 !important;
    }}

    /* Icon lịch & nút xoá (x) không bị ăn theo màu nền */
    [data-testid="stDateInput"] svg {{
        fill: {th['muted']} !important;
        stroke: {th['muted']} !important;
        background: transparent !important;
    }}

    /* Viền + bo góc cho khung ngoài cùng */
    [data-testid="stDateInput"] [data-baseweb="input"],
    [data-testid="stDateInput"] [data-baseweb="base-input"] {{
        border: 1px solid {th['input_border']} !important;
        border-radius: 10px !important;
    }}
    /* ---------- SELECTBOX ---------- */
    .stSelectbox [data-baseweb="select"],
    .stSelectbox [data-baseweb="select"] > div,
    .stSelectbox [data-baseweb="select"] > div > div {{
        background: {th['input_bg']} !important;
        color: {th['input_text']} !important;
        border-color: {th['input_border']} !important;
    }}
    .stSelectbox [data-baseweb="select"] input {{
        color: {th['input_text']} !important;
        -webkit-text-fill-color: {th['input_text']} !important;
    }}
    .stSelectbox [data-baseweb="select"] span,
    .stSelectbox [data-baseweb="select"] div[role="option"] {{
        color: {th['input_text']} !important;
    }}
    ul[data-baseweb="menu"],
    ul[data-baseweb="menu"] > li,
    div[data-baseweb="popover"] ul {{
        background: {th['input_bg']} !important;
        color: {th['input_text']} !important;
    }}
    ul[data-baseweb="menu"] li[aria-selected="true"],
    ul[data-baseweb="menu"] li:hover {{
        background: {th['slider_track']} !important;
        color: {th['input_text']} !important;
    }}
    .stSelectbox svg {{
        color: {th['muted']} !important;
        fill: currentColor !important;
    }}

    /* ---------- NUMBER / TEXT INPUT ---------- */
    .stTextInput [data-baseweb="input"],
    .stNumberInput [data-baseweb="input"],
    .stTextArea [data-baseweb="base-input"],
    .stTextArea textarea,
    .stTextInput input,
    .stNumberInput input {{
        background: {th['input_bg']} !important;
        color: {th['input_text']} !important;
        -webkit-text-fill-color: {th['input_text']} !important;
        border-color: {th['input_border']} !important;
        opacity: 1 !important;
    }}
    .stTextInput input::placeholder,
    .stNumberInput input::placeholder,
    .stTextArea textarea::placeholder {{
        color: {th['placeholder']} !important;
        -webkit-text-fill-color: {th['placeholder']} !important;
        opacity: 1 !important;
    }}

    /* ---------- SLIDER ---------- */
    div[data-testid="stSlider"] {{ color: {th['text']} !important; }}
    div[data-testid="stSlider"] label,
    div[data-testid="stSlider"] p,
    div[data-testid="stSlider"] span {{
        color: {th['text']} !important;
    }}
    div[data-testid="stSlider"] [data-baseweb="slider"] > div {{
        background: transparent !important;
    }}
    div[data-testid="stSlider"] [data-baseweb="slider"] > div > div {{
        background: {th['slider_track']} !important;
    }}
    div[data-testid="stSlider"] [role="slider"] {{
        background: {th['emerald']} !important;
        border: 2px solid {th['emerald']} !important;
        box-shadow: 0 0 0 3px {th['slider_track']} !important;
    }}
    div[data-testid="stSlider"] [data-testid="stThumbValue"],
    div[data-testid="stSlider"] [data-testid="stSliderTickBarMin"],
    div[data-testid="stSlider"] [data-testid="stSliderTickBarMax"] {{
        color: {th['muted']} !important;
        -webkit-text-fill-color: {th['muted']} !important;
    }}

    /* ---------- BUTTON ---------- */
    .stButton > button,
    .stDownloadButton > button {{
        color: {th['sapphire']} !important;
        background: {th['chip_bg']} !important;
        border: 1px solid {th['input_border']} !important;
        opacity: 1 !important;
    }}
    .stButton > button p,
    .stButton > button span,
    .stDownloadButton > button p,
    .stDownloadButton > button span {{
        color: inherit !important;
        -webkit-text-fill-color: currentColor !important;
    }}
    .stButton > button:hover,
    .stDownloadButton > button:hover {{
        border-color: {th['emerald']} !important;
        color: {th['emerald']} !important;
    }}
    .st-key-calc_btn .stButton > button,
    .st-key-calc_btn .stButton > button p,
    .st-key-calc_btn .stButton > button span {{
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
    }}

    /* ---------- TABS / EXPANDER / CHECKBOX / RADIO ---------- */
    div[data-testid="stTabs"] button,
    div[data-testid="stTabs"] button p,
    div[data-testid="stTabs"] button span {{
        color: {th['text']} !important;
    }}
    div[data-testid="stTabs"] button[aria-selected="true"],
    div[data-testid="stTabs"] button[aria-selected="true"] p {{
        color: {th['sapphire']} !important;
    }}
    div[data-testid="stExpander"] summary,
    div[data-testid="stExpander"] summary span {{
        color: {th['heading']} !important;
    }}
    div[role="radiogroup"] label,
    div[role="radiogroup"] label p,
    div[role="radiogroup"] label span {{
        color: {th['text']} !important;
    }}

    /* ---------- BẢNG HTML ---------- */
    .bank-table-wrap {{
        background: {th['table_bg']} !important;
        border-color: {th['table_border']} !important;
    }}
    table.bank-table,
    table.bank-table thead,
    table.bank-table tbody {{
        background: {th['table_bg']} !important;
        color: {th['text']} !important;
    }}
    table.bank-table thead th {{
        background: {th['table_head_bg']} !important;
        color: {th['heading']} !important;
        border-color: {th['table_border']} !important;
    }}
    table.bank-table tbody td {{
        background: transparent !important;
        color: {th['text']} !important;
        border-color: {th['table_border']} !important;
    }}
    table.bank-table tbody tr:nth-child(even) td {{
        background: {th['table_row_alt']} !important;
    }}
    table.bank-table tbody tr:hover td {{
        background: {th['slider_track']} !important;
    }}

</style>
"""


st.markdown(build_css(TH), unsafe_allow_html=True)


def toggle_theme():
    st.session_state.theme = "dark" if st.session_state.theme == "light" else "light"


top_l, top_r = st.columns([6, 1])
with top_r:
    with st.container(key="theme_btn"):
        st.button(
            "🌙 Tối" if st.session_state.theme == "light" else "☀️ Sáng",
            on_click=toggle_theme, use_container_width=True,
        )


# ============================================================
# HÀM ĐỊNH DẠNG
# ============================================================

def format_money(value: float) -> str:
    return f"{round(value):,.0f} VNĐ"


def format_million(value: float) -> str:
    return f"{value:,.2f} triệu đồng"


def auto_label(v: float) -> str:
    v = float(v)
    if v >= 1_000_000_000:
        return f"{v / 1_000_000_000:g} tỷ"
    if v >= 1_000_000:
        return f"{v / 1_000_000:g} triệu"
    if v >= 1_000:
        return f"{v / 1_000:g} nghìn"
    return f"{v:g} đồng"


def kpi_card(label, value, icon="wallet", variant="navy", note_html=""):
    st.markdown(
        f"""
        <div class="kpi-card kpi-{variant}">
            <div class="kpi-bg-icon">{svg_icon(icon, 90)}</div>
            <div class="kpi-label"><span class="ic">{svg_icon(icon, 15)}</span>{label}</div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-note">{note_html}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def progress_bar_custom(percent, left_label, right_label):
    percent = max(0, min(100, percent))
    st.markdown(
        f"""
        <div class="progress-wrap">
            <div class="progress-labels"><span>{left_label}</span><span>{right_label}</span></div>
            <div class="progress-track"><div class="progress-fill" style="width:{percent}%;"></div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_html_table(df: pd.DataFrame, currency_cols=None, date_cols=None):
    """Vẽ bảng bằng HTML/CSS thuần để tô màu đúng theo theme sáng/tối (khác với st.dataframe
    vốn render trong iframe riêng và không ăn theo CSS tuỳ biến của trang)."""
    currency_cols = currency_cols or []
    date_cols = date_cols or []
    df2 = df.copy()
    for c in currency_cols:
        if c in df2.columns:
            df2[c] = df2[c].map(lambda x: f"{round(x):,.0f} ₫" if pd.notna(x) else "")
    for c in date_cols:
        if c in df2.columns:
            df2[c] = df2[c].map(lambda x: x.strftime("%d/%m/%Y") if hasattr(x, "strftime") else x)

    head = "".join(f"<th>{c}</th>" for c in df2.columns)
    body_rows = []
    for _, row in df2.iterrows():
        cells = "".join(f"<td>{row[c]}</td>" for c in df2.columns)
        body_rows.append(f"<tr>{cells}</tr>")
    html = f"""
    <div class="bank-table-wrap">
    <table class="bank-table">
        <thead><tr>{head}</tr></thead>
        <tbody>{''.join(body_rows)}</tbody>
    </table>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


# ============================================================
# Ô NHẬP TIỀN THÔNG MINH — hỗ trợ: 500000000 / 500 triệu / 1.5 tỷ / 1,5 tỷ / 200k / 50tr
# ============================================================

_SUFFIX_MULT = {
    "": 1, "d": 1, "dong": 1, "đ": 1, "đồng": 1,
    "k": 1_000, "nghin": 1_000, "nghìn": 1_000,
    "tr": 1_000_000, "trieu": 1_000_000, "triệu": 1_000_000, "m": 1_000_000,
    "ty": 1_000_000_000, "tỷ": 1_000_000_000, "b": 1_000_000_000,
}
_PARSE_RE = re.compile(r"^([\d]+(?:[.,]\d+)?)\s*([^\d\s]*)$", re.UNICODE)


def parse_smart_amount(text: str):
    if not text:
        return None
    t = text.strip().lower().replace("vnđ", "").replace("vnd", "").strip()

    # Số nguyên lớn có dấu phân cách hàng nghìn kiểu 500.000.000 hoặc 500,000,000
    # (nhiều nhóm 3 chữ số cách nhau bởi , hoặc . và không có hậu tố chữ)
    bare_grouped = re.match(r"^\d{1,3}([.,]\d{3})+$", t)
    if bare_grouped:
        return float(t.replace(".", "").replace(",", ""))

    m = _PARSE_RE.match(t)
    if not m:
        return None
    num_str, suffix = m.groups()
    suffix = suffix.strip()
    if suffix not in _SUFFIX_MULT:
        return None

    if suffix == "":
        # Số trần không có hậu tố: dấu , hoặc . đơn lẻ chỉ có thể là phân cách thập phân
        # nếu theo sau là 1-2 chữ số; nhưng vì không có hậu tố nên số trần thường là số nguyên.
        num_str_clean = num_str.replace(",", ".")
    else:
        # Có hậu tố (triệu/tỷ/k/tr...): dấu , hoặc . đều hiểu là dấu thập phân.
        num_str_clean = num_str.replace(",", ".")

    try:
        number = float(num_str_clean)
    except ValueError:
        return None
    return number * _SUFFIX_MULT[suffix]


def is_bare_small_number(text: str):
    if not text:
        return None
    t = text.strip().replace(",", "").replace(".", "")
    if re.match(r"^\d+$", t):
        n = float(t)
        if 0 < n < 1_000_000:
            return n
    return None


# ============================================================
# HẰNG SỐ KỲ HẠN
# ============================================================

TERM_OPTIONS = {
    "-- Chọn kỳ hạn --": None,
    "Không kỳ hạn": 0,
    "1 tháng": 1, "2 tháng": 2, "3 tháng": 3,
    "6 tháng": 6, "9 tháng": 9, "12 tháng": 12,
    "18 tháng": 18, "24 tháng": 24, "36 tháng": 36,
}

METHOD_OPTIONS = ["💵 Nhận lãi trước", "📆 Nhận lãi hàng tháng", "🏁 Nhận lãi cuối kỳ"]


# ============================================================
# HÀM LÕI TÍNH TOÁN (không đổi logic tài chính)
# ============================================================

def get_maturity_date(start_date, term_months):
    if term_months == 0:
        return None
    return start_date + relativedelta(months=term_months)


def get_days(start_date, end_date):
    return (end_date - start_date).days


def simple_interest(principal, annual_rate_percent, days):
    if days <= 0:
        return 0.0
    return principal * (annual_rate_percent / 100) * days / 365


def monthly_breakdown(principal, annual_rate_percent, start_date, end_date):
    rows = []
    total_interest = 0.0
    current = start_date
    while current < end_date:
        next_month = current + relativedelta(months=1)
        period_end = min(next_month, end_date)
        days = get_days(current, period_end)
        interest = simple_interest(principal, annual_rate_percent, days)
        total_interest += interest
        rows.append({
            "Kỳ": len(rows) + 1, "Từ ngày": current, "Đến trước ngày": period_end,
            "Số ngày": days, "Tiền lãi": interest,
        })
        current = period_end
    return total_interest, rows


def renewal_periods(principal, term_rate, non_term_rate, start_date, withdrawal_date, term_months):
    periods = []
    current_start = start_date
    current_principal = principal
    while current_start < withdrawal_date:
        maturity = current_start + relativedelta(months=term_months)
        period_end = min(maturity, withdrawal_date)
        is_full_period = period_end == maturity
        applied_rate = term_rate if is_full_period else non_term_rate
        days = get_days(current_start, period_end)
        interest = simple_interest(current_principal, applied_rate, days)
        periods.append({
            "Kỳ": len(periods) + 1, "Ngày bắt đầu": current_start, "Ngày kết thúc": period_end,
            "Số ngày": days, "Gốc đầu kỳ": current_principal, "Lãi suất áp dụng": applied_rate,
            "Tiền lãi": interest, "Đủ kỳ hạn": is_full_period,
        })
        current_start = period_end
        if is_full_period:
            current_principal += interest
    return periods


# ============================================================
# BIỂU ĐỒ (Plotly)
# ============================================================

def plotly_font(th):
    return dict(family="Plus Jakarta Sans, Inter, sans-serif", color=th["text"], size=12)


def render_donut_chart(th, principal, interest):
    fig = go.Figure(data=[go.Pie(
        labels=["Tiền gốc", "Tiền lãi"], values=[principal, max(interest, 0)], hole=0.64,
        marker=dict(colors=[th["sapphire"], th["emerald"]], line=dict(color=th["app_bg"].split(" ")[2] if False else "rgba(0,0,0,0)", width=2)),
        textinfo="percent", textfont=dict(size=13, color="white"),
        hovertemplate="%{label}: %{value:,.0f} VNĐ (%{percent})<extra></extra>",
    )])
    total = principal + max(interest, 0)
    fig.update_layout(
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.16, xanchor="center", x=0.5, font=plotly_font(th)),
        margin=dict(t=10, b=10, l=10, r=10), height=300, font=plotly_font(th),
        annotations=[dict(
            text=f"<b>{auto_label(total)}</b><br><span style='font-size:11px;color:{th['muted']}'>Tổng giá trị</span>",
            x=0.5, y=0.5, showarrow=False, font=dict(size=15, color=th["heading"]),
        )],
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def render_waterfall_area_chart(th, principal, timeline):
    if not timeline:
        st.info("Không có dữ liệu theo kỳ để vẽ biểu đồ.")
        return
    labels = [t["label"] for t in timeline]
    lai_ky = [t["lai_ky"] for t in timeline]
    cumulative = []
    running = principal
    for v in lai_ky:
        running += v
        cumulative.append(running)

    wf_labels = ["Gốc ban đầu"] + labels
    wf_values = [principal] + lai_ky
    wf_measure = ["absolute"] + ["relative"] * len(lai_ky)

    fig = go.Figure()
    fig.add_trace(go.Waterfall(
        orientation="v", measure=wf_measure, x=wf_labels, y=wf_values,
        text=[f"{v:,.0f}" for v in wf_values], textposition="outside",
        connector=dict(line=dict(color=th["grid_line"])),
        increasing=dict(marker=dict(color=th["emerald"])),
        decreasing=dict(marker=dict(color=th["crimson"])),
        totals=dict(marker=dict(color=th["sapphire"])),
    ))
    fig.update_layout(
        height=380, margin=dict(t=30, b=10, l=10, r=10), font=plotly_font(th),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(title="VNĐ", showgrid=True, gridcolor=th["grid_line"], color=th["text"]),
        xaxis=dict(title=None, color=th["text"]), showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x=labels, y=cumulative, mode="lines+markers", name="Giá trị luỹ kế",
        line=dict(color=th["emerald"], width=3), marker=dict(size=7, color=th["emerald"]),
        fill="tozeroy", fillcolor="rgba(0,210,106,0.12)",
        hovertemplate="%{x}<br>Luỹ kế: %{y:,.0f} VNĐ<extra></extra>",
    ))
    fig2.update_layout(
        height=250, margin=dict(t=10, b=10, l=10, r=10), font=plotly_font(th),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(title="Giá trị luỹ kế (VNĐ)", showgrid=True, gridcolor=th["grid_line"], color=th["text"]),
        xaxis=dict(title=None, color=th["text"]), hovermode="x unified",
    )
    st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})


def battle_tab(th, value_A, principal, interest_A, value_B, loan_cost, interest_B, term_rate, loan_rate,
               days_remaining, maturity_date):
    a_wins = value_A >= value_B
    st.markdown('<div class="battle-wrap">', unsafe_allow_html=True)
    colA, colVS, colB = st.columns([1, 0.18, 1])
    with colA:
        crown = '<div class="winner-crown">👑</div>' if a_wins else ""
        st.markdown(
            f"""<div class="battle-card {'winner' if a_wins else ''}">{crown}
            <div class="bc-tag">PHƯƠNG ÁN A</div>
            <div class="bc-title">🏃 Rút trước hạn ngay</div>
            <div class="bc-value">{format_money(value_A)}</div>
            <div class="bc-line">Gốc {format_money(principal)} + lãi không kỳ hạn {format_money(interest_A)}</div>
            <div class="bc-line">Quy đổi giá trị tại ngày đáo hạn {maturity_date.strftime('%d/%m/%Y')}</div>
            </div>""",
            unsafe_allow_html=True,
        )
    with colVS:
        st.markdown('<div style="height:60px;"></div><div class="battle-vs">VS</div>', unsafe_allow_html=True)
    with colB:
        crown = '<div class="winner-crown">👑</div>' if not a_wins else ""
        st.markdown(
            f"""<div class="battle-card {'winner' if not a_wins else ''}">{crown}
            <div class="bc-tag">PHƯƠNG ÁN B</div>
            <div class="bc-title">🏦 Vay cầm cố sổ, giữ đến đáo hạn</div>
            <div class="bc-value">{format_money(value_B)}</div>
            <div class="bc-line">Vay {format_money(principal)} @ {loan_rate:.2f}%/năm trong {days_remaining} ngày</div>
            <div class="bc-line">Chi phí vay {format_money(loan_cost)} · Lãi kỳ hạn {format_money(interest_B)}</div>
            </div>""",
            unsafe_allow_html=True,
        )
    st.markdown('</div>', unsafe_allow_html=True)

    diff = value_B - value_A
    if diff > 0:
        st.markdown(
            f"""<div class="verdict-box">✅ <b>Nên VAY CẦM CỐ sổ tiết kiệm.</b> Lợi hơn khoảng
            <b>{format_money(diff)}</b> tại thời điểm đáo hạn vì lãi suất có kỳ hạn ({term_rate:.2f}%/năm)
            bù đắp được chi phí vay ({loan_rate:.2f}%/năm).</div>""",
            unsafe_allow_html=True,
        )
    elif diff < 0:
        st.markdown(
            f"""<div class="verdict-box neg">⚠️ <b>Nên RÚT TRƯỚC HẠN.</b> Vay cầm cố thiệt hơn khoảng
            <b>{format_money(-diff)}</b> tại thời điểm đáo hạn vì chi phí vay ({loan_rate:.2f}%/năm) cao hơn
            phần lãi có kỳ hạn giữ được.</div>""",
            unsafe_allow_html=True,
        )
    else:
        st.info("➖ Hai phương án cho kết quả tương đương nhau.")
    st.caption(
        "⚠️ So sánh mang tính tham khảo dựa trên lãi đơn theo ngày thực tế, giả định vay đúng số tiền gốc "
        "và trả nợ một lần khi sổ đáo hạn. Điều kiện thực tế có thể khác nhau tuỳ ngân hàng."
    )


# ============================================================
# HERO BANNER
# ============================================================

st.markdown(
    f"""
    <div class="hero-banner">
        <div class="hero-top">
            <div>
                <span class="hero-badge">{svg_icon('check', 13)} HỆ THỐNG ĐANG HOẠT ĐỘNG</span>
                <div class="hero-title">🏦 Trung tâm tính tiền gửi tiết kiệm</div>
                <div class="hero-sub">Mô phỏng gốc – lãi – đáo hạn – rút trước hạn – tự động tái tục theo thời gian thực</div>
            </div>
            <div class="hero-glow-icon">{svg_icon('trending', 24)}</div>
        </div>
        <div class="ticker-wrap">
            <div class="ticker-track">
                <span class="ticker-item"><span class="dot"></span>Cơ sở tính lãi: 365 ngày/năm</span>
                <span class="ticker-item info"><span class="dot"></span>Không tính ngày đáo hạn / ngày rút</span>
                <span class="ticker-item warn"><span class="dot"></span>Rút trước hạn → lãi suất không kỳ hạn</span>
                <span class="ticker-item"><span class="dot"></span>Đến hạn không rút → tự động tái tục</span>
                <span class="ticker-item"><span class="dot"></span>Cơ sở tính lãi: 365 ngày/năm</span>
                <span class="ticker-item info"><span class="dot"></span>Không tính ngày đáo hạn / ngày rút</span>
                <span class="ticker-item warn"><span class="dot"></span>Rút trước hạn → lãi suất không kỳ hạn</span>
                <span class="ticker-item"><span class="dot"></span>Đến hạn không rút → tự động tái tục</span>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# LAYOUT 2 CỘT
# ============================================================

col_left, col_right = st.columns([0.35, 0.65], gap="medium")

with col_left:
    with st.container(border=True):
        st.markdown(
            f'<div class="panel-title"><span class="pt-icon">{svg_icon("wallet", 15)}</span>BẢNG ĐIỀU KHIỂN</div>',
            unsafe_allow_html=True,
        )

        # ---- Số tiền: giao diện sạch, KHÔNG có dữ liệu mẫu ----
        if "so_tien_goc" not in st.session_state:
            st.session_state.so_tien_goc = 0.0
        if "so_tien_text" not in st.session_state:
            st.session_state.so_tien_text = ""

        def _set_amount(new_val: float):
            new_val = max(float(new_val), 0.0)
            st.session_state.so_tien_goc = new_val
            st.session_state.so_tien_text = f"{new_val:,.0f}" if new_val > 0 else ""

        def _on_change_amount_text():
            raw = st.session_state.so_tien_text
            if not raw.strip():
                st.session_state.so_tien_goc = 0.0
                return
            val = parse_smart_amount(raw)
            if val is not None:
                st.session_state.so_tien_goc = max(val, 0.0)
                st.session_state.so_tien_text = f"{val:,.0f}"
            # nếu không hiểu được thì giữ nguyên text người dùng đang gõ, không ép sửa

        def _on_slider_change():
            _set_amount(st.session_state["slider_amount"])

        st.markdown("**💰 Số tiền gửi**")
        st.text_input(
            "Nhập số tiền", key="so_tien_text", on_change=_on_change_amount_text,
            placeholder="Ví dụ: 500 triệu, 1.5 tỷ, 200k, 500000000...",
            label_visibility="collapsed",
        )

        st.slider(
            "Điều chỉnh bằng thanh trượt", min_value=0, max_value=5_000_000_000,
            value=int(st.session_state.so_tien_goc), step=1_000_000,
            key="slider_amount", on_change=_on_slider_change, label_visibility="collapsed",
        )

        if st.session_state.so_tien_goc > 0:
            st.caption(f"➡️ Đang chọn: **{format_money(st.session_state.so_tien_goc)}** (≈ {auto_label(st.session_state.so_tien_goc)})")
        else:
            st.caption("➡️ Chưa nhập số tiền.")

        st.markdown(f"<div style='font-size:12.5px;font-weight:700;color:{TH['muted']};margin-top:6px;'>Chọn nhanh</div>", unsafe_allow_html=True)
        with st.container(key="quick_chips"):
            QUICK_AMOUNTS = [50_000_000, 100_000_000, 200_000_000, 500_000_000, 1_000_000_000, 2_000_000_000]
            qc = st.columns(3)
            for i, amt in enumerate(QUICK_AMOUNTS):
                qc[i % 3].button(auto_label(amt), key=f"quick_{amt}", use_container_width=True, on_click=_set_amount, args=(amt,))

        with st.container(key="adj_chips"):
            st.markdown(f"<div style='font-size:12.5px;font-weight:700;color:{TH['muted']};margin-top:8px;'>Điều chỉnh nhanh</div>", unsafe_allow_html=True)
            ac = st.columns(3)
            deltas = [("➕1tr", 1_000_000), ("➕10tr", 10_000_000), ("➕50tr", 50_000_000),
                      ("➖1tr", -1_000_000), ("➖10tr", -10_000_000), ("➖50tr", -50_000_000)]
            for i, (nhan, delta) in enumerate(deltas):
                ac[i % 3].button(nhan, key=f"delta_{delta}", use_container_width=True,
                                  on_click=_set_amount, args=(st.session_state.so_tien_goc + delta,))

        st.divider()
        st.markdown("**📅 Kỳ hạn & lãi suất**")
        term_text = st.selectbox("Kỳ hạn gửi tiền", list(TERM_OPTIONS.keys()), index=0)
        term_months = TERM_OPTIONS[term_text]

        term_rate = st.number_input("📈 Lãi suất có kỳ hạn (%/năm)", min_value=0.0, max_value=100.0,
                                     value=None, step=0.1, format="%.2f", placeholder="Ví dụ: 5.0")
        non_term_rate = st.number_input("📉 Lãi suất không kỳ hạn (%/năm)", min_value=0.0, max_value=100.0,
                                         value=None, step=0.1, format="%.2f", placeholder="Ví dụ: 0.2")
        loan_rate = st.number_input("🏦 Lãi suất vay cầm cố sổ (%/năm)", min_value=0.0, max_value=100.0,
                                     value=None, step=0.1, format="%.2f", placeholder="Ví dụ: 8.0",
                                     help="Dùng để so sánh: nếu cần tiền trước hạn, nên rút sổ hay vay cầm cố chính sổ đó?")

        st.divider()
        st.markdown("**🗓️ Thời gian**")
        start_date = st.date_input("Ngày gửi tiền", value=None, format="DD/MM/YYYY")
        withdrawal_date = st.date_input("Ngày rút tiền", value=None, format="DD/MM/YYYY")

        st.divider()
        st.markdown("**💵 Phương thức nhận lãi**")
        with st.container(key="toggle_method"):
            interest_method = st.radio(
                "Phương thức (áp dụng khi gửi đủ kỳ hạn)", METHOD_OPTIONS,
                index=None, horizontal=True, label_visibility="collapsed",
            )

        st.write("")
        with st.container(key="calc_btn"):
            calc_clicked = st.button("⚡ TÍNH TOÁN NGAY", use_container_width=True)
        with st.container(key="reset_btn"):
            reset_clicked = st.button("↺ Làm mới toàn bộ", use_container_width=True)

# ---- Xử lý reset ----
if reset_clicked:
    for k in ["so_tien_goc", "so_tien_text", "last_calc"]:
        st.session_state.pop(k, None)
    st.rerun()

# ---- Xử lý khi bấm tính toán: validate + lưu snapshot vào session_state ----
if calc_clicked:
    errors = []
    principal_in = st.session_state.so_tien_goc
    if principal_in <= 0:
        errors.append("Vui lòng nhập **số tiền gửi** lớn hơn 0.")
    if term_months is None:
        errors.append("Vui lòng chọn **kỳ hạn gửi tiền**.")
    if term_rate is None:
        errors.append("Vui lòng nhập **lãi suất có kỳ hạn**.")
    if non_term_rate is None:
        errors.append("Vui lòng nhập **lãi suất không kỳ hạn**.")
    if loan_rate is None:
        errors.append("Vui lòng nhập **lãi suất vay cầm cố**.")
    if start_date is None:
        errors.append("Vui lòng chọn **ngày gửi tiền**.")
    if withdrawal_date is None:
        errors.append("Vui lòng chọn **ngày rút tiền**.")
    if start_date and withdrawal_date and withdrawal_date <= start_date:
        errors.append("**Ngày rút tiền** phải lớn hơn ngày gửi tiền.")
    if term_months not in (0, None) and interest_method is None:
        errors.append("Vui lòng chọn **phương thức nhận lãi**.")

    if errors:
        st.session_state["calc_errors"] = errors
    else:
        st.session_state["calc_errors"] = []
        st.session_state["last_calc"] = dict(
            principal=principal_in, term_months=term_months, term_rate=term_rate,
            non_term_rate=non_term_rate, loan_rate=loan_rate,
            start_date=start_date, withdrawal_date=withdrawal_date,
            interest_method=interest_method,
        )


# ============================================================
# CỘT PHẢI — HIỂN THỊ KẾT QUẢ (đọc từ session_state, không phụ thuộc rerun do UI khác)
# ============================================================

with col_right:
    if st.session_state.get("calc_errors"):
        st.error("⚠️ Vui lòng hoàn thiện thông tin trước khi tính toán:\n\n" +
                  "\n\n".join(f"- {e}" for e in st.session_state["calc_errors"]))

    tab1, tab2, tab3 = st.tabs(["📊 Tổng quan", "📋 Bảng dòng tiền chi tiết", "⚔️ So sánh thông minh"])

    lc = st.session_state.get("last_calc")

    if not lc:
        with tab1:
            st.info("👈 Nhập đầy đủ thông tin ở Bảng điều khiển bên trái rồi bấm **TÍNH TOÁN NGAY** để xem kết quả.")
        with tab2:
            st.info("Chưa có dữ liệu để hiển thị.")
        with tab3:
            st.info("Chưa có dữ liệu để so sánh.")
    else:
        principal = lc["principal"]
        term_months = lc["term_months"]
        term_rate = lc["term_rate"]
        non_term_rate = lc["non_term_rate"]
        loan_rate = lc["loan_rate"]
        start_date = lc["start_date"]
        withdrawal_date = lc["withdrawal_date"]
        interest_method = lc["interest_method"]

        # ---------------- KHÔNG KỲ HẠN ----------------
        if term_months == 0:
            days = get_days(start_date, withdrawal_date)
            interest = simple_interest(principal, non_term_rate, days)
            total = principal + interest
            detail_df = pd.DataFrame([{
                "Loại tiền gửi": "Không kỳ hạn", "Ngày gửi": start_date, "Ngày rút": withdrawal_date,
                "Số ngày": days, "Lãi suất áp dụng (%/năm)": non_term_rate,
                "Tiền gốc (VNĐ)": round(principal), "Tiền lãi (VNĐ)": round(interest),
                "Tổng nhận (VNĐ)": round(total),
            }])

            with tab1:
                st.markdown('<span class="badge-pill amber">🕊️ KHÔNG KỲ HẠN</span>', unsafe_allow_html=True)
                st.caption("Áp dụng lãi suất không kỳ hạn cho toàn bộ thời gian gửi.")
                k1, k2, k3, k4 = st.columns(4)
                with k1: kpi_card("Tiền gốc", format_million(principal / 1e6), "wallet", "navy")
                with k2: kpi_card("Số ngày gửi", f"{days} ngày", "calendar", "navy")
                with k3: kpi_card("Tiền lãi", format_million(interest / 1e6), "trending", "emerald",
                                   f'<span class="kpi-chip pos">+{non_term_rate:.2f}%/năm</span>')
                with k4: kpi_card("Tổng nhận", format_million(total / 1e6), "banknote", "emerald")

                colA, colB = st.columns([1.3, 1])
                with colA:
                    st.markdown(
                        f"""<div class="result-hero"><div class="rh-label">Tổng số tiền nhận được</div>
                        <div class="rh-value">{format_money(total)}</div>
                        <div class="rh-detail">Gốc {format_money(principal)} · Lãi {format_money(interest)}<br>
                        Lãi suất {non_term_rate:.2f}%/năm · {days} ngày</div></div>""",
                        unsafe_allow_html=True,
                    )
                    st.download_button("⬇️ Tải kết quả (CSV)", detail_df.to_csv(index=False).encode("utf-8-sig"),
                                        file_name="ket_qua_tiet_kiem.csv", mime="text/csv")
                with colB:
                    render_donut_chart(TH, principal, interest)

                st.markdown("##### 📈 Dòng tiền theo thời gian")
                render_waterfall_area_chart(TH, principal, [{"label": "Không kỳ hạn", "lai_ky": interest}])

            with tab2:
                st.markdown("##### 📋 Chi tiết dòng tiền")
                render_html_table(detail_df, currency_cols=["Tiền gốc (VNĐ)", "Tiền lãi (VNĐ)", "Tổng nhận (VNĐ)"],
                                   date_cols=["Ngày gửi", "Ngày rút"])
            with tab3:
                st.info("Tiền gửi không kỳ hạn không phát sinh so sánh vay cầm cố vs rút trước hạn.")

        else:
            maturity_date = get_maturity_date(start_date, term_months)
            early_withdrawal = withdrawal_date < maturity_date
            exact_maturity = withdrawal_date == maturity_date

            # ============ RÚT TRƯỚC HẠN ============
            if early_withdrawal:
                days = get_days(start_date, withdrawal_date)
                interest = simple_interest(principal, non_term_rate, days)
                total = principal + interest

                days_full_term = get_days(start_date, maturity_date)
                days_remaining = get_days(withdrawal_date, maturity_date)
                value_A = total
                interest_if_hold = simple_interest(principal, term_rate, days_full_term)
                loan_cost = simple_interest(principal, loan_rate, days_remaining)
                value_B = principal + interest_if_hold - loan_cost

                detail_df = pd.DataFrame([{
                    "Trạng thái": "Rút trước hạn", "Ngày gửi": start_date, "Ngày rút": withdrawal_date,
                    "Số ngày": days, "Lãi suất áp dụng (%/năm)": non_term_rate,
                    "Tiền gốc (VNĐ)": round(principal), "Tiền lãi (VNĐ)": round(interest),
                    "Tổng nhận (VNĐ)": round(total),
                }])

                with tab1:
                    st.markdown('<span class="badge-pill crimson">⚠️ RÚT TRƯỚC HẠN</span>', unsafe_allow_html=True)
                    pct = round(100 * days / max(days_full_term, 1), 1)
                    progress_bar_custom(pct, f"Đã gửi {days}/{days_full_term} ngày", f"{pct}%")

                    k1, k2, k3, k4 = st.columns(4)
                    with k1: kpi_card("Tiền gốc", format_million(principal / 1e6), "wallet", "navy")
                    with k2: kpi_card("Số ngày gửi", f"{days} ngày", "calendar", "navy")
                    with k3: kpi_card("Tiền lãi", format_million(interest / 1e6), "trending", "crimson",
                                       f'<span class="kpi-chip warn">{non_term_rate:.2f}%/năm (không kỳ hạn)</span>')
                    with k4: kpi_card("Tổng nhận", format_million(total / 1e6), "banknote", "crimson")

                    colA, colB = st.columns([1.3, 1])
                    with colA:
                        st.markdown(
                            f"""<div class="result-hero crimson"><div class="rh-label">Tổng nhận khi rút trước hạn</div>
                            <div class="rh-value">{format_money(total)}</div>
                            <div class="rh-detail">Gốc {format_money(principal)} · Lãi {format_money(interest)}<br>
                            Lãi suất {non_term_rate:.2f}%/năm · {days} ngày</div></div>""",
                            unsafe_allow_html=True,
                        )
                        st.download_button("⬇️ Tải kết quả (CSV)", detail_df.to_csv(index=False).encode("utf-8-sig"),
                                            file_name="ket_qua_rut_truoc_han.csv", mime="text/csv")
                    with colB:
                        render_donut_chart(TH, principal, interest)

                    st.markdown("##### 📈 Dòng tiền theo thời gian")
                    render_waterfall_area_chart(TH, principal, [{"label": "Rút trước hạn", "lai_ky": interest}])

                with tab2:
                    st.markdown("##### 📋 Chi tiết dòng tiền")
                    render_html_table(detail_df, currency_cols=["Tiền gốc (VNĐ)", "Tiền lãi (VNĐ)", "Tổng nhận (VNĐ)"],
                                       date_cols=["Ngày gửi", "Ngày rút"])

                with tab3:
                    st.markdown("##### ⚔️ Rút trước hạn vs Vay cầm cố sổ tiết kiệm")
                    battle_tab(TH, value_A, principal, interest, value_B, loan_cost, interest_if_hold,
                               term_rate, loan_rate, days_remaining, maturity_date)

            # ============ RÚT ĐÚNG HẠN ============
            elif exact_maturity:
                days = get_days(start_date, maturity_date)

                if interest_method == METHOD_OPTIONS[0]:
                    interest = simple_interest(principal, term_rate, days)
                    total = principal + interest
                    detail_df = pd.DataFrame([
                        {"Mốc": "Ngày gửi (nhận lãi trước)", "Ngày": start_date, "Số tiền (VNĐ)": round(interest)},
                        {"Mốc": "Ngày đáo hạn (nhận gốc)", "Ngày": maturity_date, "Số tiền (VNĐ)": round(principal)},
                    ])
                    timeline = [{"label": "Nhận lãi trước", "lai_ky": interest}]
                elif interest_method == METHOD_OPTIONS[1]:
                    total_interest, rows = monthly_breakdown(principal, term_rate, start_date, maturity_date)
                    interest = total_interest
                    total = principal + total_interest
                    detail_df = pd.DataFrame([{
                        "Kỳ": r["Kỳ"], "Từ ngày": r["Từ ngày"], "Đến trước ngày": r["Đến trước ngày"],
                        "Số ngày": r["Số ngày"], "Tiền lãi (VNĐ)": round(r["Tiền lãi"]),
                    } for r in rows])
                    timeline = [{"label": f"Kỳ {r['Kỳ']}", "lai_ky": r["Tiền lãi"]} for r in rows]
                else:
                    interest = simple_interest(principal, term_rate, days)
                    total = principal + interest
                    detail_df = pd.DataFrame([{
                        "Mốc": "Ngày đáo hạn (nhận gốc + lãi)", "Ngày": maturity_date,
                        "Tiền gốc (VNĐ)": round(principal), "Tiền lãi (VNĐ)": round(interest),
                        "Tổng nhận (VNĐ)": round(total),
                    }])
                    timeline = [{"label": "Đáo hạn", "lai_ky": interest}]

                with tab1:
                    st.markdown('<span class="badge-pill emerald">🏁 GỬI ĐÚNG KỲ HẠN</span>', unsafe_allow_html=True)
                    progress_bar_custom(100.0, f"Ngày gửi {start_date.strftime('%d/%m/%Y')}",
                                         f"Đáo hạn {maturity_date.strftime('%d/%m/%Y')} · 100%")

                    k1, k2, k3, k4 = st.columns(4)
                    with k1: kpi_card("Tiền gốc", format_million(principal / 1e6), "wallet", "navy")
                    with k2: kpi_card("Số ngày", f"{days} ngày", "calendar", "navy")
                    with k3: kpi_card("Tiền lãi", format_million(interest / 1e6), "trending", "emerald",
                                       f'<span class="kpi-chip pos">{term_rate:.2f}%/năm</span>')
                    with k4: kpi_card("Tổng nhận", format_million(total / 1e6), "banknote", "emerald")

                    colA, colB = st.columns([1.3, 1])
                    with colA:
                        st.markdown(
                            f"""<div class="result-hero"><div class="rh-label">Tổng dòng tiền nhận được</div>
                            <div class="rh-value">{format_money(total)}</div>
                            <div class="rh-detail">Gốc {format_money(principal)} · Lãi {format_money(interest)}<br>
                            Phương thức: {interest_method} · Lãi suất {term_rate:.2f}%/năm</div></div>""",
                            unsafe_allow_html=True,
                        )
                        st.download_button("⬇️ Tải kết quả (CSV)", detail_df.to_csv(index=False).encode("utf-8-sig"),
                                            file_name="ket_qua_dao_han.csv", mime="text/csv")
                    with colB:
                        render_donut_chart(TH, principal, interest)

                    st.markdown("##### 📈 Dòng tiền theo thời gian")
                    render_waterfall_area_chart(TH, principal, timeline)

                with tab2:
                    st.markdown("##### 📋 Chi tiết dòng tiền")
                    currency_cols = [c for c in detail_df.columns if "VNĐ" in c]
                    date_cols = [c for c in detail_df.columns if c in ("Ngày", "Từ ngày", "Đến trước ngày")]
                    render_html_table(detail_df, currency_cols=currency_cols, date_cols=date_cols)

                with tab3:
                    st.info("Khách hàng rút đúng ngày đáo hạn nên không phát sinh so sánh vay cầm cố vs rút trước hạn.")

            # ============ TÁI TỤC ============
            else:
                periods = renewal_periods(principal, term_rate, non_term_rate, start_date, withdrawal_date, term_months)
                total_interest = sum(p["Tiền lãi"] for p in periods)
                total = principal + total_interest
                last_full = periods[-1]["Đủ kỳ hạn"] if periods else True
                last_p = periods[-1]
                last_p_len = get_days(last_p["Ngày bắt đầu"], last_p["Ngày bắt đầu"] + relativedelta(months=term_months))
                last_p_elapsed = last_p["Số ngày"]
                progress_pct = round(100 * last_p_elapsed / max(last_p_len, 1), 1)

                detail_df = pd.DataFrame([{
                    "Kỳ": p["Kỳ"], "Ngày bắt đầu": p["Ngày bắt đầu"], "Ngày kết thúc": p["Ngày kết thúc"],
                    "Số ngày": p["Số ngày"], "Gốc đầu kỳ (VNĐ)": round(p["Gốc đầu kỳ"]),
                    "Lãi suất áp dụng (%/năm)": p["Lãi suất áp dụng"], "Tiền lãi (VNĐ)": round(p["Tiền lãi"]),
                    "Trạng thái": "Đủ kỳ hạn (tái tục)" if p["Đủ kỳ hạn"] else "Rút giữa kỳ (không kỳ hạn)",
                } for p in periods])
                timeline = [{"label": f"Kỳ {p['Kỳ']}", "lai_ky": p["Tiền lãi"]} for p in periods]

                with tab1:
                    st.markdown('<span class="badge-pill amber">🔄 TỰ ĐỘNG TÁI TỤC</span>', unsafe_allow_html=True)
                    if not last_full:
                        st.info("ℹ️ Kỳ cuối cùng rút **giữa chừng** nên được tính theo **lãi suất không kỳ hạn**.")
                    progress_bar_custom(progress_pct, f"Kỳ hiện tại: {last_p_elapsed}/{last_p_len} ngày", f"{progress_pct}%")

                    k1, k2, k3, k4 = st.columns(4)
                    with k1: kpi_card("Tiền gốc", format_million(principal / 1e6), "wallet", "navy")
                    with k2: kpi_card("Số lần tái tục", f"{max(len(periods) - 1, 0)} lần", "repeat", "amber")
                    with k3: kpi_card("Tổng tiền lãi", format_million(total_interest / 1e6), "trending", "emerald")
                    with k4: kpi_card("Tổng nhận", format_million(total / 1e6), "banknote", "emerald")

                    colA, colB = st.columns([1.3, 1])
                    with colA:
                        st.markdown(
                            f"""<div class="result-hero amber"><div class="rh-label">Tổng tiền khi rút ngày {withdrawal_date.strftime('%d/%m/%Y')}</div>
                            <div class="rh-value">{format_money(total)}</div>
                            <div class="rh-detail">Gốc {format_money(principal)} · Tổng lãi {format_money(total_interest)}</div></div>""",
                            unsafe_allow_html=True,
                        )
                        st.download_button("⬇️ Tải lịch sử tái tục (CSV)", detail_df.to_csv(index=False).encode("utf-8-sig"),
                                            file_name="lich_su_tai_tuc.csv", mime="text/csv")
                    with colB:
                        render_donut_chart(TH, principal, total_interest)

                    st.markdown("##### 📈 Dòng tiền qua các lần tái tục")
                    render_waterfall_area_chart(TH, principal, timeline)

                with tab2:
                    st.markdown("##### 📋 Lịch sử tái tục — dòng tiền chi tiết")
                    st.caption("💡 Từ kỳ thứ 2 trở đi, **Gốc đầu kỳ** = gốc kỳ trước + lãi đã tái tục (lãi nhập gốc).")
                    render_html_table(detail_df, currency_cols=["Gốc đầu kỳ (VNĐ)", "Tiền lãi (VNĐ)"],
                                       date_cols=["Ngày bắt đầu", "Ngày kết thúc"])

                with tab3:
                    st.info("Trường hợp tái tục tự động không áp dụng so sánh vay cầm cố vs rút trước hạn.")


# ============================================================
# HƯỚNG DẪN & CÔNG THỨC
# ============================================================

st.divider()
with st.expander("📖 Hướng dẫn sử dụng"):
    st.markdown("""
    **1. Số tiền gửi** — gõ tự do (`50 triệu`, `1.5 tỷ`, `1,5 tỷ`, `200k`, `50tr`, `500000000`...), dùng thanh trượt, nút chọn nhanh dạng chip, hoặc nút ➕➖.

    **2. Lãi suất** — nhập lãi suất có kỳ hạn, không kỳ hạn và lãi suất vay cầm cố.

    **3. Kỳ hạn** — chọn từ Không kỳ hạn đến 36 tháng.

    **4. Phương thức nhận lãi** — Nhận lãi trước / hàng tháng / cuối kỳ (áp dụng khi gửi đủ kỳ hạn).

    **5. Rút trước hạn** — toàn bộ thời gian được tính lại theo lãi suất không kỳ hạn.

    **6. Tự động tái tục** — nếu rút sau đáo hạn, hệ thống chia nhiều kỳ theo đúng kỳ hạn ban đầu; kỳ cuối rút giữa chừng dùng lãi suất không kỳ hạn.

    **7. Kết quả được giữ nguyên** cho đến khi bạn bấm lại **TÍNH TOÁN NGAY** — chuyển tab, đổi giao diện sáng/tối không làm mất kết quả.
    """)

with st.expander("🧮 Công thức tính lãi"):
    st.markdown("""
    **Tiền lãi = Tiền gốc × Lãi suất năm × Số ngày / 365**

    **Tổng tiền nhận = Tiền gốc + Tiền lãi**

    - Rút trước hạn (hoặc rút giữa một kỳ tái tục) → dùng lãi suất không kỳ hạn.
    - Đến hạn không rút → tự động tái tục đúng kỳ hạn ban đầu (lãi nhập gốc).
    """)

st.divider()
st.caption("🏦 Hệ thống mô phỏng tính tiền gửi tiết kiệm | Streamlit + Plotly | Hỗ trợ chế độ Sáng/Tối")
