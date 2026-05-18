import os
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st

# =============================================================================
# PAGE CONFIGURATION
# =============================================================================
st.set_page_config(
    page_title="Understanding and Forecasting U.S Inflation (2000-2025)",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =============================================================================
# CUSTOM CSS
# =============================================================================
st.markdown("""
<style>

/* ============================================================================
MAIN APP
============================================================================ */

.stApp {
    background-color: #0E1117;
    color: #F8FAFC;
}

/* Hide Streamlit Header */
header {
    visibility: hidden;
}

/* ============================================================================
GLOBAL TEXT
============================================================================ */

html, body, [class*="css"]  {
    color: #F8FAFC !important;
}

/* Paragraph Text */
p {
    color: #E2E8F0 !important;
    font-size: 16px;
}

/* Markdown Text */
div[data-testid="stMarkdownContainer"] {
    color: #E2E8F0 !important;
}

/* Labels */
label {
    color: #F8FAFC !important;
    font-weight: 600 !important;
}

/* ============================================================================
HEADINGS
============================================================================ */

h1 {
    color: #FFFFFF !important;
    font-weight: 800 !important;
}

h2 {
    color: #F8FAFC !important;
    font-weight: 700 !important;
}

h3 {
    color: #E2E8F0 !important;
    font-weight: 700 !important;
}

/* ============================================================================
TABS
============================================================================ */

.stTabs [data-baseweb="tab-list"] {
    gap: 18px;
}

.stTabs [data-baseweb="tab"] {
    height: 55px;
    background-color: #111827;
    border-radius: 14px;

    color: #CBD5E1 !important;

    padding: 10px 24px;

    font-size: 16px;
    font-weight: 600;

    transition: 0.3s;
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(
        90deg,
        #2563EB,
        #3B82F6
    );

    color: white !important;
}

/* ============================================================================
KPI CARDS
============================================================================ */

[data-testid="metric-container"] {
    background-color: #1E293B;
    border: 1px solid #334155;
    padding: 18px;
    border-radius: 16px;
}

/* KPI Label */
[data-testid="stMetricLabel"] {
    color: #CBD5E1 !important;
    font-size: 16px !important;
    font-weight: 700 !important;
}

/* KPI Value */
[data-testid="stMetricValue"] {
    color: #FFFFFF !important;
    font-size: 32px !important;
    font-weight: 800 !important;
}

/* ============================================================================
DATAFRAME
============================================================================ */

[data-testid="stDataFrame"] {
    background-color: #111827 !important;
    border-radius: 14px;
    overflow: hidden;
}

/* Table Text */
[data-testid="stDataFrame"] * {
    color: #F8FAFC !important;
}

/* ============================================================================
MULTISELECT / SELECTBOX
============================================================================ */

.stMultiSelect label,
.stSelectbox label {
    color: #F8FAFC !important;
    font-weight: 600;
}

/* ============================================================================
SLIDER
============================================================================ */

.stSlider label {
    color: #F8FAFC !important;
}

/* ============================================================================
INFO / ALERT BOXES
============================================================================ */

.stAlert {
    border-radius: 14px;
    background-color: #1E293B !important;
    color: #F8FAFC !important;
}

/* Info Box Text */
.stAlert p {
    color: #F8FAFC !important;
}

/* ============================================================================
EXPANDER
============================================================================ */

.streamlit-expanderHeader {
    color: #F8FAFC !important;
    font-weight: 600 !important;
}

.streamlit-expanderContent {
    color: #E2E8F0 !important;
}

/* ============================================================================
SIDEBAR
============================================================================ */

section[data-testid="stSidebar"] {
    background-color: #111827;
    color: #F8FAFC;
}

/* ============================================================================
BUTTONS
============================================================================ */

.stButton button {
    background-color: #2563EB;
    color: white !important;
    border-radius: 10px;
    border: none;
    font-weight: 600;
}

.stButton button:hover {
    background-color: #3B82F6;
}

/* ============================================================================
CAPTIONS
============================================================================ */

caption {
    color: #CBD5E1 !important;
}

</style>
""", unsafe_allow_html=True)

# =============================================================================
# COLOR PALETTE
# =============================================================================
COLORS = {
    "headline": "#94A3B8",
    "core": "#60A5FA",
    "supercore": "#F59E0B",
    "actual": "#22D3EE",
    "ensemble": "#34D399",
    "northeast": "#A78BFA",
    "midwest": "#F472B6",
    "south": "#22C55E",
    "west": "#F97316"
}

# =============================================================================
# GLOBAL CHART THEME
# =============================================================================
def apply_dark_theme(fig):

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#0E1117",
        plot_bgcolor="#0E1117",

        font=dict(
            family="Arial",
            size=14,
            color="#F8FAFC"
        ),

        hoverlabel=dict(
            bgcolor="#1E293B",
            font_size=13,
            font_color="#F8FAFC"
        ),

        hovermode="x unified",

        legend=dict(
            orientation="h",
            y=1.05,
            bgcolor="rgba(0,0,0,0)",

            # ✅ THIS IS THE IMPORTANT FIX
            font=dict(
                color="#F8FAFC",
                size=12
            )
        ),

        margin=dict(l=30, r=30, t=60, b=30)
    )

    fig.update_xaxes(
        showgrid=True,
        gridcolor="rgba(255,255,255,0.08)",
        color="#F8FAFC"   # axis text color
    )

    fig.update_yaxes(
        showgrid=True,
        gridcolor="rgba(255,255,255,0.08)",
        color="#F8FAFC"   # axis text color
    )

    return fig

# =============================================================================
# FILE ROUTING
# =============================================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def get_file_path(filename):

    path = os.path.join(BASE_DIR, filename)

    if not os.path.exists(path):
        st.error(f"Missing File: {filename}")
        st.stop()

    return path

# =============================================================================
# DATA LOADING
# =============================================================================
@st.cache_data
def load_inflation_rates():

    df = pd.read_csv(get_file_path("merged_inflation_rates.csv"))

    if 'Unnamed: 0' in df.columns:
        df = df.drop(columns=['Unnamed: 0'])

    df['Date'] = pd.to_datetime(df['Date'])

    return df.sort_values('Date').reset_index(drop=True)

@st.cache_data
def load_categorical_rates():

    df = pd.read_csv(get_file_path("merged_categorical_inflation_rates.csv"))

    if 'Unnamed: 0' in df.columns:
        df = df.drop(columns=['Unnamed: 0'])

    df['Date'] = pd.to_datetime(df['Date'])

    return df.sort_values('Date').reset_index(drop=True)

@st.cache_data
def load_regional_rates():

    df = pd.read_csv(get_file_path("merged_regional_inflation.csv"))

    if 'Unnamed: 0' in df.columns:
        df = df.drop(columns=['Unnamed: 0'])

    df['Date'] = pd.to_datetime(df['Date'])

    return df.sort_values('Date').reset_index(drop=True)

@st.cache_data
def load_forecast_matrix():

    df = pd.read_csv(get_file_path("final_inflation_12m_forecast.csv"))

    if df.columns[0].startswith("Unnamed"):
        df = df.rename(columns={df.columns[0]: "Date"})

    df['Date'] = pd.to_datetime(df['Date'])

    return df.sort_values('Date').reset_index(drop=True)

# =============================================================================
# LOAD DATA
# =============================================================================
df_us = load_inflation_rates()
df_cat = load_categorical_rates()
df_reg = load_regional_rates()
df_fc = load_forecast_matrix()

# =============================================================================
# HERO SECTION
# =============================================================================
st.markdown("""
<div style="
padding:22px;
border-radius:18px;
background: linear-gradient(135deg, #111827, #1E293B);
margin-bottom:25px;
">

<h1 style="margin-bottom:10px;">
Understanding and Forecasting U.S Inflation (2000-2025)
</h1>

<p style="font-size:18px; color:#CBD5E1;">
Interactive dashboard for analyzing and forecasting U.S inflation trends
between 2000–2025 using data visualization and machine learning.
</p>

</div>
""", unsafe_allow_html=True)

# =============================================================================
# TABS
# =============================================================================
tab1, tab2, tab3 = st.tabs([
    "Home",
    "Exploratory Data Analysis",
    "Model Forecasting"
])

# =============================================================================
# HOME PAGE
# =============================================================================
with tab1:

    st.header("Motivations behind this Senior Capstone Project")

    st.markdown("""
The first-hand experience of high inflation in Myanmar drives my curiosity to explore the country’s economic situation and sparked my interest in economic data analysis. The original inspiration for this project is to analyze the inflation trend in Myanmar and the corresponding events related to inflation. However, due to the lack of comprehensive and accessible economic data for Myanmar, it led to the utilization of the U.S. Bureau of Labor Statistics (BLS) and FRED-MD databases as a reliable testing environment for analytical frameworks that can later be tailored to local contexts.
""")

    st.markdown("---")

    profile_df = pd.DataFrame({
        "Field": [
            "Student Name",
            "Student ID",
            "Batch",
            "Project Focus",
            "Project Objective",
            "Expected Outcome"
        ],
        "Details": [
            "May Thiri Phyoe",
            "PLUS20220031",
            "Class of 2026",
            "Understanding and Forecasting U.S Inflation",
            
            # ✅ SHORTENED + CLEANED
            "Analyze inflation trends across U.S regions and key expenditure categories and make forecasts for next 12 months",
            # ✅ SHORTENED + CLEANED
            "Develop an interactive dashboard using EDA and machine learning models"
        ]
    })

    # ✅ SIMPLE STREAMLIT TABLE (NO HTML)
    st.dataframe(
        profile_df,
        use_container_width=True,
        hide_index=True
    )

    st.markdown("---")

    st.info("""
This dashboard uses Consumer Price Index datasets from U.S Bureau of Labor and Statistics (BLS) to produce economic analysis and Federal Economic Deserve Monthly Database (FRED-MD database) to produce forecasting results for 12-month horizon.
It aims to better understand inflation behavior and long-term price movements in the U.S economy.
""")

# =============================================================================
# EDA PAGE
# =============================================================================
with tab2:

    st.header("Exploratory Data Analysis")

    # =========================================================================
    # FILTER
    # =========================================================================
    st.subheader("Analysis Time Window")

    min_date = df_us['Date'].min().to_pydatetime()
    max_date = df_us['Date'].max().to_pydatetime()

    start_dt, end_dt = st.slider(
        "Select Time Period",
        min_value=min_date,
        max_value=max_date,
        value=(min_date, max_date),
        format="YYYY-MM"
    )

    # FILTER DATA
    df_us_filt = df_us[
        (df_us['Date'] >= start_dt) &
        (df_us['Date'] <= end_dt)
    ]

    df_cat_filt = df_cat[
        (df_cat['Date'] >= start_dt) &
        (df_cat['Date'] <= end_dt)
    ]

    df_reg_filt = df_reg[
        (df_reg['Date'] >= start_dt) &
        (df_reg['Date'] <= end_dt)
    ]

    st.markdown("---")

    # =========================================================================
    # KPI CARDS
    # =========================================================================
    st.info("Latest value as of 2025 December")
    latest_headline = df_us_filt['Standard'].iloc[-1]
    latest_core = df_us_filt['Core'].iloc[-1]
    latest_supercore = df_us_filt['Supercore'].iloc[-1]

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Headline CPI",
        f"{latest_headline:.2f}%"
    )

    col2.metric(
        "Core Inflation",
        f"{latest_core:.2f}%"
    )

    col3.metric(
        "Supercore Inflation",
        f"{latest_supercore:.2f}%"
    )

    st.markdown("---")

    # =========================================================================
    # CHART 1
    # =========================================================================
    st.subheader("Inflation Comparison in the United States")

    fig1 = go.Figure()

    fig1.add_trace(go.Scatter(
        x=df_us_filt['Date'],
        y=df_us_filt['Standard'],
        name='Headline CPI',
        line=dict(
            color=COLORS["headline"],
            width=3
        ),
        line_shape='spline'
    ))

    fig1.add_trace(go.Scatter(
        x=df_us_filt['Date'],
        y=df_us_filt['Core'],
        name='Core Inflation',
        line=dict(
            color=COLORS["core"],
            width=3
        ),
        line_shape='spline'
    ))

    fig1.add_trace(go.Scatter(
        x=df_us_filt['Date'],
        y=df_us_filt['Supercore'],
        name='Supercore Inflation',
        line=dict(
            color=COLORS["supercore"],
            width=3,
            dash='dash'
        ),
        line_shape='spline'
    ))

    fig1 = apply_dark_theme(fig1)

    fig1.update_layout(
        height=500,
        xaxis_title="Date",
        yaxis_title="Inflation Rate (%)"
    )

    st.plotly_chart(fig1, use_container_width=True)

    st.info("""
This line chart shows year-over-year inflation trends across three key measures: Standard, Core, and Supercore inflation. Standard inflation rate measures the price change for a basket of goods and services whereas Core inflation rate excludes volatile food and energy consumption and Supercore inflation rate further excludes services less rent of shelter.

Standard inflation is the most volatile, especially during economic shocks such as the 2008–2009 financial crisis (deflation) and the 2022–2023 inflation surge above 8% driven by supply chain disruptions.
Core inflation is more stable and generally closer to the Fed’s 2% target, as it excludes food and energy volatility, particularly during 2012–2020.
Supercore inflation, which focuses on services, often stays elevated above other measures, highlighting persistent service-sector price pressures.
Since 2021, all three measures rose sharply, breaking the previous stability pattern. By 2025, inflation has eased overall, but Supercore remains relatively high, indicating continued pressure in service costs despite declining headline inflation.
""")

    st.markdown("---")

    # =========================================================================
    # CHART 2
    # =========================================================================
    st.subheader("Inflation Trends Across Consumer Sectors")

    fig2 = go.Figure()

    yoy_columns = [c for c in df_cat.columns if c.endswith("_YoY")]

    for col in yoy_columns:

        label = col.replace("_YoY", "")

        fig2.add_trace(go.Scatter(
            x=df_cat_filt['Date'],
            y=df_cat_filt[col],
            name=label,
            mode='lines',
            line=dict(width=2),
            line_shape='spline'
        ))

    fig2 = apply_dark_theme(fig2)

    fig2.update_layout(
        height=500,
        xaxis_title="Date",
        yaxis_title="YoY Inflation Rate (%)"
    )

    st.plotly_chart(fig2, use_container_width=True)

    st.info("""
Different sectors experience inflation differently.
Energy is the most volatile expenditure category with massive spikes and drops. It is followed by the Transportation category and this explains that transportation strongly co-moves with the Energy category. Moreover, it is also found that during the pandemic period of 2020 to 2021, the Food and Beverages category shows a more gradual but steady increase when Energy and Transportation shows sudden, volatile peaks and exceeds over 10-15%.
""")

    st.markdown("---")

    # =========================================================================
    # CHART 3
    # =========================================================================
    st.subheader("Cumulative Price Growth Since 2000")

    fig3 = go.Figure()

    index_columns = [c for c in df_cat.columns if c.endswith("_Index")]

    for col in index_columns:

        label = col.replace("_Index", "")

        fig3.add_trace(go.Scatter(
            x=df_cat_filt['Date'],
            y=df_cat_filt[col],
            name=label,
            mode='lines',
            line=dict(width=2),
            line_shape='spline'
        ))

    fig3 = apply_dark_theme(fig3)

    fig3.update_layout(
        height=500,
        xaxis_title="Date",
        yaxis_title="Index Level"
    )

    st.plotly_chart(fig3, use_container_width=True)

    st.info("""
This cumulative growth plot depicts the long-term "compounding effect" of inflation over 25 years, whereas YOY charts show short-term fluctuations. 
This chart shows that in the long term, the expenditure categories diverged rather than simply went up. For example, the cumulative price growth for some categories such as Education and Medicare significantly outpaced other categories and showed a straight upward trend. On the other hand, the cumulative price growth for some categories such as Apparel and Communications became lower over time, particularly due to technological growth and global supply chain improvements. This chart is essential as it uncovers why some households are still struggling to squeeze their budget even though the yearly inflation rate seems to be declining. 

""")

    st.markdown("---")

    # =========================================================================
    # CHART 4
    # =========================================================================
    st.subheader("Sector Inflation Heatmap by Year")

    heatmap_df = df_cat_filt.copy()

    heatmap_df['Year'] = heatmap_df['Date'].dt.year

    yoy_cols = [c for c in heatmap_df.columns if c.endswith('_YoY')]

    annual_summary = heatmap_df.groupby('Year')[yoy_cols].mean()

    annual_summary.columns = [
        c.replace('_YoY', '')
        for c in annual_summary.columns
    ]

    fig4 = px.imshow(
        annual_summary,
        aspect="auto",
        color_continuous_scale="Viridis",
        labels=dict(
            x="Sector",
            y="Year",
            color="Inflation"
        )
    )

    fig4 = apply_dark_theme(fig4)

    fig4.update_layout(height=550)

    st.plotly_chart(fig4, use_container_width=True)

    st.info("""
This heatmap provides a high-level overview of inflation intensity of major expenditure categories for the timeframe of 2000 to 2025. 
The heatmap shows that during the 2021-2023 era, almost all categories were impacted and high inflation can be seen. 2022 can be noted as the most broad-based inflationary year with high inflation across all categories.
""")

    st.markdown("---")

    # =========================================================================
    # CHART 5
    # =========================================================================
    st.subheader("Regional Inflation Divergence in the U.S.")

    fig5 = go.Figure()

    regions = [
        'Standard_YoY',
        'Northeast',
        'Midwest',
        'South',
        'West'
    ]

    color_map = {
        'Standard_YoY': COLORS["actual"],
        'Northeast': COLORS["northeast"],
        'Midwest': COLORS["midwest"],
        'South': COLORS["south"],
        'West': COLORS["west"]
    }

    for region in regions:

        if region in df_reg_filt.columns:

            label = (
                "National Average"
                if region == 'Standard_YoY'
                else region
            )

            fig5.add_trace(go.Scatter(
                x=df_reg_filt['Date'],
                y=df_reg_filt[region],
                name=label,
                mode='lines',
                line=dict(
                    color=color_map[region],
                    width=4 if region == 'Standard_YoY' else 2.5
                ),
                line_shape='spline'
            ))

    fig5 = apply_dark_theme(fig5)

    fig5.update_layout(
        height=500,
        xaxis_title="Date",
        yaxis_title="Inflation Rate (%)"
    )

    st.plotly_chart(fig5, use_container_width=True)

    st.info("""
This chart shows the national headline inflation against specific regional inflation metrics. 
Generally, it can be seen that inflation from four census regions move in the same direction with the headline inflation. However, the intensity of the inflation tends to differ geographically. The chart shows that the South and West tend to have higher inflation rates while the Northeast and Midwest have comparatively lower and more stable inflation trends. Moreover, regional inflation divergence is most visible during major economic shocks such as global pandemic and post pandemic recovery periods. 

""")

# =============================================================================
# FORECAST PAGE
# =============================================================================
with tab3:

    st.header("Machine Learning Inflation Forecasts")

    st.markdown("""
Compare machine learning forecasting models
against actual inflation behavior.
""")

    st.markdown("---")

    model_columns = [
        col for col in df_fc.columns
        if col not in ['Date', 'Actual']
    ]

    selected_models = st.multiselect(
        "Select Forecast Models",
        model_columns,
        default=model_columns[:2]
    )

    fig6 = go.Figure()

    # ACTUAL LINE
    fig6.add_trace(go.Scatter(
        x=df_fc['Date'],
        y=df_fc['Actual'],
        name='Actual Inflation',

        mode='lines+markers',

        line=dict(
            color=COLORS["actual"],
            width=5
        ),

        marker=dict(
            size=6,
            color=COLORS["actual"]
        ),

        line_shape='spline'
    ))

    # MODEL LINES
    for model in selected_models:

        fig6.add_trace(go.Scatter(
            x=df_fc['Date'],
            y=df_fc[model],
            name=model,
            mode='lines',
            line=dict(width=2.5),
            line_shape='spline'
        ))

    fig6 = apply_dark_theme(fig6)

    fig6.update_layout(
        height=600,
        xaxis_title="Forecast Timeline",
        yaxis_title="Predicted Inflation Rate (%)"
    )

    st.plotly_chart(fig6, use_container_width=True)


    st.markdown("---")

    with st.expander("Forecasting Methodology and Performance Comparison"):
        st.write("""
Through the backtesting of 60 months (5 years) based on the data of the rolling window of 240 months (20 years), the models’ performance are compared as follows. 
""")



        h1 = pd.DataFrame({
            "Model": ["Random Walk", "Adaptive Lasso", "Ridge", "Random Forest"],
            "RMSE": [0.00459, 0.00267, 0.00302, 0.00297],
            "MAE": [0.00309, 0.00182, 0.00213, 0.00200],
            "MAD": [0.00218, 0.00126, 0.00159, 0.00144],
            "Rel RW": [1, 0.581, 0.657, 0.647]
        })

        h3 = pd.DataFrame({
            "Model": ["Random Walk", "Adaptive Lasso", "Ridge", "Random Forest"],
            "RMSE": [0.00369, 0.00288, 0.00294, 0.00292],
            "MAE": [0.00309, 0.00203, 0.00215, 0.00207],
            "MAD": [0.00218, 0.00136, 0.00152, 0.00147],
            "Rel RW": [1, 0.780, 0.797, 0.790]
        })

        h6 = pd.DataFrame({
            "Model": ["Random Walk", "Adaptive Lasso", "Ridge", "Random Forest"],
            "RMSE": [0.00454, 0.00287, 0.00308, 0.00302],
            "MAE": [0.00319, 0.00203, 0.00222, 0.00225],
            "MAD": [0.00261, 0.00136, 0.00161, 0.00171],
            "Rel RW": [1, 0.632, 0.678, 0.665]
        })

        h12 = pd.DataFrame({
            "Model": ["Random Walk", "Adaptive Lasso", "Ridge", "Random Forest"],
            "RMSE": [0.00415, 0.00303, 0.00324, 0.00282],
            "MAE": [0.00325, 0.00220, 0.00233, 0.00203],
            "MAD": [0.00260, 0.00154, 0.00157, 0.00179],
            "Rel RW": [1, 0.731, 0.782, 0.681]
        })

        st.markdown("Horizon = 1 month")
        st.dataframe(h3, use_container_width=True, hide_index=True)

        st.markdown("Horizon = 3 months")
        st.dataframe(h3, use_container_width=True, hide_index=True)

        st.markdown("Horizon = 6 months")
        st.dataframe(h6, use_container_width=True, hide_index=True)

        st.markdown("Horizon = 12 months")
        st.dataframe(h12, use_container_width=True, hide_index=True)

        st.markdown("---")

        