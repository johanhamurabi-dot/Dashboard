import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# ============================================================
# WRAP v2 - Water Research Analytics Platform
# Dalhousie Water Research | Traditional Jar Tests + Future Robot Integration
# ============================================================

st.set_page_config(
    page_title="WRAP | Dalhousie Water Research",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------- LOGIN CONFIG --------------------
VALID_USER = "fj415321@dal.ca"
VALID_PASSWORD = "JohanHamurabi0727"

# -------------------- STYLE --------------------
st.markdown("""
<style>
.stApp {
    background-color: #f5f6f8;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #050505 0%, #121820 100%);
}

[data-testid="stSidebar"] * {
    color: white !important;
}

.card {
    background: white;
    padding: 22px;
    border-radius: 18px;
    box-shadow: 0 4px 18px rgba(0,0,0,0.08);
    border: 1px solid #e8e8e8;
}

.metric-card {
    background: white;
    padding: 20px;
    border-radius: 18px;
    border-left: 7px solid #FFD200;
    box-shadow: 0 4px 14px rgba(0,0,0,0.08);
}

.big-number {
    font-size: 30px;
    font-weight: 800;
    color: #111111;
}

.small-label {
    font-size: 14px;
    color: #666666;
}

.section-title {
    font-size: 25px;
    font-weight: 800;
    margin-top: 12px;
    margin-bottom: 8px;
}

.warning-box {
    background: #fff8dd;
    border-left: 6px solid #FFD200;
    padding: 16px;
    border-radius: 12px;
}

.success-box {
    background: #eaf7ee;
    border-left: 6px solid #2e7d32;
    padding: 16px;
    border-radius: 12px;
}
</style>
""", unsafe_allow_html=True)

# -------------------- SESSION --------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "traditional_df" not in st.session_state:
    st.session_state.traditional_df = None

if "robot_df" not in st.session_state:
    st.session_state.robot_df = None

# -------------------- HELPERS --------------------
def clean_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = (
        df.columns
        .astype(str)
        .str.strip()
        .str.replace(" ", "_")
        .str.replace("-", "_")
        .str.lower()
    )
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

        # Convert date columns
        for col in ["sample_date", "analysis_date", "date_sampled", "date_analyzed"]:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors="coerce")

        # Convert only known numeric columns
        possible_numeric_cols = [
            "test",
            "aim_ph",
            "alum_dose",
            "true_colour",
            "uv254",
            "turb",
            "ph",
            "toc",
            "doc",
            "suva",
            "total_al",
            "dissolved_al",
            "tot_al_ppm",
            "diss_al_ppm"
        ]

        for col in possible_numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        # Friendly aliases used by the dashboard
        alias_map = {
            "total_al": "tot_al_ppm",
            "dissolved_al": "diss_al_ppm",
            "date_sampled": "sample_date",
            "date_analyzed": "analysis_date",
        }
        for old, new in alias_map.items():
            if old in df.columns and new not in df.columns:
                df[new] = df[old]

        return df

    except Exception as e:
        st.error(f"Error loading file: {e}")
        return None

def numeric_columns(df):
    if df is None:
        return []
    return df.select_dtypes(include="number").columns.tolist()

def first_existing(df, options):
    for col in options:
        if col in df.columns:
            return col
    return None


def show_logo(width=230):
    """Show Dalhousie logo if the file exists; otherwise show a clean text fallback."""
    from pathlib import Path
    logo_path = Path("dalhousie_logo.png")
    if logo_path.exists():
        st.image(str(logo_path), width=width)
    else:
        st.markdown(
            "<div style='font-size:26px;font-weight:900;color:#111;margin-bottom:8px;'>DALHOUSIE</div>",
            unsafe_allow_html=True
        )

def metric_card(value, label):
    st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
    st.markdown(f"<div class='big-number'>{value}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='small-label'>{label}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

def scatter_plot(df, x_col, y_col, title, y_label=None, color_col=None):
    if df is None or x_col not in df.columns or y_col not in df.columns:
        st.warning(f"Missing required columns for: {title}")
        return

    hover_cols = [
        c for c in [
            "test", "sample", "sample_date", "analysis_date", "aim_ph",
            "ph", "alum_dose", "doc", "toc", "uv254", "turb", "true_colour", "suva",
            "total_al", "dissolved_al", "tot_al_ppm", "diss_al_ppm"
        ]
        if c in df.columns
    ]

    fig = px.scatter(
        df,
        x=x_col,
        y=y_col,
        color=color_col if color_col in df.columns else None,
        hover_data=hover_cols,
        title=title,
        labels={
            x_col: "Alum Dose (mg/L)" if x_col == "alum_dose" else x_col,
            y_col: y_label if y_label else y_col
        }
    )
    fig.update_traces(marker=dict(size=11, opacity=0.85))
    fig.update_layout(
        height=430,
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=20, r=20, t=60, b=20)
    )
    st.plotly_chart(fig, use_container_width=True)

def heatmap(df, value_col, title, color_label):
    if df is None:
        st.warning("No dataset loaded.")
        return

    required = ["aim_ph", "alum_dose", value_col]
    missing = [c for c in required if c not in df.columns]

    if missing:
        st.warning(f"Missing columns for {title}: {missing}")
        return

    pivot = df.pivot_table(
        values=value_col,
        index="aim_ph",
        columns="alum_dose",
        aggfunc="mean"
    )

    fig = px.imshow(
        pivot,
        aspect="auto",
        color_continuous_scale="Viridis",
        title=title,
        labels=dict(x="Alum Dose (mg/L)", y="Target pH", color=color_label)
    )
    fig.update_layout(
        height=560,
        plot_bgcolor="white",
        paper_bgcolor="white"
    )
    st.plotly_chart(fig, use_container_width=True)

def boxplot_ph_variability(df):
    if df is None:
        st.warning("No dataset loaded.")
        return

    if "aim_ph" not in df.columns or "ph" not in df.columns:
        st.warning("Columns 'aim_ph' and 'ph' are required for pH variability.")
        return

    temp = df.copy()
    temp["pH_deviation"] = temp["ph"] - temp["aim_ph"]

    fig = px.box(
        temp,
        x="aim_ph",
        y="pH_deviation",
        points="outliers",
        title="Operational Variability of pH",
        labels={"aim_ph": "Target pH", "pH_deviation": "Deviation"}
    )
    fig.update_layout(height=520, plot_bgcolor="white", paper_bgcolor="white")
    st.plotly_chart(fig, use_container_width=True)

def mean_error_plot(df, y_col, title, y_label):
    if df is None:
        st.warning("No dataset loaded.")
        return

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
    fig.update_traces(marker=dict(size=10))
    fig.update_layout(height=650, plot_bgcolor="white", paper_bgcolor="white")
    st.plotly_chart(fig, use_container_width=True)

def correlation_matrix(df):
    if df is None:
        st.warning("No dataset loaded.")
        return

    num = df.select_dtypes(include="number")

    if num.empty:
        st.warning("No numeric columns available.")
        return

    corr = num.corr()

    fig = px.imshow(
        corr,
        text_auto=".2f",
        aspect="auto",
        color_continuous_scale="RdBu_r",
        zmin=-1,
        zmax=1,
        title="Correlation Matrix"
    )
    fig.update_layout(height=650)
    st.plotly_chart(fig, use_container_width=True)
    st.caption("The diagonal is always 1.0 because each variable is perfectly correlated with itself. Correlation does not prove causation.")

def filter_traditional_data(df):
    filtered = df.copy()

    st.subheader("Filters")

    f1, f2, f3 = st.columns(3)

    # Sample Date filter
    with f1:
        if "sample_date" in filtered.columns and filtered["sample_date"].notna().any():
            min_date = filtered["sample_date"].min().date()
            max_date = filtered["sample_date"].max().date()
            selected_date_range = st.date_input(
                "Sample Date Range",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date
            )

            if isinstance(selected_date_range, tuple) and len(selected_date_range) == 2:
                start_date, end_date = selected_date_range
                filtered = filtered[
                    (filtered["sample_date"].dt.date >= start_date) &
                    (filtered["sample_date"].dt.date <= end_date)
                ]
        else:
            st.info("No sample_date column found.")

    # Analysis Date filter
    with f2:
        if "analysis_date" in filtered.columns and filtered["analysis_date"].notna().any():
            available_analysis_dates = sorted(filtered["analysis_date"].dropna().dt.date.unique())
            selected_analysis = st.multiselect(
                "Analysis Date",
                available_analysis_dates,
                default=available_analysis_dates
            )
            if selected_analysis:
                filtered = filtered[filtered["analysis_date"].dt.date.isin(selected_analysis)]
        else:
            st.info("No analysis_date column found.")

    # Test filter
    with f3:
        if "test" in filtered.columns:
            available_tests = sorted(filtered["test"].dropna().unique())
            selected_tests = st.multiselect(
                "Jar Test",
                available_tests,
                default=available_tests
            )
            if selected_tests:
                filtered = filtered[filtered["test"].isin(selected_tests)]
        else:
            st.info("No test column found.")

    return filtered

def dataset_overview(df):
    if df is None:
        st.warning("No dataset loaded.")
        return

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card(len(df), "Records")
    with c2:
        metric_card(df["test"].nunique() if "test" in df.columns else "N/A", "Jar Tests")
    with c3:
        metric_card(df["aim_ph"].nunique() if "aim_ph" in df.columns else "N/A", "Target pH Levels")
    with c4:
        metric_card(f"{df['alum_dose'].max()} mg/L" if "alum_dose" in df.columns else "N/A", "Max Alum Dose")

# -------------------- LOGIN --------------------
if not st.session_state.logged_in:
    c1, c2, c3 = st.columns([1, 1.2, 1])
    with c2:
        show_logo(width=330)
        st.title("WRAP Login")
        st.caption("Water Research Analytics Platform")

        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        if st.button("Sign In", use_container_width=True):
            if email == VALID_USER and password == VALID_PASSWORD:
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Invalid credentials")

        st.info("Prototype access | Research use only")

    st.stop()

# -------------------- SIDEBAR --------------------
with st.sidebar:
    show_logo(width=230)
    st.title("WRAP")
    st.caption("Water Research Analytics Platform")

    page = st.radio(
        "Navigation",
        [
            "Home",
            "Traditional Jar Tests",
            "Heatmaps",
            "pH Variability",
            "Mean Response",
            "Robot Data",
            "Compare Methods",
            "Analytics",
            "Robot Integration Status"
        ]
    )

    st.divider()

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
        st.rerun()

# -------------------- HEADER --------------------
st.title("Water Research Analytics Platform")
st.caption("Manual Jar Tests | Future Brigit Robot Data | Comparative Analytics")

# -------------------- HOME --------------------
if page == "Home":
    traditional_loaded = st.session_state.traditional_df is not None
    robot_loaded = st.session_state.robot_df is not None

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card(len(st.session_state.traditional_df) if traditional_loaded else 0, "Traditional Records")
    with c2:
        metric_card(len(st.session_state.robot_df) if robot_loaded else 0, "Robot Records")
    with c3:
        metric_card("Ready" if traditional_loaded else "Waiting", "Traditional Data Layer")
    with c4:
        metric_card("Pending", "Robot Integration")

    st.markdown("## Platform Purpose")
    st.markdown("""
    WRAP is designed to organize, visualize, and analyze **traditional jar test datasets** first.

    When the Brigit / MANTECH automated jar tester becomes available, this same platform can receive robot-generated CSV, Excel, database, or API exports.

    The long-term goal is to compare manual and automated jar testing methods in one research environment.
    """)

    st.info("No fake data is loaded. The platform only displays data after a CSV or Excel file is uploaded.")

# -------------------- TRADITIONAL JAR TESTS --------------------
elif page == "Traditional Jar Tests":
    st.header("Traditional Jar Test Analysis")

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

    st.subheader("Data Preview")
    st.dataframe(filtered_df.head(50), use_container_width=True)

    st.divider()

    st.subheader("Experimental Scatter Plots")
    st.caption("Each point represents an experimental jar test condition. Points are not connected because these are discrete experimental conditions, not continuous time-series data.")

    color_col = "aim_ph" if "aim_ph" in filtered_df.columns else None

    col1, col2 = st.columns(2)
    with col1:
        scatter_plot(filtered_df, "alum_dose", "doc", "DOC vs Alum Dose", "DOC (mg/L)", color_col)
    with col2:
        scatter_plot(filtered_df, "alum_dose", "toc", "TOC vs Alum Dose", "TOC (mg/L)", color_col)

    col3, col4 = st.columns(2)
    with col3:
        scatter_plot(filtered_df, "alum_dose", "uv254", "UV254 vs Alum Dose", "UV254 (cm⁻¹)", color_col)
    with col4:
        scatter_plot(filtered_df, "alum_dose", "turb", "Turbidity vs Alum Dose", "Turbidity (NTU)", color_col)

    col5, col6 = st.columns(2)
    with col5:
        scatter_plot(filtered_df, "alum_dose", "true_colour", "True Colour vs Alum Dose", "True Colour", color_col)
    with col6:
        scatter_plot(filtered_df, "alum_dose", "suva", "SUVA vs Alum Dose", "SUVA", color_col)

    st.divider()

    st.subheader("Aluminum Analysis")
    col7, col8 = st.columns(2)
    with col7:
        scatter_plot(filtered_df, "alum_dose", "tot_al_ppm", "Total Aluminum vs Alum Dose", "Total Al (mg/L)", color_col)
    with col8:
        scatter_plot(filtered_df, "alum_dose", "diss_al_ppm", "Dissolved Aluminum vs Alum Dose", "Dissolved Al (mg/L)", color_col)

    st.divider()

    st.subheader("Quick Optimization")
    target_options = [c for c in ["doc", "toc", "uv254", "turb", "true_colour", "suva", "tot_al_ppm", "diss_al_ppm"] if c in filtered_df.columns]
    if target_options:
        target = st.selectbox("Optimization target", target_options)
        clean_target = filtered_df.dropna(subset=[target])
        if not clean_target.empty:
            best_row = clean_target.loc[clean_target[target].idxmin()]
            st.success(
                f"Lowest {target} observed at {best_row.get('alum_dose', 'N/A')} mg/L alum dose "
                f"and target pH {best_row.get('aim_ph', 'N/A')} "
                f"({target} = {best_row[target]:.4f})"
            )
            st.dataframe(best_row.to_frame("Best Condition"), use_container_width=True)
    else:
        st.warning("No optimization target columns were found.")

# -------------------- HEATMAPS --------------------
elif page == "Heatmaps":
    st.header("Heatmap Analysis")

    df = st.session_state.traditional_df
    if df is None:
        st.warning("Upload traditional jar test data first.")
        st.stop()

    filtered_df = filter_traditional_data(df)

    st.divider()

    heatmap_options = {
        "UV254": ("uv254", "UV254 Heatmap", "UV254 (cm⁻¹)"),
        "TOC": ("toc", "TOC Heatmap", "TOC (mg/L)"),
        "DOC": ("doc", "DOC Heatmap", "DOC (mg/L)"),
        "Turbidity": ("turb", "Turbidity Heatmap", "Turbidity (NTU)"),
        "True Colour": ("true_colour", "True Colour Heatmap", "True Colour"),
        "Total Aluminum": ("tot_al_ppm", "Residual Total Aluminum Heatmap", "Total Al (mg/L)"),
        "Dissolved Aluminum": ("diss_al_ppm", "Residual Dissolved Aluminum Heatmap", "Dissolved Al (mg/L)")
    }

    selected_heatmap = st.selectbox("Select heatmap", list(heatmap_options.keys()))
    value_col, title, color_label = heatmap_options[selected_heatmap]

    heatmap(filtered_df, value_col, title, color_label)

# -------------------- PH VARIABILITY --------------------
elif page == "pH Variability":
    st.header("Operational Variability of pH")

    df = st.session_state.traditional_df
    if df is None:
        st.warning("Upload traditional jar test data first.")
        st.stop()

    filtered_df = filter_traditional_data(df)
    boxplot_ph_variability(filtered_df)

# -------------------- MEAN RESPONSE --------------------
elif page == "Mean Response":
    st.header("Mean Response Across Jar Test Conditions")

    df = st.session_state.traditional_df
    if df is None:
        st.warning("Upload traditional jar test data first.")
        st.stop()

    filtered_df = filter_traditional_data(df)

    response_options = {
        "UV254": ("uv254", "Mean UV254 Across Different Jar Test Conditions", "Mean UV254 (cm⁻¹)"),
        "TOC": ("toc", "Mean TOC Across Different Jar Test Conditions", "Mean TOC (mg/L)"),
        "DOC": ("doc", "Mean DOC Across Different Jar Test Conditions", "Mean DOC (mg/L)"),
        "Turbidity": ("turb", "Mean Turbidity Across Different Jar Test Conditions", "Mean Turbidity (NTU)")
    }

    selected_response = st.selectbox("Select response parameter", list(response_options.keys()))
    y_col, title, y_label = response_options[selected_response]

    mean_error_plot(filtered_df, y_col, title, y_label)

# -------------------- ROBOT DATA --------------------
elif page == "Robot Data":
    st.header("Robot Data")

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
            st.plotly_chart(fig, use_container_width=True)

# -------------------- COMPARE METHODS --------------------
elif page == "Compare Methods":
    st.header("Traditional vs Robot Comparison")

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

            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(comparison, use_container_width=True)

# -------------------- ANALYTICS --------------------
elif page == "Analytics":
    st.header("Advanced Analytics")

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
elif page == "Robot Integration Status":
    st.header("Robot Integration Status")

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