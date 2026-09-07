import streamlit as st
from datetime import date
from dateutil.relativedelta import relativedelta
import pandas as pd
import plotly.graph_objects as go
import re
import io

# ============================================================
# CONFIG
# ============================================================
st.set_page_config(
    page_title="Tính tiền gửi tiết kiệm",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ============================================================
# CONSTANTS
# ============================================================
NAVY = "#0B192C"
SAPPHIRE = "#1E3E62"
EMERALD = "#00D26A"
CRIMSON = "#FF4D4D"
AMBER = "#FFB020"
INK = "#0F172A"
MUTED = "#64748B"

TERM_OPTIONS = {
    "Không kỳ hạn": 0,
    "1 tháng": 1,
    "2 tháng": 2,
    "3 tháng": 3,
    "6 tháng": 6,
    "9 tháng": 9,
    "12 tháng": 12,
    "18 tháng": 18,
    "24 tháng": 24,
    "36 tháng": 36,
}

QUICK_AMOUNTS = [
    50_000_000, 100_000_000, 200_000_000,
    500_000_000, 1_000_000_000, 2_000_000_000
]

SUFFIX_MULT = {
    "": 1,
    "d": 1, "dong": 1, "đ": 1, "đồng": 1,
    "k": 1_000, "nghin": 1_000, "nghìn": 1_000,
    "tr": 1_000_000, "trieu": 1_000_000, "triệu": 1_000_000, "m": 1_000_000,
    "ty": 1_000_000_000, "tỷ": 1_000_000_000, "b": 1_000_000_000,
}

# ============================================================
# SESSION STATE
# ============================================================
DEFAULTS = {
    "so_tien_goc": 500_000_000.0,
    "so_tien_text": "500000000",
    "slider_amount": 500_000_000,
    "calculate": False,
    "dark_mode": False,
}

for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value

# ============================================================
# SMART MONEY INPUT
# Supports:
# 500000000
# 500,000,000
# 500 triệu
# 1.5 tỷ
# 200k
# 50tr
# 1,5 tỷ
# ============================================================
def parse_smart_amount(text: str):
    if text is None:
        return None

    t = str(text).strip().lower()
    if not t:
        return None

    t = (
        t.replace("vnđ", "")
         .replace("vnd", "")
         .replace("₫", "")
         .replace(",", ".")
         .strip()
    )

    # Remove spaces between number and unit only
    t = re.sub(r"\s+", " ", t)

    match = re.fullmatch(r"([0-9]+(?:\.[0-9]+)?)\s*([^\d\s]*)", t)
    if not match:
        return None

    number_text, suffix = match.groups()
    suffix = suffix.strip()

    # Handle 500.000.000 style after comma replacement
    if suffix == "" and number_text.count(".") >= 2:
        try:
            return float(number_text.replace(".", ""))
        except ValueError:
            return None

    if suffix not in SUFFIX_MULT:
        return None

    try:
        number = float(number_text)
    except ValueError:
        return None

    return number * SUFFIX_MULT[suffix]


def format_money(value: float) -> str:
    return f"{round(value):,} VNĐ"


def format_million(value: float) -> str:
    return f"{value:,.2f} triệu đồng"


def auto_label(value: float) -> str:
    value = float(value)
    if value >= 1_000_000_000:
        return f"{value / 1_000_000_000:g} tỷ"
    if value >= 1_000_000:
        return f"{value / 1_000_000:g} triệu"
    if value >= 1_000:
        return f"{value / 1_000:g} nghìn"
    return f"{value:g} đồng"


def set_amount(value: float):
    value = max(float(value), 0.0)
    st.session_state.so_tien_goc = value
    st.session_state.so_tien_text = f"{value:,.0f}"
    st.session_state.slider_amount = min(int(value), 5_000_000_000)


def on_amount_change():
    value = parse_smart_amount(st.session_state.so_tien_text)
    if value is not None:
        set_amount(value)
    else:
        st.session_state.so_tien_text = f"{st.session_state.so_tien_goc:,.0f}"


def calculate_now():
    st.session_state.calculate = True


def reset_all():
    st.session_state.so_tien_goc = DEFAULTS["so_tien_goc"]
    st.session_state.so_tien_text = DEFAULTS["so_tien_text"]
    st.session_state.slider_amount = DEFAULTS["slider_amount"]
    st.session_state.calculate = False


def change_amount(delta):
    set_amount(st.session_state.so_tien_goc + delta)

# ============================================================
# FINANCE CORE
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
            "Kỳ": len(rows) + 1,
            "Từ ngày": current,
            "Đến trước ngày": period_end,
            "Số ngày": days,
            "Tiền lãi": interest,
            "Đủ tháng": period_end == next_month,
        })
        current = period_end

    return total_interest, rows


def renewal_periods(
    principal,
    term_rate,
    non_term_rate,
    start_date,
    withdrawal_date,
    term_months,
):
    periods = []
    current_start = start_date
    current_principal = principal

    while current_start < withdrawal_date:
        maturity = current_start + relativedelta(months=term_months)
        period_end = min(maturity, withdrawal_date)
        full_period = period_end == maturity

        applied_rate = term_rate if full_period else non_term_rate
        days = get_days(current_start, period_end)
        interest = simple_interest(current_principal, applied_rate, days)

        periods.append({
            "Kỳ": len(periods) + 1,
            "Ngày bắt đầu": current_start,
            "Ngày kết thúc": period_end,
            "Số ngày": days,
            "Gốc đầu kỳ": current_principal,
            "Lãi suất áp dụng": applied_rate,
            "Tiền lãi": interest,
            "Đủ kỳ hạn": full_period,
        })

        current_start = period_end

        if full_period:
            current_principal += interest

    return periods

# ============================================================
# CSS / THEME
# ============================================================
dark = st.session_state.dark_mode

if dark:
    BG = "#07111F"
    PANEL = "rgba(15, 30, 50, 0.82)"
    CARD = "rgba(18, 36, 58, 0.90)"
    TEXT = "#F1F5F9"
    SUBTEXT = "#A8B5C7"
    BORDER = "rgba(148,163,184,0.18)"
    GRID = "rgba(255,255,255,0.08)"
else:
    BG = "#F3F7FB"
    PANEL = "rgba(255,255,255,0.72)"
    CARD = "rgba(255,255,255,0.84)"
    TEXT = INK
    SUBTEXT = MUTED
    BORDER = "rgba(255,255,255,0.70)"
    GRID = "rgba(11,25,44,0.08)"

st.markdown(
    f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"], .stApp, p, span, div, label, button {{
    font-family: 'Plus Jakarta Sans', Inter, sans-serif !important;
}}

.stApp {{
    background:
        radial-gradient(circle at 10% 10%, rgba(30,62,98,0.12), transparent 30%),
        radial-gradient(circle at 90% 20%, rgba(0,210,106,0.08), transparent 25%),
        {BG};
    color: {TEXT};
}}

#MainMenu, footer {{
    visibility: hidden;
}}

.block-container {{
    padding-top: 1.2rem;
    padding-bottom: 2rem;
    max-width: 1700px;
}}

.hero {{
    position: relative;
    overflow: hidden;
    border-radius: 26px;
    padding: 28px 32px 20px;
    margin-bottom: 20px;
    background: linear-gradient(120deg, {NAVY}, {SAPPHIRE}, #24507F);
    box-shadow: 0 20px 45px rgba(11,25,44,0.30);
}}

.hero:before {{
    content: "";
    position: absolute;
    width: 300px;
    height: 300px;
    right: -100px;
    top: -120px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(0,210,106,.28), transparent 68%);
}}

.hero-title {{
    color: white;
    font-size: 29px;
    font-weight: 800;
    margin-top: 12px;
    position: relative;
}}

.hero-sub {{
    color: rgba(255,255,255,.72);
    font-size: 14px;
    position: relative;
}}

.badge {{
    display: inline-block;
    padding: 6px 13px;
    border-radius: 999px;
    background: rgba(0,210,106,.15);
    border: 1px solid rgba(0,210,106,.35);
    color: {EMERALD};
    font-size: 12px;
    font-weight: 800;
}}

.panel-title {{
    font-size: 15px;
    font-weight: 800;
    color: {TEXT};
    margin-bottom: 10px;
}}

div[data-testid="stVerticalBlockBorderWrapper"] {{
    border-radius: 22px !important;
    border: 1px solid {BORDER} !important;
    background: {PANEL} !important;
    backdrop-filter: blur(16px);
    box-shadow: 8px 10px 28px rgba(0,0,0,.10);
}}

.kpi {{
    position: relative;
    overflow: hidden;
    border-radius: 19px;
    padding: 17px;
    min-height: 120px;
    background: {CARD};
    border: 1px solid {BORDER};
    box-shadow: 7px 8px 18px rgba(0,0,0,.08);
}}

.kpi-label {{
    color: {SUBTEXT};
    font-size: 11.5px;
    font-weight: 800;
    text-transform: uppercase;
}}

.kpi-value {{
    color: {TEXT};
    font-size: 22px;
    font-weight: 800;
    margin-top: 8px;
}}

.kpi-note {{
    color: {SUBTEXT};
    font-size: 11.5px;
    margin-top: 6px;
}}

.result {{
    border-radius: 22px;
    padding: 24px 26px;
    color: white;
    background: linear-gradient(135deg, {NAVY}, {SAPPHIRE});
    box-shadow: 0 16px 30px rgba(11,25,44,.25);
}}

.result.red {{
    background: linear-gradient(135deg, #681313, {CRIMSON});
}}

.result.amber {{
    background: linear-gradient(135deg, #6D4300, {AMBER});
}}

.result-label {{
    font-size: 12px;
    text-transform: uppercase;
    font-weight: 800;
    opacity: .78;
}}

.result-value {{
    font-size: 34px;
    font-weight: 800;
    margin: 5px 0 10px;
}}

.result-detail {{
    font-size: 13px;
    line-height: 1.8;
}}

.verdict {{
    margin-top: 14px;
    padding: 14px 16px;
    border-radius: 15px;
    background: rgba(0,210,106,.11);
    border: 1px solid rgba(0,210,106,.30);
    color: {EMERALD};
    font-size: 13px;
    font-weight: 700;
}}

.verdict.red {{
    background: rgba(255,77,77,.11);
    border-color: rgba(255,77,77,.30);
    color: {CRIMSON};
}}

.progress {{
    height: 11px;
    border-radius: 99px;
    background: rgba(148,163,184,.18);
    overflow: hidden;
    margin: 7px 0 4px;
}}

.progress > div {{
    height: 100%;
    border-radius: 99px;
    background: linear-gradient(90deg, {SAPPHIRE}, {EMERALD});
}}

.small {{
    color: {SUBTEXT};
    font-size: 12px;
}}

div.stButton > button {{
    border-radius: 12px !important;
    font-weight: 700 !important;
}}

.stDownloadButton button {{
    border-radius: 12px !important;
    font-weight: 700 !important;
}}

div[data-testid="stTabs"] button[aria-selected="true"] {{
    font-weight: 800;
    color: {EMERALD};
}}

div[data-testid="stTabs"] div[data-baseweb="tab-highlight"] {{
    background-color: {EMERALD} !important;
}}

[data-testid="stDataFrame"] {{
    border-radius: 14px;
    overflow: hidden;
}}

@media (min-width: 1000px) {{
    div[data-testid="column"]:first-child > div {{
        position: sticky;
        top: 12px;
    }}
}}
</style>
""",
    unsafe_allow_html=True,
)

# ============================================================
# PLOTLY HELPERS
# ============================================================
PLOTLY_FONT = dict(
    family="Plus Jakarta Sans, Inter, sans-serif",
    color=TEXT,
    size=12,
)


def render_donut_chart(principal, interest):
    values = [principal, max(interest, 0)]
    labels = ["Tiền gốc", "Tiền lãi"]

    fig = go.Figure(
        data=[
            go.Pie(
                labels=labels,
                values=values,
                hole=0.64,
                marker=dict(
                    colors=[SAPPHIRE, EMERALD],
                    line=dict(color=BG, width=3),
                ),
                textinfo="percent",
                textfont=dict(size=13, color="white"),
                hovertemplate="%{label}: %{value:,.0f} VNĐ (%{percent})<extra></extra>",
            )
        ]
    )

    total = principal + max(interest, 0)

    fig.update_layout(
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.15,
            xanchor="center",
            x=0.5,
            font=PLOTLY_FONT,
        ),
        margin=dict(t=10, b=10, l=10, r=10),
        height=310,
        font=PLOTLY_FONT,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        annotations=[
            dict(
                text=f"<b>{auto_label(total)}</b><br>"
                     "<span style='font-size:11px'>Tổng giá trị</span>",
                x=.5, y=.5,
                showarrow=False,
                font=dict(size=15, color=TEXT),
            )
        ],
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={"displayModeBar": False},
    )


def render_cashflow_chart(principal, timeline):
    if not timeline:
        st.info("Không có dữ liệu để vẽ biểu đồ.")
        return

    labels = [x["label"] for x in timeline]
    interest_values = [x["lai_ky"] for x in timeline]

    cumulative = []
    running = principal

    for value in interest_values:
        running += value
        cumulative.append(running)

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=labels,
            y=interest_values,
            name="Tiền lãi",
            marker=dict(color=EMERALD),
            hovertemplate="%{x}<br>Lãi: %{y:,.0f} VNĐ<extra></extra>",
        )
    )

    fig.update_layout(
        height=300,
        margin=dict(t=20, b=20, l=10, r=10),
        font=PLOTLY_FONT,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(
            title="Tiền lãi (VNĐ)",
            gridcolor=GRID,
        ),
        showlegend=False,
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={"displayModeBar": False},
    )

    fig2 = go.Figure()
    fig2.add_trace(
        go.Scatter(
            x=labels,
            y=cumulative,
            mode="lines+markers",
            name="Tổng giá trị",
            line=dict(color=EMERALD, width=3),
            marker=dict(size=7, color=EMERALD),
            fill="tozeroy",
            fillcolor="rgba(0,210,106,.10)",
            hovertemplate="%{x}<br>Tổng: %{y:,.0f} VNĐ<extra></extra>",
        )
    )

    fig2.update_layout(
        height=260,
        margin=dict(t=10, b=20, l=10, r=10),
        font=PLOTLY_FONT,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(
            title="Tổng giá trị (VNĐ)",
            gridcolor=GRID,
        ),
        showlegend=False,
    )

    st.plotly_chart(
        fig2,
        use_container_width=True,
        config={"displayModeBar": False},
    )


def render_dataframe(df, currency_cols=None, date_cols=None, rate_cols=None):
    currency_cols = currency_cols or []
    date_cols = date_cols or []
    rate_cols = rate_cols or []

    config = {}

    for col in currency_cols:
        if col in df.columns:
            config[col] = st.column_config.NumberColumn(
                col, format="%,.0f ₫"
            )

    for col in date_cols:
        if col in df.columns:
            config[col] = st.column_config.DateColumn(
                col, format="DD/MM/YYYY"
            )

    for col in rate_cols:
        if col in df.columns:
            config[col] = st.column_config.NumberColumn(
                col, format="%.2f %%"
            )

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config=config,
    )


def kpi_card(label, value, note="", accent=EMERALD):
    st.markdown(
        f"""
        <div class="kpi" style="border-top:3px solid {accent};">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-note">{note}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def result_box(title, total, detail, variant=""):
    st.markdown(
        f"""
        <div class="result {variant}">
            <div class="result-label">{title}</div>
            <div class="result-value">{format_money(total)}</div>
            <div class="result-detail">{detail}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def progress_bar(percent, left, right):
    percent = max(0, min(100, float(percent)))
    st.markdown(
        f"""
        <div style="display:flex;justify-content:space-between;
                    font-size:12px;font-weight:700;color:{SUBTEXT};">
            <span>{left}</span><span>{right}</span>
        </div>
        <div class="progress"><div style="width:{percent}%"></div></div>
        """,
        unsafe_allow_html=True,
    )

# ============================================================
# HERO
# ============================================================
hero_col1, hero_col2 = st.columns([5, 1])

with hero_col1:
    st.markdown(
        """
        <div class="hero">
            <span class="badge">✓ HỆ THỐNG ĐANG HOẠT ĐỘNG</span>
            <div class="hero-title">🏦 Trung tâm tính tiền gửi tiết kiệm</div>
            <div class="hero-sub">
                Mô phỏng gốc – lãi – đáo hạn – rút trước hạn – tái tục
                và phân tích phương án tài chính.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with hero_col2:
    st.write("")
    st.toggle(
        "🌙 Chế độ tối",
        key="dark_mode",
        help="Chuyển giao diện sáng/tối.",
    )

# ============================================================
# MAIN LAYOUT
# ============================================================
col_left, col_right = st.columns([0.34, 0.66], gap="medium")

# ============================================================
# CONTROL PANEL
# ============================================================
with col_left:
    with st.container(border=True):
        st.markdown(
            '<div class="panel-title">🎛️ BẢNG ĐIỀU KHIỂN</div>',
            unsafe_allow_html=True,
        )

        st.markdown("**💰 Số tiền gửi**")

        st.text_input(
            "Số tiền",
            key="so_tien_text",
            on_change=on_amount_change,
            label_visibility="collapsed",
            placeholder="VD: 500 triệu, 1.5 tỷ, 200k...",
        )

        # Quick suggestion
        st.caption(
            "Nhập: `500000000` · `500 triệu` · `1.5 tỷ` · `200k`"
        )

        st.slider(
            "Số tiền",
            min_value=0,
            max_value=5_000_000_000,
            step=1_000_000,
            key="slider_amount",
            on_change=lambda: set_amount(st.session_state.slider_amount),
            label_visibility="collapsed",
        )

        st.caption(
            f"Đang chọn: **{format_money(st.session_state.so_tien_goc)}** "
            f"(≈ {auto_label(st.session_state.so_tien_goc)})"
        )

        st.markdown("**Chọn nhanh**")

        qcols = st.columns(3)
        for i, amount in enumerate(QUICK_AMOUNTS):
            qcols[i % 3].button(
                auto_label(amount),
                key=f"quick_{amount}",
                use_container_width=True,
                on_click=set_amount,
                args=(amount,),
            )

        st.markdown("**Điều chỉnh nhanh**")

        deltas = [
            ("➕ 1tr", 1_000_000),
            ("➕ 10tr", 10_000_000),
            ("➕ 50tr", 50_000_000),
            ("➖ 1tr", -1_000_000),
            ("➖ 10tr", -10_000_000),
            ("➖ 50tr", -50_000_000),
        ]

        acols = st.columns(3)
        for i, (label, delta) in enumerate(deltas):
            acols[i % 3].button(
                label,
                key=f"delta_{delta}",
                use_container_width=True,
                on_click=change_amount,
                args=(delta,),
            )

        st.divider()

        st.markdown("**📅 Kỳ hạn & lãi suất**")

        term_text = st.selectbox(
            "Kỳ hạn",
            list(TERM_OPTIONS.keys()),
            index=3,
        )
        term_months = TERM_OPTIONS[term_text]

        term_rate = st.number_input(
            "📈 Lãi suất có kỳ hạn (%/năm)",
            min_value=0.0,
            max_value=100.0,
            value=5.0,
            step=0.01,
            format="%.2f",
        )

        non_term_rate = st.number_input(
            "📉 Lãi suất không kỳ hạn (%/năm)",
            min_value=0.0,
            max_value=100.0,
            value=0.20,
            step=0.01,
            format="%.2f",
        )

        loan_rate = st.number_input(
            "🏦 Lãi suất vay cầm cố (%/năm)",
            min_value=0.0,
            max_value=100.0,
            value=8.0,
            step=0.01,
            format="%.2f",
            help="Dùng trong tab So sánh thông minh.",
        )

        st.divider()

        st.markdown("**🗓️ Thời gian**")

        start_date = st.date_input(
            "Ngày gửi tiền",
            value=date.today(),
        )

        withdrawal_date = st.date_input(
            "Ngày rút tiền",
            value=date.today() + relativedelta(months=3),
        )

        st.divider()

        st.markdown("**💵 Phương thức nhận lãi**")

        interest_method = st.radio(
            "Phương thức",
            [
                "💵 Nhận lãi trước",
                "📆 Nhận lãi hàng tháng",
                "🏁 Nhận lãi cuối kỳ",
            ],
            horizontal=True,
            label_visibility="collapsed",
        )

        st.write("")

        st.button(
            "⚡ TÍNH TOÁN NGAY",
            use_container_width=True,
            type="primary",
            on_click=calculate_now,
        )

        st.button(
            "↺ Đặt lại",
            use_container_width=True,
            on_click=reset_all,
        )

# ============================================================
# CALCULATION
# ============================================================
with col_right:
    tab1, tab2, tab3, tab4 = st.tabs(
        [
            "📊 Tổng quan",
            "📋 Dòng tiền",
            "⚔️ So sánh thông minh",
            "🧮 Công thức",
        ]
    )

    if not st.session_state.calculate:
        with tab1:
            st.info(
                "👈 Nhập thông tin bên trái rồi bấm **TÍNH TOÁN NGAY**."
            )
        with tab2:
            st.info("Chưa có dữ liệu.")
        with tab3:
            st.info("Chưa có dữ liệu.")
        with tab4:
            st.markdown(
                """
                ### Công thức cơ bản

                **Tiền lãi = Tiền gốc × Lãi suất năm × Số ngày / 365**

                **Tổng nhận = Tiền gốc + Tiền lãi**

                - Rút trước hạn → dùng lãi suất không kỳ hạn.
                - Rút sau ngày đáo hạn → các kỳ đủ hạn được tái tục.
                - Lãi của kỳ tái tục được nhập vào gốc kỳ tiếp theo.
                """
            )
    else:
        principal = float(st.session_state.so_tien_goc)

        if principal <= 0:
            st.error("Số tiền gửi phải lớn hơn 0.")
            st.stop()

        if withdrawal_date <= start_date:
            st.error("Ngày rút tiền phải lớn hơn ngày gửi tiền.")
            st.stop()

        # ====================================================
        # NON-TERM
        # ====================================================
        if term_months == 0:
            days = get_days(start_date, withdrawal_date)
            interest = simple_interest(principal, non_term_rate, days)
            total = principal + interest

            detail_df = pd.DataFrame([{
                "Loại tiền gửi": "Không kỳ hạn",
                "Ngày gửi": start_date,
                "Ngày rút": withdrawal_date,
                "Số ngày": days,
                "Lãi suất (%/năm)": non_term_rate,
                "Tiền gốc (VNĐ)": round(principal),
                "Tiền lãi (VNĐ)": round(interest),
                "Tổng nhận (VNĐ)": round(total),
            }])

            with tab1:
                st.success("🕊️ **KHÔNG KỲ HẠN**")

                k1, k2, k3, k4 = st.columns(4)
                with k1:
                    kpi_card(
                        "Tiền gốc",
                        format_million(principal / 1e6),
                        accent=SAPPHIRE,
                    )
                with k2:
                    kpi_card(
                        "Số ngày",
                        f"{days} ngày",
                        accent=SAPPHIRE,
                    )
                with k3:
                    kpi_card(
                        "Tiền lãi",
                        format_million(interest / 1e6),
                        f"{non_term_rate:.2f}%/năm",
                        EMERALD,
                    )
                with k4:
                    kpi_card(
                        "Tổng nhận",
                        format_million(total / 1e6),
                        accent=EMERALD,
                    )

                c1, c2 = st.columns([1.3, 1])
                with c1:
                    result_box(
                        "TỔNG SỐ TIỀN NHẬN ĐƯỢC",
                        total,
                        f"Gốc: {format_money(principal)} · "
                        f"Lãi: {format_money(interest)}<br>"
                        f"Lãi suất: {non_term_rate:.2f}%/năm · {days} ngày",
                    )

                    st.download_button(
                        "⬇️ Tải CSV",
                        detail_df.to_csv(index=False).encode("utf-8-sig"),
                        file_name="ket_qua_tiet_kiem.csv",
                        mime="text/csv",
                        use_container_width=True,
                    )

                with c2:
                    render_donut_chart(principal, interest)

                render_cashflow_chart(
                    principal,
                    [{"label": "Không kỳ hạn", "lai_ky": interest}],
                )

            with tab2:
                render_dataframe(
                    detail_df,
                    currency_cols=[
                        "Tiền gốc (VNĐ)",
                        "Tiền lãi (VNĐ)",
                        "Tổng nhận (VNĐ)",
                    ],
                    date_cols=["Ngày gửi", "Ngày rút"],
                    rate_cols=["Lãi suất (%/năm)"],
                )

            with tab3:
                st.info(
                    "Tiền gửi không kỳ hạn không phát sinh bài toán "
                    "rút trước hạn vs vay cầm cố."
                )

        # ====================================================
        # TERM DEPOSIT
        # ====================================================
        else:
            maturity_date = get_maturity_date(start_date, term_months)

            early_withdrawal = withdrawal_date < maturity_date
            exact_maturity = withdrawal_date == maturity_date

            # =================================================
            # EARLY WITHDRAWAL
            # =================================================
            if early_withdrawal:
                days = get_days(start_date, withdrawal_date)
                full_days = get_days(start_date, maturity_date)

                interest = simple_interest(
                    principal,
                    non_term_rate,
                    days,
                )
                total = principal + interest

                days_remaining = get_days(
                    withdrawal_date,
                    maturity_date,
                )

                interest_if_hold = simple_interest(
                    principal,
                    term_rate,
                    full_days,
                )

                loan_cost = simple_interest(
                    principal,
                    loan_rate,
                    days_remaining,
                )

                value_A = total
                value_B = principal + interest_if_hold - loan_cost

                detail_df = pd.DataFrame([{
                    "Trạng thái": "Rút trước hạn",
                    "Ngày gửi": start_date,
                    "Ngày rút": withdrawal_date,
                    "Ngày đáo hạn": maturity_date,
                    "Số ngày": days,
                    "Lãi suất (%/năm)": non_term_rate,
                    "Tiền gốc (VNĐ)": round(principal),
                    "Tiền lãi (VNĐ)": round(interest),
                    "Tổng nhận (VNĐ)": round(total),
                }])

                with tab1:
                    st.error("⚠️ **RÚT TRƯỚC HẠN**")

                    progress = 100 * days / max(full_days, 1)
                    progress_bar(
                        progress,
                        f"Đã gửi {days}/{full_days} ngày",
                        f"{progress:.1f}%",
                    )

                    k1, k2, k3, k4 = st.columns(4)
                    with k1:
                        kpi_card(
                            "Tiền gốc",
                            format_million(principal / 1e6),
                            accent=SAPPHIRE,
                        )
                    with k2:
                        kpi_card(
                            "Đã gửi",
                            f"{days} ngày",
                            accent=SAPPHIRE,
                        )
                    with k3:
                        kpi_card(
                            "Tiền lãi",
                            format_million(interest / 1e6),
                            f"{non_term_rate:.2f}%/năm",
                            CRIMSON,
                        )
                    with k4:
                        kpi_card(
                            "Tổng nhận",
                            format_million(total / 1e6),
                            accent=CRIMSON,
                        )

                    c1, c2 = st.columns([1.3, 1])
                    with c1:
                        result_box(
                            "TỔNG NHẬN KHI RÚT TRƯỚC HẠN",
                            total,
                            f"Gốc: {format_money(principal)} · "
                            f"Lãi: {format_money(interest)}<br>"
                            f"Lãi không kỳ hạn: {non_term_rate:.2f}%/năm",
                            "red",
                        )

                        st.download_button(
                            "⬇️ Tải CSV",
                            detail_df.to_csv(index=False).encode("utf-8-sig"),
                            file_name="ket_qua_rut_truoc_han.csv",
                            mime="text/csv",
                            use_container_width=True,
                        )

                    with c2:
                        render_donut_chart(principal, interest)

                    render_cashflow_chart(
                        principal,
                        [{"label": "Rút trước hạn", "lai_ky": interest}],
                    )

                with tab2:
                    render_dataframe(
                        detail_df,
                        currency_cols=[
                            "Tiền gốc (VNĐ)",
                            "Tiền lãi (VNĐ)",
                            "Tổng nhận (VNĐ)",
                        ],
                        date_cols=[
                            "Ngày gửi",
                            "Ngày rút",
                            "Ngày đáo hạn",
                        ],
                        rate_cols=["Lãi suất (%/năm)"],
                    )

                with tab3:
                    st.markdown("### ⚔️ Rút trước hạn vs vay cầm cố")

                    diff = value_B - value_A

                    ca, cb = st.columns(2)

                    with ca:
                        st.markdown(
                            f"""
                            <div class="kpi">
                                <div class="kpi-label">PHƯƠNG ÁN A</div>
                                <div class="kpi-value">{format_money(value_A)}</div>
                                <div class="kpi-note">
                                    Rút trước hạn<br>
                                    Lãi không kỳ hạn: {format_money(interest)}
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

                    with cb:
                        st.markdown(
                            f"""
                            <div class="kpi">
                                <div class="kpi-label">PHƯƠNG ÁN B</div>
                                <div class="kpi-value">{format_money(value_B)}</div>
                                <div class="kpi-note">
                                    Giữ sổ đến đáo hạn + vay cầm cố<br>
                                    Chi phí vay: {format_money(loan_cost)}
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

                    if diff > 0:
                        st.markdown(
                            f"""
                            <div class="verdict">
                                ✅ Nên cân nhắc <b>VAY CẦM CỐ</b>.
                                Chênh lệch mô phỏng khoảng
                                <b>{format_money(diff)}</b>.
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                    elif diff < 0:
                        st.markdown(
                            f"""
                            <div class="verdict red">
                                ⚠️ Trong mô hình này,
                                <b>RÚT TRƯỚC HẠN</b> có lợi hơn khoảng
                                <b>{format_money(-diff)}</b>.
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                    else:
                        st.info("Hai phương án tương đương theo mô hình.")

                    st.caption(
                        "Lưu ý: đây là mô phỏng toán học. Lãi suất, phí, tỷ lệ cho vay "
                        "trên giá trị sổ, cách tính ngày và điều kiện thực tế của ngân hàng "
                        "có thể khác."
                    )

            # =================================================
            # EXACT MATURITY
            # =================================================
            elif exact_maturity:
                days = get_days(start_date, maturity_date)

                if interest_method == "💵 Nhận lãi trước":
                    interest = simple_interest(
                        principal, term_rate, days
                    )
                    total = principal + interest

                    detail_df = pd.DataFrame([
                        {
                            "Mốc": "Ngày gửi - nhận lãi trước",
                            "Ngày": start_date,
                            "Tiền lãi (VNĐ)": round(interest),
                        },
                        {
                            "Mốc": "Ngày đáo hạn - nhận gốc",
                            "Ngày": maturity_date,
                            "Tiền gốc (VNĐ)": round(principal),
                        },
                    ])

                    timeline = [
                        {"label": "Lãi trước", "lai_ky": interest}
                    ]

                elif interest_method == "📆 Nhận lãi hàng tháng":
                    interest, rows = monthly_breakdown(
                        principal,
                        term_rate,
                        start_date,
                        maturity_date,
                    )

                    total = principal + interest

                    detail_df = pd.DataFrame([
                        {
                            "Kỳ": r["Kỳ"],
                            "Từ ngày": r["Từ ngày"],
                            "Đến trước ngày": r["Đến trước ngày"],
                            "Số ngày": r["Số ngày"],
                            "Tiền lãi (VNĐ)": round(r["Tiền lãi"]),
                        }
                        for r in rows
                    ])

                    timeline = [
                        {
                            "label": f"Kỳ {r['Kỳ']}",
                            "lai_ky": r["Tiền lãi"],
                        }
                        for r in rows
                    ]

                else:
                    interest = simple_interest(
                        principal, term_rate, days
                    )
                    total = principal + interest

                    detail_df = pd.DataFrame([{
                        "Mốc": "Ngày đáo hạn",
                        "Ngày": maturity_date,
                        "Tiền gốc (VNĐ)": round(principal),
                        "Tiền lãi (VNĐ)": round(interest),
                        "Tổng nhận (VNĐ)": round(total),
                    }])

                    timeline = [
                        {"label": "Đáo hạn", "lai_ky": interest}
                    ]

                with tab1:
                    st.success("🏁 **GỬI ĐÚNG KỲ HẠN**")

                    progress_bar(
                        100,
                        f"Ngày gửi {start_date.strftime('%d/%m/%Y')}",
                        f"Đáo hạn {maturity_date.strftime('%d/%m/%Y')}",
                    )

                    k1, k2, k3, k4 = st.columns(4)

                    with k1:
                        kpi_card(
                            "Tiền gốc",
                            format_million(principal / 1e6),
                            accent=SAPPHIRE,
                        )
                    with k2:
                        kpi_card(
                            "Số ngày",
                            f"{days} ngày",
                            accent=SAPPHIRE,
                        )
                    with k3:
                        kpi_card(
                            "Tiền lãi",
                            format_million(interest / 1e6),
                            f"{term_rate:.2f}%/năm",
                            EMERALD,
                        )
                    with k4:
                        kpi_card(
                            "Tổng nhận",
                            format_million(total / 1e6),
                            accent=EMERALD,
                        )

                    c1, c2 = st.columns([1.3, 1])

                    with c1:
                        result_box(
                            "TỔNG DÒNG TIỀN NHẬN",
                            total,
                            f"Gốc: {format_money(principal)} · "
                            f"Lãi: {format_money(interest)}<br>"
                            f"Phương thức: {interest_method}<br>"
                            f"Lãi suất: {term_rate:.2f}%/năm",
                        )

                        st.download_button(
                            "⬇️ Tải CSV",
                            detail_df.to_csv(index=False).encode("utf-8-sig"),
                            file_name="ket_qua_dao_han.csv",
                            mime="text/csv",
                            use_container_width=True,
                        )

                    with c2:
                        render_donut_chart(principal, interest)

                    render_cashflow_chart(principal, timeline)

                with tab2:
                    currency_cols = [
                        c for c in detail_df.columns
                        if "VNĐ" in c
                    ]
                    date_cols = [
                        c for c in detail_df.columns
                        if c in [
                            "Ngày",
                            "Từ ngày",
                            "Đến trước ngày",
                        ]
                    ]

                    render_dataframe(
                        detail_df,
                        currency_cols=currency_cols,
                        date_cols=date_cols,
                    )

                with tab3:
                    st.info(
                        "Rút đúng ngày đáo hạn nên không phát sinh "
                        "so sánh vay cầm cố."
                    )

            # =================================================
            # RENEWAL
            # =================================================
            else:
                periods = renewal_periods(
                    principal,
                    term_rate,
                    non_term_rate,
                    start_date,
                    withdrawal_date,
                    term_months,
                )

                total_interest = sum(
                    p["Tiền lãi"] for p in periods
                )

                total = principal + total_interest

                last_period = periods[-1]

                full_period_days = get_days(
                    last_period["Ngày bắt đầu"],
                    last_period["Ngày bắt đầu"]
                    + relativedelta(months=term_months),
                )

                progress = 100 * last_period["Số ngày"] / max(
                    full_period_days, 1
                )

                detail_df = pd.DataFrame([
                    {
                        "Kỳ": p["Kỳ"],
                        "Ngày bắt đầu": p["Ngày bắt đầu"],
                        "Ngày kết thúc": p["Ngày kết thúc"],
                        "Số ngày": p["Số ngày"],
                        "Gốc đầu kỳ (VNĐ)": round(p["Gốc đầu kỳ"]),
                        "Lãi suất (%/năm)": p["Lãi suất áp dụng"],
                        "Tiền lãi (VNĐ)": round(p["Tiền lãi"]),
                        "Trạng thái": (
                            "Đủ kỳ hạn - tái tục"
                            if p["Đủ kỳ hạn"]
                            else "Rút giữa kỳ - không kỳ hạn"
                        ),
                    }
                    for p in periods
                ])

                timeline = [
                    {
                        "label": f"Kỳ {p['Kỳ']}",
                        "lai_ky": p["Tiền lãi"],
                    }
                    for p in periods
                ]

                with tab1:
                    st.warning("🔄 **TỰ ĐỘNG TÁI TỤC**")

                    if not last_period["Đủ kỳ hạn"]:
                        st.info(
                            "Kỳ cuối rút giữa chừng nên dùng "
                            "lãi suất không kỳ hạn."
                        )

                    progress_bar(
                        progress,
                        f"Kỳ hiện tại: {last_period['Số ngày']}/{full_period_days} ngày",
                        f"{progress:.1f}%",
                    )

                    k1, k2, k3, k4 = st.columns(4)

                    with k1:
                        kpi_card(
                            "Gốc ban đầu",
                            format_million(principal / 1e6),
                            accent=SAPPHIRE,
                        )
                    with k2:
                        kpi_card(
                            "Số lần tái tục",
                            f"{max(len(periods)-1, 0)} lần",
                            accent=AMBER,
                        )
                    with k3:
                        kpi_card(
                            "Tổng tiền lãi",
                            format_million(total_interest / 1e6),
                            accent=EMERALD,
                        )
                    with k4:
                        kpi_card(
                            "Tổng nhận",
                            format_million(total / 1e6),
                            accent=EMERALD,
                        )

                    c1, c2 = st.columns([1.3, 1])

                    with c1:
                        result_box(
                            "TỔNG TIỀN KHI RÚT",
                            total,
                            f"Gốc ban đầu: {format_money(principal)} · "
                            f"Tổng lãi: {format_money(total_interest)}<br>"
                            f"Ngày rút: {withdrawal_date.strftime('%d/%m/%Y')}",
                            "amber",
                        )

                        st.download_button(
                            "⬇️ Tải lịch sử tái tục",
                            detail_df.to_csv(index=False).encode("utf-8-sig"),
                            file_name="lich_su_tai_tuc.csv",
                            mime="text/csv",
                            use_container_width=True,
                        )

                    with c2:
                        render_donut_chart(
                            principal,
                            total_interest,
                        )

                    render_cashflow_chart(principal, timeline)

                with tab2:
                    st.caption(
                        "💡 Từ kỳ thứ 2, gốc đầu kỳ = gốc kỳ trước + "
                        "lãi đã nhập gốc."
                    )

                    render_dataframe(
                        detail_df,
                        currency_cols=[
                            "Gốc đầu kỳ (VNĐ)",
                            "Tiền lãi (VNĐ)",
                        ],
                        date_cols=[
                            "Ngày bắt đầu",
                            "Ngày kết thúc",
                        ],
                        rate_cols=["Lãi suất (%/năm)"],
                    )

                with tab3:
                    st.info(
                        "Trường hợp tái tục tự động không áp dụng "
                        "so sánh vay cầm cố."
                    )

# ============================================================
# FOOTER / GUIDE
# ============================================================
st.divider()

with st.expander("📖 Hướng dẫn sử dụng"):
    st.markdown(
        """
### 1. Số tiền gửi
Có thể nhập:
- `500000000`
- `500 triệu`
- `1.5 tỷ`
- `1,5 tỷ`
- `200k`

Ngoài ra có thanh trượt, nút chọn nhanh và nút tăng/giảm.

### 2. Kỳ hạn
Chọn từ không kỳ hạn đến 36 tháng.

### 3. Ngày rút
- Trước đáo hạn → rút trước hạn.
- Đúng đáo hạn → nhận đủ lãi kỳ hạn.
- Sau đáo hạn → hệ thống mô phỏng tái tục.

### 4. Tái tục
Khi một kỳ đủ hạn, lãi được nhập vào gốc để tính kỳ tiếp theo.

### 5. So sánh vay cầm cố
Chỉ xuất hiện khi rút trước hạn.
Đây là mô hình tham khảo, không phải tư vấn tài chính.
"""
    )

with st.expander("🧮 Công thức tính"):
    st.latex(
        r"I = P \times \frac{r}{100} \times \frac{n}{365}"
    )
    st.markdown(
        """
Trong đó:

- **P** = tiền gốc
- **r** = lãi suất %/năm
- **n** = số ngày thực tế
- **I** = tiền lãi

**Tổng nhận = P + I**

Hệ thống đang sử dụng cơ sở **365 ngày/năm**.
"""
    )

st.caption(
    "🏦 Hệ thống mô phỏng tính tiền gửi tiết kiệm · "
    "Streamlit + Plotly · Giao diện Light/Dark"
)
