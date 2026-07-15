
import streamlit as st
import pandas as pd
import plotly.express as px
import base64
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

            /* Glass-style card behind the login form */
            div[data-testid="stVerticalBlock"]:has(input[type="password"]) {{
                background: rgba(255, 255, 255, 0.90) !important;
                border: 1px solid rgba(255, 255, 255, 0.60) !important;
                border-radius: 24px !important;
                padding: 28px 32px 30px 32px !important;
                box-shadow: 0 18px 55px rgba(0, 0, 0, 0.45) !important;
                backdrop-filter: blur(12px) !important;
                -webkit-backdrop-filter: blur(12px) !important;
            }}

            div[data-testid="stVerticalBlock"]:has(input[type="password"]) h1,
            div[data-testid="stVerticalBlock"]:has(input[type="password"]) h2,
            div[data-testid="stVerticalBlock"]:has(input[type="password"]) h3,
            div[data-testid="stVerticalBlock"]:has(input[type="password"]) p,
            div[data-testid="stVerticalBlock"]:has(input[type="password"]) label {{
                color: #111111 !important;
            }}

            div[data-testid="stVerticalBlock"]:has(input[type="password"]) input {{
                background: #ffffff !important;
                color: #111111 !important;
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
            "🧬 DBP Analysis",
            "🎯 Optimal Dose Finder",
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
st.caption("Manual Jar Tests | Future Automated Data | Comparative Analytics")

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
    st.header("🤖 Robot Data")

    st.warning("Robot data connection is not active yet. This module is ready for future exported datasets.")

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
