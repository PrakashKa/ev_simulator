# # config/parameters.py
motor_specs = {
    "Induction": {
        "max_torque": 160,     # Nm
        "efficiency": 0.80
    },
    "Permanent Magnet": {
        "max_torque": 200,     # Nm
        "efficiency": 0.90
    },
    "Synchronous Reluctance": {
        "max_torque": 250,     # Nm
        "efficiency": 0.85
    }
}

# Wheel radius for torque calculations
wheel_size_map = {
    "15": {
        "wheel_radius": 0.191,
        "cost_inr": 16000,
    },
    "17": {
        "wheel_radius": 0.216,
        "cost_inr": 24000,
    },
    "20": {
        "wheel_radius": 0.254,
        "cost_inr": 32000,
    },
}

tyre_cost = {
    "Aerodynamic": 280,
    "Standard": 320,
    "Sporty": 450,
    "SUV-like": 600
}


style_cd_map = {
        "Aerodynamic": 0.25,
        "Sporty": 0.30,
        "Standard": 0.32,
        "SUV-like": 0.35
}

style_cost_factor = {
    "Aerodynamic": 1.15,   # higher cost due to precision shaping, lightweight materials
    "Sporty": 1.20,        # performance-oriented design, moderate premium
    "Standard": 1.00,      # baseline cost
    "SUV-like": 1.30       # larger body, higher material and assembly cost
}


# Simple weight estimation (scales with length, wheelbase, clearance, style)
style_mass_factor = {
    "Aerodynamic": 280,
    "Standard": 320,
    "Sporty": 450,
    "SUV-like": 600
}


# Default values based on preset
presets = {
    "City EV": {
        "battery_capacity": 35,
        "motor_power": 45,
        "vehicle_mass": 1100,
        "auxiliary_load": 1.5
    },
    "Performance EV": {
        "battery_capacity": 80,
        "motor_power": 250,
        "vehicle_mass": 1800,
        "auxiliary_load": 2.5
    },
    "Economy EV": {
        "battery_capacity": 40,
        "motor_power": 90,
        "vehicle_mass": 1200,
        "auxiliary_load": 1.0
    },
    "Custom": {}
}

# Battery configurations
# Cell database (example values)
# Battery data table
battery_data = {
    "Li-ion (NMC)": {"capacity_mAh": 3600, "voltage": 3.6, "max_c_rate": 3, "cost_kW": 9750,
                     "energy_density": 200, "diameter_mm": 18, "volumetric_density": None},
    "Li-ion (NCA)": {"capacity_mAh": 3200, "voltage": 3.6, "max_c_rate": 5, "cost_kW": 8900,
                     "energy_density": 220, "diameter_mm": 18, "volumetric_density": None},
    "Li-ion (LFP)": {"capacity_mAh": 3600, "voltage": 3.2, "max_c_rate": 6, "cost_kW": 12550,
                     "energy_density": 150, "diameter_mm": 26, "volumetric_density": None},
    "LTO":          {"capacity_mAh": 1500, "voltage": 2.4, "max_c_rate": 10, "cost_kW": 8000,
                     "energy_density": 70,  "diameter_mm": 66, "volumetric_density": None},
    "Solid-State":  {"capacity_mAh": 4500, "voltage": 3.8, "max_c_rate": 3, "cost_kW": 18000,
                     "energy_density": 300, "diameter_mm": None, "volumetric_density": 800}
}


motor_specs = {
    "Permanent Magnet Synchronous Motor (PMSM / PSM)": {
        "code": "PMSM",
        "power_kw": 100,
        "torque_nm": 250,
        "efficiency": 92,
        "cost_inr": 300000
    },
    "Interior Permanent Magnet Motor (IPM)": {
        "code": "IPM",
        "power_kw": 200,
        "torque_nm": 300,
        "efficiency": 93,
        "cost_inr": 400000
    },
    "Induction Motor (IM)": {
        "code": "IM",
        "power_kw": 150,
        "torque_nm": 250,
        "efficiency": 85,
        "cost_inr": 200000
    },
    "Switched Reluctance Motor (SRM)": {
        "code": "SRM",
        "power_kw": 100,
        "torque_nm": 250,
        "efficiency": 85,
        "cost_inr": 200000
    },
    "Brushless DC Motor (BLDC)": {
        "code": "BLDC",
        "power_kw": 10,
        "torque_nm": 150,
        "efficiency": 88,
        "cost_inr": 80000
    },
    "Axial Flux Permanent Magnet Motor (AFPM)": {
        "code": "AFPM",
        "power_kw": 300,
        "torque_nm": 350,
        "efficiency": 94,
        "cost_inr": 700000
    }
}


transmission_models = {
    "eGearDrive": {
        "Type": "Single-speed reduction",
        "Gear Ratio": 6,
        "Max Torque Capacity [Nm]": 300,
        "Efficiency": 0.98,
        "Cost": 80000
    },
    "Module-e-Drive": {
        "Type": "Single-speed integrated axle",
        "Gear Ratio": 9,
        "Max Torque Capacity [Nm]": 350,
        "Efficiency": 0.98,
        "Cost": 120000
    },
    "Module-3 Gearbox": {
        "Type": "Single-speed planetary",
        "Gear Ratio": 10,
        "Max Torque Capacity [Nm]": 400,
        "Efficiency": 0.97,
        "Cost": 150000
    },
    "Integrated e-Drive": {
        "Type": "Single-speed helical gear",
        "Gear Ratio": 10,
        "Max Torque Capacity [Nm]": 400,
        "Efficiency": 0.98,
        "Cost": 130000
    },
    "2-Speed EV Transmission": {
        "Type": "2-speed",
        "Gear Ratio": 8,
        "Max Torque Capacity [Nm]": 450,
        "Efficiency": 0.99,
        "Cost": 160000
    }
}

inverter_specs = {
    "2-Level IGBT VSI": {
        "efficiency": 96,
        "supports_400V": True,
        "supports_800V": False,
        "cost_inr": 6000
    },
    "2-Level MOSFET VSI (Silicon)": {
        "efficiency": 97,
        "supports_400V": True,
        "supports_800V": False,
        "cost_inr": 8000
    },
    "2-Level NPC (IGBT or Si MOSFET)": {
        "efficiency": 98,
        "supports_400V": True,
        "supports_800V": True,
        "cost_inr": 20000
    },
    "2-Level SiC MOSFET VSI": {
        "efficiency": 99,
        "supports_400V": True,
        "supports_800V": True,
        "cost_inr": 20000
    }
}

hvac_specs = {
    "HVAC Resistive": {
        "efficiency": 40,
        "power_kw": 2,
        "cost_inr": 45000
    },
    "HVAC Heatpump": {
        "efficiency": 60,
        "power_kw": 1.5,
        "cost_inr": 75000
    }
}

regen_specs = {
    "Full Hardware": {
        "efficiency": 0.35,
        "Max. Recovery": 80000,
        "cost_inr": 90000
    },
    "Software Only": {
        "efficiency": 0.2,
        "Max. Recovery": 40000,
        "cost_inr": 45000
    }
}