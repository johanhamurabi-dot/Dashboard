
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# ============================================================
# WRAP v11 - Water Research Analytics Platform
# Dalhousie Water Research
# Traditional Jar Tests + Dose Response + Removal + Marginal Gain + Reviewer Updates
# Future Brigit / MANTECH Robot Integration
# ============================================================

st.set_page_config(
    page_title="WRAP | Dalhousie Water Research",
    layout="wide",
    initial_sidebar_state="expanded"
)

VALID_USERS = {
    "fj415321@dal.ca": "JohanHamurabi0727",
    "riley.gray@dal.ca": "Cheema-2002",
}

PLOTLY_CONFIG = {
    "displaylogo": False,
    "modeBarButtonsToAdd": ["toImage"],
    "toImageButtonOptions": {
        "format": "png",
        "filename": "WRAP_chart",
        "height": 720,
        "width": 1200,
        "scale": 2
    }
}

# -------------------- STYLE --------------------
st.markdown("""
<style>
/* ---------- GLOBAL LIGHT UI LOCK ---------- */
.stApp {
    background: linear-gradient(180deg, #f7f8fb 0%, #eef1f5 100%) !important;
    color: #111111 !important;
}

html, body, [class*="css"] {
    color: #111111 !important;
}

/* ---------- SIDEBAR ---------- */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #030303 0%, #141a23 100%) !important;
}

[data-testid="stSidebar"] * {
    color: white !important;
}

/* ---------- MAIN TEXT ---------- */
h1, h2, h3, h4, h5, h6, p, label, span, div {
    color: #111111;
}

[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] div {
    color: white !important;
}

/* ---------- INPUTS / SELECTBOXES / MULTISELECT / DATE INPUT ---------- */
.stTextInput input,
.stNumberInput input,
.stDateInput input,
.stTextArea textarea,
div[data-baseweb="input"] input,
div[data-baseweb="select"] > div,
div[data-baseweb="popover"] div,
div[data-baseweb="menu"] div,
div[data-baseweb="calendar"] *,
div[data-baseweb="tag"] {
    background-color: #ffffff !important;
    color: #111111 !important;
    -webkit-text-fill-color: #111111 !important;
    border-color: #d0d7de !important;
}

div[data-baseweb="select"] span,
div[data-baseweb="select"] svg,
div[data-baseweb="input"] svg {
    color: #111111 !important;
    fill: #111111 !important;
}

div[data-baseweb="tag"] span {
    color: #111111 !important;
}

input::placeholder {
    color: #6b7280 !important;
    opacity: 1 !important;
}

/* ---------- FILE UPLOADER ---------- */
[data-testid="stFileUploader"] section {
    background: #ffffff !important;
    color: #111111 !important;
    border: 1px dashed #9ca3af !important;
}

[data-testid="stFileUploader"] * {
    color: #111111 !important;
}

/* ---------- BUTTONS ---------- */
.stButton button,
.stDownloadButton button {
    background-color: #FFD200 !important;
    color: #111111 !important;
    border: 1px solid #111111 !important;
    font-weight: 700 !important;
    border-radius: 10px !important;
}

.stButton button:hover,
.stDownloadButton button:hover {
    background-color: #f4c300 !important;
    color: #111111 !important;
}

/* ---------- ALERT BOX READABILITY ---------- */
.stAlert,
[data-testid="stAlert"] {
    background-color: #ffffff !important;
    color: #111111 !important;
    border-radius: 12px !important;
}

/* ---------- CARDS ---------- */
.metric-card {
    background: white;
    padding: 20px;
    border-radius: 18px;
    border-left: 7px solid #FFD200;
    box-shadow: 0 4px 14px rgba(0,0,0,0.08);
}

.metric-card-blue {
    background: white;
    padding: 20px;
    border-radius: 18px;
    border-left: 7px solid #1f77b4;
    box-shadow: 0 4px 14px rgba(0,0,0,0.08);
}

.metric-card-green {
    background: white;
    padding: 20px;
    border-radius: 18px;
    border-left: 7px solid #2e7d32;
    box-shadow: 0 4px 14px rgba(0,0,0,0.08);
}

.metric-card-red {
    background: white;
    padding: 20px;
    border-radius: 18px;
    border-left: 7px solid #c0392b;
    box-shadow: 0 4px 14px rgba(0,0,0,0.08);
}

.big-number {
    font-size: 30px;
    font-weight: 800;
    color: #111111 !important;
}

.small-label {
    font-size: 14px;
    color: #666666 !important;
}

.info-box {
    background: white;
    padding: 18px;
    border-radius: 16px;
    border-left: 6px solid #FFD200;
    box-shadow: 0 3px 12px rgba(0,0,0,0.06);
}

.report-box {
    background: #ffffff;
    padding: 24px;
    border-radius: 18px;
    box-shadow: 0 4px 18px rgba(0,0,0,0.08);
    border-top: 6px solid #FFD200;
}
</style>
""", unsafe_allow_html=True)

# -------------------- SESSION --------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_email" not in st.session_state:
    st.session_state.user_email = None
if "traditional_df" not in st.session_state:
    st.session_state.traditional_df = None
if "robot_df" not in st.session_state:
    st.session_state.robot_df = None

# Reset chart counter on every rerun.
# This prevents StreamlitDuplicateElementId when multiple Plotly charts look similar.
st.session_state["_plot_counter"] = 0

# -------------------- HELPERS --------------------
def render_plot(fig, key_prefix="plot"):
    """Render Plotly charts with unique keys to avoid StreamlitDuplicateElementId on Cloud."""
    st.session_state["_plot_counter"] = st.session_state.get("_plot_counter", 0) + 1
    unique_key = f"{key_prefix}_{st.session_state['_plot_counter']}"
    st.plotly_chart(
        apply_plot_theme(fig),
        use_container_width=True,
        config=PLOTLY_CONFIG,
        key=unique_key
    )

def apply_plot_theme(fig):
    """Force charts to remain readable even when Streamlit is in dark mode."""
    fig.update_layout(
        template="plotly_white",
        font=dict(color="#111111", size=13),
        title_font=dict(color="#111111", size=20),
        legend=dict(font=dict(color="#111111")),
        plot_bgcolor="#ffffff",
        paper_bgcolor="#ffffff",
        xaxis=dict(
            color="#111111",
            title_font=dict(color="#111111"),
            tickfont=dict(color="#111111"),
            gridcolor="#d9dee7",
            zerolinecolor="#aab2bd",
            linecolor="#111111"
        ),
        yaxis=dict(
            color="#111111",
            title_font=dict(color="#111111"),
            tickfont=dict(color="#111111"),
            gridcolor="#d9dee7",
            zerolinecolor="#aab2bd",
            linecolor="#111111"
        ),
        coloraxis_colorbar=dict(
            tickfont=dict(color="#111111"),
            title_font=dict(color="#111111")
        )
    )
    return fig

def clean_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.replace(" ", "_")
        .str.replace("-", "_")
    )
    # Remove useless index column from Excel exports
    if "Unnamed:_0" in df.columns:
        df = df.drop(columns=["Unnamed:_0"])
    if "Unnamed:_0.1" in df.columns:
        df = df.drop(columns=["Unnamed:_0.1"])
    return df

def add_removal_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds removal percentage columns for available parameters.
    Baseline is the raw water sample from the same test/date/pH group.
    If no explicit raw sample exists, it uses alum_dose == 0.
    """
    if df is None or df.empty:
        return df

    df = df.copy()

    parameter_cols = [
        "uv254", "doc", "toc", "turb", "true_colour", "suva",
        "tot_al_ppm", "diss_al_ppm"
    ]

    available_params = [c for c in parameter_cols if c in df.columns]

    if not available_params:
        return df

    group_cols = [c for c in ["sample_date", "analysis_date", "test", "aim_ph"] if c in df.columns]
    if not group_cols:
        group_cols = ["__all__"]
        df["__all__"] = "all"

    for param in available_params:
        removal_col = f"{param}_removal_percent"
        df[removal_col] = pd.NA

    for _, group in df.groupby(group_cols, dropna=False):
        raw_rows = pd.DataFrame()

        if "sample_type" in group.columns:
            raw_rows = group[group["sample_type"].astype(str).str.lower().str.contains("raw", na=False)]

        if raw_rows.empty and "sample" in group.columns:
            raw_rows = group[group["sample"].astype(str).str.lower().str.contains("raw", na=False)]

        if raw_rows.empty and "alum_dose" in group.columns:
            raw_rows = group[group["alum_dose"].fillna(-999999) == 0]

        if raw_rows.empty:
            continue

        idx = group.index

        for param in available_params:
            if raw_rows[param].dropna().empty:
                continue

            raw_value = raw_rows[param].dropna().iloc[0]

            if pd.isna(raw_value) or raw_value == 0:
                continue

            removal_col = f"{param}_removal_percent"
            df.loc[idx, removal_col] = ((raw_value - df.loc[idx, param]) / raw_value) * 100

    if "__all__" in df.columns:
        df = df.drop(columns=["__all__"])

    for param in available_params:
        removal_col = f"{param}_removal_percent"
        df[removal_col] = pd.to_numeric(df[removal_col], errors="coerce")

    return df

def load_file(uploaded_file):
    try:
        if uploaded_file.name.lower().endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        elif uploaded_file.name.lower().endswith((".xlsx", ".xls")):
            df = pd.read_excel(uploaded_file)
        else:
            st.error("Unsupported file type. Please upload CSV or Excel.")
            return None

        df = clean_columns(df)

        for col in ["sample_date", "analysis_date", "Date_Sampled", "Date_Analyzed"]:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors="coerce")

        possible_numeric_cols = [
            "test", "aim_ph", "alum_dose", "true_colour", "uv254", "turb", "ph",
            "toc", "doc", "suva", "Total_al", "Dissolved_Al", "tot_al_ppm",
            "diss_al_ppm", "THAA", "TTHM", "THM", "pecod", "PeCOD",
            "conductivity", "temperature", "colour", "apparent_colour",
            "zeta_mean", "zeta", "alkalinity", "Talk", "Mn", "Fe", "Al",
            "raw_alkalinity", "raw_uv254", "month"
        ]

        for col in possible_numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        df = add_removal_columns(df)
        df = add_ph_bin_column(df)

        return df

    except Exception as e:
        st.error(f"Error loading file: {e}")
        return None

def numeric_columns(df):
    if df is None:
        return []
    return df.select_dtypes(include="number").columns.tolist()


def add_ph_bin_column(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create broader measured-pH bins requested by reviewers.

    Bins:
    - <5.6
    - 5.6-5.9999
    - 6.0-6.3999
    - 6.4-6.7999
    - >=6.8
    """
    if df is None or "ph" not in df.columns:
        return df

    df = df.copy()
    ph_numeric = pd.to_numeric(df["ph"], errors="coerce")

    def label_ph_bin(value):
        if pd.isna(value):
            return "Unknown"
        if value < 5.6:
            return "<5.6"
        if value < 6.0:
            return "5.6-5.9999"
        if value < 6.4:
            return "6.0-6.3999"
        if value < 6.8:
            return "6.4-6.7999"
        return ">=6.8"

    df["ph_bin"] = ph_numeric.apply(label_ph_bin)
    return df


def available_color_columns(df):
    """Preferred color choices for plots. Actual measured pH is prioritized over target pH."""
    preferred = [
        "ph",
        "ph_bin",
        "aim_ph",
        "test",
        "sample",
        "sample_type",
        "sample_date",
        "analysis_date",
        "alum_dose"
    ]
    return ["None"] + [c for c in preferred if c in df.columns]


def default_color_index(options, preferred="ph_bin"):
    if preferred in options:
        return options.index(preferred)
    if "ph" in options:
        return options.index("ph")
    if "aim_ph" in options:
        return options.index("aim_ph")
    return 0


def prepare_plot_categories(df: pd.DataFrame) -> pd.DataFrame:
    """Sort pH bins and dates in a readable order for legends and axes."""
    if df is None:
        return df

    df = df.copy()

    if "ph_bin" in df.columns:
        ph_order = ["<5.6", "5.6-5.9999", "6.0-6.3999", "6.4-6.7999", ">=6.8", "Unknown"]
        df["ph_bin"] = pd.Categorical(df["ph_bin"], categories=ph_order, ordered=True)

    for date_col in ["sample_date", "analysis_date"]:
        if date_col in df.columns:
            converted = pd.to_datetime(df[date_col], errors="coerce")
            df[date_col] = converted.dt.strftime("%Y-%m-%d")
            df[date_col] = df[date_col].fillna("Unknown")

    return df


def duplicate_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Detect repeated experimental points at the same alum dose and condition."""
    if df is None or df.empty or "alum_dose" not in df.columns:
        return pd.DataFrame()

    group_cols = [c for c in ["sample_date", "analysis_date", "test", "aim_ph", "ph_bin", "alum_dose"] if c in df.columns]

    if len(group_cols) < 2:
        return pd.DataFrame()

    dup = (
        df.groupby(group_cols, dropna=False)
        .size()
        .reset_index(name="point_count")
        .query("point_count > 1")
        .sort_values("point_count", ascending=False)
    )

    return dup


def compute_optimal_point(df: pd.DataFrame, parameter: str):
    """
    Pick an optimal point using removal and marginal gain rather than simply
    selecting the lowest final concentration.
    """
    if df is None or df.empty or "alum_dose" not in df.columns or parameter not in df.columns:
        return None, pd.DataFrame()

    removal_col = f"{parameter}_removal_percent"
    if removal_col not in df.columns:
        return None, pd.DataFrame()

    work = df.dropna(subset=["alum_dose", parameter, removal_col]).copy()

    if work.empty:
        return None, pd.DataFrame()

    grouped = (
        work.groupby("alum_dose", as_index=False)
        .agg(
            mean_value=(parameter, "mean"),
            mean_removal=(removal_col, "mean"),
            n=("alum_dose", "count")
        )
        .sort_values("alum_dose")
    )

    if grouped.empty:
        return None, grouped

    grouped["marginal_gain"] = grouped["mean_removal"].diff()
    grouped["dose_step"] = grouped["alum_dose"].diff()
    grouped["gain_per_mg"] = grouped["marginal_gain"] / grouped["dose_step"]

    max_removal = grouped["mean_removal"].max()
    candidates = grouped[grouped["mean_removal"] >= 0.95 * max_removal].copy()

    if candidates.empty:
        best = grouped.loc[grouped["mean_removal"].idxmax()]
    else:
        best = candidates.sort_values(["alum_dose", "mean_removal"], ascending=[True, False]).iloc[0]

    return best, grouped


def metric_card(value, label, style="metric-card"):
    st.markdown(f"<div class='{style}'>", unsafe_allow_html=True)
    st.markdown(f"<div class='big-number'>{value}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='small-label'>{label}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

def dataset_overview(df):
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card(len(df), "📄 Records", "metric-card")
    with c2:
        metric_card(df["test"].nunique() if "test" in df.columns else "N/A", "🧪 Jar Tests", "metric-card-blue")
    with c3:
        metric_card(df["aim_ph"].nunique() if "aim_ph" in df.columns else "N/A", "⚗️ Target pH Levels", "metric-card-green")
    with c4:
        metric_card(f"{df['alum_dose'].max()} mg/L" if "alum_dose" in df.columns else "N/A", "💧 Max Alum Dose", "metric-card-red")

def filter_traditional_data(df):
    filtered = df.copy()
    st.subheader("🔎 Filters")
    f1, f2, f3 = st.columns(3)

    with f1:
        if "sample_date" in filtered.columns and filtered["sample_date"].notna().any():
            min_date = filtered["sample_date"].min().date()
            max_date = filtered["sample_date"].max().date()
            date_range = st.date_input(
                "Sample Date Range",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date
            )
            if isinstance(date_range, tuple) and len(date_range) == 2:
                start_date, end_date = date_range
                filtered = filtered[
                    (filtered["sample_date"].dt.date >= start_date) &
                    (filtered["sample_date"].dt.date <= end_date)
                ]
        else:
            st.info("No sample_date column found.")

    with f2:
        if "analysis_date" in filtered.columns and filtered["analysis_date"].notna().any():
            available = sorted(filtered["analysis_date"].dropna().dt.date.unique())
            selected = st.multiselect("Analysis Date", available, default=available)
            if selected:
                filtered = filtered[filtered["analysis_date"].dt.date.isin(selected)]
        else:
            st.info("No analysis_date column found.")

    with f3:
        if "test" in filtered.columns:
            tests = sorted(filtered["test"].dropna().unique())
            selected_tests = st.multiselect("Jar Test", tests, default=tests)
            if selected_tests:
                filtered = filtered[filtered["test"].isin(selected_tests)]
        else:
            st.info("No test column found.")

    st.caption("Additional analysis filters")

    f4, f5, f6 = st.columns(3)

    with f4:
        if "aim_ph" in filtered.columns:
            aim_values = sorted(filtered["aim_ph"].dropna().unique())
            selected_aim = st.multiselect("Target pH", aim_values, default=aim_values)
            if selected_aim:
                filtered = filtered[filtered["aim_ph"].isin(selected_aim)]

    with f5:
        if "ph_bin" in filtered.columns:
            ph_bins = sorted(filtered["ph_bin"].dropna().unique())
            selected_bins = st.multiselect("Measured pH bin", ph_bins, default=ph_bins)
            if selected_bins:
                filtered = filtered[filtered["ph_bin"].isin(selected_bins)]

    with f6:
        if "alum_dose" in filtered.columns:
            dose_values = sorted(filtered["alum_dose"].dropna().unique())
            selected_doses = st.multiselect("Coagulant dose (mg/L)", dose_values, default=dose_values)
            if selected_doses:
                filtered = filtered[filtered["alum_dose"].isin(selected_doses)]

    return filtered

def scatter_plot(df, x_col, y_col, title, y_label=None, color_col=None, use_line=False):
    if df is None or x_col not in df.columns or y_col not in df.columns:
        st.warning(f"Missing required columns for: {title}")
        return

    hover_cols = [
        c for c in [
            "test", "sample", "sample_type", "sample_date", "analysis_date", "aim_ph", "ph_bin",
            "ph", "alum_dose", "doc", "toc", "uv254", "turb", "true_colour",
            "suva", "Total_al", "Dissolved_Al", "tot_al_ppm", "diss_al_ppm",
            "uv254_removal_percent", "doc_removal_percent", "toc_removal_percent",
            "conductivity", "temperature", "zeta_mean"
        ] if c in df.columns
    ]

    plot_df = df.dropna(subset=[x_col, y_col]).copy()
    if plot_df.empty:
        st.warning(f"No data available for: {title}")
        return

    plot_df = prepare_plot_categories(plot_df)
    plot_df = plot_df.sort_values(x_col)

    category_orders = {
        "ph_bin": ["<5.6", "5.6-5.9999", "6.0-6.3999", "6.4-6.7999", ">=6.8", "Unknown"]
    }

    for date_col in ["sample_date", "analysis_date"]:
        if date_col in plot_df.columns:
            category_orders[date_col] = sorted(plot_df[date_col].dropna().unique().tolist())

    if use_line:
        fig = px.line(
            plot_df,
            x=x_col,
            y=y_col,
            color=color_col if color_col and color_col in plot_df.columns else None,
            markers=True,
            hover_data=hover_cols,
            title=title,
            category_orders=category_orders,
            labels={
                x_col: "Alum Dose (mg/L)" if x_col == "alum_dose" else x_col,
                y_col: y_label if y_label else y_col
            }
        )
        fig.update_traces(line=dict(width=3), marker=dict(size=10))
    else:
        fig = px.scatter(
            plot_df,
            x=x_col,
            y=y_col,
            color=color_col if color_col and color_col in plot_df.columns else None,
            hover_data=hover_cols,
            title=title,
            category_orders=category_orders,
            labels={
                x_col: "Alum Dose (mg/L)" if x_col == "alum_dose" else x_col,
                y_col: y_label if y_label else y_col
            }
        )
        fig.update_traces(marker=dict(size=12, opacity=0.85, line=dict(width=1, color="black")))

    fig.update_layout(
        height=440,
        plot_bgcolor="white",
        paper_bgcolor="white",
        title_font=dict(size=20),
        margin=dict(l=20, r=20, t=70, b=20)
    )
    render_plot(fig, "chart")

def heatmap(df, value_col, title, color_label, y_axis="aim_ph", x_axis="alum_dose"):
    required = [y_axis, x_axis, value_col]
    missing = [c for c in required if c not in df.columns]
    if missing:
        st.warning(f"Missing columns for {title}: {missing}")
        return

    plot_df = df.dropna(subset=[y_axis, x_axis, value_col]).copy()
    plot_df = prepare_plot_categories(plot_df)

    if plot_df.empty:
        st.warning(f"No data available for {title}.")
        return

    pivot = plot_df.pivot_table(values=value_col, index=y_axis, columns=x_axis, aggfunc="mean", observed=False)
    if y_axis == "ph_bin":
        desired_order = ["<5.6", "5.6-5.9999", "6.0-6.3999", "6.4-6.7999", ">=6.8", "Unknown"]
        pivot = pivot.reindex([x for x in desired_order if x in pivot.index])

    fig = px.imshow(
        pivot,
        aspect="auto",
        color_continuous_scale="Viridis",
        title=title,
        labels=dict(
            x="Coagulant Dose (mg/L)" if x_axis == "alum_dose" else x_axis,
            y="Measured pH Bin" if y_axis == "ph_bin" else ("Target pH" if y_axis == "aim_ph" else y_axis),
            color=color_label
        )
    )
    fig.update_layout(height=560, plot_bgcolor="white", paper_bgcolor="white")
    render_plot(fig, "chart")

def boxplot_ph_variability(df):
    if "aim_ph" not in df.columns or "ph" not in df.columns:
        st.warning("Columns 'aim_ph' and 'ph' are required for pH variability.")
        return

    temp = df.copy()
    temp["pH_deviation"] = temp["ph"] - temp["aim_ph"]

    fig = px.box(
        temp,
        x="aim_ph",
        y="pH_deviation",
        points="all",
        title="Operational Variability of pH",
        labels={"aim_ph": "Target pH", "pH_deviation": "Measured pH - Target pH"}
    )
    fig.update_layout(height=540, plot_bgcolor="white", paper_bgcolor="white")
    render_plot(fig, "chart")

def mean_error_plot(df, y_col, title, y_label):
    required = ["aim_ph", "alum_dose", y_col]
    missing = [c for c in required if c not in df.columns]
    if missing:
        st.warning(f"Missing columns for {title}: {missing}")
        return

    grouped = (
        df.groupby(["aim_ph", "alum_dose"], as_index=False)
        .agg(mean_value=(y_col, "mean"), sd_value=(y_col, "std"), n=(y_col, "count"))
    )
    grouped["sd_value"] = grouped["sd_value"].fillna(0)

    fig = px.scatter(
        grouped,
        x="alum_dose",
        y="mean_value",
        color="alum_dose",
        facet_col="aim_ph",
        facet_col_wrap=3,
        error_y="sd_value",
        title=title,
        labels={
            "alum_dose": "Alum Dose (mg/L)",
            "mean_value": y_label,
            "aim_ph": "Target pH"
        }
    )
    fig.update_traces(marker=dict(size=11, line=dict(width=1, color="black")))
    fig.update_layout(height=680, plot_bgcolor="white", paper_bgcolor="white")
    render_plot(fig, "chart")

def correlation_matrix(df):
    num = df.select_dtypes(include="number")
    if num.empty:
        st.warning("No numeric columns available.")
        return

    st.subheader("Correlation Scope")
    default_cols = [
        c for c in [
            "alum_dose", "aim_ph", "ph", "doc", "toc", "uv254",
            "uv254_removal_percent", "doc_removal_percent", "toc_removal_percent",
            "turb", "true_colour", "suva", "tot_al_ppm", "diss_al_ppm"
        ] if c in num.columns
    ]
    if not default_cols:
        default_cols = list(num.columns)

    selected_cols = st.multiselect(
        "Include / exclude variables in the correlation matrix",
        list(num.columns),
        default=default_cols
    )

    if len(selected_cols) < 2:
        st.warning("Select at least two numeric variables to generate the correlation matrix.")
        return

    corr = num[selected_cols].corr()

    fig = px.imshow(
        corr,
        text_auto=".2f",
        aspect="auto",
        color_continuous_scale="RdBu_r",
        zmin=-1,
        zmax=1,
        title="Correlation Matrix"
    )
    fig.update_layout(height=700)
    render_plot(fig, "chart")
    st.caption("The diagonal is always 1.0 because each variable is perfectly correlated with itself. Correlation does not prove causation.")

def get_parameter_catalog(df):
    all_specs = [
        ("doc", "DOC", "DOC (mg/L)"),
        ("doc_removal_percent", "DOC Removal", "DOC removal (%)"),
        ("toc", "TOC", "TOC (mg/L)"),
        ("toc_removal_percent", "TOC Removal", "TOC removal (%)"),
        ("uv254", "UV254", "UV254 (cm⁻¹)"),
        ("uv254_removal_percent", "UV254 Removal", "UV254 removal (%)"),
        ("turb", "Turbidity", "Turbidity (NTU)"),
        ("turb_removal_percent", "Turbidity Removal", "Turbidity removal (%)"),
        ("true_colour", "True Colour", "True Colour"),
        ("true_colour_removal_percent", "True Colour Removal", "True colour removal (%)"),
        ("suva", "SUVA", "SUVA"),
        ("suva_removal_percent", "SUVA Removal", "SUVA removal (%)"),
        ("ph", "Measured pH", "Measured pH"),
        ("tot_al_ppm", "Total Aluminum", "Total Al (mg/L)"),
        ("diss_al_ppm", "Dissolved Aluminum", "Dissolved Al (mg/L)"),
        ("raw_alkalinity", "Raw Alkalinity", "Raw alkalinity"),
        ("raw_uv254", "Raw UV254", "Raw UV254"),
    ]
    return [spec for spec in all_specs if spec[0] in df.columns]

def parameter_explorer(df):
    if df is None or df.empty:
        st.warning("No data available.")
        return

    if "alum_dose" not in df.columns:
        st.warning("Column 'alum_dose' is required for this plot.")
        return

    parameter_catalog = get_parameter_catalog(df)

    if not parameter_catalog:
        st.warning("No supported parameters found for plotting.")
        return

    label_to_spec = {label: (col, label, axis_label) for col, label, axis_label in parameter_catalog}

    c1, c2, c3 = st.columns(3)
    with c1:
        selected_label = st.selectbox("Select parameter to visualize", list(label_to_spec.keys()))
    with c2:
        chart_style = st.selectbox("Chart style", ["Points only", "Dose-response line"])
    with c3:
        color_options = available_color_columns(df)
        selected_color = st.selectbox(
            "Color points by",
            color_options,
            index=default_color_index(color_options, preferred="ph_bin")
        )

    y_col, label, axis_label = label_to_spec[selected_label]

    scatter_plot(
        df,
        "alum_dose",
        y_col,
        f"{label} vs Alum Dose",
        axis_label,
        None if selected_color == "None" else selected_color,
        use_line=(chart_style == "Dose-response line")
    )

def dose_response_removal_gain(df):
    if df is None or df.empty:
        st.warning("No data available.")
        return

    if "alum_dose" not in df.columns:
        st.warning("Column 'alum_dose' is required.")
        return

    parameter_options = []
    for base, label, unit in [
        ("uv254", "UV254", "UV254"),
        ("doc", "DOC", "DOC"),
        ("toc", "TOC", "TOC"),
        ("turb", "Turbidity", "Turbidity"),
        ("true_colour", "True Colour", "True Colour"),
        ("suva", "SUVA", "SUVA"),
    ]:
        if base in df.columns and f"{base}_removal_percent" in df.columns:
            parameter_options.append((base, label, unit))

    if not parameter_options:
        st.warning("No parameters with removal percentage are available.")
        return

    label_to_spec = {label: (base, label, unit) for base, label, unit in parameter_options}
    selected_label = st.selectbox("Select parameter for dose-response analysis", list(label_to_spec.keys()))
    base, label, unit = label_to_spec[selected_label]
    removal_col = f"{base}_removal_percent"

    # Optional single test/date selection to make this plot similar to the provided lab reference
    work = df.copy()
    st.caption("Tip: Use the filters above to isolate one test/date if you want a clean lab-style dose-response figure.")

    grouped = (
        work.dropna(subset=["alum_dose", base])
        .groupby("alum_dose", as_index=False)
        .agg(value=(base, "mean"), removal=(removal_col, "mean"))
        .sort_values("alum_dose")
    )

    if grouped.empty:
        st.warning("Not enough data for dose-response analysis.")
        return

    grouped["marginal_gain"] = grouped["removal"].diff()

    raw_points = pd.DataFrame()
    if "sample_type" in work.columns:
        raw_points = work[work["sample_type"].astype(str).str.lower().str.contains("raw", na=False)]
    if raw_points.empty and "sample" in work.columns:
        raw_points = work[work["sample"].astype(str).str.lower().str.contains("raw", na=False)]
    if raw_points.empty and "alum_dose" in work.columns:
        raw_points = work[work["alum_dose"].fillna(-999999) == 0]

    fig_a = px.line(
        grouped,
        x="alum_dose",
        y="value",
        markers=True,
        title=f"A) {label}",
        labels={"alum_dose": "Alum Dose (mg/L)", "value": unit}
    )
    fig_a.update_traces(line=dict(width=3), marker=dict(size=10))

    if not raw_points.empty and base in raw_points.columns:
        fig_raw = px.scatter(
            raw_points,
            x="alum_dose",
            y=base
        )
        fig_raw.update_traces(marker=dict(size=13, color="red", symbol="circle"), name="CW")
        for tr in fig_raw.data:
            fig_a.add_trace(tr)

    fig_b = px.line(
        grouped.dropna(subset=["removal"]),
        x="alum_dose",
        y="removal",
        markers=True,
        title=f"B) {label} Removal (%)",
        labels={"alum_dose": "Alum Dose (mg/L)", "removal": f"{label} Removal (%)"}
    )
    fig_b.update_traces(line=dict(width=3), marker=dict(size=10))

    fig_c = px.line(
        grouped.dropna(subset=["marginal_gain"]),
        x="alum_dose",
        y="marginal_gain",
        markers=True,
        title=f"C) Marginal {label} Removal Gain",
        labels={"alum_dose": "Alum Dose (mg/L)", "marginal_gain": "Marginal Gain (%)"}
    )
    fig_c.update_traces(line=dict(width=3), marker=dict(size=10))

    c1, c2 = st.columns([1.15, 1])
    with c1:
        render_plot(fig_a, "dose_response_a")
    with c2:
        render_plot(fig_b, "dose_response_b")
        render_plot(fig_c, "dose_response_c")

    if not grouped["removal"].dropna().empty:
        best = grouped.loc[grouped["removal"].idxmax()]
        st.success(
            f"Highest {label} removal observed at {best['alum_dose']} mg/L "
            f"({best['removal']:.2f}% removal)."
        )

def generate_html_report(
    df,
    source_name="Traditional Jar Tests",
    include_preview=True,
    include_statistics=True,
    include_optimization=True,
    include_correlation=True,
    correlation_cols=None
):
    if df is None or df.empty:
        return "<html><body><h1>No data available</h1></body></html>"

    numeric = df.select_dtypes(include="number")

    summary_html = numeric.describe().to_html() if include_statistics and not numeric.empty else ""
    preview_html = df.head(40).to_html(index=False) if include_preview else ""

    optimization_table = ""
    if include_optimization:
        best_sections = ""
        for target in [
            "doc", "doc_removal_percent", "toc", "toc_removal_percent",
            "uv254", "uv254_removal_percent", "turb", "turb_removal_percent",
            "true_colour", "true_colour_removal_percent", "ph", "suva",
            "tot_al_ppm", "diss_al_ppm"
        ]:
            if target in df.columns and "alum_dose" in df.columns and not df[target].dropna().empty:
                if "removal_percent" in target:
                    best = df.loc[df[target].idxmax()]
                    criterion = "Highest"
                else:
                    best = df.loc[df[target].idxmin()]
                    criterion = "Lowest"

                best_sections += f"""
                <tr>
                    <td>{target}</td>
                    <td>{criterion}</td>
                    <td>{best[target]:.4f}</td>
                    <td>{best.get('alum_dose', 'N/A')}</td>
                    <td>{best.get('aim_ph', 'N/A')}</td>
                    <td>{best.get('ph', 'N/A')}</td>
                    <td>{best.get('test', 'N/A')}</td>
                </tr>
                """

        if best_sections:
            optimization_table = f"""
            <h2>Optimization Summary</h2>
            <table>
                <tr>
                    <th>Target</th>
                    <th>Criterion</th>
                    <th>Value</th>
                    <th>Alum Dose</th>
                    <th>Target pH</th>
                    <th>Measured pH</th>
                    <th>Test</th>
                </tr>
                {best_sections}
            </table>
            """

    correlation_html = ""
    if include_correlation and not numeric.empty:
        if correlation_cols is None or len(correlation_cols) < 2:
            correlation_cols = list(numeric.columns)
        corr = numeric[correlation_cols].corr().round(3)
        correlation_html = f"""
        <h2>Correlation Matrix</h2>
        {corr.to_html()}
        """

    preview_section = f"<h2>Data Preview</h2>{preview_html}" if include_preview else ""
    stats_section = f"<h2>Descriptive Statistics</h2>{summary_html}" if include_statistics else ""

    html = f"""
    <html>
    <head>
        <title>WRAP Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; background:#f7f8fb; color:#111; }}
            h1 {{ color: #111; }}
            h2 {{ color: #222; margin-top: 30px; }}
            table {{ border-collapse: collapse; width: 100%; margin-top: 10px; background:white; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; font-size: 12px; }}
            th {{ background-color: #FFD200; color: #111; }}
            .box {{ background: white; padding: 15px; border-left: 6px solid #FFD200; margin-top: 20px; border-radius:12px; }}
        </style>
    </head>
    <body>
        <h1>WRAP - Water Research Analytics Report</h1>
        <div class="box">
            <p><b>Source:</b> {source_name}</p>
            <p><b>Generated:</b> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
            <p><b>Rows:</b> {len(df)}</p>
            <p><b>Columns:</b> {len(df.columns)}</p>
            <p><b>Note:</b> Interactive charts can be exported directly from the dashboard using the camera icon on each Plotly chart.</p>
        </div>
        {optimization_table}
        {correlation_html}
        {preview_section}
        {stats_section}
        <h2>Notes</h2>
        <p>This report was generated from uploaded experimental data. Robot integration is pending and will be added once Brigit/MANTECH exports are available.</p>
    </body>
    </html>
    """
    return html

# -------------------- LOGIN --------------------
if not st.session_state.logged_in:
    c1, c2, c3 = st.columns([1, 1.2, 1])
    with c2:
        st.image("dalhousie_logo.png", width=330)
        st.title("🔐 WRAP Login")
        st.caption("Water Research Analytics Platform")

        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        if st.button("Sign In", use_container_width=True):
            if email in VALID_USERS and password == VALID_USERS[email]:
                st.session_state.logged_in = True
                st.session_state.user_email = email
                st.rerun()
            else:
                st.error("Invalid credentials")

        st.info("Prototype access | Research use only")

    st.stop()

# -------------------- SIDEBAR --------------------
with st.sidebar:
    st.image("dalhousie_logo.png", width=230)
    st.title("WRAP")
    st.caption("Water Research Analytics Platform")

    page = st.radio(
        "Navigation",
        [
            "🏠 Home",
            "🧪 Traditional Jar Tests",
            "📉 Dose Response",
            "⚗️ pH Analysis",
            "🌡️ Extra Parameters",
            "🧊 Heatmaps",
            "📊 Mean Response",
            "📄 Reports",
            "🤖 Robot Data",
            "🔁 Compare Methods",
            "📈 Analytics",
            "🛰️ Robot Integration Status"
        ]
    )

    st.divider()

    if st.session_state.user_email:
        st.caption(f"Signed in as: {st.session_state.user_email}")

    if st.session_state.traditional_df is not None:
        st.success("Traditional data loaded")
    else:
        st.warning("Traditional data missing")

    if st.session_state.robot_df is not None:
        st.success("Robot data loaded")
    else:
        st.info("Robot data pending")

    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.user_email = None
        st.rerun()

# -------------------- HEADER --------------------
st.title("💧 Water Research Analytics Platform")
st.caption("Manual Jar Tests | Future Brigit Robot Data | Comparative Analytics")

# -------------------- HOME --------------------
if page == "🏠 Home":
    traditional_loaded = st.session_state.traditional_df is not None
    robot_loaded = st.session_state.robot_df is not None

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card(len(st.session_state.traditional_df) if traditional_loaded else 0, "📄 Traditional Records")
    with c2:
        metric_card(len(st.session_state.robot_df) if robot_loaded else 0, "🤖 Robot Records", "metric-card-blue")
    with c3:
        metric_card("Ready" if traditional_loaded else "Waiting", "🧪 Traditional Data Layer", "metric-card-green")
    with c4:
        metric_card("Pending", "🛰️ Robot Integration", "metric-card-red")

    st.markdown("## 🚀 Platform Purpose")
    st.markdown("""
    WRAP organizes, visualizes, and analyzes **traditional jar test datasets** first.

    When the Brigit / MANTECH automated jar tester becomes available, this same platform can receive robot-generated CSV, Excel, database, or API exports.

    The long-term goal is to compare manual and automated jar testing methods in one research environment.
    """)

    st.info("No fake data is loaded. The platform only displays data after a CSV or Excel file is uploaded.")

# -------------------- TRADITIONAL JAR TESTS --------------------
elif page == "🧪 Traditional Jar Tests":
    st.header("🧪 Traditional Jar Test Analysis")

    uploaded = st.file_uploader(
        "Upload traditional jar test file (CSV or Excel)",
        type=["csv", "xlsx", "xls"],
        key="traditional_upload"
    )

    if uploaded is not None:
        st.session_state.traditional_df = load_file(uploaded)

    df = st.session_state.traditional_df

    if df is None:
        st.warning("Upload a traditional jar test dataset to begin.")
        st.stop()

    st.success("Dataset Loaded Successfully")
    filtered_df = filter_traditional_data(df)

    st.divider()
    dataset_overview(filtered_df)

    st.divider()
    st.subheader("📋 Data Preview")
    st.dataframe(filtered_df.head(60), use_container_width=True)

    st.download_button(
        "⬇️ Download filtered data as CSV",
        filtered_df.to_csv(index=False).encode("utf-8"),
        file_name="WRAP_filtered_traditional_data.csv",
        mime="text/csv"
    )

    st.divider()

    st.subheader("📌 Parameter Explorer")
    st.caption("Choose any available water-quality parameter and visualize it against alum dose.")
    parameter_explorer(filtered_df)

    st.divider()
    st.subheader("📌 Standard Experimental Scatter Plots")
    st.caption("Each point represents a discrete jar test condition. Points are not connected because these are not continuous time-series data.")

    color_col = "ph_bin" if "ph_bin" in filtered_df.columns else ("ph" if "ph" in filtered_df.columns else None)

    plot_specs = [
        ("doc", "DOC vs Alum Dose", "DOC (mg/L)"),
        ("toc", "TOC vs Alum Dose", "TOC (mg/L)"),
        ("uv254", "UV254 vs Alum Dose", "UV254 (cm⁻¹)"),
        ("uv254_removal_percent", "UV254 Removal (%) vs Alum Dose", "UV254 Removal (%)"),
        ("turb", "Turbidity vs Alum Dose", "Turbidity (NTU)"),
        ("true_colour", "True Colour vs Alum Dose", "True Colour"),
        ("suva", "SUVA vs Alum Dose", "SUVA"),
        ("ph", "Measured pH vs Alum Dose", "Measured pH"),
        ("tot_al_ppm", "Total Aluminum vs Alum Dose", "Total Al (mg/L)"),
        ("diss_al_ppm", "Dissolved Aluminum vs Alum Dose", "Dissolved Al (mg/L)")
    ]

    for i in range(0, len(plot_specs), 2):
        cols = st.columns(2)
        for j, col in enumerate(cols):
            if i + j < len(plot_specs):
                y, title, label = plot_specs[i + j]
                with col:
                    scatter_plot(filtered_df, "alum_dose", y, title, label, color_col)

    st.divider()
    st.subheader("🎯 Optimal Point")
    st.caption(
        "This section considers removal efficiency and marginal gain, not only the lowest final concentration. "
        "A lower dose can be preferred if it reaches near-maximum removal with less coagulant."
    )

    target_options = [
        c for c in [
            "uv254", "doc", "toc", "turb", "true_colour", "suva"
        ] if c in filtered_df.columns and f"{c}_removal_percent" in filtered_df.columns
    ]

    if target_options:
        target = st.selectbox("Optimization target", target_options)
        best_point, optimization_table = compute_optimal_point(filtered_df, target)

        if best_point is not None:
            c1, c2, c3, c4 = st.columns(4)

            with c1:
                metric_card(f"{best_point['alum_dose']} mg/L", "Recommended Dose", "metric-card-green")
            with c2:
                metric_card(f"{best_point['mean_removal']:.2f}%", "Mean Removal", "metric-card-blue")
            with c3:
                gain_value = best_point["gain_per_mg"]
                gain_text = "N/A" if pd.isna(gain_value) else f"{gain_value:.2f}%/mg"
                metric_card(gain_text, "Marginal Gain", "metric-card")
            with c4:
                metric_card(int(best_point["n"]), "Points at Dose", "metric-card-red")

            st.dataframe(optimization_table, use_container_width=True)

            st.info(
                "Interpretation: repeated points at the same alum dose may be true replicates, repeated jars, or duplicated records. "
                "The table aggregates them by dose using the mean response."
            )
        else:
            st.warning("Not enough removal data to calculate an optimal point.")
    else:
        st.warning("No removal-percent target columns were found. Make sure raw water or alum dose = 0 rows are included.")

    st.divider()
    st.subheader("🔍 Repeated Point Check")
    repeated = duplicate_summary(filtered_df)

    if repeated.empty:
        st.success("No repeated experimental points detected for the selected filters.")
    else:
        st.caption(
            "These are repeated points with the same date/test/pH/dose grouping. "
            "They are not necessarily errors; they may be replicates or repeated jars."
        )
        st.dataframe(repeated, use_container_width=True)

# -------------------- DOSE RESPONSE --------------------
elif page == "📉 Dose Response":
    st.header("📉 Dose-Response and Marginal Removal Analysis")

    df = st.session_state.traditional_df
    if df is None:
        st.warning("Upload traditional jar test data first.")
        st.stop()

    filtered_df = filter_traditional_data(df)
    st.divider()

    dose_response_removal_gain(filtered_df)

# -------------------- PH ANALYSIS --------------------
elif page == "⚗️ pH Analysis":
    st.header("⚗️ pH Analysis")

    df = st.session_state.traditional_df
    if df is None:
        st.warning("Upload traditional jar test data first.")
        st.stop()

    filtered_df = filter_traditional_data(df)

    st.divider()
    st.subheader("Measured pH vs Alum Dose")
    color_col = "ph_bin" if "ph_bin" in filtered_df.columns else ("ph" if "ph" in filtered_df.columns else None)
    scatter_plot(filtered_df, "alum_dose", "ph", "Measured pH vs Alum Dose", "Measured pH", color_col)

    st.divider()
    st.subheader("Measured pH vs Target pH")
    scatter_plot(filtered_df, "aim_ph", "ph", "Measured pH vs Target pH", "Measured pH", "test" if "test" in filtered_df.columns else None)

    st.divider()
    st.subheader("Operational Variability of pH")
    boxplot_ph_variability(filtered_df)

# -------------------- EXTRA PARAMETERS --------------------
elif page == "🌡️ Extra Parameters":
    st.header("🌡️ Extra Parameters Explorer")

    df = st.session_state.traditional_df
    if df is None:
        st.warning("Upload traditional jar test data first.")
        st.stop()

    filtered_df = filter_traditional_data(df)
    nums = numeric_columns(filtered_df)

    if not nums:
        st.warning("No numeric parameters found.")
        st.stop()

    st.markdown("Use this section for any parameter that is not already shown in the main jar test module.")

    c1, c2, c3 = st.columns(3)
    with c1:
        x_col = st.selectbox("X Axis", nums, index=nums.index("alum_dose") if "alum_dose" in nums else 0)
    with c2:
        y_col = st.selectbox("Y Axis", nums, index=nums.index("ph") if "ph" in nums else min(1, len(nums)-1))
    with c3:
        color_options = available_color_columns(filtered_df)
        color_col = st.selectbox(
            "Color By",
            color_options,
            index=default_color_index(color_options, preferred="ph_bin")
        )

    scatter_plot(
        filtered_df,
        x_col,
        y_col,
        f"{y_col} vs {x_col}",
        y_col,
        None if color_col == "None" else color_col
    )

# -------------------- HEATMAPS --------------------
elif page == "🧊 Heatmaps":
    st.header("🧊 Heatmap Analysis")

    df = st.session_state.traditional_df
    if df is None:
        st.warning("Upload traditional jar test data first.")
        st.stop()

    filtered_df = filter_traditional_data(df)

    heatmap_options = {
        "UV254": ("uv254", "UV254 Heatmap", "UV254 (cm⁻¹)"),
        "UV254 Removal": ("uv254_removal_percent", "UV254 Removal Heatmap", "UV254 Removal (%)"),
        "TOC": ("toc", "TOC Heatmap", "TOC (mg/L)"),
        "TOC Removal": ("toc_removal_percent", "TOC Removal Heatmap", "TOC Removal (%)"),
        "DOC": ("doc", "DOC Heatmap", "DOC (mg/L)"),
        "DOC Removal": ("doc_removal_percent", "DOC Removal Heatmap", "DOC Removal (%)"),
        "Turbidity": ("turb", "Turbidity Heatmap", "Turbidity (NTU)"),
        "Turbidity Removal": ("turb_removal_percent", "Turbidity Removal Heatmap", "Turbidity Removal (%)"),
        "True Colour": ("true_colour", "True Colour Heatmap", "True Colour"),
        "Measured pH": ("ph", "Measured pH Heatmap", "Measured pH"),
        "SUVA": ("suva", "SUVA Heatmap", "SUVA"),
        "Total Aluminum": ("tot_al_ppm", "Residual Total Aluminum Heatmap", "Total Al (mg/L)"),
        "Dissolved Aluminum": ("diss_al_ppm", "Residual Dissolved Aluminum Heatmap", "Dissolved Al (mg/L)")
    }

    heatmap_options = {k: v for k, v in heatmap_options.items() if v[0] in filtered_df.columns}

    if not heatmap_options:
        st.warning("No supported heatmap parameters found.")
        st.stop()

    h1, h2 = st.columns(2)
    with h1:
        selected_heatmap = st.selectbox("Select heatmap", list(heatmap_options.keys()))
    with h2:
        y_axis_options = [c for c in ["ph_bin", "ph", "aim_ph"] if c in filtered_df.columns]
        if not y_axis_options:
            y_axis_options = ["aim_ph"]
        selected_y_axis = st.selectbox(
            "Heatmap pH axis",
            y_axis_options,
            index=0 if "ph_bin" in y_axis_options else 0
        )

    value_col, title, color_label = heatmap_options[selected_heatmap]
    heatmap(filtered_df, value_col, title, color_label, y_axis=selected_y_axis, x_axis="alum_dose")

# -------------------- MEAN RESPONSE --------------------
elif page == "📊 Mean Response":
    st.header("📊 Mean Response Across Jar Test Conditions")

    df = st.session_state.traditional_df
    if df is None:
        st.warning("Upload traditional jar test data first.")
        st.stop()

    filtered_df = filter_traditional_data(df)

    response_options = {
        "UV254": ("uv254", "Mean UV254 Across Different Jar Test Conditions", "Mean UV254 (cm⁻¹)"),
        "UV254 Removal": ("uv254_removal_percent", "Mean UV254 Removal Across Different Jar Test Conditions", "Mean UV254 Removal (%)"),
        "TOC": ("toc", "Mean TOC Across Different Jar Test Conditions", "Mean TOC (mg/L)"),
        "TOC Removal": ("toc_removal_percent", "Mean TOC Removal Across Different Jar Test Conditions", "Mean TOC Removal (%)"),
        "DOC": ("doc", "Mean DOC Across Different Jar Test Conditions", "Mean DOC (mg/L)"),
        "DOC Removal": ("doc_removal_percent", "Mean DOC Removal Across Different Jar Test Conditions", "Mean DOC Removal (%)"),
        "Turbidity": ("turb", "Mean Turbidity Across Different Jar Test Conditions", "Mean Turbidity (NTU)"),
        "Measured pH": ("ph", "Mean Measured pH Across Different Jar Test Conditions", "Mean measured pH"),
        "True Colour": ("true_colour", "Mean True Colour Across Different Jar Test Conditions", "Mean true colour"),
        "SUVA": ("suva", "Mean SUVA Across Different Jar Test Conditions", "Mean SUVA"),
        "Total Aluminum": ("tot_al_ppm", "Mean Total Aluminum Across Different Jar Test Conditions", "Mean total Al"),
        "Dissolved Aluminum": ("diss_al_ppm", "Mean Dissolved Aluminum Across Different Jar Test Conditions", "Mean dissolved Al")
    }

    response_options = {k: v for k, v in response_options.items() if v[0] in filtered_df.columns}

    if not response_options:
        st.warning("No supported response parameters found.")
        st.stop()

    selected_response = st.selectbox("Select response parameter", list(response_options.keys()))
    y_col, title, y_label = response_options[selected_response]
    mean_error_plot(filtered_df, y_col, title, y_label)

# -------------------- REPORTS --------------------
elif page == "📄 Reports":
    st.header("📄 Report Generator")

    df = st.session_state.traditional_df
    if df is None:
        st.warning("Upload traditional jar test data first.")
        st.stop()

    filtered_df = filter_traditional_data(df)

    st.divider()
    st.markdown("<div class='report-box'>", unsafe_allow_html=True)
    st.subheader("Report Preview")
    dataset_overview(filtered_df)
    st.markdown("</div>", unsafe_allow_html=True)

    st.subheader("Report Contents")
    r1, r2, r3, r4 = st.columns(4)
    with r1:
        include_preview = st.checkbox("Data preview", value=True)
    with r2:
        include_statistics = st.checkbox("Descriptive statistics", value=True)
    with r3:
        include_optimization = st.checkbox("Optimization summary", value=True)
    with r4:
        include_correlation = st.checkbox("Correlation matrix", value=True)

    numeric_cols = numeric_columns(filtered_df)
    default_corr_cols = [
        c for c in [
            "alum_dose", "aim_ph", "ph", "doc", "toc", "uv254",
            "uv254_removal_percent", "turb", "true_colour", "suva",
            "tot_al_ppm", "diss_al_ppm"
        ] if c in numeric_cols
    ]

    correlation_cols = []
    if include_correlation and numeric_cols:
        correlation_cols = st.multiselect(
            "Report correlation variables",
            numeric_cols,
            default=default_corr_cols if default_corr_cols else numeric_cols
        )

    html_report = generate_html_report(
        filtered_df,
        "Traditional Jar Tests",
        include_preview=include_preview,
        include_statistics=include_statistics,
        include_optimization=include_optimization,
        include_correlation=include_correlation,
        correlation_cols=correlation_cols
    )

    st.download_button(
        "📄 Download HTML Report",
        html_report.encode("utf-8"),
        file_name="WRAP_traditional_jar_test_report.html",
        mime="text/html"
    )

    st.download_button(
        "📊 Download Report Data as CSV",
        filtered_df.to_csv(index=False).encode("utf-8"),
        file_name="WRAP_report_data.csv",
        mime="text/csv"
    )

    st.info("Open the HTML report in a browser and use Print > Save as PDF. Charts can be exported from the dashboard using the camera icon on each chart.")

# -------------------- ROBOT DATA --------------------
elif page == "🤖 Robot Data":
    st.header("🤖 Robot Data")

    st.warning("Robot data connection is not active yet. This module is ready for future Brigit / MANTECH exports.")

    uploaded = st.file_uploader(
        "Upload robot-generated CSV or Excel when available",
        type=["csv", "xlsx", "xls"],
        key="robot_upload"
    )

    if uploaded is not None:
        st.session_state.robot_df = load_file(uploaded)

    df = st.session_state.robot_df

    if df is None:
        st.info("No robot data has been uploaded yet.")
    else:
        dataset_overview(df)
        st.dataframe(df.head(50), use_container_width=True)

        nums = numeric_columns(df)
        if len(nums) >= 2:
            x = st.selectbox("X Axis", nums, key="robot_x")
            y = st.selectbox("Y Axis", nums, index=1, key="robot_y")
            fig = px.scatter(df, x=x, y=y, title=f"Robot Data: {y} vs {x}")
            render_plot(fig, "chart")

# -------------------- COMPARE METHODS --------------------
elif page == "🔁 Compare Methods":
    st.header("🔁 Traditional vs Robot Comparison")

    traditional_df = st.session_state.traditional_df
    robot_df = st.session_state.robot_df

    if traditional_df is None:
        st.warning("Upload traditional jar test data first.")

    if robot_df is None:
        st.info("Robot data is not available yet. This comparison module is ready, but waiting for Brigit / MANTECH output files.")

    if traditional_df is not None and robot_df is not None:
        traditional_numeric = numeric_columns(traditional_df)
        robot_numeric = numeric_columns(robot_df)
        common_numeric = sorted(list(set(traditional_numeric).intersection(set(robot_numeric))))

        if not common_numeric:
            st.warning("No matching numeric columns were found between both datasets.")
        else:
            selected = st.selectbox("Select parameter to compare", common_numeric)

            comparison = pd.DataFrame({
                "Method": ["Traditional", "Robot"],
                "Average Value": [
                    traditional_df[selected].mean(),
                    robot_df[selected].mean()
                ]
            })

            fig = px.bar(
                comparison,
                x="Method",
                y="Average Value",
                title=f"Average {selected}: Traditional vs Robot"
            )

            render_plot(fig, "chart")
            st.dataframe(comparison, use_container_width=True)

# -------------------- ANALYTICS --------------------
elif page == "📈 Analytics":
    st.header("📈 Advanced Analytics")

    source = st.radio(
        "Select data source",
        ["Traditional Jar Tests", "Robot Data"],
        horizontal=True
    )

    df = st.session_state.traditional_df if source == "Traditional Jar Tests" else st.session_state.robot_df

    if df is None:
        st.warning("No dataset loaded for this source.")
    else:
        if source == "Traditional Jar Tests":
            df = filter_traditional_data(df)

        correlation_matrix(df)

        st.subheader("Descriptive Statistics")
        nums = numeric_columns(df)
        if nums:
            st.dataframe(df[nums].describe(), use_container_width=True)
        else:
            st.warning("No numeric columns found.")

# -------------------- ROBOT INTEGRATION STATUS --------------------
elif page == "🛰️ Robot Integration Status":
    st.header("🛰️ Robot Integration Status")

    st.markdown("""
    ### Current Status

    **Robot connection:** Not connected  
    **Expected system:** MANTECH / Brigit automated jar tester  
    **Current integration mode:** Pending  
    **Available workflow today:** Manual CSV / Excel upload  
    """)

    st.markdown("""
    ### Expected Future Data Flow

    **Current workflow**

    Traditional jar test → CSV / Excel file → WRAP dashboard

    **Future workflow**

    Brigit / MANTECH robot → CSV, database, or API export → WRAP dashboard → comparative analytics
    """)

    st.markdown("""
    ### Integration Questions to Confirm

    - Does Brigit export CSV files?
    - Does MANTECH software store data in a local database?
    - Is there an available API?
    - Can the MiniHub or software export timestamped sensor readings?
    - Are experiment IDs automatically generated?
    """)

    st.success("WRAP is ready for CSV / Excel based robot data once available.")

    st.caption(f"Last platform check: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
