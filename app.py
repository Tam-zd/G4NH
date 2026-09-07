
import re
from datetime import date, timedelta

import pandas as pd
import plotly.graph_objects as go
import streamlit as st


# =========================================================
# CẤU HÌNH TRANG
# =========================================================
st.set_page_config(
    page_title="Tính tiền gửi tiết kiệm",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# =========================================================
# SESSION STATE
# =========================================================
if "theme_mode" not in st.session_state:
    st.session_state.theme_mode = "dark"

if "calculated" not in st.session_state:
    st.session_state.calculated = False


# =========================================================
# HÀM XỬ LÝ TIỀN
# =========================================================
def parse_smart_amount(value):
    """
    Cho phép nhập:
    500000000
    100,000,000
    50 triệu / 50tr
    1.5 tỷ / 1,5 tỷ
    200k
    """
    if value is None:
        return 0

    s = str(value).strip().lower()
    s = s.replace(" ", "").replace("_", "")

    if not s:
        return 0

    # Chuẩn hóa đơn vị
    multiplier = 1

    if s.endswith("tỷ") or s.endswith("ty"):
        multiplier = 1_000_000_000
        s = re.sub(r"(tỷ|ty)$", "", s)
    elif s.endswith("triệu") or s.endswith("tr"):
        multiplier = 1_000_000
        s = re.sub(r"(triệu|tr)$", "", s)
    elif s.endswith("nghìn") or s.endswith("ngan") or s.endswith("k"):
        multiplier = 1_000
        s = re.sub(r"(nghìn|ngan|k)$", "", s)

    # Xử lý 1,5 và 1.5 là số thập phân khi có đơn vị
    if multiplier != 1:
        if "," in s and "." not in s:
            s = s.replace(",", ".")
        else:
            s = s.replace(",", "")

        try:
            return float(s) * multiplier
        except ValueError:
            return 0

    # Không có đơn vị: coi dấu phẩy là phân cách hàng nghìn
    s = s.replace(",", "").replace(".", "") if s.replace(".", "").isdigit() else s

    try:
        return float(s)
    except ValueError:
        return 0


def money_vnd(value):
    return f"{value:,.0f} VNĐ"


def money_million(value):
    return f"{value / 1_000_000:,.2f} triệu"


def money_billion(value):
    return f"{value / 1_000_000_000:,.2f} tỷ"


# =========================================================
# TÍNH LÃI
# =========================================================
def simple_interest(principal, annual_rate, days):
    return principal * (1 + annual_rate / 100 * days / 365)


def compound_interest(principal, annual_rate, days):
    return principal * ((1 + annual_rate / 100 / 365) ** days)


def calculate_deposit(principal, rate, days, compound=False):
    if compound:
        total = compound_interest(principal, rate, days)
    else:
        total = simple_interest(principal, rate, days)

    interest = total - principal
    return total, interest


# =========================================================
# CSS THEO LIGHT / DARK
# QUAN TRỌNG:
# - Không hard-code chữ trắng cho mọi nền.
# - Container có key khác nhau theo theme để CSS chính xác.
# =========================================================
mode = st.session_state.theme_mode
root_key = "app_root_dark" if mode == "dark" else "app_root_light"

if mode == "dark":
    BG = "#071525"
    PANEL = "#0d1d31"
    PANEL2 = "#10243a"
    TEXT = "#f5f7fb"
    MUTED = "#aebbc9"
    BORDER = "#24384e"
    INPUT_BG = "#f4f6f8"
    INPUT_TEXT = "#111827"
    BUTTON_BG = "#ffffff"
    BUTTON_TEXT = "#172033"
    ACCENT = "#38d39f"
    SOFT = "#142b43"
else:
    BG = "#f4f7fb"
    PANEL = "#ffffff"
    PANEL2 = "#eef3f8"
    TEXT = "#172033"
    MUTED = "#596579"
    BORDER = "#d6dee8"
    INPUT_BG = "#ffffff"
    INPUT_TEXT = "#172033"
    BUTTON_BG = "#ffffff"
    BUTTON_TEXT = "#172033"
    ACCENT = "#087f5b"
    SOFT = "#e9f7f1"


st.markdown(
    f"""
    <style>
    /* =====================================================
       BIẾN MÀU
       ===================================================== */
    :root {{
        --app-bg: {BG};
        --panel: {PANEL};
        --panel-2: {PANEL2};
        --text: {TEXT};
        --muted: {MUTED};
        --border: {BORDER};
        --input-bg: {INPUT_BG};
        --input-text: {INPUT_TEXT};
        --button-bg: {BUTTON_BG};
        --button-text: {BUTTON_TEXT};
        --accent: {ACCENT};
        --soft: {SOFT};
    }}

    .stApp {{
        background: var(--app-bg);
    }}

    .block-container {{
        max-width: 1450px;
        padding-top: 1.5rem;
    }}

    /* =========================
       TEXT CHUNG
       ========================= */
    .st-key-{root_key} p,
    .st-key-{root_key} label,
    .st-key-{root_key} span,
    .st-key-{root_key} div,
    .st-key-{root_key} small {{
        color: var(--text);
    }}

    .st-key-{root_key} .muted {{
        color: var(--muted) !important;
    }}

    /* Không cho markdown/code nhỏ bị trắng trên nền sáng */
    .st-key-{root_key} [data-testid="stMarkdownContainer"] {{
        color: var(--text);
    }}

    /* =========================
       HEADER
       ========================= */
    .hero {{
        background: linear-gradient(135deg, var(--panel-2), var(--panel));
        border: 1px solid var(--border);
        border-radius: 24px;
        padding: 24px 28px;
        margin-bottom: 18px;
    }}

    .hero h1 {{
        margin: 0;
        color: var(--text) !important;
        font-size: 30px;
        font-weight: 800;
    }}

    .hero p {{
        color: var(--muted) !important;
        margin: 8px 0 0 0;
        font-size: 15px;
    }}

    .status {{
        display: inline-block;
        border: 1px solid var(--accent);
        color: var(--accent) !important;
        background: color-mix(in srgb, var(--accent) 12%, transparent);
        border-radius: 999px;
        padding: 6px 13px;
        font-size: 12px;
        font-weight: 800;
        margin-bottom: 10px;
    }}

    /* =========================
       PANEL
       ========================= */
    .panel {{
        background: var(--panel);
        border: 1px solid var(--border);
        border-radius: 18px;
        padding: 20px;
        margin-bottom: 18px;
    }}

    .panel-title {{
        color: var(--text) !important;
        font-size: 17px;
        font-weight: 800;
        margin-bottom: 12px;
    }}

    /* =========================
       INPUT
       ========================= */
    .st-key-{root_key} input,
    .st-key-{root_key} textarea {{
        background: var(--input-bg) !important;
        color: var(--input-text) !important;
        -webkit-text-fill-color: var(--input-text) !important;
        border: 1px solid var(--border) !important;
        border-radius: 9px !important;
    }}

    .st-key-{root_key} input::placeholder,
    .st-key-{root_key} textarea::placeholder {{
        color: #718096 !important;
        opacity: 1 !important;
        -webkit-text-fill-color: #718096 !important;
    }}

    .st-key-{root_key} input:focus,
    .st-key-{root_key} textarea:focus {{
        border-color: var(--accent) !important;
        box-shadow: 0 0 0 1px var(--accent) !important;
    }}

    /* Slider */
    .st-key-{root_key} [data-testid="stSlider"] {{
        color: var(--text);
    }}

    .st-key-{root_key} [data-testid="stSlider"] [role="slider"] {{
        background: var(--accent) !important;
    }}

    /* =========================
       BUTTON
       ========================= */
    .st-key-{root_key} button {{
        background: var(--button-bg) !important;
        color: var(--button-text) !important;
        -webkit-text-fill-color: var(--button-text) !important;
        border: 1px solid var(--border) !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
    }}

    .st-key-{root_key} button p,
    .st-key-{root_key} button span,
    .st-key-{root_key} button div {{
        color: var(--button-text) !important;
        -webkit-text-fill-color: var(--button-text) !important;
    }}

    .st-key-{root_key} button:hover {{
        border-color: var(--accent) !important;
        color: var(--button-text) !important;
    }}

    /* Nút primary */
    .st-key-{root_key} button[kind="primary"] {{
        background: var(--accent) !important;
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        border-color: var(--accent) !important;
    }}

    .st-key-{root_key} button[kind="primary"] p,
    .st-key-{root_key} button[kind="primary"] span {{
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
    }}

    /* =========================
       SELECTBOX / DATE
       ========================= */
    .st-key-{root_key} [data-baseweb="select"] > div {{
        background: var(--input-bg) !important;
        color: var(--input-text) !important;
        border-color: var(--border) !important;
    }}

    .st-key-{root_key} [data-baseweb="select"] span {{
        color: var(--input-text) !important;
    }}

    /* =========================
       EXPANDER
       ========================= */
    .st-key-{root_key} [data-testid="stExpander"] {{
        background: var(--panel);
        border: 1px solid var(--border);
        border-radius: 12px;
    }}

    .st-key-{root_key} [data-testid="stExpander"] summary,
    .st-key-{root_key} [data-testid="stExpander"] summary p {{
        color: var(--text) !important;
    }}

    /* =========================
       TABS
       ========================= */
    .st-key-{root_key} button[data-baseweb="tab"] {{
        background: transparent !important;
        color: var(--muted) !important;
        border: none !important;
        -webkit-text-fill-color: var(--muted) !important;
    }}

    .st-key-{root_key} button[data-baseweb="tab"] p,
    .st-key-{root_key} button[data-baseweb="tab"] span {{
        color: var(--muted) !important;
        -webkit-text-fill-color: var(--muted) !important;
    }}

    .st-key-{root_key} button[data-baseweb="tab"][aria-selected="true"],
    .st-key-{root_key} button[data-baseweb="tab"][aria-selected="true"] p,
    .st-key-{root_key} button[data-baseweb="tab"][aria-selected="true"] span {{
        color: var(--accent) !important;
        -webkit-text-fill-color: var(--accent) !important;
    }}

    /* =========================
       DATAFRAME
       ========================= */
    .st-key-{root_key} [data-testid="stDataFrame"] {{
        border: 1px solid var(--border);
        border-radius: 10px;
        overflow: hidden;
    }}

    /* =========================
       ALERT / INFO / SUCCESS
       ========================= */
    .st-key-{root_key} [data-testid="stAlert"] {{
        border-radius: 12px;
    }}

    /* =========================
       KPI
       ========================= */
    .kpi {{
        background: var(--panel-2);
        border: 1px solid var(--border);
        border-radius: 15px;
        padding: 16px;
        min-height: 115px;
    }}

    .kpi-label {{
        color: var(--muted) !important;
        font-size: 13px;
        margin-bottom: 8px;
    }}

    .kpi-value {{
        color: var(--text) !important;
        font-size: 23px;
        font-weight: 800;
    }}

    .kpi-note {{
        color: var(--muted) !important;
        font-size: 12px;
        margin-top: 5px;
    }}

    /* =========================
       HINT CHIPS
       ========================= */
    .hint {{
        display: inline-block;
        padding: 3px 7px;
        margin-right: 4px;
        margin-top: 3px;
        background: var(--soft);
        border: 1px solid var(--border);
        border-radius: 5px;
        color: var(--text) !important;
        font-size: 11px;
        font-family: monospace;
    }}

    /* =========================
       MOBILE
       ========================= */
    @media (max-width: 800px) {{
        .block-container {{
            padding-left: 0.7rem;
            padding-right: 0.7rem;
        }}

        .hero h1 {{
            font-size: 23px;
        }}

        .panel {{
            padding: 15px;
        }}
    }}
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# TOGGLE THEME
# =========================================================
top_left, top_right = st.columns([6, 1])

with top_right:
    theme_label = "☀️ Sáng" if mode == "dark" else "🌙 Tối"
    if st.button(theme_label, key="theme_toggle"):
        st.session_state.theme_mode = "light" if mode == "dark" else "dark"
        st.rerun()


# =========================================================
# ROOT CONTAINER
# =========================================================
with st.container(key=root_key):

    # =====================================================
    # HEADER
    # =====================================================
    st.markdown(
        """
        <div class="hero">
            <div class="status">✓ HỆ THỐNG ĐANG HOẠT ĐỘNG</div>
            <h1>🏦 Trung tâm tính tiền gửi tiết kiệm</h1>
            <p>
                Mô phỏng gốc – lãi – đáo hạn – rút trước hạn – tái tục
                và phân tích phương án tiền gửi.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # =====================================================
    # 2 CỘT CHÍNH
    # =====================================================
    left, right = st.columns([1.15, 0.85], gap="large")

    # =====================================================
    # BẢNG ĐIỀU KHIỂN
    # =====================================================
    with left:
        st.markdown('<div class="panel-title">🧮 BẢNG ĐIỀU KHIỂN</div>', unsafe_allow_html=True)

        st.markdown("### 💰 Số tiền gửi")

        amount_text = st.text_input(
            "Số tiền",
            value="100,000,000",
            label_visibility="collapsed",
            key="amount_text",
            help="Có thể nhập 100000000, 100 triệu, 100tr, 1.5 tỷ, 200k...",
        )

        amount = parse_smart_amount(amount_text)

        st.markdown(
            """
            <div class="muted">
                Nhập:
                <span class="hint">500000000</span>
                <span class="hint">500 triệu</span>
                <span class="hint">1.5 tỷ</span>
                <span class="hint">200k</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        amount_slider = st.slider(
            "Điều chỉnh số tiền",
            min_value=1_000_000,
            max_value=10_000_000_000,
            value=max(1_000_000, min(int(amount or 100_000_000), 10_000_000_000)),
            step=1_000_000,
            format="%,d VNĐ",
            key="amount_slider",
        )

        # Nếu người dùng nhập text khác giá trị slider, ưu tiên text.
        if amount > 0:
            selected_amount = amount
        else:
            selected_amount = amount_slider

        st.caption(
            f"Đang chọn: {money_vnd(selected_amount)} "
            f"(≈ {selected_amount / 1_000_000:,.2f} triệu)"
        )

        st.markdown("**Chọn nhanh**")

        quick_cols = st.columns(3)
        quick_values = [
            ("50 triệu", 50_000_000),
            ("100 triệu", 100_000_000),
            ("200 triệu", 200_000_000),
            ("500 triệu", 500_000_000),
            ("1 tỷ", 1_000_000_000),
            ("2 tỷ", 2_000_000_000),
        ]

        for idx, (label, value) in enumerate(quick_values):
            with quick_cols[idx % 3]:
                if st.button(label, key=f"quick_{idx}", use_container_width=True):
                    st.session_state.amount_text = f"{value:,}"
                    st.rerun()

        st.markdown("**Điều chỉnh nhanh**")

        adjust_cols = st.columns(3)
        adjustments = [
            ("＋ 1tr", 1_000_000),
            ("＋ 10tr", 10_000_000),
            ("＋ 50tr", 50_000_000),
            ("－ 1tr", -1_000_000),
            ("－ 10tr", -10_000_000),
            ("－ 50tr", -50_000_000),
        ]

        for idx, (label, value) in enumerate(adjustments):
            with adjust_cols[idx % 3]:
                if st.button(label, key=f"adjust_{idx}", use_container_width=True):
                    new_value = max(1_000_000, selected_amount + value)
                    st.session_state.amount_text = f"{new_value:,}"
                    st.rerun()

        st.divider()

        st.markdown("### 📈 Lãi suất")

        rate = st.number_input(
            "Lãi suất (%/năm)",
            min_value=0.0,
            max_value=30.0,
            value=5.0,
            step=0.01,
            format="%.2f",
        )

        st.markdown("### 📅 Thời gian gửi")

        col_date, col_days = st.columns(2)

        with col_date:
            start_date = st.date_input(
                "Ngày gửi",
                value=date.today(),
                format="DD/MM/YYYY",
            )

        with col_days:
            days = st.number_input(
                "Số ngày gửi",
                min_value=1,
                max_value=3650,
                value=92,
                step=1,
            )

        end_date = start_date + timedelta(days=int(days))

        st.info(
            f"Ngày đáo hạn dự kiến: **{end_date.strftime('%d/%m/%Y')}**"
        )

        st.markdown("### ⚙️ Phương thức tính")

        calculation_type = st.radio(
            "Phương thức",
            [
                "So sánh lãi đơn và lãi kép",
                "Lãi đơn",
                "Lãi kép",
            ],
            horizontal=True,
        )

        st.divider()

        calculate_button = st.button(
            "🚀 TÍNH TOÁN NGAY",
            type="primary",
            use_container_width=True,
            key="calculate_button",
        )

        if calculate_button:
            st.session_state.calculated = True

    # =====================================================
    # KẾT QUẢ
    # =====================================================
    with right:
        st.markdown('<div class="panel-title">📊 KẾT QUẢ TÍNH TOÁN</div>', unsafe_allow_html=True)

        if not st.session_state.calculated:
            st.info("Nhập thông tin bên trái rồi bấm **🚀 TÍNH TOÁN NGAY**.")
        else:
            principal = selected_amount
            total_simple, interest_simple = calculate_deposit(
                principal, rate, int(days), compound=False
            )
            total_compound, interest_compound = calculate_deposit(
                principal, rate, int(days), compound=True
            )

            if calculation_type == "Lãi đơn":
                total_main = total_simple
                interest_main = interest_simple
                method_name = "Lãi đơn"
            elif calculation_type == "Lãi kép":
                total_main = total_compound
                interest_main = interest_compound
                method_name = "Lãi kép"
            else:
                total_main = total_compound
                interest_main = interest_compound
                method_name = "So sánh"

            if calculation_type == "So sánh lãi đơn và lãi kép":
                c1, c2 = st.columns(2)

                with c1:
                    st.markdown(
                        f"""
                        <div class="kpi">
                            <div class="kpi-label">LÃI ĐƠN</div>
                            <div class="kpi-value">{total_simple/1_000_000:,.2f} triệu</div>
                            <div class="kpi-note">Tiền lãi: {interest_simple/1_000_000:,.2f} triệu</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                with c2:
                    st.markdown(
                        f"""
                        <div class="kpi">
                            <div class="kpi-label">LÃI KÉP</div>
                            <div class="kpi-value">{total_compound/1_000_000:,.2f} triệu</div>
                            <div class="kpi-note">Tiền lãi: {interest_compound/1_000_000:,.2f} triệu</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
            else:
                st.markdown(
                    f"""
                    <div class="kpi">
                        <div class="kpi-label">{method_name.upper()}</div>
                        <div class="kpi-value">{total_main/1_000_000:,.2f} triệu</div>
                        <div class="kpi-note">Tiền lãi: {interest_main/1_000_000:,.2f} triệu</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            st.write("")

            k1, k2, k3 = st.columns(3)

            with k1:
                st.metric("Gốc", money_million(principal))

            with k2:
                st.metric("Tiền lãi", money_million(interest_main))

            with k3:
                st.metric("Tổng nhận", money_million(total_main))

            st.success(
                f"📅 Gửi từ **{start_date.strftime('%d/%m/%Y')}** "
                f"đến **{end_date.strftime('%d/%m/%Y')}** — {days} ngày."
            )

            st.download_button(
                "📥 Xuất CSV",
                data=pd.DataFrame(
                    [{
                        "Số tiền gửi": principal,
                        "Lãi suất (%/năm)": rate,
                        "Ngày gửi": start_date.strftime("%d/%m/%Y"),
                        "Ngày đáo hạn": end_date.strftime("%d/%m/%Y"),
                        "Số ngày": days,
                        "Phương thức": method_name,
                        "Tiền lãi": interest_main,
                        "Tổng tiền nhận": total_main,
                    }]
                ).to_csv(index=False).encode("utf-8-sig"),
                file_name="ket_qua_tinh_lai.csv",
                mime="text/csv",
                use_container_width=True,
            )

    # =====================================================
    # PHÂN TÍCH / BIỂU ĐỒ
    # =====================================================
    if st.session_state.calculated:
        st.divider()

        tab1, tab2, tab3 = st.tabs(
            ["📈 Biểu đồ", "🧮 Công thức", "📋 Bảng chi tiết"]
        )

        with tab1:
            principal = selected_amount
            total_simple, interest_simple = calculate_deposit(
                principal, rate, int(days), False
            )
            total_compound, interest_compound = calculate_deposit(
                principal, rate, int(days), True
            )

            chart_df = pd.DataFrame(
                {
                    "Phương thức": ["Lãi đơn", "Lãi kép"],
                    "Tổng nhận": [total_simple, total_compound],
                    "Tiền lãi": [interest_simple, interest_compound],
                }
            )

            fig = go.Figure()

            fig.add_trace(
                go.Bar(
                    x=chart_df["Phương thức"],
                    y=chart_df["Tổng nhận"],
                    name="Tổng tiền nhận",
                    text=[f"{x/1_000_000:,.2f} triệu" for x in chart_df["Tổng nhận"]],
                    textposition="auto",
                )
            )

            fig.add_trace(
                go.Bar(
                    x=chart_df["Phương thức"],
                    y=chart_df["Tiền lãi"],
                    name="Tiền lãi",
                    text=[f"{x/1_000_000:,.2f} triệu" for x in chart_df["Tiền lãi"]],
                    textposition="auto",
                )
            )

            fig.update_layout(
                barmode="group",
                height=420,
                margin=dict(l=10, r=10, t=30, b=10),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color=TEXT),
                legend=dict(font=dict(color=TEXT)),
                xaxis=dict(
                    title="Phương thức",
                    tickfont=dict(color=TEXT),
                    title_font=dict(color=TEXT),
                ),
                yaxis=dict(
                    title="VNĐ",
                    tickfont=dict(color=TEXT),
                    title_font=dict(color=TEXT),
                    gridcolor=BORDER,
                ),
            )

            st.plotly_chart(fig, use_container_width=True)

        with tab2:
            st.markdown("### 🧮 Công thức lãi đơn")
            st.code(
                "A = P × (1 + r × n / 365)",
                language="text",
            )

            st.markdown("### 🧮 Công thức lãi kép")
            st.code(
                "A = P × (1 + r / 365)ⁿ",
                language="text",
            )

            st.markdown(
                f"""
                **Trong đó:**
                - `P` = {money_vnd(selected_amount)}
                - `r` = {rate:.2f}%/năm
                - `n` = {days} ngày
                - Quy ước: **365 ngày/năm**
                """
            )

        with tab3:
            detail_df = pd.DataFrame(
                [
                    {
                        "Phương thức": "Lãi đơn",
                        "Tiền gốc": principal,
                        "Tiền lãi": interest_simple,
                        "Tổng nhận": total_simple,
                    },
                    {
                        "Phương thức": "Lãi kép",
                        "Tiền gốc": principal,
                        "Tiền lãi": interest_compound,
                        "Tổng nhận": total_compound,
                    },
                ]
            )

            st.dataframe(
                detail_df.style.format(
                    {
                        "Tiền gốc": "{:,.0f}",
                        "Tiền lãi": "{:,.0f}",
                        "Tổng nhận": "{:,.0f}",
                    }
                ),
                use_container_width=True,
                hide_index=True,
            )

    # =====================================================
    # FOOTER
    # =====================================================
    st.markdown(
        """
        <div class="muted" style="text-align:center; padding:20px 0 5px;">
            🏦 Hệ thống mô phỏng tiền gửi tiết kiệm · Streamlit + Plotly ·
            Giao diện Light/Dark
        </div>
        """,
        unsafe_allow_html=True,
    )
