import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import os

st.set_page_config(
    page_title="Sustainable Resources Dashboard",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_data
def generate_sustainable_data_on_the_fly(num_entries=500, num_countries=15):
    """Generates a synthetic dataset for sustainable resources."""
    np.random.seed(42)
    countries = [f"Country_{i}" for i in range(1, num_countries + 1)]
    
    data = []
    for _ in range(num_entries):
        country = np.random.choice(countries)
        year = np.random.randint(2000, 2024) 
        renewable_prod = np.random.uniform(50, 1000) * (1 + (year - 2000) * 0.05)
        co2_emissions = np.random.uniform(1000, 10000) * (1 - (year - 2000) * 0.02)
        population = np.random.uniform(10, 1000) * 1e6
        gdp = np.random.uniform(100, 5000) * (1 + (year - 2000) * 0.03)
        
        data.append({
            'Country': country,
            'Year': year,
            'Renewable Energy Production (TWh)': max(0, renewable_prod + np.random.normal(0, 50)),
            'CO2 Emissions (kt)': max(0, co2_emissions + np.random.normal(0, 500)),
            'Population': max(1000000, population + np.random.normal(0, 1e6)),
            'GDP (USD billions)': max(10, gdp + np.random.normal(0, 100))
        })
        
    df = pd.DataFrame(data)
    df['Year'] = df['Year'].astype(int)
    df = df.sort_values(by=['Country', 'Year']).reset_index(drop=True)
    return df

BASE_DIR = os.path.dirname(__file__)
CSV_FILE_PATH = os.path.join(BASE_DIR, 'sustainable_resources_sample.csv')
if os.path.exists(CSV_FILE_PATH):
    df = pd.read_csv(CSV_FILE_PATH)
    st.sidebar.info(f"Loaded data from '{os.path.basename(CSV_FILE_PATH)}'.")
else:
    st.sidebar.warning(f"'{CSV_FILE_PATH}' not found. Generating sample data...")
    df = generate_sustainable_data_on_the_fly()
    if st.sidebar.button("Save Generated Data to CSV"):
        df.to_csv(CSV_FILE_PATH, index=False)
        st.sidebar.success(f"Sample data saved to '{os.path.basename(CSV_FILE_PATH)}'.")
        st.rerun()
denominator = (df['Renewable Energy Production (TWh)'] + df['CO2 Emissions (kt)'] / 1000)
df['Renewable Energy Share (%)'] = (df['Renewable Energy Production (TWh)'] / denominator) * 100
st.sidebar.title("Dashboard Controls")
st.sidebar.markdown("Adjust parameters to explore the data.")
all_countries = sorted(df['Country'].unique())
selected_countries = st.sidebar.multiselect(
    "Select Countries",
    options=all_countries,
    default=all_countries[:5] if len(all_countries) > 5 else all_countries
)
min_year = int(df['Year'].min())
max_year = int(df['Year'].max())

if min_year == max_year:
    year_range = (min_year, max_year)
    st.sidebar.write(f"Year: {min_year}")
else:
    year_range = st.sidebar.slider(
        "Select Year Range",
        min_value=min_year,
        max_value=max_year,
        value=(min_year, max_year)
    )
filtered_df = df[
    (df['Country'].isin(selected_countries)) &
    (df['Year'] >= year_range[0]) &
    (df['Year'] <= year_range[1]) 
]

if filtered_df.empty:
    st.warning("No data available for the selected filters. Please adjust your selections.")
    st.stop()

# --- 5. Main Content Area ---
st.title("🌍 Sustainable Resources Insights")
st.markdown("""
This dashboard visualizes key metrics related to sustainable resource development. 
Explore trends in renewable energy, CO2 emissions, population, and economic growth across different countries and years.
""")

st.markdown("---")

# Section 1: Overview Metrics
st.header("Overall Trends")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(
        label="Total Renewable Energy (TWh)", 
        value=f"{filtered_df['Renewable Energy Production (TWh)'].sum():,.0f}"
    )
with col2:
    st.metric(
        label="Total CO2 Emissions (kt)", 
        value=f"{filtered_df['CO2 Emissions (kt)'].sum():,.0f}"
    )
with col3:
    st.metric(
        label="Avg. Renewable Share (%)", 
        value=f"{filtered_df['Renewable Energy Share (%)'].mean():.1f}%"
    )

st.markdown("---")

# Section 2: Time-series Analysis
st.header("Time-Series Analysis")
st.markdown("Observe the evolution of key indicators over time.")

col_ts1, col_ts2 = st.columns(2)

with col_ts1:
    # Renewable Energy Production over Time
    fig_energy = px.line(
        filtered_df,
        x='Year',
        y='Renewable Energy Production (TWh)',
        color='Country',
        title='Renewable Energy Production Over Time',
        # FIX: Removed template='plotly_white' to respect Streamlit theme
    )
    # FIX: Ensure X-axis format is integer (d) so it doesn't show commas (2,022)
    fig_energy.update_layout(hovermode="x unified", legend=dict(orientation="h", y=-0.2))
    fig_energy.update_xaxes(tickformat="d") 
    st.plotly_chart(fig_energy, use_container_width=True)

with col_ts2:
    # CO2 Emissions over Time
    fig_co2 = px.line(
        filtered_df,
        x='Year',
        y='CO2 Emissions (kt)',
        color='Country',
        title='CO2 Emissions Over Time',
        # FIX: Removed template='plotly_white'
    )
    fig_co2.update_layout(hovermode="x unified", legend=dict(orientation="h", y=-0.2))
    fig_co2.update_xaxes(tickformat="d")
    st.plotly_chart(fig_co2, use_container_width=True)

st.markdown("---")

# Section 3: Comparative Analysis (Yearly Snapshot)
st.header("Comparative View")
st.markdown("Compare countries based on selected metrics for a specific year.")

# Select a single year for comparison
comparison_year = st.slider(
    "Select a Year for Comparison",
    min_value=year_range[0],
    max_value=year_range[1],
    value=year_range[1]
)

# FIX: Removed .dt.year
df_comparison = filtered_df[filtered_df['Year'] == comparison_year]

if not df_comparison.empty:
    col_comp1, col_comp2 = st.columns(2)
    with col_comp1:
        fig_bar_energy = px.bar(
            df_comparison.sort_values('Renewable Energy Production (TWh)', ascending=False),
            x='Country',
            y='Renewable Energy Production (TWh)',
            title=f'Renewable Energy (TWh) - {comparison_year}',
            color='Renewable Energy Production (TWh)',
            color_continuous_scale=px.colors.sequential.Viridis
        )
        st.plotly_chart(fig_bar_energy, use_container_width=True)
    
    with col_comp2:
        fig_bar_co2 = px.bar(
            df_comparison.sort_values('CO2 Emissions (kt)', ascending=False),
            x='Country',
            y='CO2 Emissions (kt)',
            title=f'CO2 Emissions (kt) - {comparison_year}',
            color='CO2 Emissions (kt)',
            color_continuous_scale=px.colors.sequential.RdBu_r
        )
        st.plotly_chart(fig_bar_co2, use_container_width=True)

    # Scatter plot: GDP vs CO2 Emissions
    st.subheader(f"GDP vs. CO2 Emissions ({comparison_year})")
    fig_scatter = px.scatter(
        df_comparison,
        x='GDP (USD billions)',
        y='CO2 Emissions (kt)',
        size='Population',
        color='Country',
        hover_name='Country',
        title=f'Economic Output vs. Emissions (Bubble Size = Population)',
        labels={'GDP (USD billions)': 'GDP ($B)', 'CO2 Emissions (kt)': 'CO2 (kt)'},
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

else:
    st.info(f"No data available for comparison in {comparison_year} with current filters.")

st.markdown("---")

# Section 4: Data Table & Download
st.header("Raw Data")
st.markdown("Review the filtered data in a table format.")
st.dataframe(filtered_df, use_container_width=True)

col_d1, col_d2 = st.columns(2)
with col_d1:
    st.download_button(
        label="Download Filtered Data (CSV)",
        data=filtered_df.to_csv(index=False).encode('utf-8'),
        file_name='sustainable_resources_filtered.csv',
        mime='text/csv'
    )

with col_d2:
    if os.path.exists(CSV_FILE_PATH):
        with open(CSV_FILE_PATH, "rb") as file:
            st.download_button(
                label="Download Full Source Data (CSV)",
                data=file,
                file_name=os.path.basename(CSV_FILE_PATH),
                mime='text/csv'
            )
    else:
        st.caption("Source CSV not saved to disk yet.")

st.markdown("---")
st.caption("Dashboard created with Python, Streamlit, Pandas, and Plotly.")

# ".\.venv\Scripts\Activate.ps1"; streamlit run spro.py