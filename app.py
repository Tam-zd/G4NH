import streamlit as st
from datetime import date
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
initial_sidebar_state="collapsed"
)

# ============================================================
# DESIGN SYSTEM — bảng màu, font, CSS Neumorphism + Glassmorphism
# ============================================================

NAVY = "#0B192C" # Deep Navy
SAPPHIRE = "#1E3E62" # Sapphire Blue
EMERALD = "#00D26A" # Accent Emerald (lợi nhuận / lãi)
CRIMSON = "#FF4D4D" # Coral Crimson (cảnh báo rút trước hạn)
AMBER = "#FFB020" # phụ trợ (tái tục)
INK = "#0F172A"
MUTED = "#64748B"

ICONS = {
"wallet": '<path d="M21 12V7H5a2 2 0 0 1 0-4h14v4"/><path d="M3 5v14a2 2 0 0 0 2 2h16v-5"/><path d="M18 12a2 2 0 0 0 0 4h4v-4Z"/>',
"calendar": '<rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/>',
"trending": '<polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/>',
"alert": '<path d="M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0Z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/>',
"banknote": '<rect x="2" y="6" width="20" height="12" rx="2"/><circle cx="12" cy="12" r="2"/><path d="M6 12h.01M18 12h.01"/>',
"repeat": '<polyline points="17 1 21 5 17 9"/><path d="M3 11V9a4 4 0 0 1 4-4h14"/><polyline points="7 23 3 19 7 15"/><path d="M21 13v2a4 4 0 0 1-4 4H3"/>',
"check": '<path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/>',
"scale": '<path d="M12 3v18"/><path d="m4 6 4 8H2l4-8Z"/><path d="m16 6 4 8h-8l4-8Z"/><path d="M2 6h20"/><path d="M7 21h10"/>',
}

def svg_icon(name, size=20):
return f'<svg viewBox="0 0 24 24" width="{size}" height="{size}" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">{ICONS[name]}</svg>'

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Inter:wght@400;500;600;700&display=swap');

html, body, [class\*="css"], .stApp, p, span, div, label {{
    font-family: 'Plus Jakarta Sans', 'Inter', -apple-system, sans-serif !important;
}}

/\* Khôi phục font gốc cho icon Material Symbols của Streamlit.
   Các icon (mũi tên expander, mũi tên selectbox, icon eye của password...) được vẽ
   bằng ligature text (vd: "keyboard\_arrow\_right") thông qua font "Material Symbols".
   Nếu bị ép sang Plus Jakarta Sans, ligature vỡ và hiện ra chữ thô thay vì icon. \*/
[data-testid="stIconMaterial"],
span[data-testid="stIconMaterial"],
.material-symbols-rounded,
.material-symbols-outlined,
.material-icons,
[class\*="material-symbols"] {{
    font-family: 'Material Symbols Rounded', 'Material Symbols Outlined', 'Material Icons' !important;
}}

.stApp {{
    background: linear-gradient(135deg, #F8FAFC 0%, #E2E8F0 100%);
}}

\#MainMenu, footer {{ visibility: hidden; }}

/\* ================= HERO BANNER ================= \*/
.hero-banner {{
    position: relative;
    background: linear-gradient(120deg, {NAVY} 0%, {SAPPHIRE} 60%, #24507F 100%);
    border-radius: 24px;
    padding: 30px 34px 22px 34px;
    margin-bottom: 22px;
    overflow: hidden;
    box-shadow: 0 20px 45px rgba(11, 25, 44, 0.35);
}}
.hero-banner::before {{
    content: "";
    position: absolute; top: -80px; right: -60px;
    width: 260px; height: 260px; border-radius: 50%;
    background: radial-gradient(circle, rgba(0,210,106,0.22) 0%, transparent 70%);
    filter: blur(2px);
}}
.hero-banner::after {{
    content: "";
    position: absolute; bottom: -100px; left: 10%;
    width: 220px; height: 220px; border-radius: 50%;
    background: radial-gradient(circle, rgba(30,62,98,0.5) 0%, transparent 70%);
}}
.hero-top {{ display: flex; align-items: center; justify-content: space-between; position: relative; z-index: 2; }}
.hero-badge {{
    display: inline-flex; align-items: center; gap: 6px;
    background: rgba(0, 210, 106, 0.15); border: 1px solid rgba(0,210,106,0.4);
    color: {EMERALD}; padding: 5px 14px; border-radius: 999px;
    font-size: 12.5px; font-weight: 700; letter-spacing: 0.3px;
}}
.hero-glow-icon {{
    width: 52px; height: 52px; border-radius: 16px;
    background: radial-gradient(circle at 30% 30%, rgba(0,210,106,0.35), rgba(30,62,98,0.6));
    display: flex; align-items: center; justify-content: center;
    box-shadow: 0 0 24px rgba(0,210,106,0.45), inset 0 0 12px rgba(255,255,255,0.15);
    color: {EMERALD}; font-size: 26px;
}}
.hero-title {{
    font-size: 28px; font-weight: 800; color: #FFFFFF; margin: 14px 0 2px 0;
    position: relative; z-index: 2; letter-spacing: -0.3px;
}}
.hero-sub {{ color: rgba(255,255,255,0.65); font-size: 14px; position: relative; z-index: 2; }}

/\* mini ticker \*/
.ticker-wrap {{
    margin-top: 18px; overflow: hidden; position: relative; z-index: 2;
    border-top: 1px solid rgba(255,255,255,0.12); padding-top: 12px;
}}
.ticker-track {{
    display: flex; gap: 34px; white-space: nowrap;
    animation: ticker-scroll 18s linear infinite;
}}
@keyframes ticker-scroll {{
    0% {{ transform: translateX(0); }}
    100% {{ transform: translateX(-50%); }}
}}
.ticker-item {{ color: rgba(255,255,255,0.85); font-size: 13px; font-weight: 600; display: inline-flex; align-items: center; gap: 6px; }}
.ticker-item .dot {{ width: 6px; height: 6px; border-radius: 50%; background: {EMERALD}; box-shadow: 0 0 8px {EMERALD}; }}
.ticker-item.warn .dot {{ background: {CRIMSON}; box-shadow: 0 0 8px {CRIMSON}; }}
.ticker-item.info .dot {{ background: {AMBER}; box-shadow: 0 0 8px {AMBER}; }}

/\* ================= GLASS / NEUMORPHIC PANELS ================= \*/
div[data-testid="stVerticalBlockBorderWrapper"] {{
    border-radius: 22px !important;
    border: 1px solid rgba(255,255,255,0.6) !important;
    background: rgba(255, 255, 255, 0.65) !important;
    backdrop-filter: blur(14px);
    box-shadow: 10px 10px 26px rgba(163,177,198,0.35), -10px -10px 26px rgba(255,255,255,0.65);
}}

.panel-title {{
    font-size: 15.5px; font-weight: 800; color: {NAVY};
    display: flex; align-items: center; gap: 8px;
    margin-bottom: 10px; text-transform: uppercase; letter-spacing: 0.4px;
}}
.panel-title .pt-icon {{
    width: 26px; height: 26px; border-radius: 8px;
    background: linear-gradient(135deg, {SAPPHIRE}, {NAVY});
    color: white; display: flex; align-items: center; justify-content: center;
}}

/\* ================= KPI CARDS ================= \*/
.kpi-card {{
    position: relative; overflow: hidden;
    border-radius: 20px; padding: 18px 18px 16px 18px;
    background: rgba(255,255,255,0.75);
    border: 1px solid rgba(255,255,255,0.7);
    box-shadow: 8px 8px 18px rgba(163,177,198,0.35), -8px -8px 18px rgba(255,255,255,0.75);
    transition: transform 0.25s ease, box-shadow 0.25s ease;
    \--accent: {NAVY};
    height: 100%;
}}
.kpi-card\:hover {{
    transform: translateY(-4px);
    box-shadow: 0 14px 28px color-mix(in srgb, var(--accent) 28%, transparent),
                -6px -6px 16px rgba(255,255,255,0.7);
}}
.kpi-card .kpi-bg-icon {{
    position: absolute; top: -10px; right: -6px; opacity: 0.10; color: var(--accent);
    transform: scale(2.6);
}}
.kpi-card .kpi-label {{
    font-size: 12px; font-weight: 700; color: {MUTED};
    text-transform: uppercase; letter-spacing: 0.4px; margin-bottom: 8px;
    display: flex; align-items: center; gap: 6px;
}}
.kpi-card .kpi-label .ic {{ color: var(--accent); }}
.kpi-card .kpi-value {{ font-size: 23px; font-weight: 800; color: {INK}; line-height: 1.15; position: relative; z-index: 2; }}
.kpi-card .kpi-note {{ margin-top: 9px; position: relative; z-index: 2; }}
.kpi-chip {{
    display: inline-flex; align-items: center; gap: 5px;
    font-size: 11.5px; font-weight: 700; padding: 3px 10px; border-radius: 999px;
}}
.kpi-chip.pos {{ background: rgba(0,210,106,0.14); color: #0B8A46; }}
.kpi-chip.neg {{ background: rgba(255,77,77,0.14); color: #C4231F; }}
.kpi-chip.info {{ background: rgba(30,62,98,0.12); color: {SAPPHIRE}; }}
.kpi-chip.warn {{ background: rgba(255,176,32,0.16); color: #A15C00; }}

/\* accent variants \*/
.kpi-navy {{ --accent: {SAPPHIRE}; }}
.kpi-emerald {{ --accent: {EMERALD}; }}
.kpi-crimson {{ --accent: {CRIMSON}; }}
.kpi-amber {{ --accent: {AMBER}; }}

/\* ================= HERO RESULT BOX ================= \*/
.result-hero {{
    border-radius: 22px; padding: 26px 28px; color: white; position: relative; overflow: hidden;
    background: linear-gradient(135deg, {NAVY} 0%, {SAPPHIRE} 100%);
    box-shadow: 0 18px 34px rgba(11,25,44,0.3);
}}
.result-hero.crimson {{ background: linear-gradient(135deg, #7A1414 0%, {CRIMSON} 100%); box-shadow: 0 18px 34px rgba(255,77,77,0.28); }}
.result-hero.amber {{ background: linear-gradient(135deg, #7A4B00 0%, {AMBER} 100%); box-shadow: 0 18px 34px rgba(255,176,32,0.28); }}
.result-hero .rh-label {{ font-size: 13px; letter-spacing: 0.4px; opacity: 0.8; font-weight: 700; text-transform: uppercase; }}
.result-hero .rh-value {{ font-size: 36px; font-weight: 800; margin: 6px 0 12px 0; }}
.result-hero .rh-detail {{ font-size: 13.5px; opacity: 0.92; line-height: 1.8; }}

/\* ================= PROGRESS BAR ================= \*/
.progress-wrap {{ margin: 6px 0 4px 0; }}
.progress-labels {{ display: flex; justify-content: space-between; font-size: 12.5px; font-weight: 700; color: {MUTED}; margin-bottom: 6px; }}
.progress-track {{
    height: 12px; border-radius: 999px; background: rgba(30,62,98,0.10);
    box-shadow: inset 3px 3px 6px rgba(163,177,198,0.4), inset -3px -3px 6px rgba(255,255,255,0.6);
    overflow: hidden;
}}
.progress-fill {{
    height: 100%; border-radius: 999px;
    background: linear-gradient(90deg, {SAPPHIRE}, {EMERALD});
    box-shadow: 0 0 10px rgba(0,210,106,0.5);
    transition: width 0.4s ease;
}}

/\* ================= BATTLE CARDS (so sánh) ================= \*/
.battle-wrap {{ display: flex; align-items: stretch; gap: 14px; }}
.battle-card {{
    flex: 1; border-radius: 20px; padding: 20px 20px 18px 20px; position: relative;
    background: rgba(255,255,255,0.8);
    border: 1.5px solid rgba(255,255,255,0.7);
    box-shadow: 8px 8px 18px rgba(163,177,198,0.3), -8px -8px 18px rgba(255,255,255,0.75);
}}
.battle-card.winner {{ border-color: {EMERALD}; box-shadow: 0 0 0 3px rgba(0,210,106,0.18), 8px 8px 18px rgba(163,177,198,0.3); }}
.battle-card .bc-tag {{ font-size: 11.5px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.4px; color: {MUTED}; }}
.battle-card .bc-title {{ font-size: 15.5px; font-weight: 800; color: {NAVY}; margin: 4px 0 12px 0; }}
.battle-card .bc-value {{ font-size: 24px; font-weight: 800; color: {INK}; }}
.battle-card .bc-line {{ font-size: 12.5px; color: {MUTED}; margin-top: 4px; }}
.battle-vs {{
    display: flex; align-items: center; justify-content: center;
    font-weight: 800; font-size: 13px; color: white;
    background: linear-gradient(135deg, {NAVY}, {SAPPHIRE});
    width: 40px; height: 40px; border-radius: 50%;
    box-shadow: 0 6px 14px rgba(11,25,44,0.3);
    align-self: center; flex-shrink: 0;
}}
.winner-crown {{ position: absolute; top: -10px; right: 16px; font-size: 20px; }}
.verdict-box {{
    margin-top: 14px; padding: 14px 16px; border-radius: 14px;
    background: rgba(0,210,106,0.10); border: 1px solid rgba(0,210,106,0.3);
    color: #0B8A46; font-size: 13.5px; font-weight: 600; line-height: 1.6;
}}
.verdict-box.neg {{ background: rgba(255,77,77,0.10); border-color: rgba(255,77,77,0.3); color: #C4231F; }}

/\* ================= BADGES ================= \*/
.badge-pill {{ display: inline-flex; align-items: center; gap: 6px; padding: 5px 14px; border-radius: 999px; font-size: 12.5px; font-weight: 700; margin-bottom: 10px; }}
.badge-pill.emerald {{ background: rgba(0,210,106,0.14); color: #0B8A46; }}
.badge-pill.crimson {{ background: rgba(255,77,77,0.14); color: #C4231F; }}
.badge-pill.amber {{ background: rgba(255,176,32,0.18); color: #A15C00; }}

/\* ================= QUICK-SELECT PILLS (chips) ================= \*/
.st-key-quick\_chips .stButton>button, .st-key-adj\_chips .stButton>button {{
    border-radius: 999px !important;
    border: 1px solid rgba(30,62,98,0.18) !important;
    background: rgba(255,255,255,0.75) !important;
    color: {SAPPHIRE} !important; font-weight: 700 !important; font-size: 12.5px !important;
    box-shadow: 3px 3px 8px rgba(163,177,198,0.35), -3px -3px 8px rgba(255,255,255,0.7) !important;
    padding: 2px 4px !important;
}}
.st-key-quick\_chips .stButton>button\:hover, .st-key-adj\_chips .stButton>button\:hover {{
    border-color: {EMERALD} !important; color: #0B8A46 !important;
}}

/\* toggle (radio) segmented control style \*/
.st-key-toggle\_method div[role="radiogroup"] {{
    background: rgba(30,62,98,0.08); padding: 5px; border-radius: 14px; gap: 4px;
}}
.st-key-toggle\_method label {{
    border-radius: 10px !important; padding: 6px 10px !important; font-weight: 600 !important;
}}

/\* main action buttons \*/
.st-key-calc\_btn .stButton>button {{
    background: linear-gradient(135deg, {NAVY} 0%, {SAPPHIRE} 50%, #146356 100%) !important;
    background-size: 200% 200% !important;
    color: white !important; border: none !important; font-weight: 800 !important;
    border-radius: 14px !important; padding: 12px !important; font-size: 15px !important;
    box-shadow: 0 10px 24px rgba(11,25,44,0.3) !important;
    transition: background-position 0.5s ease, transform 0.2s ease !important;
}}
.st-key-calc\_btn .stButton>button\:hover {{
    background-position: 100% 50% !important; transform: translateY(-2px) !important;
}}
.st-key-reset\_btn .stButton>button {{
    border-radius: 14px !important; font-weight: 700 !important;
    background: rgba(255,255,255,0.7) !important; color: {SAPPHIRE} !important;
    border: 1px solid rgba(30,62,98,0.2) !important;
}}

div[data-testid="stTabs"] button[aria-selected="true"] {{ color: {SAPPHIRE}; font-weight: 800; }}
div[data-testid="stTabs"] div[data-baseweb="tab-highlight"] {{ background-color: {EMERALD} !important; }}

hr {{ opacity: 0.12; }}

/\* sticky control panel on wide screens \*/
@media (min-width: 1000px) {{
    div[data-testid="column"]\:first-child > div {{ position: sticky; top: 14px; }}
}}

</style>
""", unsafe_allow_html=True)

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
unsafe_allow_html=True
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
unsafe_allow_html=True
)

# Hiểu các cách gõ: "50000000", "50 triệu", "1.5 tỷ", "200k"...
import re as _re

_SUFFIX_MULT = {
"": 1, "d": 1, "dong": 1, "đ": 1, "đồng": 1,
"k": 1_000, "nghin": 1_000, "nghìn": 1_000,
"tr": 1_000_000, "trieu": 1_000_000, "triệu": 1_000_000, "m": 1_000_000,
"ty": 1_000_000_000, "tỷ": 1_000_000_000, "b": 1_000_000_000,
}
_PARSE_RE = _re.compile(r"^([\d]*\.?[\d]+)\s*([^\d\s]*)$", _re.UNICODE)

def parse_smart_amount(text: str):
if not text:
return None
t = text.strip().lower().replace(",", "").replace("vnđ", "").replace("vnd", "").strip()
m = _PARSE_RE.match(t)
if not m:
return None
num_str, suffix = m.groups()
suffix = suffix.strip()
if suffix not in _SUFFIX_MULT:
return None
try:
number = float(num_str)
except ValueError:
return None
return number * _SUFFIX_MULT[suffix]

# ============================================================
# HẰNG SỐ KỲ HẠN
# ============================================================

TERM_OPTIONS = {
"Không kỳ hạn": 0,
"1 tháng": 1, "2 tháng": 2, "3 tháng": 3,
"6 tháng": 6, "9 tháng": 9, "12 tháng": 12,
"18 tháng": 18, "24 tháng": 24, "36 tháng": 36
}

# ============================================================
# HÀM LÕI TÍNH TOÁN (giữ nguyên 100% logic tài chính so với bản gốc)
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

while current < end\_date:
    next\_month = current + relativedelta(months=1)
    period\_end = min(next\_month, end\_date)
    days = get\_days(current, period\_end)
    interest = simple\_interest(principal, annual\_rate\_percent, days)
    total\_interest += interest

    rows.append({
        "Kỳ": len(rows) + 1,
        "Từ ngày": current.strftime("%d/%m/%Y"),
        "Đến trước ngày": period\_end.strftime("%d/%m/%Y"),
        "Số ngày": days,
        "Tiền lãi": interest,
        "full\_month": period\_end == next\_month
    })
    current = period\_end

return total\_interest, rows

def renewal_periods(principal, term_rate, non_term_rate, start_date, withdrawal_date, term_months):
"""
Mỗi lần đáo hạn mà khách không rút, ngân hàng tự động tái tục CẢ GỐC LẪN LÃI
(gốc kỳ mới = gốc kỳ trước + tiền lãi vừa phát sinh). Vì vậy lãi của kỳ tái tục
phải được tính trên số dư mới này, không phải trên số tiền gửi ban đầu.
Ví dụ: gửi 500 triệu, kỳ hạn 3 tháng, đến hạn được +lãi ~6.x triệu -> gốc kỳ kế
tiếp là ~506 triệu, và lãi của kỳ đó (kể cả khi rút giữa kỳ) phải tính trên ~506 triệu.
"""
periods = []
current_start = start_date
current_principal = principal # số dư (gốc) đang sinh lãi ở đầu mỗi kỳ

while current\_start < withdrawal\_date:
    maturity = current\_start + relativedelta(months=term\_months)
    period\_end = min(maturity, withdrawal\_date)
    is\_full\_period = period\_end == maturity

    applied\_rate = term\_rate if is\_full\_period else non\_term\_rate
    days = get\_days(current\_start, period\_end)
    interest = simple\_interest(current\_principal, applied\_rate, days)

    periods.append({
        "Kỳ": len(periods) + 1,
        "Ngày bắt đầu": current\_start,
        "Ngày kết thúc": period\_end,
        "Số ngày": days,
        "Gốc đầu kỳ": current\_principal,
        "Lãi suất áp dụng": applied\_rate,
        "Tiền lãi": interest,
        "Đủ kỳ hạn": is\_full\_period
    })
    current\_start = period\_end
    if is\_full\_period:
        \# Đáo hạn mà không rút -> gộp lãi vào gốc để tái tục kỳ tiếp theo
        current\_principal += interest

return periods

# ============================================================
# BIỂU ĐỒ (Plotly — theme trong suốt / dark navy)
# ============================================================

PLOTLY_FONT = dict(family="Plus Jakarta Sans, Inter, sans-serif", color=INK, size=12)

def render_donut_chart(principal, interest):
fig = go.Figure(data=[go.Pie(
labels=["Tiền gốc", "Tiền lãi"],
values=[principal, max(interest, 0)],
hole=0.64,
marker=dict(colors=[SAPPHIRE, EMERALD], line=dict(color="#F8FAFC", width=3)),
textinfo="percent",
textfont=dict(size=13, color="white"),
hovertemplate="%{label}: %{value:,.0f} VNĐ (%{percent})<extra></extra>",
)])
total = principal + max(interest, 0)
fig.update_layout(
showlegend=True,
legend=dict(orientation="h", yanchor="bottom", y=-0.16, xanchor="center", x=0.5, font=PLOTLY_FONT),
margin=dict(t=10, b=10, l=10, r=10),
height=300,
font=PLOTLY_FONT,
annotations=[dict(
text=f"<b>{auto_label(total)}</b><br><span style='font-size:11px;color:#64748B'>Tổng giá trị</span>",
x=0.5, y=0.5, showarrow=False, font=dict(size=15, color=NAVY)
)],
paper_bgcolor="rgba(0,0,0,0)",
plot_bgcolor="rgba(0,0,0,0)",
)
st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

def render_waterfall_area_chart(principal, timeline):
"""Kết hợp Waterfall (đóng góp lãi từng kỳ) + Area chart (giá trị luỹ kế) trên nền trong suốt."""
if not timeline:
st.info("Không có dữ liệu theo kỳ để vẽ biểu đồ.")
return

labels = [t["label"] for t in timeline]
lai\_ky = [t["lai\_ky"] for t in timeline]
cumulative = []
running = principal
for v in lai\_ky:
    running += v
    cumulative.append(running)

wf\_labels = ["Gốc ban đầu"] + labels
wf\_values = [principal] + lai\_ky
wf\_measure = ["absolute"] + ["relative"] \* len(lai\_ky)

fig = go.Figure()

fig.add\_trace(go.Waterfall(
    name="Dòng tiền",
    orientation="v",
    measure=wf\_measure,
    x=wf\_labels,
    y=wf\_values,
    text=[f"{v:,.0f}" for v in wf\_values],
    textposition="outside",
    connector=dict(line=dict(color="rgba(148,163,184,0.4)")),
    increasing=dict(marker=dict(color=EMERALD)),
    decreasing=dict(marker=dict(color=CRIMSON)),
    totals=dict(marker=dict(color=SAPPHIRE)),
))

fig.update\_layout(
    height=400,
    margin=dict(t=30, b=10, l=10, r=10),
    font=PLOTLY\_FONT,
    paper\_bgcolor="rgba(0,0,0,0)",
    plot\_bgcolor="rgba(0,0,0,0)",
    yaxis=dict(title="VNĐ", showgrid=True, gridcolor="rgba(11,25,44,0.08)"),
    xaxis=dict(title=None),
    showlegend=False,
)
st.plotly\_chart(fig, use\_container\_width=True, config={"displayModeBar": False})

fig2 = go.Figure()
fig2.add\_trace(go.Scatter(
    x=labels, y=cumulative, mode="lines+markers", name="Giá trị luỹ kế",
    line=dict(color=EMERALD, width=3), marker=dict(size=7, color=EMERALD),
    fill="tozeroy", fillcolor="rgba(0,210,106,0.12)",
    hovertemplate="%{x}\<br>Luỹ kế: %{y:,.0f} VNĐ\<extra>\</extra>",
))
fig2.update\_layout(
    height=260,
    margin=dict(t=10, b=10, l=10, r=10),
    font=PLOTLY\_FONT,
    paper\_bgcolor="rgba(0,0,0,0)",
    plot\_bgcolor="rgba(0,0,0,0)",
    yaxis=dict(title="Giá trị luỹ kế (VNĐ)", showgrid=True, gridcolor="rgba(11,25,44,0.08)"),
    xaxis=dict(title=None),
    hovermode="x unified",
)
st.plotly\_chart(fig2, use\_container\_width=True, config={"displayModeBar": False})

def render_dataframe_bank_style(df, currency_cols=None, date_cols=None, rate_cols=None):
currency_cols = currency_cols or []
date_cols = date_cols or []
rate_cols = rate_cols or []

column\_config = {}
for c in currency\_cols:
    if c in df.columns:
        column\_config[c] = st.column\_config.NumberColumn(c, format="%,.0f ₫")
for c in date\_cols:
    if c in df.columns:
        column\_config[c] = st.column\_config.DateColumn(c, format="DD/MM/YYYY")
for c in rate\_cols:
    if c in df.columns:
        column\_config[c] = st.column\_config.NumberColumn(c, format="%.2f %%")

st.dataframe(df, use\_container\_width=True, hide\_index=True, column\_config=column\_config)

def battle_tab(value_A, principal, interest_A, value_B, loan_cost, interest_B, term_rate, loan_rate,
days_remaining, maturity_date):
a_wins = value_A >= value_B
st.markdown('<div class="battle-wrap">', unsafe_allow_html=True)
colA, colVS, colB = st.columns([1, 0.18, 1])

with colA:
    crown = '\<div class="winner-crown">👑\</div>' if a\_wins else ""
    html\_a = (
        f'\<div class="battle-card {"winner" if a\_wins else ""}">'
        f'{crown}'
        f'\<div class="bc-tag">PHƯƠNG ÁN A\</div>'
        f'\<div class="bc-title">🏃 Rút trước hạn ngay\</div>'
        f'\<div class="bc-value">{format\_money(value\_A)}\</div>'
        f'\<div class="bc-line">Gốc {format\_money(principal)} + lãi không kỳ hạn {format\_money(interest\_A)}\</div>'
        f'\<div class="bc-line">Quy đổi giá trị tại ngày đáo hạn {maturity\_date.strftime("%d/%m/%Y")}\</div>'
        f'\</div>'
    )
    st.markdown(html\_a, unsafe\_allow\_html=True
    )
with colVS:
    st.markdown('\<div style="height:60px;">\</div>\<div class="battle-vs">VS\</div>', unsafe\_allow\_html=True)
with colB:
    crown = '\<div class="winner-crown">👑\</div>' if not a\_wins else ""
    st.markdown(
        f"""
        \<div class="battle-card {'winner' if not a\_wins else ''}">
            {crown}
            \<div class="bc-tag">PHƯƠNG ÁN B\</div>
            \<div class="bc-title">🏦 Vay cầm cố sổ, giữ đến đáo hạn\</div>
            \<div class="bc-value">{format\_money(value\_B)}\</div>
            \<div class="bc-line">Vay {format\_money(principal)} @ {loan\_rate:.2f}%/năm trong {days\_remaining} ngày\</div>
            \<div class="bc-line">Chi phí vay {format\_money(loan\_cost)} · Lãi kỳ hạn {format\_money(interest\_B)}\</div>
        \</div>
        """, unsafe\_allow\_html=True
    )
st.markdown('\</div>', unsafe\_allow\_html=True)

diff = value\_B - value\_A
if diff > 0:
    st.markdown(
        f"""\<div class="verdict-box">✅ \<b>Nên VAY CẦM CỐ sổ tiết kiệm.\</b> Lợi hơn khoảng
        \<b>{format\_money(diff)}\</b> tại thời điểm đáo hạn vì lãi suất có kỳ hạn ({term\_rate:.2f}%/năm)
        bù đắp được chi phí vay ({loan\_rate:.2f}%/năm).\</div>""",
        unsafe\_allow\_html=True
    )
elif diff < 0:
    st.markdown(
        f"""\<div class="verdict-box neg">⚠️ \<b>Nên RÚT TRƯỚC HẠN.\</b> Vay cầm cố thiệt hơn khoảng
        \<b>{format\_money(-diff)}\</b> tại thời điểm đáo hạn vì chi phí vay ({loan\_rate:.2f}%/năm) cao hơn
        phần lãi có kỳ hạn giữ được.\</div>""",
        unsafe\_allow\_html=True
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
<div class="hero-glow-icon">{svg_icon('trending', 26)}</div>
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
unsafe_allow_html=True
)

# ============================================================
# LAYOUT 2 CỘT — MASTER (35%) / DETAIL (65%)
# ============================================================

col_left, col_right = st.columns([0.35, 0.65], gap="medium")

# ---------------------------------------------------------------
# CỘT TRÁI — CONTROL PANEL
# ---------------------------------------------------------------
with col_left:
with st.container(border=True):
st.markdown(
f'<div class="panel-title"><span class="pt-icon">{svg_icon("wallet", 15)}</span>BẢNG ĐIỀU KHIỂN</div>',
unsafe_allow_html=True
)

    DEFAULT\_AMOUNT = 500\_000\_000.0
    if "so\_tien\_goc" not in st.session\_state:
        st.session\_state.so\_tien\_goc = DEFAULT\_AMOUNT
    if "so\_tien\_text" not in st.session\_state:
        st.session\_state.so\_tien\_text = f"{DEFAULT\_AMOUNT:,.0f}"

    def \_set\_amount(new\_val: float):
        new\_val = max(float(new\_val), 0.0)
        st.session\_state.so\_tien\_goc = new\_val
        st.session\_state.so\_tien\_text = f"{new\_val:,.0f}"

    def \_on\_change\_amount\_text():
        val = parse\_smart\_amount(st.session\_state.so\_tien\_text)
        if val is not None:
            \_set\_amount(val)
        else:
            st.session\_state.so\_tien\_text = f"{st.session\_state.so\_tien\_goc:,.0f}"

    st.markdown("\*\*💰 Số tiền gửi\*\*")
    st.text\_input(
        "Nhập số tiền (vd: 500000000, 50 triệu, 1.5 tỷ, 200k...)",
        key="so\_tien\_text", on\_change=\_on\_change\_amount\_text, label\_visibility="collapsed",
    )

    \# Slider điều chỉnh nhanh (0 - 5 tỷ)
    def \_on\_slider\_change():
        \_set\_amount(st.session\_state["slider\_amount"])

    st.slider(
        "Điều chỉnh bằng thanh trượt", min\_value=0, max\_value=5\_000\_000\_000,
        value=int(st.session\_state.so\_tien\_goc), step=1\_000\_000,
        key="slider\_amount", on\_change=\_on\_slider\_change,
        label\_visibility="collapsed"
    )

    st.caption(f"➡️ Đang chọn: \*\*{format\_money(st.session\_state.so\_tien\_goc)}\*\* (≈ {auto\_label(st.session\_state.so\_tien\_goc)})")

    st.markdown("\<div style='font-size:12.5px;font-weight:700;color:#64748B;margin-top:6px;'>Chọn nhanh\</div>", unsafe\_allow\_html=True)
    with st.container(key="quick\_chips"):
        QUICK\_AMOUNTS = [50\_000\_000, 100\_000\_000, 200\_000\_000, 500\_000\_000, 1\_000\_000\_000, 2\_000\_000\_000]
        qc = st.columns(3)
        for i, amt in enumerate(QUICK\_AMOUNTS):
            qc[i % 3].button(auto\_label(amt), key=f"quick\_{amt}", use\_container\_width=True,
                              on\_click=\_set\_amount, args=(amt,))

    with st.container(key="adj\_chips"):
        st.markdown("\<div style='font-size:12.5px;font-weight:700;color:#64748B;margin-top:8px;'>Điều chỉnh nhanh\</div>", unsafe\_allow\_html=True)
        ac = st.columns(3)
        deltas = [("➕1tr", 1\_000\_000), ("➕10tr", 10\_000\_000), ("➕50tr", 50\_000\_000),
                  ("➖1tr", -1\_000\_000), ("➖10tr", -10\_000\_000), ("➖50tr", -50\_000\_000)]
        for i, (nhan, delta) in enumerate(deltas):
            ac[i % 3].button(nhan, key=f"delta\_{delta}", use\_container\_width=True,
                              on\_click=\_set\_amount, args=(st.session\_state.so\_tien\_goc + delta,))

    st.divider()
    st.markdown("\*\*📅 Kỳ hạn & lãi suất\*\*")
    term\_text = st.selectbox("Kỳ hạn gửi tiền", list(TERM\_OPTIONS.keys()), index=3)
    term\_months = TERM\_OPTIONS[term\_text]

    term\_rate = st.number\_input("📈 Lãi suất có kỳ hạn (%/năm)", min\_value=0.0, max\_value=100.0, value=5.0, step=0.01, format="%.2f")
    non\_term\_rate = st.number\_input("📉 Lãi suất không kỳ hạn (%/năm)", min\_value=0.0, max\_value=100.0, value=0.2, step=0.01, format="%.2f")
    loan\_rate = st.number\_input("🏦 Lãi suất vay cầm cố sổ (%/năm)", min\_value=0.0, max\_value=100.0, value=8.0, step=0.01, format="%.2f",
                                 help="Dùng để so sánh: nếu cần tiền trước hạn, nên rút sổ hay vay cầm cố chính sổ đó?")

    st.divider()
    st.markdown("\*\*🗓️ Thời gian\*\*")
    start\_date = st.date\_input("Ngày gửi tiền", value=date.today())
    withdrawal\_date = st.date\_input("Ngày rút tiền", value=date.today() + relativedelta(months=3))

    st.divider()
    st.markdown("\*\*💵 Phương thức nhận lãi\*\*")
    with st.container(key="toggle\_method"):
        interest\_method = st.radio(
            "Phương thức (áp dụng khi gửi đủ kỳ hạn)",
            ["💵 Nhận lãi trước", "📆 Nhận lãi hàng tháng", "🏁 Nhận lãi cuối kỳ"],
            horizontal=True, label\_visibility="collapsed"
        )

    st.write("")
    with st.container(key="calc\_btn"):
        calculate\_button = st.button("⚡ TÍNH TOÁN NGAY", use\_container\_width=True)
    with st.container(key="reset\_btn"):
        st.button("↺ Đặt lại số tiền mặc định", use\_container\_width=True,
                  on\_click=\_set\_amount, args=(DEFAULT\_AMOUNT,))

# ---------------------------------------------------------------
# CỘT PHẢI — ANALYTICS & REPORTS
# ---------------------------------------------------------------
with col_right:
tab1, tab2, tab3 = st.tabs(["📊 Tổng quan", "📋 Bảng dòng tiền chi tiết", "⚔️ So sánh thông minh"])

if not calculate\_button:
    with tab1:
        st.info("👈 Nhập thông tin ở Bảng điều khiển bên trái rồi bấm \*\*TÍNH TOÁN NGAY\*\* để xem kết quả.")
    with tab2:
        st.info("Chưa có dữ liệu để hiển thị.")
    with tab3:
        st.info("Chưa có dữ liệu để so sánh.")

else:
    principal = st.session\_state.so\_tien\_goc

    if principal <= 0:
        st.error("Số tiền gửi phải lớn hơn 0.")
        st.stop()
    if withdrawal\_date <= start\_date:
        st.error("Ngày rút tiền phải lớn hơn ngày gửi tiền.")
        st.stop()

    \# ---------------- KHÔNG KỲ HẠN ----------------
    if term\_months == 0:
        days = get\_days(start\_date, withdrawal\_date)
        interest = simple\_interest(principal, non\_term\_rate, days)
        total = principal + interest

        detail\_df = pd.DataFrame([{
            "Loại tiền gửi": "Không kỳ hạn", "Ngày gửi": start\_date, "Ngày rút": withdrawal\_date,
            "Số ngày": days, "Lãi suất áp dụng (%/năm)": non\_term\_rate,
            "Tiền gốc (VNĐ)": round(principal), "Tiền lãi (VNĐ)": round(interest),
            "Tổng nhận (VNĐ)": round(total)
        }])

        with tab1:
            st.markdown('\<span class="badge-pill amber">🕊️ KHÔNG KỲ HẠN\</span>', unsafe\_allow\_html=True)
            st.caption("Áp dụng lãi suất không kỳ hạn cho toàn bộ thời gian gửi.")

            k1, k2, k3, k4 = st.columns(4)
            with k1: kpi\_card("Tiền gốc", format\_million(principal / 1e6), "wallet", "navy")
            with k2: kpi\_card("Số ngày gửi", f"{days} ngày", "calendar", "navy")
            with k3: kpi\_card("Tiền lãi", format\_million(interest / 1e6), "trending", "emerald",
                               '\<span class="kpi-chip pos">+' + f"{non\_term\_rate:.2f}%/năm" + '\</span>')
            with k4: kpi\_card("Tổng nhận", format\_million(total / 1e6), "banknote", "emerald")

            colA, colB = st.columns([1.3, 1])
            with colA:
                st.markdown(
                    f"""\<div class="result-hero">\<div class="rh-label">Tổng số tiền nhận được\</div>
                    \<div class="rh-value">{format\_money(total)}\</div>
                    \<div class="rh-detail">Gốc {format\_money(principal)} · Lãi {format\_money(interest)}\<br>
                    Lãi suất {non\_term\_rate:.2f}%/năm · {days} ngày\</div>\</div>""",
                    unsafe\_allow\_html=True
                )
                st.download\_button("⬇️ Tải kết quả (CSV)", detail\_df.to\_csv(index=False).encode("utf-8-sig"),
                                    file\_name="ket\_qua\_tiet\_kiem.csv", mime="text/csv")
            with colB:
                render\_donut\_chart(principal, interest)

            st.markdown("##### 📈 Dòng tiền theo thời gian")
            render\_waterfall\_area\_chart(principal, [{"label": "Không kỳ hạn", "lai\_ky": interest}])

        with tab2:
            st.markdown("##### 📋 Chi tiết dòng tiền")
            render\_dataframe\_bank\_style(detail\_df, currency\_cols=["Tiền gốc (VNĐ)", "Tiền lãi (VNĐ)", "Tổng nhận (VNĐ)"],
                                         date\_cols=["Ngày gửi", "Ngày rút"], rate\_cols=["Lãi suất áp dụng (%/năm)"])
        with tab3:
            st.info("Tiền gửi không kỳ hạn không phát sinh so sánh vay cầm cố vs rút trước hạn.")

        st.stop()

    \# ---------------- CÓ KỲ HẠN ----------------
    maturity\_date = get\_maturity\_date(start\_date, term\_months)
    early\_withdrawal = withdrawal\_date < maturity\_date
    exact\_maturity = withdrawal\_date == maturity\_date

    \# ============ RÚT TRƯỚC HẠN ============
    if early\_withdrawal:
        days = get\_days(start\_date, withdrawal\_date)
        interest = simple\_interest(principal, non\_term\_rate, days)
        total = principal + interest

        days\_full\_term = get\_days(start\_date, maturity\_date)
        days\_remaining = get\_days(withdrawal\_date, maturity\_date)
        value\_A = total
        interest\_if\_hold = simple\_interest(principal, term\_rate, days\_full\_term)
        loan\_cost = simple\_interest(principal, loan\_rate, days\_remaining)
        value\_B = principal + interest\_if\_hold - loan\_cost

        detail\_df = pd.DataFrame([{
            "Trạng thái": "Rút trước hạn", "Ngày gửi": start\_date, "Ngày rút": withdrawal\_date,
            "Số ngày": days, "Lãi suất áp dụng (%/năm)": non\_term\_rate,
            "Tiền gốc (VNĐ)": round(principal), "Tiền lãi (VNĐ)": round(interest),
            "Tổng nhận (VNĐ)": round(total)
        }])

        with tab1:
            st.markdown('\<span class="badge-pill crimson">⚠️ RÚT TRƯỚC HẠN\</span>', unsafe\_allow\_html=True)
            progress\_bar\_custom(round(100 \* days / max(days\_full\_term, 1), 1),
                                 f"Đã gửi {days}/{days\_full\_term} ngày",
                                 f"{round(100 \* days / max(days\_full\_term, 1), 1)}%")

            k1, k2, k3, k4 = st.columns(4)
            with k1: kpi\_card("Tiền gốc", format\_million(principal / 1e6), "wallet", "navy")
            with k2: kpi\_card("Số ngày gửi", f"{days} ngày", "calendar", "navy")
            with k3: kpi\_card("Tiền lãi", format\_million(interest / 1e6), "trending", "crimson",
                               f'\<span class="kpi-chip warn">{non\_term\_rate:.2f}%/năm (không kỳ hạn)\</span>')
            with k4: kpi\_card("Tổng nhận", format\_million(total / 1e6), "banknote", "crimson")

            colA, colB = st.columns([1.3, 1])
            with colA:
                st.markdown(
                    f"""\<div class="result-hero crimson">\<div class="rh-label">Tổng nhận khi rút trước hạn\</div>
                    \<div class="rh-value">{format\_money(total)}\</div>
                    \<div class="rh-detail">Gốc {format\_money(principal)} · Lãi {format\_money(interest)}\<br>
                    Lãi suất {non\_term\_rate:.2f}%/năm · {days} ngày\</div>\</div>""",
                    unsafe\_allow\_html=True
                )
                st.download\_button("⬇️ Tải kết quả (CSV)", detail\_df.to\_csv(index=False).encode("utf-8-sig"),
                                    file\_name="ket\_qua\_rut\_truoc\_han.csv", mime="text/csv")
            with colB:
                render\_donut\_chart(principal, interest)

            st.markdown("##### 📈 Dòng tiền theo thời gian")
            render\_waterfall\_area\_chart(principal, [{"label": "Rút trước hạn", "lai\_ky": interest}])

        with tab2:
            st.markdown("##### 📋 Chi tiết dòng tiền")
            render\_dataframe\_bank\_style(detail\_df, currency\_cols=["Tiền gốc (VNĐ)", "Tiền lãi (VNĐ)", "Tổng nhận (VNĐ)"],
                                         date\_cols=["Ngày gửi", "Ngày rút"], rate\_cols=["Lãi suất áp dụng (%/năm)"])

        with tab3:
            st.markdown("##### ⚔️ Rút trước hạn vs Vay cầm cố sổ tiết kiệm")
            battle\_tab(value\_A, principal, interest, value\_B, loan\_cost, interest\_if\_hold,
                       term\_rate, loan\_rate, days\_remaining, maturity\_date)

    \# ============ RÚT ĐÚNG HẠN ============
    elif exact\_maturity:
        days = get\_days(start\_date, maturity\_date)
        progress\_pct = 100.0

        if interest\_method == "💵 Nhận lãi trước":
            interest = simple\_interest(principal, term\_rate, days)
            total = principal + interest
            detail\_df = pd.DataFrame([
                {"Mốc": "Ngày gửi (nhận lãi trước)", "Ngày": start\_date, "Số tiền (VNĐ)": round(interest)},
                {"Mốc": "Ngày đáo hạn (nhận gốc)", "Ngày": maturity\_date, "Số tiền (VNĐ)": round(principal)},
            ])
            timeline = [{"label": "Nhận lãi trước", "lai\_ky": interest}]

        elif interest\_method == "📆 Nhận lãi hàng tháng":
            total\_interest, rows = monthly\_breakdown(principal, term\_rate, start\_date, maturity\_date)
            interest = total\_interest
            total = principal + total\_interest
            detail\_df = pd.DataFrame([{
                "Kỳ": r["Kỳ"],
                "Từ ngày": pd.to\_datetime(r["Từ ngày"], format="%d/%m/%Y").date(),
                "Đến trước ngày": pd.to\_datetime(r["Đến trước ngày"], format="%d/%m/%Y").date(),
                "Số ngày": r["Số ngày"], "Tiền lãi (VNĐ)": round(r["Tiền lãi"])
            } for r in rows])
            timeline = [{"label": f"Kỳ {r['Kỳ']}", "lai\_ky": r["Tiền lãi"]} for r in rows]

        else:
            interest = simple\_interest(principal, term\_rate, days)
            total = principal + interest
            detail\_df = pd.DataFrame([{
                "Mốc": "Ngày đáo hạn (nhận gốc + lãi)", "Ngày": maturity\_date,
                "Tiền gốc (VNĐ)": round(principal), "Tiền lãi (VNĐ)": round(interest),
                "Tổng nhận (VNĐ)": round(total)
            }])
            timeline = [{"label": "Đáo hạn", "lai\_ky": interest}]

        with tab1:
            st.markdown('\<span class="badge-pill emerald">🏁 GỬI ĐÚNG KỲ HẠN\</span>', unsafe\_allow\_html=True)
            progress\_bar\_custom(progress\_pct, f"Ngày gửi {start\_date.strftime('%d/%m/%Y')}",
                                 f"Đáo hạn {maturity\_date.strftime('%d/%m/%Y')} · 100%")

            k1, k2, k3, k4 = st.columns(4)
            with k1: kpi\_card("Tiền gốc", format\_million(principal / 1e6), "wallet", "navy")
            with k2: kpi\_card("Số ngày", f"{days} ngày", "calendar", "navy")
            with k3: kpi\_card("Tiền lãi", format\_million(interest / 1e6), "trending", "emerald",
                               f'\<span class="kpi-chip pos">{term\_rate:.2f}%/năm\</span>')
            with k4: kpi\_card("Tổng nhận", format\_million(total / 1e6), "banknote", "emerald")

            colA, colB = st.columns([1.3, 1])
            with colA:
                st.markdown(
                    f"""\<div class="result-hero">\<div class="rh-label">Tổng dòng tiền nhận được\</div>
                    \<div class="rh-value">{format\_money(total)}\</div>
                    \<div class="rh-detail">Gốc {format\_money(principal)} · Lãi {format\_money(interest)}\<br>
                    Phương thức: {interest\_method} · Lãi suất {term\_rate:.2f}%/năm\</div>\</div>""",
                    unsafe\_allow\_html=True
                )
                st.download\_button("⬇️ Tải kết quả (CSV)", detail\_df.to\_csv(index=False).encode("utf-8-sig"),
                                    file\_name="ket\_qua\_dao\_han.csv", mime="text/csv")
            with colB:
                render\_donut\_chart(principal, interest)

            st.markdown("##### 📈 Dòng tiền theo thời gian")
            render\_waterfall\_area\_chart(principal, timeline)

        with tab2:
            st.markdown("##### 📋 Chi tiết dòng tiền")
            currency\_cols = [c for c in detail\_df.columns if "VNĐ" in c]
            date\_cols = [c for c in detail\_df.columns if c in ("Ngày", "Từ ngày", "Đến trước ngày")]
            render\_dataframe\_bank\_style(detail\_df, currency\_cols=currency\_cols, date\_cols=date\_cols)

        with tab3:
            st.info("Khách hàng rút đúng ngày đáo hạn nên không phát sinh so sánh vay cầm cố vs rút trước hạn.")

    \# ============ TÁI TỤC ============
    else:
        periods = renewal\_periods(principal, term\_rate, non\_term\_rate, start\_date, withdrawal\_date, term\_months)
        total\_interest = sum(p["Tiền lãi"] for p in periods)
        total = principal + total\_interest
        last\_full = periods[-1]["Đủ kỳ hạn"] if periods else True

        last\_p = periods[-1]
        last\_p\_len = get\_days(last\_p["Ngày bắt đầu"], last\_p["Ngày bắt đầu"] + relativedelta(months=term\_months))
        last\_p\_elapsed = last\_p["Số ngày"]
        progress\_pct = round(100 \* last\_p\_elapsed / max(last\_p\_len, 1), 1)

        detail\_df = pd.DataFrame([{
            "Kỳ": p["Kỳ"], "Ngày bắt đầu": p["Ngày bắt đầu"], "Ngày kết thúc": p["Ngày kết thúc"],
            "Số ngày": p["Số ngày"], "Gốc đầu kỳ (VNĐ)": round(p["Gốc đầu kỳ"]),
            "Lãi suất áp dụng (%/năm)": p["Lãi suất áp dụng"],
            "Tiền lãi (VNĐ)": round(p["Tiền lãi"]),
            "Trạng thái": "Đủ kỳ hạn (tái tục)" if p["Đủ kỳ hạn"] else "Rút giữa kỳ (không kỳ hạn)"
        } for p in periods])

        timeline = [{"label": f"Kỳ {p['Kỳ']}", "lai\_ky": p["Tiền lãi"]} for p in periods]

        with tab1:
            st.markdown('\<span class="badge-pill amber">🔄 TỰ ĐỘNG TÁI TỤC\</span>', unsafe\_allow\_html=True)
            if not last\_full:
                st.info("ℹ️ Kỳ cuối cùng rút \*\*giữa chừng\*\* nên được tính theo \*\*lãi suất không kỳ hạn\*\*.")
            progress\_bar\_custom(progress\_pct, f"Kỳ hiện tại: {last\_p\_elapsed}/{last\_p\_len} ngày",
                                 f"{progress\_pct}%")

            k1, k2, k3, k4 = st.columns(4)
            with k1: kpi\_card("Tiền gốc", format\_million(principal / 1e6), "wallet", "navy")
            with k2: kpi\_card("Số lần tái tục", f"{max(len(periods) - 1, 0)} lần", "repeat", "amber")
            with k3: kpi\_card("Tổng tiền lãi", format\_million(total\_interest / 1e6), "trending", "emerald")
            with k4: kpi\_card("Tổng nhận", format\_million(total / 1e6), "banknote", "emerald")

            colA, colB = st.columns([1.3, 1])
            with colA:
                st.markdown(
                    f"""\<div class="result-hero amber">\<div class="rh-label">Tổng tiền khi rút ngày {withdrawal\_date.strftime('%d/%m/%Y')}\</div>
                    \<div class="rh-value">{format\_money(total)}\</div>
                    \<div class="rh-detail">Gốc {format\_money(principal)} · Tổng lãi {format\_money(total\_interest)}\</div>\</div>""",
                    unsafe\_allow\_html=True
                )
                st.download\_button("⬇️ Tải lịch sử tái tục (CSV)", detail\_df.to\_csv(index=False).encode("utf-8-sig"),
                                    file\_name="lich\_su\_tai\_tuc.csv", mime="text/csv")
            with colB:
                render\_donut\_chart(principal, total\_interest)

            st.markdown("##### 📈 Dòng tiền qua các lần tái tục")
            render\_waterfall\_area\_chart(principal, timeline)

        with tab2:
            st.markdown("##### 📋 Lịch sử tái tục — dòng tiền chi tiết")
            st.caption("💡 Từ kỳ thứ 2 trở đi, \*\*Gốc đầu kỳ\*\* = gốc kỳ trước + lãi đã tái tục (lãi nhập gốc).")
            render\_dataframe\_bank\_style(detail\_df, currency\_cols=["Gốc đầu kỳ (VNĐ)", "Tiền lãi (VNĐ)"],
                                         date\_cols=["Ngày bắt đầu", "Ngày kết thúc"],
                                         rate\_cols=["Lãi suất áp dụng (%/năm)"])

        with tab3:
            st.info("Trường hợp tái tục tự động không áp dụng so sánh vay cầm cố vs rút trước hạn.")

# ============================================================
# HƯỚNG DẪN & CÔNG THỨC
# ============================================================

st.divider()
with st.expander("📖 Hướng dẫn sử dụng"):
st.markdown("""
**1. Số tiền gửi** — gõ tự do (`50 triệu`, `1.5 tỷ`, `200k`...), dùng thanh trượt, nút chọn nhanh dạng chip, hoặc nút ➕➖.

\*\*2. Lãi suất\*\* — nhập lãi suất có kỳ hạn, không kỳ hạn và lãi suất vay cầm cố.

\*\*3. Kỳ hạn\*\* — chọn từ Không kỳ hạn đến 36 tháng.

\*\*4. Phương thức nhận lãi\*\* — Nhận lãi trước / hàng tháng / cuối kỳ (áp dụng khi gửi đủ kỳ hạn).

\*\*5. Rút trước hạn\*\* — toàn bộ thời gian được tính lại theo lãi suất không kỳ hạn.

\*\*6. Tự động tái tục\*\* — nếu rút sau đáo hạn, hệ thống chia nhiều kỳ theo đúng kỳ hạn ban đầu; kỳ cuối rút giữa chừng dùng lãi suất không kỳ hạn.

\*\*7. Các tab kết quả\*\* — Tổng quan (KPI + Donut + Waterfall/Area chart), Bảng dòng tiền chi tiết, So sánh thông minh (chỉ có dữ liệu khi rút trước hạn).
""")

with st.expander("🧮 Công thức tính lãi"):
st.markdown("""
**Tiền lãi = Tiền gốc × Lãi suất năm × Số ngày / 365**

\*\*Tổng tiền nhận = Tiền gốc + Tiền lãi\*\*

\- Rút trước hạn (hoặc rút giữa một kỳ tái tục) → dùng lãi suất không kỳ hạn.
\- Đến hạn không rút → tự động tái tục đúng kỳ hạn ban đầu.
""")

st.divider()
st.caption("🏦 Hệ thống mô phỏng tính tiền gửi tiết kiệm | Streamlit + Plotly | Neumorphism × Glassmorphism SaaS Dashboard")
