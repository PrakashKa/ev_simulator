import time
import streamlit as st
import plotly.graph_objects as go

from logic.physics import calculate_parameters
from config.parameters import motor_specs

def run_simulation(df, config):

    soc = 90
    distance = 0
    
    soc_list = []
    temp_list = []
    speed_list = []
    elevation_list = []
    distance_list = []
    time_list = []
    torque_list = []
    voltage_list = []
    current_list = []
    energy_consumed_list = []
    battery_current_list = []
    force_gradient = []

    # Lock layout with containers
    with st.container():
        row1_col1, row1_col2, row1_col3 = st.columns(3)
        graph_speed = row1_col1.empty()
        graph_distance = row1_col2.empty()
        graph_elevation = row1_col3.empty()

    with st.container():
        row2_col1, row2_col2, row2_col3 = st.columns(3)
        graph_motor_torque = row2_col1.empty()
        graph_motor_current = row2_col2.empty()
        graph_motor_voltage = row2_col3.empty()

    with st.container():
        row3_col1, row3_col2, row3_col3 = st.columns(3)
        graph_battery_soc = row3_col1.empty()
        graph_battery_current = row3_col2.empty()
        graph_motor_temperature = row3_col3.empty()

    # Calculate the vehicle dynamics
    df = calculate_parameters(df, config)

    total_steps = len(df)
    display_duration = 382  # seconds
    steps_per_second = total_steps // display_duration

    # Simulation loop
    for i in range(0, total_steps, steps_per_second):

        # Torque calculation
        motor_type = config["motor_type"]
        motor_data = motor_specs[motor_type]
        max_motor_torque = motor_data["torque_nm"]
        max_battery_current = config["battery_max_current"]

        torque = df["Motor Torque [Nm]"].iloc[i]
        battery_current = df["Invertor Current [A]"].iloc[i]

        soc = df["SOC [%]"].iloc[i]
        distance = df["Distance Travelled [km]"].iloc[i]
        temp = df["Motor Net Temp Rise [K]"].iloc[i]
        # temp = update_temperature(temp, total_power_kw, config["cooling_type"])

        # Append values
        time_list.append(df["Time [s]"].iloc[i])
        speed_list.append(df["Velocity [km/h]"].iloc[i])
        elevation_list.append(df["Elevation [m]"].iloc[i])
        distance_list.append(distance)
        soc_list.append(soc)
        temp_list.append(temp)
        torque_list.append(torque)
        voltage_list.append(df["Motor Voltage [V]"].iloc[i])
        current_list.append(df["Motor Current [A]"].iloc[i])
        energy_consumed_list.append(df["Energy Used [kWh]"].iloc[i])
        battery_current_list.append(battery_current)
        force_gradient.append(df['force_gradient'].iloc[i])

        # Plot 1: Speed vs Time
        fig_speed = go.Figure()
        fig_speed.add_trace(go.Scatter(x=time_list, y=speed_list, name="Speed (km/h)", line=dict(color="blue")))
        fig_speed.update_layout(title="Vehicle Speed", xaxis_title="Time (s)", yaxis_title="Speed (km/h)", width=500)
        graph_speed.plotly_chart(fig_speed, config={"responsive": True})

        # Plot 2: Distance vs Time
        fig_distance = go.Figure()
        fig_distance.add_trace(go.Scatter(x=time_list, y=distance_list, name="Distance (km)", line=dict(color="green")))
        fig_distance.update_layout(title="Distance Travelled", xaxis_title="Time (s)", yaxis_title="Distance (km)", width=500)
        graph_distance.plotly_chart(fig_distance, config={"responsive": True})

        # Plot 3: Elevation vs Time
        fig_elevation = go.Figure()
        fig_elevation.add_trace(go.Scatter(x=time_list, y=elevation_list, name="Altitude (m)", line=dict(color="purple")))
        fig_elevation.update_layout(title="Altitude (m)" , xaxis_title="Time (s)", yaxis_title="Altitude (m)", width=500)
        graph_elevation.plotly_chart(fig_elevation, config={"responsive": True})

        # Plot 4: Motor Torque vs Time
        fig_torque = go.Figure()
        fig_torque.add_trace(go.Scatter(x=time_list, y=torque_list, name="Motor Torque [Nm]", line=dict(color="orange")))
        fig_torque.update_layout(title="Motor Torque [Nm]", xaxis_title="Time (s)", yaxis_title="Motor Torque [Nm]", width=500)
        graph_motor_torque.plotly_chart(fig_torque, config={"responsive": True})

        # Plot 5: Motor Current vs Time
        fig_motor_current = go.Figure()
        fig_motor_current.add_trace(go.Scatter(x=time_list, y=current_list, name="Motor Current [A]", line=dict(color="green")))
        fig_motor_current.update_layout(title="Motor Current [A]", xaxis_title="Time (s)", yaxis_title="Motor Current [A]", width=500)
        graph_motor_current.plotly_chart(fig_motor_current, config={"responsive": True})

        # Plot 6: Motor Voltage
        fig_motor_voltage = go.Figure()
        fig_motor_voltage.add_trace(go.Scatter(x=time_list, y=voltage_list, name="Motor Voltage [V]", line=dict(color="red")))
        fig_motor_voltage.update_layout(title="Motor Voltage [V]", xaxis_title="Time (s)", yaxis_title="Motor Voltage [V]", width=500)
        graph_motor_voltage.plotly_chart(fig_motor_voltage, config={"responsive": True})

        # Plot 7: Battery SOC
        fig_soc = go.Figure()
        fig_soc.add_trace(go.Scatter(x=time_list, y=soc_list, name="SOC [%]", line=dict(color="red")))
        fig_soc.update_layout(title="State of Charge [%]", xaxis_title="Time (s)", yaxis_title="State of Charge [%]", width=500)
        graph_battery_soc.plotly_chart(fig_soc, config={"responsive": True})

        # Plot 7: Battery Current
        fig_bat_current = go.Figure()
        fig_bat_current.add_trace(go.Scatter(x=time_list, y=battery_current_list, name="Battery Current [A]", line=dict(color="green")))
        fig_bat_current.update_layout(title="Battery Current [A]", xaxis_title="Time (s)", yaxis_title="Battery Current [A]", width=500)
        graph_battery_current.plotly_chart(fig_bat_current, config={"responsive": True})

        # Plot 7: Motor temperature
        fig_motor_temp = go.Figure()
        fig_motor_temp.add_trace(go.Scatter(x=time_list, y=temp_list, name="Motor Temp Rise [K]", line=dict(color="red")))
        fig_motor_temp.update_layout(title="Motor Temp Rise [K]", xaxis_title="Time (s)", yaxis_title="Motor Temp Rise [K]", width=500)
        graph_motor_temperature.plotly_chart(fig_motor_temp, config={"responsive": True})


        # time.sleep(0.01)
        if soc <= 0:
            st.success("✅ Battery depleted. Vehicle Stopped")
            break
        
        # Check torque limit
        if torque > max_motor_torque:
            st.error("❌ Vehicle stalled: torque demand exceeded motor limit. Invalid Configuration!")
            break

        # Check battery current limit
        if battery_current > max_battery_current:
            st.error("❌ Battery overloaded: Max. Current limit reached. Invalid Configuration!")
            break


    # Split into two columns
    col1, col2 = st.columns([1, 1])  # Wider plot column

    with col1:
        st.subheader("📊 Simulation Summary")
        st.metric("Total Distance Travelled (km)", round(distance, 2))
        st.metric("Final State of Charge (%)", round(soc, 1))
        st.metric("Energy Consumed (kW)", round(df["Energy Used [kWh]"].iloc[:i].sum(), 1))
        st.metric("Energy Recovered (kW)", round(df["Recovered_kWh"].iloc[:i].sum(), 1))
        # st.metric("Peak Battery Temperature (°C)", round(max(temp_list), 1))
    with col2:
        st.subheader("📊 Performance Metrics")
        distance_range = (distance/(90-soc))*85
        ratio =  config["vehicle_cost"] /distance_range
        st.metric("Estimated Range (km)", round(distance_range, 2))
        st.metric("Vehicle Cost", round(config["vehicle_cost"], 1))
        st.metric("Cost to Range ratio", round(ratio, 1))


