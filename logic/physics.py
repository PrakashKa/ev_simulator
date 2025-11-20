# logic/physics.py
from config.parameters import motor_specs, transmission_models, regen_specs,cooling_params
import math
import pandas as pd
import numpy as np
from logic.motor_calculations import calculate_pmsm_electrical, calculate_srm_electrical


def calculate_parameters(df, config):
    
    df["Speed [m/s]"] = df["Velocity [km/h]"] / 3.6   # Convert speed to m/s

    df["Acceleration [m/s²]"] = df["Speed [m/s]"].diff() / df["Time [s]"].diff()

    df["Distance Travelled [km]"] = calculate_distance(df)

    df["Slope"] = compute_slope(df["Elevation [m]"], df["Speed [m/s]"], df["Time [s]"])

    compute_resistive_forces(df, config)

    compute_power_draw(df, config)

    compute_required_torque(df, config)

    motor_temperature(df, config)

    compute_voltage_current(df, config)

    regen_energy_kwh(df, config)

    compute_soc(df, config)

    return df

def calculate_distance(df):

    # Distance travelled using trapezoidal integration
    delta_time= df["Time [s]"].diff().fillna(0)
    average_speed = (df["Speed [m/s]"] + df["Speed [m/s]"].shift(1)) / 2
    delta_distance = average_speed * delta_time
    df["Distance Travelled [km]"] = delta_distance.cumsum().fillna(0) / 1000

    return df["Distance Travelled [km]"]

def compute_slope(elevation_series, speed_series, time_series, min_dx=1.0, clamp_range=(-0.2, 0.2)):
    """
    Compute road slope as delta_h / delta_x using elevation, speed, and time.
    
    Parameters:
        elevation_series (pd.Series): Elevation in meters
        speed_series (pd.Series): Speed in m/s
        time_series (pd.Series): Time in seconds
        min_dx (float): Minimum horizontal distance to avoid instability (default = 1.0 m)
        clamp_range (tuple): Optional min/max slope clamp (e.g., ±20%)
    
    Returns:
        pd.Series: Slope values (unitless, e.g., 0.05 = 5%)
    """
    delta_h = elevation_series.diff()
    avg_speed = (speed_series + speed_series.shift(1)) / 2
    delta_t = time_series.diff()
    delta_x = avg_speed * delta_t
    delta_x = delta_x.clip(lower=min_dx)  # avoid divide-by-near-zero

    slope = delta_h / delta_x
    slope = slope.clip(lower=clamp_range[0], upper=clamp_range[1])
    
    return slope.fillna(0)

# Calculate power required to drive the car
# Weight + Drag + Rolling friction
# Force for accleration
def compute_resistive_forces(df, config):
    g = 9.81
    air_density = 1.225

    # Tyre rolling resistance coefficient
    tyre_map = {"Eco": 0.008, "Standard": 0.010, "Performance": 0.014}

    C_rr = tyre_map[config["tyre_type"]]

    # Rolling resistance
    force_rolling_resistance = C_rr * config["vehicle_mass"] * g

    # Aerodynamic drag
    force_drag = 0.5 * air_density * config["frontal_area"] * config["drag_coefficient"] * df["Speed [m/s]"]**2

    # Gradient force
    df['force_gradient'] = config["vehicle_mass"] * g * df["Slope"]

    # Acceleration force
    force_accel = config["vehicle_mass"] * df["Acceleration [m/s²]"]

    # Total force
    df["Total Force [N]"] = force_rolling_resistance + force_drag + force_accel + df['force_gradient'] 

    return

def compute_power_draw(df, config):

    # Motor efficiency lookup
    motor_data = motor_specs[config["motor_type"]]
    motor_efficiency = motor_data["efficiency"]
    inverter_eff = config["inverter_efficiency"] 
    hvac_eff = config["hvac_efficiency"] 
    sys_efficiency = config["system_efficiency"]
    
    # Mechanical power
    mechanical_power = (df["Total Force [N]"] * df["Speed [m/s]"]) / 1000

    throttle_mask = df["Velocity [km/h]"] > 0

    auxiliary_load = np.where(throttle_mask, config["auxiliary_load"], 0)

    coolant_load = np.where(throttle_mask, config["coolant_power"], 0)

    auxiliary_load = auxiliary_load / hvac_eff

    # Adjust for efficiency
    Power_Draw = mechanical_power/ (motor_efficiency * inverter_eff * sys_efficiency)

    # Adjust for efficiency
    df["Power Drawn [kW]"] = Power_Draw + auxiliary_load + coolant_load

    return
def motor_temperature(df, config):

    # Motor efficiency lookup
    motor_data = motor_specs[config["motor_type"]]
    motor_efficiency = motor_data["efficiency"]

        # --- Thermal modeling ---
    P_in = df["Power Drawn [kW]"] * 1000  # convert to W
    P_loss = P_in * (1 - motor_efficiency)

    # Motor parameters
    motor_mass = motor_data["mass"]           # kg
    motor_cp = motor_data["specific_heat"]    # J/(kg*K)

    timestep = df["Time [s]"].diff()
    # Temperature rise without cooling
    df["Motor Temp Rise [K]"] = (P_loss * timestep) / (motor_mass * motor_cp) 

    # Cooling effect

    coolant_spec = cooling_params[config["coolant_flow"]]
    coolant_flow = coolant_spec['approx_L_per_min']   # kg/s
    coolant_cp = coolant_spec['coolant_cp']          # J/(kg*K) water

    Q_cool = coolant_flow * coolant_cp * (df["Motor Temp Rise [K]"]) 

    df["Motor Net Temp Rise [K]"] = 300 + ((P_loss - Q_cool) * timestep / (motor_mass * motor_cp))*100


def compute_required_torque(df, config, drivetrain_eff = 0.9):

    wheel_torque = (df["Total Force [N]"] * config["wheel_radius"])  # Wheel Torque [Nm]
    transmission_spec = transmission_models[config["transmission_type"]]

    gear_ratio = transmission_spec["Gear Ratio"]
    drivetrain_eff = transmission_spec["Efficiency"]

    df["Motor Torque [Nm]"] = wheel_torque / (gear_ratio * drivetrain_eff)

    df["Motor Speed [rpm]"] = (df["Speed [m/s]"] * 60 / (2 * np.pi * config["wheel_radius"])) * gear_ratio
    
    return

def compute_voltage_current(df, config):

    # Motor efficiency lookup
    motor_data = motor_specs[config["motor_type"]]
    motor_code = motor_data["code"]

    Vdc = config["system_voltage"]

    if motor_code == "SRM":
        calculate_srm_electrical (df, Vdc)
    else:
         calculate_pmsm_electrical (df, Vdc)

def compute_soc(df, config):
    """
    Computes SOC [%] over time based on power draw and battery capacity.
    Assumes:
    - df["Power Drawn [kW]"] exists
    - df["Time [s]"] is cumulative time
    - config["battery_capacity"] is in kWh
    """
    battery_capacity_kwh = config["battery_capacity"]

    # Time step (dt) in seconds
    time_diff = df["Time [s]"].diff().fillna(0)

    # Energy used per step in kWh
    df["Energy Used [kWh]"] = (df["Power Drawn [kW]"] * time_diff) / 3600

    # Energy Recovery
    df["Energy Used [kWh]"] = df["Energy Used [kWh]"] - df["Recovered_kWh"]

    # SOC drop per step
    delta_soc = (df["Energy Used [kWh]"] / battery_capacity_kwh) * 100

    # Cumulative SOC drop
    df["SOC [%]"] = 90 - delta_soc.cumsum()
    df["SOC [%]"] = df["SOC [%]"].clip(lower=0)

    return

def regen_energy_kwh(df, config):
    """
    df must have columns: 'Speed [m/s]', 'Elevation [m]'
    mass_kg: vehicle mass
    dt_s: timestep between rows (seconds)
    mode: 'software' or 'hardware'
    """

    regen_type = config["regen_mode"]

    if regen_type != None:
        regen_spec = regen_specs[regen_type]
        efficiency = regen_spec['efficiency']
        Pmax_watts = regen_spec['Max. Recovery']

        # Acceleration from speed/time
        g = 9.81

        # ΔKE and ΔPE
        kinetic_energy = 0.5 * config["vehicle_mass"] * (df["Speed [m/s]"]**2).diff()
        potential_energy = config["vehicle_mass"] * g * df["Elevation [m]"].diff()

        # Net energy change
        total_energy = kinetic_energy + potential_energy

        # Braking energy available (only when energy decreases)
        BrakeEnergyRaw_J = -np.minimum(0, total_energy)

        # Power cap per step
        Cap_power_J= Pmax_watts * df["Time [s]"].diff()

        # Recovered energy
        Recovered_J = efficiency * np.minimum(BrakeEnergyRaw_J, Cap_power_J)
        df["Recovered_kWh"] = Recovered_J / 3_600_000.0
    else:
        # Return 0
        df["Recovered_kWh"] = df["Elevation [m]"] * 0

    return
