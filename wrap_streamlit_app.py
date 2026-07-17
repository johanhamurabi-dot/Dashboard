
import streamlit as st
import pandas as pd
import plotly.express as px
import base64
import re
from pathlib import Path
from datetime import datetime

# ============================================================
# WRAP v16 - Water Research Analytics Platform
# Dalhousie Water Research
# Traditional Jar Tests + Expanded Parameters + Robust Optimal-Dose Validation
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
    "lindsaya@halifaxwater.ca": "lindsaya123#",
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
if "robot_long_df" not in st.session_state:
    st.session_state.robot_long_df = None
if "robot_last_comparison" not in st.session_state:
    st.session_state.robot_last_comparison = None
if "robot_last_comparison_title" not in st.session_state:
    st.session_state.robot_last_comparison_title = None

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

def get_base64_image(image_path: str) -> str | None:
    """
    Read a local image and convert it to a base64 data URI payload.
    This is required for reliable CSS background images on Streamlit Cloud.
    """
    try:
        path = Path(image_path)
        if not path.exists():
            return None

        with path.open("rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")
    except Exception:
        return None


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
    # Remove useless index/empty columns from Excel or CSV exports
    unnamed_cols = [col for col in df.columns if str(col).startswith("Unnamed")]
    if unnamed_cols:
        df = df.drop(columns=unnamed_cols)
    return df

def normalize_parameter_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Standardize important chemistry parameter names so the dashboard works even if
    the source file uses different naming conventions.

    Example source columns:
    - Total_al -> total_al
    - Dissolved_Al -> dissolved_al
    - tthms -> tthms
    - thaas -> thaas
    """
    if df is None:
        return df

    df = df.copy()

    rename_map = {
        "Total_al": "total_al",
        "Total_Al": "total_al",
        "tot_al_ppm": "total_al",
        "total_al": "total_al",
        "Total_Aluminum": "total_al",
        "Total_Aluminium": "total_al",
        "Dissolved_Al": "dissolved_al",
        "Dissolved_al": "dissolved_al",
        "diss_al_ppm": "dissolved_al",
        "dissolved_al": "dissolved_al",
        "Dissolved_Aluminum": "dissolved_al",
        "Dissolved_Aluminium": "dissolved_al",
        "TTHM": "tthms",
        "TTHMs": "tthms",
        "tthm": "tthms",
        "tthms": "tthms",
        "THM": "tthms",
        "THAA": "thaas",
        "THAAs": "thaas",
        "thaa": "thaas",
        "thaas": "thaas",
        "HAA": "thaas",
        "HAAs": "thaas",
        "step_uv_rem": "step_uv_rem",
        "delta_rem": "delta_rem",
    }

    # Rename only existing columns; avoid duplicate overwrites
    for old, new in rename_map.items():
        if old in df.columns and new not in df.columns:
            df = df.rename(columns={old: new})

    return df


def parameter_specs():
    """
    Central parameter catalog.
    Anything listed here will appear across the dashboard wherever the column exists.
    """
    return [
        ("uv254", "UV254", "UV254 (cm⁻¹)", True),
        ("uv254_removal_percent", "UV254 Removal", "UV254 removal (%)", False),
        ("doc", "DOC", "DOC (mg/L)", True),
        ("doc_removal_percent", "DOC Removal", "DOC removal (%)", False),
        ("toc", "TOC", "TOC (mg/L)", True),
        ("toc_removal_percent", "TOC Removal", "TOC removal (%)", False),
        ("turb", "Turbidity", "Turbidity (NTU)", True),
        ("turb_removal_percent", "Turbidity Removal", "Turbidity removal (%)", False),
        ("true_colour", "True Colour", "True Colour", True),
        ("true_colour_removal_percent", "True Colour Removal", "True colour removal (%)", False),
        ("suva", "SUVA", "SUVA", True),
        ("suva_removal_percent", "SUVA Removal", "SUVA removal (%)", False),
        ("ph", "Measured pH", "Measured pH", False),
        ("ph_qc", "pH QC", "pH QC", False),
        ("total_al", "Total Aluminum", "Total Al", True),
        ("total_al_removal_percent", "Total Aluminum Removal", "Total Al removal (%)", False),
        ("dissolved_al", "Dissolved Aluminum", "Dissolved Al", True),
        ("dissolved_al_removal_percent", "Dissolved Aluminum Removal", "Dissolved Al removal (%)", False),
        ("tthms", "TTHMs", "TTHMs", False),
        ("tthms_removal_percent", "TTHMs Relative Change", "TTHMs relative change from lowest alum dose (%)", False),
        ("thaas", "THAAs", "THAAs", False),
        ("thaas_removal_percent", "THAAs Relative Change", "THAAs relative change from lowest alum dose (%)", False),
        ("tthms_step_change_percent", "TTHMs Step-to-Step Change", "TTHMs step-to-step change (%)", False),
        ("tthms_marginal_gain_per_mg", "TTHMs Marginal Gain", "TTHMs marginal gain (% per mg/L)", False),
        ("thaas_step_change_percent", "THAAs Step-to-Step Change", "THAAs step-to-step change (%)", False),
        ("thaas_marginal_gain_per_mg", "THAAs Marginal Gain", "THAAs marginal gain (% per mg/L)", False),
        ("raw_alkalinity", "Raw Alkalinity", "Raw alkalinity", False),
        ("raw_uv254", "Raw UV254", "Raw UV254", False),
        ("step_uv_rem", "Step UV Removal", "Step UV removal", False),
        ("delta_rem", "Delta Removal", "Delta removal", False),
        ("conductivity", "Conductivity", "Conductivity", False),
        ("temperature", "Temperature", "Temperature", False),
        ("zeta_mean", "Zeta Potential", "Zeta potential", False),
        ("alkalinity", "Alkalinity", "Alkalinity", False),
        ("Talk", "Total Alkalinity", "Total alkalinity", False),
        ("Mn", "Manganese", "Mn", False),
        ("Fe", "Iron", "Fe", False),
        ("Al", "Aluminum", "Al", False),
        ("THAA", "THAA", "THAA", False),
        ("TTHM", "TTHM", "TTHM", False),
        ("THM", "THM", "THM", False),
        ("pecod", "PeCOD", "PeCOD", False),
        ("PeCOD", "PeCOD", "PeCOD", False),
    ]


def available_parameter_specs(df: pd.DataFrame, include_removal: bool = True):
    if df is None:
        return []
    specs = []
    for col, label, axis_label, _ in parameter_specs():
        if col in df.columns:
            if include_removal or not col.endswith("_removal_percent"):
                specs.append((col, label, axis_label))
    return specs


def add_removal_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Standard parameters use raw water (or 0 alum) as baseline.

    TTHMs and THAAs use the lowest alum dose with a valid DBP measurement
    in the same jar-test group as baseline, because raw DBP data are unavailable.

    DBP Relative Change (%) =
        (DBP_lowest_dose - DBP_current_dose) / DBP_lowest_dose * 100

    Positive = decrease relative to lowest dose.
    Negative = increase relative to lowest dose.
    Lowest-dose baseline = 0% change.
    """
    if df is None or df.empty:
        return df

    df = df.copy()

    standard_params = [
        "uv254", "doc", "toc", "turb", "true_colour", "suva",
        "total_al", "dissolved_al"
    ]
    dbp_params = ["tthms", "thaas"]

    available_standard = [c for c in standard_params if c in df.columns]
    available_dbp = [c for c in dbp_params if c in df.columns]
    all_available = available_standard + available_dbp

    if not all_available:
        return df

    for param in all_available:
        df[f"{param}_removal_percent"] = pd.NA

    group_cols = [c for c in ["sample_date", "test", "aim_ph"] if c in df.columns]

    if not group_cols:
        group_cols = ["__all__"]
        df["__all__"] = "all"

    for _, group in df.groupby(group_cols, dropna=False):
        idx = group.index

        # Standard parameters: raw-water baseline.
        raw_rows = pd.DataFrame()

        if "sample_type" in group.columns:
            raw_rows = group[
                group["sample_type"].astype(str).str.lower().str.contains("raw", na=False)
            ]

        if raw_rows.empty and "sample" in group.columns:
            raw_rows = group[
                group["sample"].astype(str).str.lower().str.contains("raw", na=False)
            ]

        if raw_rows.empty and "alum_dose" in group.columns:
            raw_rows = group[
                pd.to_numeric(group["alum_dose"], errors="coerce") == 0
            ]

        if not raw_rows.empty:
            for param in available_standard:
                valid_raw = pd.to_numeric(raw_rows[param], errors="coerce").dropna()

                if valid_raw.empty:
                    continue

                raw_value = valid_raw.iloc[0]

                if pd.isna(raw_value) or raw_value == 0:
                    continue

                current_values = pd.to_numeric(df.loc[idx, param], errors="coerce")
                df.loc[idx, f"{param}_removal_percent"] = (
                    (raw_value - current_values) / raw_value
                ) * 100

        # DBPs: lowest valid alum dose is the baseline.
        if "alum_dose" in group.columns:
            dose_numeric = pd.to_numeric(group["alum_dose"], errors="coerce")

            for param in available_dbp:
                param_numeric = pd.to_numeric(group[param], errors="coerce")
                valid_mask = dose_numeric.notna() & param_numeric.notna()

                if not valid_mask.any():
                    continue

                valid_group = group.loc[valid_mask].copy()
                valid_group["_dose_numeric"] = pd.to_numeric(
                    valid_group["alum_dose"], errors="coerce"
                )
                valid_group["_param_numeric"] = pd.to_numeric(
                    valid_group[param], errors="coerce"
                )

                lowest_dose = valid_group["_dose_numeric"].min()
                baseline_values = valid_group.loc[
                    valid_group["_dose_numeric"] == lowest_dose,
                    "_param_numeric"
                ].dropna()

                if baseline_values.empty:
                    continue

                # Mean baseline if the lowest dose has replicates.
                baseline_value = baseline_values.mean()

                if pd.isna(baseline_value) or baseline_value == 0:
                    continue

                valid_indices = valid_group.index
                current_values = pd.to_numeric(
                    df.loc[valid_indices, param], errors="coerce"
                )

                df.loc[valid_indices, f"{param}_removal_percent"] = (
                    (baseline_value - current_values) / baseline_value
                ) * 100

    if "__all__" in df.columns:
        df = df.drop(columns=["__all__"])

    for param in all_available:
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
        df = normalize_parameter_columns(df)

        for col in ["sample_date", "analysis_date", "Date_Sampled", "Date_Analyzed"]:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors="coerce")

        possible_numeric_cols = [
            "test", "aim_ph", "alum_dose", "true_colour", "uv254", "turb", "ph",
            "toc", "doc", "suva", "ph_qc",
            "total_al", "dissolved_al", "total_al", "dissolved_al", "tthms", "thaas", "step_uv_rem", "delta_rem",
            "tthms", "thaas", "THAA", "TTHM", "THM", "pecod", "PeCOD",
            "step_uv_rem", "delta_rem",
            "conductivity", "temperature", "colour", "apparent_colour",
            "zeta_mean", "zeta", "alkalinity", "Talk", "Mn", "Fe", "Al",
            "raw_alkalinity", "raw_uv254", "month"
        ]

        for col in possible_numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        df = add_removal_columns(df)
        df = add_dbp_step_metrics(df)
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


def aggregate_for_line_plot(plot_df, x_col, y_col, color_col=None):
    """
    Prevent vertical line artifacts by aggregating repeated x-values before drawing lines.
    Raw points are still shown separately in the scatter layer.
    """
    if plot_df is None or plot_df.empty:
        return plot_df

    if color_col and color_col in plot_df.columns:
        group_cols = [color_col, x_col]
    else:
        group_cols = [x_col]

    line_df = (
        plot_df
        .groupby(group_cols, dropna=False, observed=False, as_index=False)
        .agg(mean_value=(y_col, "mean"), n=(y_col, "count"))
        .sort_values(group_cols)
    )
    return line_df


def compute_derivative_points(df, parameter, threshold=1.0):
    """
    Standard optimal-dose calculation based on a removal curve.

    x = alum dose
    y = removal percentage

    Outputs:
    1. Most significant improvement: maximum first derivative / marginal gain.
    2. Diminishing returns: strongest negative change in marginal gain / second derivative.
    3. Marginal threshold: first dose where marginal gain <= threshold.
    """
    removal_col = f"{parameter}_removal_percent"

    if df is None or df.empty or "alum_dose" not in df.columns or removal_col not in df.columns:
        return None, pd.DataFrame()

    work = df.dropna(subset=["alum_dose", removal_col]).copy()
    if work.empty:
        return None, pd.DataFrame()

    curve = (
        work.groupby("alum_dose", as_index=False)
        .agg(
            mean_removal=(removal_col, "mean"),
            sd_removal=(removal_col, "std"),
            n=("alum_dose", "count")
        )
        .sort_values("alum_dose")
    )

    if len(curve) < 2:
        return None, curve

    curve["delta_dose"] = curve["alum_dose"].diff()
    curve["delta_removal"] = curve["mean_removal"].diff()
    curve["first_derivative"] = curve["delta_removal"] / curve["delta_dose"]
    curve["second_derivative"] = curve["first_derivative"].diff() / curve["delta_dose"]

    valid_first = curve.dropna(subset=["first_derivative"]).copy()
    if valid_first.empty:
        return None, curve

    significant_idx = valid_first["first_derivative"].idxmax()
    significant_point = curve.loc[significant_idx]

    valid_second = curve.dropna(subset=["second_derivative"]).copy()
    if valid_second.empty:
        diminishing_point = significant_point
    else:
        diminishing_idx = valid_second["second_derivative"].idxmin()
        diminishing_point = curve.loc[diminishing_idx]

    after_first = valid_first[valid_first["alum_dose"] > curve["alum_dose"].min()].copy()
    threshold_candidates = after_first[after_first["first_derivative"] <= threshold]

    if threshold_candidates.empty:
        threshold_point = curve.loc[curve["mean_removal"].idxmax()]
    else:
        threshold_point = threshold_candidates.sort_values("alum_dose").iloc[0]

    result = {
        "significant_dose": float(significant_point["alum_dose"]),
        "significant_gain": float(significant_point["first_derivative"]),
        "diminishing_dose": float(diminishing_point["alum_dose"]),
        "diminishing_second_derivative": float(diminishing_point["second_derivative"]) if pd.notna(diminishing_point["second_derivative"]) else None,
        "threshold_dose": float(threshold_point["alum_dose"]),
        "threshold_gain": float(threshold_point["first_derivative"]) if pd.notna(threshold_point["first_derivative"]) else None,
        "threshold": threshold,
        "max_removal": float(curve["mean_removal"].max()),
    }

    return result, curve


def classify_data_quality(curve: pd.DataFrame) -> str:
    if curve is None or curve.empty:
        return "Insufficient"
    n_doses = curve["alum_dose"].nunique() if "alum_dose" in curve.columns else 0
    replicated_doses = int((curve["n"] >= 2).sum()) if "n" in curve.columns else 0
    if n_doses >= 5 and replicated_doses >= 2:
        return "Strong"
    if n_doses >= 4:
        return "Acceptable"
    if n_doses >= 3:
        return "Limited"
    return "Insufficient"


def method_consensus(result: dict) -> dict:
    if not result:
        return {"consensus_dose": None, "agreement_count": 0, "agreement_text": "No consensus available."}
    doses = [result.get("significant_dose"), result.get("diminishing_dose"), result.get("threshold_dose")]
    doses = [float(d) for d in doses if d is not None]
    if not doses:
        return {"consensus_dose": None, "agreement_count": 0, "agreement_text": "No consensus available."}
    counts = {}
    for dose in doses:
        counts[dose] = counts.get(dose, 0) + 1
    consensus_dose, agreement_count = max(counts.items(), key=lambda item: item[1])
    if agreement_count >= 2:
        text = f"{agreement_count} of 3 methods agree at {consensus_dose:.2f} mg/L."
        return {"consensus_dose": consensus_dose, "agreement_count": agreement_count, "agreement_text": text}
    return {"consensus_dose": None, "agreement_count": agreement_count, "agreement_text": "The three methods do not agree on one dose. Review the curve, replicate variability, and threshold sensitivity."}


def threshold_sensitivity_table(df: pd.DataFrame, parameter: str, thresholds) -> pd.DataFrame:
    rows = []
    for threshold in thresholds:
        result, _curve = compute_derivative_points(df, parameter, float(threshold))
        if result is None:
            continue
        rows.append({
            "threshold_percent_per_mg": float(threshold),
            "threshold_dose_mg_L": result.get("threshold_dose"),
            "threshold_gain_percent_per_mg": result.get("threshold_gain"),
            "first_derivative_dose_mg_L": result.get("significant_dose"),
            "diminishing_returns_dose_mg_L": result.get("diminishing_dose"),
        })
    return pd.DataFrame(rows)


def automatic_test_summary(df: pd.DataFrame, parameter: str, parameter_label: str, threshold: float, result: dict, curve: pd.DataFrame) -> str:
    consensus = method_consensus(result)
    quality = classify_data_quality(curve)
    selected_tests = sorted(df["test"].dropna().unique().tolist()) if "test" in df.columns else []
    test_text = ", ".join(map(str, selected_tests)) if selected_tests else "Current filtered dataset"
    threshold_gain = result.get("threshold_gain")
    threshold_gain_text = "N/A" if threshold_gain is None or pd.isna(threshold_gain) else f"{threshold_gain:.2f}%/mg"
    replicate_text = "No replicate information available."
    if curve is not None and not curve.empty and "n" in curve.columns:
        replicated = curve[curve["n"] >= 2]
        if replicated.empty:
            replicate_text = "No repeated doses were detected."
        else:
            replicated_doses = ", ".join(f"{row.alum_dose:g} mg/L (n={int(row.n)})" for row in replicated.itertuples())
            replicate_text = f"Replicated doses: {replicated_doses}."
    return f"""
**Jar Test Summary — {test_text}**

- **Optimization parameter:** {parameter_label}
- **First-derivative dose:** {result['significant_dose']:.2f} mg/L
- **Diminishing-returns dose:** {result['diminishing_dose']:.2f} mg/L
- **Threshold dose ({threshold:.2f}%/mg):** {result['threshold_dose']:.2f} mg/L
- **Marginal gain at threshold dose:** {threshold_gain_text}
- **Method agreement:** {consensus['agreement_text']}
- **Curve quality:** {quality}
- **Replicate coverage:** {replicate_text}
"""


def plot_sensitivity_analysis(sensitivity_df: pd.DataFrame):
    if sensitivity_df is None or sensitivity_df.empty:
        st.warning("Sensitivity analysis could not be calculated.")
        return
    fig = px.line(
        sensitivity_df,
        x="threshold_percent_per_mg",
        y="threshold_dose_mg_L",
        markers=True,
        title="Threshold Sensitivity Analysis",
        labels={
            "threshold_percent_per_mg": "Marginal Gain Threshold (% removal per mg/L alum)",
            "threshold_dose_mg_L": "Recommended Threshold Dose (mg/L)",
        }
    )
    fig.update_traces(line=dict(width=3), marker=dict(size=10))
    render_plot(fig, "threshold_sensitivity")


def optimal_dose_module(df):
    if df is None or df.empty:
        st.warning("No data available.")
        return

    available = []
    for param, label, _unit in available_parameter_specs(df, include_removal=False):
        if param in df.columns and f"{param}_removal_percent" in df.columns:
            available.append((param, label))

    if not available:
        st.warning("No removal curves are available. Make sure the dataset contains a valid baseline and at least two alum doses.")
        return

    label_to_param = {label: param for param, label in available}

    c1, c2 = st.columns([2, 1])
    with c1:
        selected_label = st.selectbox("Optimization parameter", list(label_to_param.keys()), index=0, key="optimal_parameter_selector")
    with c2:
        threshold = st.number_input("Marginal gain threshold (%/mg/L)", min_value=0.0, max_value=10.0, value=1.0, step=0.25, key="optimal_threshold_input")

    param = label_to_param[selected_label]
    result, curve = compute_derivative_points(df, param, threshold)
    if result is None or curve.empty:
        st.warning("Not enough data to calculate an optimal dose.")
        return

    consensus = method_consensus(result)
    quality = classify_data_quality(curve)

    st.subheader("Method Comparison")
    comparison_table = pd.DataFrame({
        "Method": [
            "Maximum First Derivative",
            "Diminishing Returns / Second Derivative",
            f"Marginal Gain Threshold ≤ {threshold:.2f}%/mg",
        ],
        "Dose (mg/L)": [result["significant_dose"], result["diminishing_dose"], result["threshold_dose"]],
        "Interpretation": [
            "Steepest improvement in removal",
            "Strongest reduction in marginal benefit",
            "First dose at or below the selected marginal gain threshold",
        ]
    })
    st.dataframe(comparison_table, use_container_width=True)
    if consensus["consensus_dose"] is not None:
        st.success(consensus["agreement_text"])
    else:
        st.warning(consensus["agreement_text"])

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card(f"{result['significant_dose']:.2f} mg/L", "First Derivative", "metric-card")
    with c2:
        metric_card(f"{result['diminishing_dose']:.2f} mg/L", "Diminishing Returns", "metric-card-red")
    with c3:
        metric_card(f"{result['threshold_dose']:.2f} mg/L", f"Threshold ≤ {threshold:.2f}%/mg", "metric-card-green")
    with c4:
        metric_card(quality, "Curve Quality", "metric-card-blue")

    fig = px.line(
        curve, x="alum_dose", y="mean_removal", markers=True, error_y="sd_removal",
        title=f"Optimal Alum Dose Based on {selected_label} Removal",
        labels={"alum_dose": "Alum Dose (mg/L)", "mean_removal": f"Mean {selected_label} Removal (%)", "sd_removal": "Standard Deviation"},
        hover_data=["n", "first_derivative", "second_derivative"]
    )
    fig.update_traces(line=dict(width=3), marker=dict(size=10))
    fig.add_vline(x=result["significant_dose"], line_dash="dash", line_color="black", annotation_text=f"First derivative: {result['significant_dose']:.2f}", annotation_position="top left")
    fig.add_vline(x=result["diminishing_dose"], line_dash="dash", line_color="red", annotation_text=f"Diminishing returns: {result['diminishing_dose']:.2f}", annotation_position="top right")
    fig.add_vline(x=result["threshold_dose"], line_dash="dot", line_color="green", annotation_text=f"Threshold: {result['threshold_dose']:.2f}", annotation_position="bottom right")
    render_plot(fig, "optimal_dose_curve")

    st.subheader("Replicate Variability by Dose")
    replicate_table = curve[["alum_dose", "mean_removal", "sd_removal", "n", "first_derivative", "second_derivative"]].copy()
    replicate_table = replicate_table.rename(columns={
        "alum_dose": "Alum Dose (mg/L)",
        "mean_removal": "Mean Removal (%)",
        "sd_removal": "Standard Deviation",
        "n": "Replicates (n)",
        "first_derivative": "First Derivative (%/mg)",
        "second_derivative": "Second Derivative",
    })
    st.dataframe(replicate_table, use_container_width=True)

    st.subheader("Threshold Sensitivity")
    s1, s2, s3 = st.columns(3)
    with s1:
        threshold_min = st.number_input("Sensitivity range minimum (%/mg)", min_value=0.0, max_value=10.0, value=0.5, step=0.25, key="sensitivity_min")
    with s2:
        threshold_max = st.number_input("Sensitivity range maximum (%/mg)", min_value=0.0, max_value=10.0, value=3.0, step=0.25, key="sensitivity_max")
    with s3:
        threshold_step = st.number_input("Sensitivity step (%/mg)", min_value=0.1, max_value=5.0, value=0.5, step=0.1, key="sensitivity_step")

    if threshold_max < threshold_min:
        st.error("The maximum sensitivity threshold must be greater than or equal to the minimum.")
    else:
        thresholds = []
        current = float(threshold_min)
        while current <= float(threshold_max) + 1e-9:
            thresholds.append(round(current, 6))
            current += float(threshold_step)
        sensitivity_df = threshold_sensitivity_table(df, param, thresholds)
        if not sensitivity_df.empty:
            st.dataframe(sensitivity_df, use_container_width=True)
            plot_sensitivity_analysis(sensitivity_df)
            unique_doses = sensitivity_df["threshold_dose_mg_L"].dropna().nunique()
            if unique_doses == 1:
                stable_dose = sensitivity_df["threshold_dose_mg_L"].dropna().iloc[0]
                st.success(f"The threshold recommendation is robust across the selected range: {stable_dose:.2f} mg/L.")
            elif unique_doses <= 2:
                st.info("The recommendation is moderately robust: only two doses are selected across the tested threshold range.")
            else:
                st.warning("The recommended dose is sensitive to the threshold choice. This should be discussed before standardizing the method.")

    st.subheader("Automatic Jar Test Summary")
    summary_text = automatic_test_summary(df, param, selected_label, threshold, result, curve)
    st.markdown(summary_text)
    st.download_button("Download Optimization Summary", summary_text.encode("utf-8"), file_name=f"WRAP_{param}_optimal_dose_summary.md", mime="text/markdown", key="download_optimal_summary")

    st.markdown(f"""
    **Mathematical interpretation**

    - **First derivative / marginal gain:** ΔRemoval% ÷ ΔAlum dose. It identifies where the removal curve improves fastest.
    - **Second derivative:** ΔMarginal gain ÷ ΔAlum dose. It estimates where marginal benefits begin to decline.
    - **Marginal-gain threshold:** the threshold dose is the first dose where gain is no more than **{threshold:.2f}% removal per mg/L alum**.
    - **Method consensus:** agreement between methods strengthens confidence in the selected operating dose.
    """)



def add_dbp_step_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add DBP-specific step metrics for TTHMs and THAAs.

    For each jar-test group:
    - Absolute concentration: original measured value
    - Relative removal/change: already calculated from the lowest alum dose baseline
    - Step-to-step change (%): relative change from the previous alum dose
    - Marginal gain per mg/L: step-to-step change divided by alum-dose increment
    """
    if df is None or df.empty:
        return df

    df = df.copy()
    dbp_params = [p for p in ["tthms", "thaas"] if p in df.columns]

    if not dbp_params or "alum_dose" not in df.columns:
        return df

    group_cols = [c for c in ["sample_date", "test", "aim_ph"] if c in df.columns]
    if not group_cols:
        group_cols = ["__all__"]
        df["__all__"] = "all"

    for param in dbp_params:
        df[f"{param}_step_change_percent"] = pd.NA
        df[f"{param}_marginal_gain_per_mg"] = pd.NA

    for _, group in df.groupby(group_cols, dropna=False):
        group = group.copy()
        group["_dose_numeric"] = pd.to_numeric(group["alum_dose"], errors="coerce")

        for param in dbp_params:
            group["_param_numeric"] = pd.to_numeric(group[param], errors="coerce")
            valid = group.dropna(subset=["_dose_numeric", "_param_numeric"]).copy()

            if valid.empty:
                continue

            # Aggregate replicate measurements at the same dose.
            dose_curve = (
                valid.groupby("_dose_numeric", as_index=False)
                .agg(mean_value=("_param_numeric", "mean"))
                .sort_values("_dose_numeric")
            )

            dose_curve["previous_value"] = dose_curve["mean_value"].shift(1)
            dose_curve["previous_dose"] = dose_curve["_dose_numeric"].shift(1)
            dose_curve["dose_step"] = dose_curve["_dose_numeric"] - dose_curve["previous_dose"]

            dose_curve["step_change_percent"] = (
                (dose_curve["previous_value"] - dose_curve["mean_value"])
                / dose_curve["previous_value"]
            ) * 100

            dose_curve["marginal_gain_per_mg"] = (
                dose_curve["step_change_percent"] / dose_curve["dose_step"]
            )

            step_map = dict(zip(dose_curve["_dose_numeric"], dose_curve["step_change_percent"]))
            gain_map = dict(zip(dose_curve["_dose_numeric"], dose_curve["marginal_gain_per_mg"]))

            valid_indices = valid.index
            valid_doses = valid["_dose_numeric"]

            df.loc[valid_indices, f"{param}_step_change_percent"] = valid_doses.map(step_map)
            df.loc[valid_indices, f"{param}_marginal_gain_per_mg"] = valid_doses.map(gain_map)

    if "__all__" in df.columns:
        df = df.drop(columns=["__all__"])

    for param in dbp_params:
        df[f"{param}_step_change_percent"] = pd.to_numeric(
            df[f"{param}_step_change_percent"], errors="coerce"
        )
        df[f"{param}_marginal_gain_per_mg"] = pd.to_numeric(
            df[f"{param}_marginal_gain_per_mg"], errors="coerce"
        )

    return df


def dbp_analysis_module(df: pd.DataFrame):
    """
    Dedicated DBP analysis view with four requested modes:
    1. Absolute concentration
    2. Relative removal/change from lowest alum dose
    3. Step-to-step change
    4. Marginal gain per mg/L alum
    """
    if df is None or df.empty:
        st.warning("No data available.")
        return

    available = []
    if "tthms" in df.columns:
        available.append(("tthms", "TTHMs"))
    if "thaas" in df.columns:
        available.append(("thaas", "THAAs"))

    if not available:
        st.warning("No TTHMs or THAAs data were found in the uploaded dataset.")
        return

    label_to_param = {label: param for param, label in available}

    c1, c2, c3 = st.columns(3)
    with c1:
        selected_label = st.selectbox(
            "DBP parameter",
            list(label_to_param.keys()),
            key="dbp_parameter_selector"
        )
    with c2:
        mode = st.selectbox(
            "DBP analysis mode",
            [
                "Absolute Concentration",
                "Relative Removal from Lowest Dose",
                "Step-to-Step Change",
                "Marginal Gain per mg/L Alum"
            ],
            key="dbp_mode_selector"
        )
    with c3:
        color_options = available_color_columns(df)
        selected_color = st.selectbox(
            "Color points by",
            color_options,
            index=default_color_index(color_options, preferred="ph_bin"),
            key="dbp_color_selector"
        )

    param = label_to_param[selected_label]

    mode_map = {
        "Absolute Concentration": (
            param,
            f"{selected_label} vs Alum Dose",
            selected_label
        ),
        "Relative Removal from Lowest Dose": (
            f"{param}_removal_percent",
            f"{selected_label} Relative Removal vs Alum Dose",
            f"{selected_label} relative removal (%)"
        ),
        "Step-to-Step Change": (
            f"{param}_step_change_percent",
            f"{selected_label} Step-to-Step Change vs Alum Dose",
            f"{selected_label} step change (%)"
        ),
        "Marginal Gain per mg/L Alum": (
            f"{param}_marginal_gain_per_mg",
            f"{selected_label} Marginal Gain vs Alum Dose",
            f"{selected_label} marginal gain (% per mg/L)"
        ),
    }

    y_col, title, y_label = mode_map[mode]

    if y_col not in df.columns or df[y_col].dropna().empty:
        st.warning(
            f"No valid data are available for {mode}. "
            "Check that multiple alum doses and valid DBP measurements exist in the selected filters."
        )
        return

    scatter_plot(
        df,
        "alum_dose",
        y_col,
        title,
        y_label,
        None if selected_color == "None" else selected_color,
        use_line=True
    )

    st.caption(
        "Absolute concentration comes directly from the laboratory dataset. "
        "Relative removal uses the lowest valid alum dose as the baseline. "
        "Step-to-step change compares each dose with the previous dose. "
        "Marginal gain normalizes that step change by the alum-dose increment."
    )


def scatter_plot(df, x_col, y_col, title, y_label=None, color_col=None, use_line=False):
    if df is None or x_col not in df.columns or y_col not in df.columns:
        st.warning(f"Missing required columns for: {title}")
        return

    hover_cols = [
        c for c in [
            "test", "sample", "sample_type", "sample_date", "analysis_date", "aim_ph", "ph_bin",
            "ph", "alum_dose", "doc", "toc", "uv254", "turb", "true_colour",
            "suva", "total_al", "dissolved_al", "tthms", "thaas", "step_uv_rem", "delta_rem",
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
        line_df = aggregate_for_line_plot(
            plot_df,
            x_col=x_col,
            y_col=y_col,
            color_col=color_col if color_col and color_col in plot_df.columns else None
        )

        fig = px.line(
            line_df,
            x=x_col,
            y="mean_value",
            color=color_col if color_col and color_col in line_df.columns else None,
            markers=True,
            title=title,
            category_orders=category_orders,
            labels={
                x_col: "Alum Dose (mg/L)" if x_col == "alum_dose" else x_col,
                "mean_value": y_label if y_label else y_col
            },
            hover_data=["n"]
        )
        fig.update_traces(line=dict(width=3), marker=dict(size=10))

        raw_fig = px.scatter(
            plot_df,
            x=x_col,
            y=y_col,
            color=color_col if color_col and color_col in plot_df.columns else None,
            category_orders=category_orders,
            hover_data=hover_cols,
            labels={
                x_col: "Alum Dose (mg/L)" if x_col == "alum_dose" else x_col,
                y_col: y_label if y_label else y_col
            }
        )
        raw_fig.update_traces(marker=dict(size=8, opacity=0.45, line=dict(width=0.5, color="black")), showlegend=False)
        for trace in raw_fig.data:
            fig.add_trace(trace)

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
            "turb", "true_colour", "suva", "total_al", "dissolved_al", "tthms", "thaas"
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
    return available_parameter_specs(df, include_removal=True)

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
    for base, label, unit in available_parameter_specs(df, include_removal=False):
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


# -------------------- ROBOT DATA HELPERS --------------------
def _robot_read_tabular_file(uploaded_file):
    """Read a robot CSV/Excel export without applying traditional jar-test calculations."""
    filename = uploaded_file.name.lower()
    if filename.endswith(".csv"):
        try:
            return pd.read_csv(uploaded_file, encoding="utf-8-sig")
        except UnicodeDecodeError:
            uploaded_file.seek(0)
            return pd.read_csv(uploaded_file, encoding="latin-1")
    if filename.endswith((".xlsx", ".xls")):
        return pd.read_excel(uploaded_file)
    raise ValueError("Unsupported robot file type. Upload CSV or Excel.")


def _robot_clean_header(value) -> str:
    value = "" if value is None else str(value)
    value = value.replace("\n", " ").replace("\r", " ")
    value = re.sub(r"\s+", " ", value).strip()
    return value


def _robot_find_column(columns, patterns):
    for col in columns:
        normalized = _robot_clean_header(col).lower()
        if any(re.search(pattern, normalized) for pattern in patterns):
            return col
    return None


def load_robot_file(uploaded_file):
    """
    Load the wide MANTECH/robot export as-is.

    This loader is intentionally separate from load_file() so the traditional
    jar-test workflow, column normalization, and removal calculations remain unchanged.
    """
    try:
        df = _robot_read_tabular_file(uploaded_file)
        df = df.copy()
        df.columns = [_robot_clean_header(col) for col in df.columns]
        df = df.dropna(axis=1, how="all").dropna(axis=0, how="all").reset_index(drop=True)

        unnamed = [col for col in df.columns if not col or col.lower().startswith("unnamed")]
        if unnamed:
            df = df.drop(columns=unnamed)

        # Parse likely date/time metadata columns.
        for col in df.columns:
            name = col.lower()
            if any(token in name for token in ["date started", "date completed", "measurement time", "start time", "end time", "timestamp"]):
                converted = pd.to_datetime(df[col], errors="coerce")
                if converted.notna().sum() > 0:
                    df[col] = converted

        # Convert columns that are predominantly numeric, while preserving text metadata.
        for col in df.columns:
            if pd.api.types.is_datetime64_any_dtype(df[col]):
                continue
            non_null = df[col].notna().sum()
            if non_null == 0:
                continue
            cleaned = df[col].astype(str).str.replace(",", "", regex=False).str.strip()
            converted = pd.to_numeric(cleaned, errors="coerce")
            if converted.notna().sum() >= max(1, int(non_null * 0.70)):
                df[col] = converted

        sample_col = _robot_find_column(
            df.columns,
            [r"^sample$", r"^sample name$", r"^sample id$", r"^test$", r"^test name$", r"^run id$", r"^run$"],
        )

        base_ids = []
        for idx, row in df.iterrows():
            if sample_col is not None and pd.notna(row.get(sample_col)):
                base = str(row.get(sample_col)).strip()
            else:
                base = f"Robot Test {idx + 1}"
            base_ids.append(base or f"Robot Test {idx + 1}")

        counts = {}
        unique_ids = []
        for base in base_ids:
            counts[base] = counts.get(base, 0) + 1
            suffix = counts[base]
            unique_ids.append(base if suffix == 1 else f"{base} | Run {suffix}")

        df.insert(0, "robot_test_id", unique_ids)
        df.insert(1, "robot_row_number", range(1, len(df) + 1))
        return df

    except Exception as exc:
        st.error(f"Error loading robot file: {exc}")
        return None


def _robot_parameter_from_column(column_name: str):
    """Return a canonical parameter key and display label from a robot export column."""
    name = _robot_clean_header(column_name).lower()

    parameter_patterns = [
        ("conductivity", "Conductivity", [r"\bconductivity\b", r"\bcond\.?\b"]),
        ("turbidity", "Turbidity", [r"\bturbidity\b", r"\bturb\.?\b"]),
        ("temperature", "Temperature", [r"\btemperature\b", r"\btemp\.?\b"]),
        ("uv254", "UV254", [r"\buv\s*254\b"]),
        ("doc", "DOC", [r"\bdoc\b"]),
        ("toc", "TOC", [r"\btoc\b"]),
        ("cod", "COD", [r"\bcod\b", r"\bpecod\b"]),
        ("ph", "pH", [r"\bp\s*h\b"]),
        ("colour", "Colour", [r"\bcolou?r\b"]),
        ("alkalinity", "Alkalinity", [r"\balkalinity\b"]),
        ("zeta", "Zeta Potential", [r"\bzeta\b"]),
        ("aluminum", "Aluminum", [r"\balumin(?:um|ium)\b", r"\btotal al\b", r"\bdissolved al\b"]),
        ("iron", "Iron", [r"\biron\b", r"\bfe\b"]),
        ("manganese", "Manganese", [r"\bmanganese\b", r"\bmn\b"]),
    ]

    for key, label, patterns in parameter_patterns:
        if any(re.search(pattern, name) for pattern in patterns):
            return key, label
    return None, None


def _robot_time_from_column(column_name: str):
    """Extract an elapsed time from headers such as 'RPM1 pH 2min'."""
    name = _robot_clean_header(column_name).lower()
    patterns = [
        (r"(?<!\d)(\d+(?:\.\d+)?)\s*(?:min|mins|minute|minutes)\b", 1.0),
        (r"(?<!\d)(\d+(?:\.\d+)?)\s*(?:sec|secs|second|seconds)\b", 1.0 / 60.0),
        (r"(?<!\d)(\d+(?:\.\d+)?)\s*(?:hr|hrs|hour|hours)\b", 60.0),
    ]
    for pattern, multiplier in patterns:
        match = re.search(pattern, name)
        if match:
            return float(match.group(1)) * multiplier
    return None


def _robot_column_descriptor(column_name: str):
    """Describe a wide robot measurement column without assuming fixed time points."""
    original = _robot_clean_header(column_name)
    name = original.lower()
    parameter, parameter_label = _robot_parameter_from_column(original)
    if parameter is None:
        return None

    # Exclude date/time metadata columns that happen to contain a parameter-like token.
    if any(token in name for token in ["measurement time", "date started", "date completed"]):
        return None

    if re.search(r"\b(initial|raw|baseline)\b", name):
        phase = "Initial"
    elif re.search(r"\b(final|settling|settled)\b", name):
        phase = "Final / Settling"
    elif re.search(r"\b(?:rpm\s*[0-9]*|mix(?:ing)?|stir(?:ring)?)\b", name):
        phase = "Mixing"
    else:
        phase = "Unstaged"

    elapsed_min = _robot_time_from_column(original)
    if phase == "Initial" and elapsed_min is None:
        elapsed_min = 0.0

    rpm_match = re.search(r"\brpm\s*([0-9]+)\b", name)
    rpm_stage = int(rpm_match.group(1)) if rpm_match else None

    # Replicate suffix, e.g. Initial Turbidity 1 or Settling Turbidity 3.
    scrubbed = re.sub(r"\d+(?:\.\d+)?\s*(?:min|mins|minute|minutes|sec|secs|second|seconds|hr|hrs|hour|hours)\b", "", name)
    scrubbed = re.sub(r"\brpm\s*[0-9]+\b", "", scrubbed)
    replicate_match = re.search(r"(?:^|\s)([1-9][0-9]*)\s*$", scrubbed)
    replicate = int(replicate_match.group(1)) if replicate_match else None

    return {
        "source_column": original,
        "parameter": parameter,
        "parameter_label": parameter_label,
        "phase": phase,
        "elapsed_min": elapsed_min,
        "rpm_stage": rpm_stage,
        "replicate": replicate,
    }


def _robot_rpm_columns(df: pd.DataFrame):
    mapping = {}
    for col in df.columns:
        match = re.search(r"\bstirring\s+rpm\s*([0-9]+)\b", _robot_clean_header(col).lower())
        if match:
            mapping[int(match.group(1))] = col
    return mapping


def _robot_settling_time_column(df: pd.DataFrame):
    return _robot_find_column(
        df.columns,
        [r"final settling time", r"settling time.*min", r"settling time"],
    )


def robot_to_long(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert a wide MANTECH-style robot export into a dynamic long time-series table.

    Time points are parsed from the column headers, so 2, 4, 6 minutes are not
    hard-coded and each test may contain a different timeline.
    """
    if df is None or df.empty:
        return pd.DataFrame()

    descriptors = []
    for col in df.columns:
        descriptor = _robot_column_descriptor(col)
        if descriptor is not None:
            descriptors.append(descriptor)

    if not descriptors:
        return pd.DataFrame()

    rpm_columns = _robot_rpm_columns(df)
    settling_time_col = _robot_settling_time_column(df)
    records = []

    metadata_candidates = [
        col for col in df.columns
        if col not in {d["source_column"] for d in descriptors}
        and col not in ["robot_row_number"]
    ]

    for row_index, row in df.iterrows():
        test_id = row.get("robot_test_id", f"Robot Test {row_index + 1}")
        settling_duration = None
        if settling_time_col is not None:
            settling_duration = pd.to_numeric(pd.Series([row.get(settling_time_col)]), errors="coerce").iloc[0]
            if pd.isna(settling_duration):
                settling_duration = None

        row_records = []
        for descriptor in descriptors:
            col = descriptor["source_column"]
            value = pd.to_numeric(pd.Series([row.get(col)]), errors="coerce").iloc[0]
            if pd.isna(value):
                continue

            rpm_setpoint = None
            rpm_stage = descriptor["rpm_stage"]
            if rpm_stage in rpm_columns:
                rpm_setpoint = pd.to_numeric(pd.Series([row.get(rpm_columns[rpm_stage])]), errors="coerce").iloc[0]
                if pd.isna(rpm_setpoint):
                    rpm_setpoint = None

            record = {
                "robot_test_id": test_id,
                "robot_row_number": row.get("robot_row_number", row_index + 1),
                **descriptor,
                "value": float(value),
                "rpm_setpoint": rpm_setpoint,
                "settling_duration_min": settling_duration,
            }

            # Carry compact metadata useful for tooltips and reports.
            for meta_col in metadata_candidates:
                meta_name = _robot_clean_header(meta_col).lower()
                if any(token in meta_name for token in ["sample", "template", "date started", "date completed", "test", "run"]):
                    record[meta_col] = row.get(meta_col)

            row_records.append(record)

        # Final/settling measurements frequently have no time in the column name.
        explicit_times = [r["elapsed_min"] for r in row_records if r["elapsed_min"] is not None]
        max_explicit = max(explicit_times) if explicit_times else None
        for record in row_records:
            if record["phase"] == "Final / Settling" and record["elapsed_min"] is None:
                if max_explicit is not None and settling_duration is not None:
                    record["elapsed_min"] = float(max_explicit) + float(settling_duration)
                elif max_explicit is not None:
                    record["elapsed_min"] = float(max_explicit)

            elapsed = record["elapsed_min"]
            if record["phase"] == "Initial":
                record["time_label"] = "Initial"
            elif record["phase"] == "Final / Settling":
                record["time_label"] = f"Final ({elapsed:g} min)" if elapsed is not None else "Final"
            elif elapsed is not None:
                record["time_label"] = f"{elapsed:g} min"
            else:
                record["time_label"] = record["phase"]

            record["phase_order"] = {
                "Initial": 0,
                "Mixing": 1,
                "Final / Settling": 2,
                "Unstaged": 3,
            }.get(record["phase"], 9)

        records.extend(row_records)

    long_df = pd.DataFrame(records)
    if long_df.empty:
        return long_df

    long_df["elapsed_min"] = pd.to_numeric(long_df["elapsed_min"], errors="coerce")
    long_df["value"] = pd.to_numeric(long_df["value"], errors="coerce")
    long_df["replicate"] = pd.to_numeric(long_df["replicate"], errors="coerce").astype("Int64")
    long_df["rpm_stage"] = pd.to_numeric(long_df["rpm_stage"], errors="coerce").astype("Int64")
    long_df["analysis_order"] = long_df["elapsed_min"].fillna(1e9) + long_df["phase_order"] * 1e-6
    return long_df.sort_values(["robot_test_id", "parameter", "analysis_order", "replicate"], na_position="last").reset_index(drop=True)


def aggregate_robot_timepoints(long_df: pd.DataFrame, parameter=None, test_ids=None) -> pd.DataFrame:
    if long_df is None or long_df.empty:
        return pd.DataFrame()

    work = long_df.copy()
    if parameter is not None:
        work = work[work["parameter"] == parameter]
    if test_ids:
        work = work[work["robot_test_id"].isin(test_ids)]
    work = work.dropna(subset=["value"])
    if work.empty:
        return pd.DataFrame()

    group_cols = [
        "robot_test_id", "parameter", "parameter_label", "phase",
        "elapsed_min", "time_label", "phase_order", "rpm_stage", "rpm_setpoint"
    ]
    group_cols = [col for col in group_cols if col in work.columns]

    aggregated = (
        work.groupby(group_cols, dropna=False, as_index=False)
        .agg(mean_value=("value", "mean"), sd_value=("value", "std"), n=("value", "count"))
    )
    aggregated["analysis_order"] = aggregated["elapsed_min"].fillna(1e9) + aggregated["phase_order"] * 1e-6
    return aggregated.sort_values(["robot_test_id", "analysis_order"]).reset_index(drop=True)


def robot_parameter_options(long_df: pd.DataFrame):
    if long_df is None or long_df.empty:
        return []
    options = (
        long_df[["parameter", "parameter_label"]]
        .drop_duplicates()
        .sort_values("parameter_label")
    )
    return list(options.itertuples(index=False, name=None))


def _robot_choose_point(points: pd.DataFrame, selector: str, target_time=None, tolerance=None):
    """Choose one aggregated point from one test without assuming common fixed times."""
    if points is None or points.empty:
        return None

    points = points.dropna(subset=["mean_value"]).copy()
    timed = points.dropna(subset=["elapsed_min"]).sort_values(["elapsed_min", "phase_order"])
    if points.empty:
        return None

    if selector == "Initial":
        candidates = points[points["phase"] == "Initial"]
        if candidates.empty:
            candidates = timed.head(1)
    elif selector == "Final":
        candidates = points[points["phase"] == "Final / Settling"]
        if candidates.empty:
            candidates = timed.tail(1)
    elif selector == "First available":
        candidates = timed.head(1)
    elif selector == "Last available":
        candidates = timed.tail(1)
    elif selector == "Middle available":
        if timed.empty:
            return None
        minimum = timed["elapsed_min"].min()
        maximum = timed["elapsed_min"].max()
        midpoint = (minimum + maximum) / 2.0
        index = (timed["elapsed_min"] - midpoint).abs().idxmin()
        candidates = timed.loc[[index]]
    elif selector == "Target time":
        if timed.empty or target_time is None:
            return None
        differences = (timed["elapsed_min"] - float(target_time)).abs()
        index = differences.idxmin()
        if tolerance is not None and differences.loc[index] > float(tolerance):
            return None
        candidates = timed.loc[[index]]
    else:
        return None

    if candidates is None or candidates.empty:
        return None

    # If several replicate-aggregated rows describe the same endpoint, average them.
    return {
        "value": float(candidates["mean_value"].mean()),
        "elapsed_min": float(candidates["elapsed_min"].dropna().mean()) if candidates["elapsed_min"].notna().any() else None,
        "phase": ", ".join(sorted(candidates["phase"].astype(str).unique())),
        "time_label": ", ".join(sorted(candidates["time_label"].astype(str).unique())),
        "n": int(candidates["n"].sum()) if "n" in candidates.columns else len(candidates),
    }


def build_robot_point_comparison(
    long_df: pd.DataFrame,
    parameter: str,
    selector_a: str,
    selector_b: str,
    target_a=None,
    target_b=None,
    tolerance=None,
    test_ids=None,
):
    aggregated = aggregate_robot_timepoints(long_df, parameter=parameter, test_ids=test_ids)
    if aggregated.empty:
        return pd.DataFrame()

    rows = []
    for test_id, points in aggregated.groupby("robot_test_id", dropna=False):
        point_a = _robot_choose_point(points, selector_a, target_a, tolerance)
        point_b = _robot_choose_point(points, selector_b, target_b, tolerance)
        if point_a is None or point_b is None:
            continue

        absolute_change = point_b["value"] - point_a["value"]
        percent_change = None
        if point_a["value"] != 0:
            percent_change = (absolute_change / point_a["value"]) * 100

        rows.append({
            "robot_test_id": test_id,
            "point_a": selector_a,
            "point_a_time_min": point_a["elapsed_min"],
            "point_a_phase": point_a["phase"],
            "point_a_value": point_a["value"],
            "point_b": selector_b,
            "point_b_time_min": point_b["elapsed_min"],
            "point_b_phase": point_b["phase"],
            "point_b_value": point_b["value"],
            "absolute_change": absolute_change,
            "percent_change": percent_change,
        })

    return pd.DataFrame(rows)


def robot_comparison_controls(long_df: pd.DataFrame, parameter: str, test_ids=None, key_prefix="robot_compare"):
    modes = {
        "Initial vs Final": ("Initial", "Final"),
        "Initial vs Middle Point": ("Initial", "Middle available"),
        "Initial vs Selected Time": ("Initial", "Target time"),
        "Selected Time A vs Selected Time B": ("Target time", "Target time"),
        "First Available vs Last Available": ("First available", "Last available"),
    }

    mode = st.selectbox("Comparison mode", list(modes.keys()), key=f"{key_prefix}_mode")
    selector_a, selector_b = modes[mode]

    parameter_times = long_df.loc[
        (long_df["parameter"] == parameter) & long_df["elapsed_min"].notna(),
        "elapsed_min",
    ]
    default_min = float(parameter_times.min()) if not parameter_times.empty else 0.0
    default_max = float(parameter_times.max()) if not parameter_times.empty else 1.0
    midpoint = (default_min + default_max) / 2.0

    target_a = None
    target_b = None
    if selector_a == "Target time" and selector_b == "Target time":
        c1, c2 = st.columns(2)
        with c1:
            target_a = st.number_input("Target time A (min)", value=float(default_min), step=0.5, key=f"{key_prefix}_target_a")
        with c2:
            target_b = st.number_input("Target time B (min)", value=float(default_max), step=0.5, key=f"{key_prefix}_target_b")
    elif selector_b == "Target time":
        target_b = st.number_input("Target comparison time (min)", value=float(midpoint), step=0.5, key=f"{key_prefix}_target_b")

    use_nearest = st.checkbox(
        "Use the nearest available time when an exact time does not exist",
        value=True,
        key=f"{key_prefix}_nearest",
    )
    tolerance = None
    if not use_nearest:
        tolerance = st.number_input(
            "Maximum matching tolerance (min)",
            min_value=0.0,
            value=0.5,
            step=0.25,
            key=f"{key_prefix}_tolerance",
        )

    comparison = build_robot_point_comparison(
        long_df,
        parameter,
        selector_a,
        selector_b,
        target_a=target_a,
        target_b=target_b,
        tolerance=tolerance,
        test_ids=test_ids,
    )
    return mode, comparison


def plot_robot_time_series(long_df: pd.DataFrame, parameter: str, test_ids=None, show_raw=False, key_prefix="robot_ts"):
    aggregated = aggregate_robot_timepoints(long_df, parameter=parameter, test_ids=test_ids)
    timed = aggregated.dropna(subset=["elapsed_min", "mean_value"]).copy()
    if timed.empty:
        st.warning("No timed measurements were found for this parameter.")
        return None

    parameter_label = timed["parameter_label"].iloc[0]
    fig = px.line(
        timed,
        x="elapsed_min",
        y="mean_value",
        color="robot_test_id",
        markers=True,
        error_y="sd_value",
        hover_data=["phase", "time_label", "n", "rpm_stage", "rpm_setpoint"],
        title=f"{parameter_label} Through the Robot Test Timeline",
        labels={
            "elapsed_min": "Elapsed Time (min)",
            "mean_value": parameter_label,
            "robot_test_id": "Robot Test",
            "sd_value": "Standard deviation",
        },
    )
    fig.update_traces(line=dict(width=3), marker=dict(size=9))

    if show_raw:
        raw = long_df[long_df["parameter"] == parameter].copy()
        if test_ids:
            raw = raw[raw["robot_test_id"].isin(test_ids)]
        raw = raw.dropna(subset=["elapsed_min", "value"])
        raw_fig = px.scatter(
            raw,
            x="elapsed_min",
            y="value",
            color="robot_test_id",
            hover_data=["phase", "source_column", "replicate", "rpm_setpoint"],
        )
        raw_fig.update_traces(marker=dict(size=7, opacity=0.35), showlegend=False)
        for trace in raw_fig.data:
            fig.add_trace(trace)

    fig.update_layout(height=560, plot_bgcolor="white", paper_bgcolor="white")
    render_plot(fig, key_prefix)
    return fig


def plot_robot_heatmap(long_df: pd.DataFrame, parameter: str, test_ids=None, key_prefix="robot_heatmap"):
    aggregated = aggregate_robot_timepoints(long_df, parameter=parameter, test_ids=test_ids)
    timed = aggregated.dropna(subset=["elapsed_min", "mean_value"]).copy()
    if timed.empty:
        st.warning("No timed measurements were found for this heatmap.")
        return None

    pivot = timed.pivot_table(
        index="robot_test_id",
        columns="elapsed_min",
        values="mean_value",
        aggfunc="mean",
    ).sort_index(axis=1)

    parameter_label = timed["parameter_label"].iloc[0]
    fig = px.imshow(
        pivot,
        aspect="auto",
        color_continuous_scale="Viridis",
        title=f"{parameter_label} Heatmap by Test and Time",
        labels={
            "x": "Elapsed Time (min)",
            "y": "Robot Test",
            "color": parameter_label,
        },
    )
    fig.update_layout(height=max(460, 70 + len(pivot.index) * 42))
    render_plot(fig, key_prefix)
    return fig


def plot_robot_comparison(comparison_df: pd.DataFrame, parameter_label: str, title: str, key_prefix="robot_compare_plot"):
    if comparison_df is None or comparison_df.empty:
        st.warning("No tests contained both requested comparison points.")
        return None

    paired = comparison_df[["robot_test_id", "point_a_value", "point_b_value"]].melt(
        id_vars="robot_test_id",
        value_vars=["point_a_value", "point_b_value"],
        var_name="comparison_point",
        value_name="value",
    )
    paired["comparison_point"] = paired["comparison_point"].map({
        "point_a_value": "Point A",
        "point_b_value": "Point B",
    })

    fig = px.line(
        paired,
        x="comparison_point",
        y="value",
        color="robot_test_id",
        markers=True,
        title=f"{parameter_label}: {title}",
        labels={"comparison_point": "Comparison Point", "value": parameter_label, "robot_test_id": "Robot Test"},
    )
    fig.update_traces(line=dict(width=2.5), marker=dict(size=10))
    fig.update_layout(height=520, plot_bgcolor="white", paper_bgcolor="white")
    render_plot(fig, key_prefix)

    percent_fig = px.bar(
        comparison_df,
        x="robot_test_id",
        y="percent_change",
        title=f"Percent Change — {title}",
        labels={"robot_test_id": "Robot Test", "percent_change": "Change (%)"},
    )
    percent_fig.update_layout(height=430, plot_bgcolor="white", paper_bgcolor="white")
    render_plot(percent_fig, f"{key_prefix}_percent")
    return fig


def generate_robot_html_report(
    raw_df: pd.DataFrame,
    long_df: pd.DataFrame,
    parameter: str,
    test_ids=None,
    comparison_df=None,
    comparison_title="Initial vs Final",
):
    """Create a robot-only report with timeline, heatmap, and selected point comparison."""
    if raw_df is None or raw_df.empty or long_df is None or long_df.empty:
        return "<html><body><h1>No robot data available</h1></body></html>"

    filtered_long = long_df.copy()
    if test_ids:
        filtered_long = filtered_long[filtered_long["robot_test_id"].isin(test_ids)]

    options = dict(robot_parameter_options(filtered_long))
    parameter_label = options.get(parameter, parameter)
    aggregated = aggregate_robot_timepoints(filtered_long, parameter=parameter)
    timed = aggregated.dropna(subset=["elapsed_min", "mean_value"]).copy()

    plotly_blocks = []
    if not timed.empty:
        time_fig = px.line(
            timed,
            x="elapsed_min",
            y="mean_value",
            color="robot_test_id",
            markers=True,
            error_y="sd_value",
            hover_data=["phase", "time_label", "n", "rpm_setpoint"],
            title=f"{parameter_label} Through the Robot Test Timeline",
            labels={"elapsed_min": "Elapsed Time (min)", "mean_value": parameter_label, "robot_test_id": "Robot Test"},
        )
        time_fig.update_traces(line=dict(width=3), marker=dict(size=9))
        plotly_blocks.append(time_fig.to_html(full_html=False, include_plotlyjs="cdn"))

        pivot = timed.pivot_table(index="robot_test_id", columns="elapsed_min", values="mean_value", aggfunc="mean").sort_index(axis=1)
        heatmap_fig = px.imshow(
            pivot,
            aspect="auto",
            color_continuous_scale="Viridis",
            title=f"{parameter_label} Heatmap by Test and Time",
            labels={"x": "Elapsed Time (min)", "y": "Robot Test", "color": parameter_label},
        )
        plotly_blocks.append(heatmap_fig.to_html(full_html=False, include_plotlyjs=False))

    comparison_html = ""
    if comparison_df is not None and not comparison_df.empty:
        paired = comparison_df[["robot_test_id", "point_a_value", "point_b_value"]].melt(
            id_vars="robot_test_id",
            value_vars=["point_a_value", "point_b_value"],
            var_name="comparison_point",
            value_name="value",
        )
        paired["comparison_point"] = paired["comparison_point"].map({"point_a_value": "Point A", "point_b_value": "Point B"})
        comparison_fig = px.line(
            paired,
            x="comparison_point",
            y="value",
            color="robot_test_id",
            markers=True,
            title=f"{parameter_label}: {comparison_title}",
            labels={"comparison_point": "Comparison Point", "value": parameter_label, "robot_test_id": "Robot Test"},
        )
        plotly_blocks.append(comparison_fig.to_html(full_html=False, include_plotlyjs=False))
        comparison_html = f"<h2>Selected Point Comparison</h2>{comparison_df.round(4).to_html(index=False)}"

    selected_tests = filtered_long["robot_test_id"].nunique()
    selected_points = filtered_long["elapsed_min"].dropna().nunique()
    selected_parameters = filtered_long["parameter"].nunique()

    charts_html = "\n".join(plotly_blocks)
    return f"""
    <html>
    <head>
        <title>WRAP Robot Time-Series Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 38px; background:#f7f8fb; color:#111; }}
            h1, h2 {{ color:#111; }}
            .summary {{ background:white; border-left:7px solid #FFD200; padding:18px; border-radius:12px; margin-bottom:22px; }}
            .grid {{ display:grid; grid-template-columns:repeat(4,1fr); gap:12px; }}
            .metric {{ background:white; padding:14px; border-radius:10px; border-top:4px solid #FFD200; }}
            table {{ border-collapse:collapse; width:100%; background:white; margin:12px 0 28px 0; }}
            th, td {{ border:1px solid #ddd; padding:7px; font-size:12px; }}
            th {{ background:#FFD200; }}
        </style>
    </head>
    <body>
        <h1>WRAP — Robot Time-Series Report</h1>
        <div class="summary">
            <b>Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br>
            <b>Selected parameter:</b> {parameter_label}<br>
            <b>Comparison:</b> {comparison_title}<br>
            <b>Important:</b> Robot time points are read dynamically from the exported column names; they are not assumed to be fixed.
        </div>
        <div class="grid">
            <div class="metric"><b>{selected_tests}</b><br>Robot tests</div>
            <div class="metric"><b>{selected_parameters}</b><br>Parameters found</div>
            <div class="metric"><b>{selected_points}</b><br>Unique timed points</div>
            <div class="metric"><b>{len(filtered_long)}</b><br>Long-format measurements</div>
        </div>
        <h2>Robot Timeline and Heatmap</h2>
        {charts_html}
        {comparison_html}
        <h2>Normalized Robot Data Preview</h2>
        {filtered_long.head(100).round(4).to_html(index=False)}
        <h2>Original Wide Export Preview</h2>
        {raw_df.head(30).to_html(index=False)}
    </body>
    </html>
    """


def robot_data_module():
    st.header("🤖 Robot Data")
    st.caption("Dynamic analysis of MANTECH/robot exports. Test times may vary from one run to another.")

    uploaded = st.file_uploader(
        "Upload the robot-generated CSV or Excel file",
        type=["csv", "xlsx", "xls"],
        key="robot_upload",
    )

    if uploaded is not None:
        loaded = load_robot_file(uploaded)
        if loaded is not None:
            st.session_state.robot_df = loaded
            st.session_state.robot_long_df = robot_to_long(loaded)

    raw_df = st.session_state.robot_df
    long_df = st.session_state.robot_long_df

    if raw_df is None:
        st.info("No robot data has been uploaded yet.")
        return

    if long_df is None or long_df.empty:
        st.error(
            "The file was loaded, but WRAP could not identify robot measurement columns. "
            "Expected names include combinations such as Initial pH, RPM1 pH 2min, Settling Turbidity, Conductivity, or COD."
        )
        st.dataframe(raw_df.head(50), use_container_width=True)
        return

    parameters = robot_parameter_options(long_df)
    parameter_map = {label: key for key, label in parameters}
    test_options = sorted(long_df["robot_test_id"].dropna().astype(str).unique().tolist())

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card(len(raw_df), "🤖 Robot Tests", "metric-card")
    with c2:
        metric_card(long_df["parameter"].nunique(), "🧪 Parameters Found", "metric-card-blue")
    with c3:
        metric_card(long_df["elapsed_min"].dropna().nunique(), "⏱️ Unique Time Points", "metric-card-green")
    with c4:
        max_time = long_df["elapsed_min"].max()
        metric_card(f"{max_time:g} min" if pd.notna(max_time) else "N/A", "⌛ Maximum Timeline", "metric-card-red")

    st.subheader("Robot Test Filters")
    selected_tests = st.multiselect(
        "Robot tests",
        test_options,
        default=test_options,
        key="robot_test_filter",
    )
    if not selected_tests:
        st.warning("Select at least one robot test.")
        return

    filtered_long = long_df[long_df["robot_test_id"].isin(selected_tests)].copy()

    overview_tab, timeline_tab, heatmap_tab, compare_tab, report_tab = st.tabs([
        "📋 Overview",
        "📈 Time-Series",
        "🧊 Heatmaps",
        "🔍 Point Comparison",
        "📄 Robot Report",
    ])

    with overview_tab:
        st.subheader("Detected Robot Structure")
        structure = (
            filtered_long.groupby(["parameter_label", "phase"], dropna=False)
            .agg(
                measurements=("value", "count"),
                tests=("robot_test_id", "nunique"),
                first_time_min=("elapsed_min", "min"),
                last_time_min=("elapsed_min", "max"),
            )
            .reset_index()
        )
        st.dataframe(structure, use_container_width=True)

        duplicates = (
            filtered_long.groupby(["robot_test_id", "parameter_label", "phase", "elapsed_min"], dropna=False)
            .size()
            .reset_index(name="replicate_count")
        )
        duplicates = duplicates[duplicates["replicate_count"] > 1]
        if duplicates.empty:
            st.info("No repeated measurements were detected at the same test, parameter, phase, and time.")
        else:
            st.markdown("**Detected replicate measurements**")
            st.dataframe(duplicates, use_container_width=True)

        with st.expander("Original robot export"):
            st.dataframe(raw_df[raw_df["robot_test_id"].isin(selected_tests)].head(100), use_container_width=True)
        with st.expander("Normalized long-format robot data"):
            st.dataframe(filtered_long.head(300), use_container_width=True)

    with timeline_tab:
        selected_label = st.selectbox("Parameter", list(parameter_map.keys()), key="robot_ts_parameter")
        selected_parameter = parameter_map[selected_label]
        show_raw = st.checkbox("Show individual replicate points", value=True, key="robot_ts_raw")
        plot_robot_time_series(filtered_long, selected_parameter, selected_tests, show_raw=show_raw, key_prefix="robot_timeline")

        table = aggregate_robot_timepoints(filtered_long, parameter=selected_parameter, test_ids=selected_tests)
        st.markdown("**Aggregated values by available time point**")
        st.dataframe(table, use_container_width=True)

    with heatmap_tab:
        selected_label = st.selectbox("Heatmap parameter", list(parameter_map.keys()), key="robot_heat_parameter")
        selected_parameter = parameter_map[selected_label]
        plot_robot_heatmap(filtered_long, selected_parameter, selected_tests, key_prefix="robot_dynamic_heatmap")
        st.caption(
            "The heatmap uses every elapsed time actually found in the export. Blank cells mean that a test did not contain that exact time point."
        )

    with compare_tab:
        selected_label = st.selectbox("Comparison parameter", list(parameter_map.keys()), key="robot_compare_parameter")
        selected_parameter = parameter_map[selected_label]
        mode, comparison = robot_comparison_controls(
            filtered_long,
            selected_parameter,
            test_ids=selected_tests,
            key_prefix="robot_point_compare",
        )
        if comparison.empty:
            st.warning("No tests contained both requested points under the selected matching rule.")
        else:
            st.session_state.robot_last_comparison = comparison
            st.session_state.robot_last_comparison_title = mode
            plot_robot_comparison(comparison, selected_label, mode, key_prefix="robot_point_comparison")
            st.dataframe(comparison, use_container_width=True)
            st.download_button(
                "Download Point Comparison CSV",
                comparison.to_csv(index=False).encode("utf-8"),
                file_name="WRAP_robot_point_comparison.csv",
                mime="text/csv",
                key="download_robot_comparison",
            )

    with report_tab:
        report_label = st.selectbox("Report parameter", list(parameter_map.keys()), key="robot_report_parameter")
        report_parameter = parameter_map[report_label]
        report_mode, report_comparison = robot_comparison_controls(
            filtered_long,
            report_parameter,
            test_ids=selected_tests,
            key_prefix="robot_report_compare",
        )

        report_html = generate_robot_html_report(
            raw_df[raw_df["robot_test_id"].isin(selected_tests)],
            filtered_long,
            report_parameter,
            test_ids=selected_tests,
            comparison_df=report_comparison,
            comparison_title=report_mode,
        )

        c1, c2 = st.columns(2)
        with c1:
            st.download_button(
                "📄 Download Robot HTML Report",
                report_html.encode("utf-8"),
                file_name="WRAP_robot_time_series_report.html",
                mime="text/html",
                key="download_robot_html_report",
            )
        with c2:
            st.download_button(
                "📊 Download Normalized Robot CSV",
                filtered_long.to_csv(index=False).encode("utf-8"),
                file_name="WRAP_robot_long_format.csv",
                mime="text/csv",
                key="download_robot_long_csv",
            )

        st.info(
            "This report belongs only to the robot workflow. The traditional jar-test report and its calculations remain unchanged."
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
        for target, _label, _axis_label in available_parameter_specs(df, include_removal=True):
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
        <p>This report was generated from uploaded experimental data. Robot integration is pending and will be added once the automated system exports are available.</p>
    </body>
    </html>
    """
    return html

# -------------------- LOGIN --------------------
if not st.session_state.logged_in:
    bg_image = get_base64_image("laboratory_background.jpg")

    if bg_image:
        st.markdown(
            f"""
            <style>
            .stApp {{
                background-image:
                    linear-gradient(rgba(0,0,0,0.52), rgba(0,0,0,0.52)),
                    url("data:image/jpeg;base64,{bg_image}") !important;
                background-size: cover !important;
                background-position: center !important;
                background-repeat: no-repeat !important;
                background-attachment: fixed !important;
            }}

            [data-testid="stHeader"] {{
                background: transparent !important;
            }}

            [data-testid="stToolbar"] {{
                background: transparent !important;
            }}

            /* Small white backgrounds behind the login title and subtitle only. */
            .login-title-badge {{
                display: table !important;
                width: fit-content !important;
                max-width: 100% !important;
                background: rgba(255, 255, 255, 0.92) !important;
                color: #111111 !important;
                -webkit-text-fill-color: #111111 !important;
                padding: 6px 14px 7px 14px !important;
                margin: 8px 0 7px 0 !important;
                border-radius: 10px !important;
                box-shadow: 0 3px 9px rgba(0, 0, 0, 0.22) !important;
                backdrop-filter: blur(2px) !important;
                -webkit-backdrop-filter: blur(2px) !important;
                font-size: clamp(2rem, 3vw, 2.75rem) !important;
                font-weight: 800 !important;
                line-height: 1.16 !important;
            }}

            .login-subtitle-badge {{
                display: table !important;
                width: fit-content !important;
                max-width: 100% !important;
                background: rgba(255, 255, 255, 0.90) !important;
                color: #222222 !important;
                -webkit-text-fill-color: #222222 !important;
                padding: 4px 10px !important;
                margin: 0 0 12px 0 !important;
                border-radius: 8px !important;
                box-shadow: 0 2px 7px rgba(0, 0, 0, 0.20) !important;
                backdrop-filter: blur(2px) !important;
                -webkit-backdrop-filter: blur(2px) !important;
                font-size: 0.95rem !important;
                font-weight: 600 !important;
                line-height: 1.35 !important;
            }}

            /* Small white background only behind the Email and Password labels. */
            [data-testid="stTextInput"] label {{
                display: inline-flex !important;
                width: fit-content !important;
                max-width: max-content !important;
                align-items: center !important;
                background: rgba(255, 255, 255, 0.90) !important;
                padding: 4px 10px !important;
                margin-bottom: 6px !important;
                border-radius: 8px !important;
                box-shadow: 0 2px 7px rgba(0, 0, 0, 0.20) !important;
                backdrop-filter: blur(2px) !important;
                -webkit-backdrop-filter: blur(2px) !important;
            }}

            [data-testid="stTextInput"] label p,
            [data-testid="stTextInput"] label span {{
                color: #111111 !important;
                -webkit-text-fill-color: #111111 !important;
                font-weight: 700 !important;
                margin: 0 !important;
            }}
</style>
            """,
            unsafe_allow_html=True
        )
    else:
        st.warning(
            "Login background image not found. Add 'laboratory_background.jpg' "
            "to the same folder as app.py in your GitHub repository."
        )

    c1, c2, c3 = st.columns([1, 1.2, 1])
    with c2:
        st.image("dalhousie_logo.png", width=330)
        st.markdown(
            """
            <div class="login-title-badge">🔐 WRAP Login</div>
            <div class="login-subtitle-badge">Water Research Analytics Platform</div>
            """,
            unsafe_allow_html=True
        )

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
            "🧬 DBP Analysis",
            "🎯 Optimal Dose Finder",
            "⚗️ pH Analysis",
            "🌡️ Extra Parameters",
            "🧊 Heatmaps",
            "📊 Mean Response",
            "📄 Reports",
            "🤖 Robot Data",
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
st.caption("Manual Jar Tests | Robot Time-Series | Research Analytics")

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

    The platform is designed to support future automated data exports when available.

    The long-term goal is to analyze manual and automated jar-test data in dedicated workflows within one research environment.
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
        (col, f"{label} vs Alum Dose", axis_label)
        for col, label, axis_label in available_parameter_specs(filtered_df, include_removal=True)
        if col not in ["raw_uv254", "raw_alkalinity"]
    ]

    for i in range(0, len(plot_specs), 2):
        cols = st.columns(2)
        for j, col in enumerate(cols):
            if i + j < len(plot_specs):
                y, title, label = plot_specs[i + j]
                with col:
                    scatter_plot(filtered_df, "alum_dose", y, title, label, color_col)

    st.divider()
    st.subheader("🎯 Optimal Alum Dose Finder")
    st.caption(
        "This module standardizes optimal-dose selection using marginal gain, first derivative, and second derivative."
    )
    optimal_dose_module(filtered_df)

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

# -------------------- DBP ANALYSIS --------------------
elif page == "🧬 DBP Analysis":
    st.header("🧬 DBP Analysis")

    df = st.session_state.traditional_df
    if df is None:
        st.warning("Upload traditional jar test data first.")
        st.stop()

    filtered_df = filter_traditional_data(df)
    st.divider()
    dbp_analysis_module(filtered_df)

# -------------------- OPTIMAL DOSE FINDER --------------------
elif page == "🎯 Optimal Dose Finder":
    st.header("🎯 Optimal Alum Dose Finder")

    df = st.session_state.traditional_df
    if df is None:
        st.warning("Upload traditional jar test data first.")
        st.stop()

    filtered_df = filter_traditional_data(df)
    st.divider()
    optimal_dose_module(filtered_df)

    st.divider()
    st.subheader("🔍 Repeated Point Check")
    repeated = duplicate_summary(filtered_df)
    if repeated.empty:
        st.success("No repeated experimental points detected for the selected filters.")
    else:
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
        label: (col, f"{label} Heatmap", axis_label)
        for col, label, axis_label in available_parameter_specs(filtered_df, include_removal=True)
        if col not in ["raw_uv254", "raw_alkalinity", "ph_qc", "step_uv_rem", "delta_rem"]
    }

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
        label: (col, f"Mean {label} Across Different Jar Test Conditions", f"Mean {axis_label}")
        for col, label, axis_label in available_parameter_specs(filtered_df, include_removal=True)
        if col not in ["raw_uv254", "raw_alkalinity", "step_uv_rem", "delta_rem"]
    }

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

    st.info("Optimization reports now include method comparison, replicate variability, threshold sensitivity, and an automatic jar-test summary in the Optimal Dose Finder.")

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
            "total_al", "dissolved_al", "tthms", "thaas"
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
    robot_data_module()

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
    **Expected system:** Automated jar testing system  
    **Current integration mode:** Pending  
    **Available workflow today:** Manual CSV / Excel upload  
    """)

    st.markdown("""
    ### Expected Future Data Flow

    **Current workflow**

    Traditional jar test → CSV / Excel file → WRAP dashboard

    **Future workflow**

    Automated jar testing system → exported data → WRAP dashboard → comparative analytics
    """)

    st.markdown("""
    ### Integration Questions to Confirm

    - Does the automated system export CSV files?
    - Does the instrument software store data in a local database?
    - Is there an available API?
    - Can the MiniHub or software export timestamped sensor readings?
    - Are experiment IDs automatically generated?
    """)

    st.success("WRAP is ready for CSV / Excel based robot data once available.")

    st.caption(f"Last platform check: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
