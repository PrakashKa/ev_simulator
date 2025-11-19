# ui/layout.py

import streamlit as st
from config.parameters import style_cd_map, style_mass_factor, battery_data, motor_specs, wheel_size_map
from config.parameters import regen_specs, transmission_models, inverter_specs, hvac_specs, style_cost_factor


def render_configuration_panel():
    st.subheader("🔧 EV Configuration")
    # Two-column layout
    col1, col2, col3,  col4 = st.columns(4)

    with col1:

        # 🚗 Vehicle Parameters
        st.header("🚗 Vehicle Parameters")

        # User inputs
        vehicle_width = st.slider("Vehicle Width [m]", min_value=1.2, max_value=2.5, value=1.8, step=0.1)
        vehicle_height = st.slider("Vehicle Height [m]", min_value=1.2, max_value=2.0, value=1.45, step=0.1)
        vehicle_length = st.slider("Vehicle Length [m]", min_value=2.5, max_value=5.0, value=4.2, step=0.1)
        wheelbase = st.slider("Wheelbase [m]", min_value=1.3, max_value=3.5, value=2.6, step=0.1)
        ground_clearance = st.slider("Ground Clearance [m]", min_value=0.1, max_value=0.3, value=0.15, step=0.1)
        vehicle_style = st.selectbox("Vehicle Style", ["Aerodynamic", "Sporty", "Standard", "SUV-like"])

        # Validation check
        if wheelbase >= 0.63 * vehicle_length or wheelbase <= 0.56 * vehicle_length:
            st.error("❌ Wheelbase not possible for the selected vehicle length. Please adjust values.")
            st.stop()  # stops execution until user fixes input

        # Derived parameters
        frontal_area = vehicle_width * vehicle_height
        drag_coefficient = style_cd_map.get(vehicle_style, 0.32)
        vehicle_mass = (vehicle_length * wheelbase * 100) + (ground_clearance * 1000) + style_mass_factor.get(vehicle_style, 320)

        # Display derived values
        st.markdown(f"**Frontal Area:** {frontal_area:.2f} m²")
        st.markdown(f"**Drag Coefficient (Cd):** {drag_coefficient:.2f}")
        st.markdown(f"**Estimated Vehicle Mass:** {vehicle_mass:.0f} kg")

        st.markdown(f"**Total Vehicle Mass (without battery):** {vehicle_mass:.1f} kg")
        tyre_size = st.selectbox("Tyre Size", list(wheel_size_map.keys()))
        tyre_spec = wheel_size_map[tyre_size]
        wheel_radius = tyre_spec['wheel_radius']
        tyre_type = st.selectbox("Tyre Type", ["Eco", "Standard", "Performance"])
        tyre_cost = tyre_spec['cost_inr']

    with col2:

        # 🔋 Electrical Configurator
        st.header("🔋 Electrical Configurator")
        system_voltage = st.selectbox("System Voltage", ["400V", "800V"])

        if system_voltage == "400V":
            sys_voltage = 400
            sys_efficiency = 0.85
            system_cost_factor = 1
        else:
            sys_voltage = 800
            sys_efficiency = 0.90
            system_cost_factor = 1.2

        
        # 🔋 Battery Configurator
        st.markdown("🔋 Battery Configurator")
        
        battery_chemistry = st.selectbox("Select Cell Chemistry", list(battery_data.keys()))
        battery_spec = battery_data[battery_chemistry]

        if battery_chemistry in ["Li-ion (NMC)", "Li-ion (NCA)", "Li-ion (LFP)", "LTO"]:
            # Display cell note
            st.markdown(f"""
            **Cell Specs:**
            - Capacity: {battery_spec['capacity_mAh']} mAh
            - Nominal Voltage: {battery_spec['voltage']} V
            - Max Discharge Rating: {battery_spec['max_c_rate']}C
            """)

            # User input: total cells
            total_cells = st.number_input("Total Number of Cells", min_value=1, max_value=5000, value=400, step=1)

            # User input: cells in series
            cells_series = st.number_input("Cells in Series", min_value=1, max_value=total_cells, value=100, step=1)

            # Derived: cells in parallel
            if total_cells % cells_series != 0:
                st.error("❌ Total cells must be divisible by series count for valid parallel configuration.")
                cells_parallel = 0
            else:
                cells_parallel = total_cells // cells_series
                st.success(f"Cells in Parallel: {cells_parallel}")

            # User input: No of layers
            layer_count = st.number_input("Cell Layers", min_value=1, max_value=4, value=2, step=1)

            # Capacity per cell in Ah
            cell_capacity_Ah = battery_spec["capacity_mAh"] / 1000.0

            # Pack capacity = cell capacity × parallel
            pack_capacity_Ah = cell_capacity_Ah * cells_parallel

            # Pack energy = capacity × voltage × series
            pack_voltage = battery_spec["voltage"] * cells_series

            pack_energy_Wh = pack_capacity_Ah * pack_voltage

            # Max current = capacity × C-rate × parallel
            max_current_A = cell_capacity_Ah * battery_spec["max_c_rate"] * cells_parallel

            if system_voltage == "400V":
                if pack_voltage < 300 or pack_voltage > 450:
                    st.error("❌For 400V System battery pack voltage should be with in 300V to 450V")
                    pack_energy_Wh = 0
            else:
                if pack_voltage < 660 or pack_voltage > 820:
                    st.error("❌For 400V System battery pack voltage should be with in 660V to 820V")
                    pack_energy_Wh = 0

            # Display results
            st.markdown(f"""
            **Battery Pack Specs:**
            - Voltage: {pack_voltage:.1f} V | Capacity: {pack_capacity_Ah:.1f} Ah
            - Energy: {pack_energy_Wh/1000:.2f} kWh
            - Max Continuous Current: {max_current_A:.1f} A
            """)

             # --- Size calculation ---
            # Cell diameter + 2 mm gap
            cell_pitch_mm = battery_spec["diameter_mm"] + 2

            # Calculate dimensions
            pack_length_series   = (cell_pitch_mm * cells_series) / (1000 * layer_count)  # meters
            pack_length_parallel = (cell_pitch_mm * cells_parallel) / 1000  # meters

            # Assign width = smaller, length = larger
            if pack_length_series < pack_length_parallel:
                pack_width_m  = pack_length_series
                pack_length_m = pack_length_parallel
            else:
                pack_width_m  = pack_length_parallel
                pack_length_m = pack_length_series


        # For LTO: direct capacity input
        elif battery_chemistry == "Solid-State":

            pack_capacity_kWh = st.number_input("Enter Pack Capacity [kWh]", min_value=1.0, value=45.0, step=1.0)
            pack_energy_Wh = pack_capacity_kWh * 1000
            pack_voltage = st.number_input("Battery Pack Voltage [V]", min_value=300, max_value=720, value=360, step=10)
            cell_capacity_Ah  = pack_energy_Wh / pack_voltage
            max_current_A = cell_capacity_Ah * battery_spec["max_c_rate"] 

            # Display results
            st.markdown(f"""
            **Battery Pack Specs:**
            - Max Continuous Current: {cell_capacity_Ah:.1f} A
            - Max Peak Current: {max_current_A:.1f} A
            """)

            # User input: No of layers
            layer_count = 3

            # Solid-state uses volumetric density (Wh/L)
            pack_volume_L = pack_energy_Wh / battery_spec["volumetric_density"]
            # Volume-based cube root approximation
            pack_volume_m3 = pack_volume_L / 1000
            cube_side = pack_volume_m3**(1/3)
            pack_width_m, pack_length_m = cube_side, cube_side / layer_count

        # --- Weight calculation ---
        pack_weight_kg = pack_energy_Wh / battery_spec["energy_density"]

        # --- Constraint checks ---
        max_length = 0.7 * wheelbase
        max_width = 0.8 * vehicle_width
        max_volume = 0.7 * wheelbase * 0.8 * vehicle_width * 0.15

        if pack_length_m > max_length:
            st.error(f"❌ Battery length {pack_length_m:.2f} m exceeds 70% of wheelbase ({max_length:.2f} m).")
            pack_energy_Wh = 0

        if pack_width_m > max_width:
            st.error(f"❌ Battery width {pack_width_m:.2f} m exceeds 80% of vehicle width ({max_width:.2f} m).")
            pack_energy_Wh = 0

        if battery_chemistry in ["Solid-State"]:
            if pack_volume_m3 > max_volume:
                st.error(f"❌ Battery volume {pack_volume_m3:.3f} m³ exceeds allowed {max_volume:.3f} m³.")
                pack_energy_Wh = 0

         # Display results
        st.markdown(f"""
        **Battery Pack Dimensions:**
        - Pack Weight: {pack_weight_kg:.1f} kg
        - Pack Length: {pack_length_m:.2f} m | Pack Width: {pack_width_m:.2f} m """)

        total_vehicle_mass = vehicle_mass + pack_weight_kg
        battery_cost = pack_energy_Wh * battery_spec["cost_kW"] / 1000 

        st.caption(f"Battery adds {pack_weight_kg:.1f} kg to base mass. |Battery pack cost: {battery_cost}")

    with col3:

        # 🔧 Motor Configurator
        st.header("🔧 Motor Configurator")

        # User selection (full name shown)
        motor_type = st.selectbox("Select Motor Type", list(motor_specs.keys()))
        motor_spec = motor_specs[motor_type]

        # Internal short code available
        motor_type = motor_spec["code"]

        # Display motor info
        st.markdown(f"""
        **Motor Specifications:**
        - Code: {motor_type}
        - Power Rating: {motor_spec['power_kw']} kW  
        - Torque: {motor_spec['torque_nm']} Nm  
        - Efficiency: {motor_spec['efficiency']} %  
        - Approx. Cost: ₹{motor_spec['cost_inr']:,}
        """)

        st.markdown("### ⚙️ Transmission")
        transmission_type = st.selectbox("Drive Model", list(transmission_models.keys()))
        transmission_spec = transmission_models[transmission_type]

        if transmission_type:
            for key, value in transmission_models[transmission_type].items():
                st.write(f"**{key}:** {value}")

    with col4:

        st.header("⚙️ Auxillary")

        hvac_type = st.selectbox("Select HVAC", list(hvac_specs.keys()))
        hvac_spec = hvac_specs[hvac_type]
        auxiliary_load = hvac_spec['power_kw'] / hvac_spec['efficiency']
        auxillary_cost = hvac_spec['cost_inr']

        # Display motor info
        st.markdown(f"""
        **HVAC Specifications:**
        - Power Rating: {auxiliary_load} kW  
        - Efficiency: {hvac_spec['efficiency']} %  
        - Approx. Cost: ₹{auxillary_cost}
        """)

        st.markdown("### 🔄 Regenerative Braking")

        regen_enabled = st.checkbox("Enable Regenerative Braking", value = False)
        if regen_enabled == True:
            regen_type = st.selectbox("Select HVAC", list(regen_specs.keys()))
            regen_spec = regen_specs[regen_type]
            regen_cost = regen_spec['cost_inr']
                    # Display motor info
            st.markdown(f"""
            **Regenerative Braking:**
            - Efficiency: {regen_spec['efficiency']} %  
            - Approx. Cost: ₹{regen_cost}
            """)
        else:
            regen_type = None
            regen_cost = 0

        # ⚡ Inverter Configurator
        st.markdown("### ⚡ Power Electronics")
        
        # User selection
        inverter_type = st.selectbox("Select Inverter Type", list(inverter_specs.keys()))
        invertor_spec = inverter_specs[inverter_type]
        inverter_efficiency = invertor_spec['efficiency']
        inverter_cost = invertor_spec['cost_inr']

        # Voltage compatibility check
        voltage_supported = (
            invertor_spec["supports_400V"] if sys_voltage == 400 else invertor_spec  ["supports_800V"]
        )

        # Display inverter info
        st.markdown(f"""
        **Inverter Specifications:**
        - Typical Efficiency: {invertor_spec['efficiency']}%
        - Compatible with 400V: {"✅" if invertor_spec['supports_400V'] else "❌"}
        - Compatible with 800V: {"✅" if invertor_spec['supports_800V'] else "❌"}
        - Cost: ₹{invertor_spec['cost_inr']:,}
        """)

        # Warning if voltage mismatch
        if not voltage_supported:
            st.error(f"❌ Selected inverter is not compatible with {sys_voltage} V system.")
            pack_energy_Wh = 0
        
    motor_cost = motor_spec['cost_inr']

    transmission_cost = transmission_spec["Cost"]


    # Base Cost 2,50,000
    chassis_cost = 350000 * style_cost_factor[vehicle_style]

    st.subheader("🔧 Configuration Cost")
    total_cost = (motor_cost + + regen_cost + inverter_cost)*system_cost_factor + battery_cost   + transmission_cost + tyre_cost + chassis_cost + auxillary_cost 
    st.markdown(f"**Estimated Vehicle Configuration Cost:** ₹{total_cost:,.0f}")

    return {
        "system_voltage" : sys_voltage,
        "system efficiency": sys_efficiency,
        "battery_capacity": pack_energy_Wh/1000,
        "battery_max_current": max_current_A,
        "battery_chemistry": battery_chemistry,
        # "cooling_type": cooling_type,
        "motor_type": motor_type,
        "motor_power": motor_spec['power_kw'],
        "inverter_efficiency": inverter_efficiency,
        "regen_enabled": regen_enabled,
        "regen_mode": regen_type,
        "vehicle_mass": total_vehicle_mass,
        "drag_coefficient": drag_coefficient,
        "auxiliary_load": auxiliary_load,
        "frontal_area": frontal_area,             # m² (optional, default ~2.2 for compact cars)
        "tyre_type": tyre_type,               # "Eco", "Standard", "Performance"
        "wheel_radius": wheel_radius,
        "transmission_type": transmission_type
    }

