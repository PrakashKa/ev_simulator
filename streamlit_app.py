# streamlit_app.py

import streamlit as st
from ui.layout import render_configuration_panel
from logic.simulator import run_simulation
from logic.plotter import plot_speed_and_elevation
import pandas as pd
import os

@st.cache_data
def load_driving_pattern():
    file_path = os.path.join("data", "bmw_i3_pattern.csv")
    try:
        df = pd.read_csv(file_path, encoding='ISO-8859-1')  # or encoding='latin1'
        return df
    except Exception as e:
        st.error(f"Error loading driving pattern: {e}")
        return pd.DataFrame()


st.set_page_config(page_title="EV Simulator", layout="wide")

st.title("🔋 EV Simulator | Design Debugger - System Design Challenge | ExtEND'25")
st.header("Input Load Profile for Simulation")
pattern = {}  # You can expand this later

df = load_driving_pattern()

if not df.empty:

    # Split into two columns
    col1, col2 = st.columns([1, 1])  # Wider plot column

    with col1:
        fig = plot_speed_and_elevation(df)
        if fig:
            st.plotly_chart(fig, config={}, use_container_width=True)
            st.markdown("Ambient temperature: 25°C - 35°C")
            # st.plotly_chart(fig, width='stretch')

    with col2:
        st.image("data/ev_system_layout.png", width='stretch')
else:
    st.warning("No data available to display.")

st.header("Configure Your EV System")
config = render_configuration_panel()

st.header("🔁 Run Simulation")
if st.button("Run Simulation"):
    run_simulation(df, config)

df.to_csv("SimulationData.csv")