import numpy as np
import pandas as pd

# ---------- helper to create a smooth, compact efficiency map ----------
def make_eff_map(eta_max, t_ref, n_ref, a=0.6, b=0.5, eta_min=0.6):
    """
    Returns a function eff(torque, rpm) producing a smooth efficiency value.
    - eta_max : peak efficiency (0-1)
    - t_ref   : reference torque (Nm) for normalization (around rated torque)
    - n_ref   : reference rpm for normalization (around rated speed)
    - a, b    : shape coefficients (higher -> steeper drop)
    - eta_min : lower clamp for efficiency
    """
    def eff_map(torque, rpm):
        # allow array-like inputs
        T = np.asarray(torque, dtype=float)
        N = np.asarray(rpm, dtype=float)

        # normalized terms (>=0)
        tn = np.abs(T) / (t_ref + 1e-12)
        nn = np.maximum(0.0, N) / (n_ref + 1e-12)

        # compact smooth model:
        # peak at low-medium torque/speed; penalize high torque (~I^2R) and high speed (iron/windage)
        # shape: eta = eta_max - A*(tn^p) - B*(nn^q)
        A = a * (eta_max - eta_min)
        B = b * (eta_max - eta_min)

        eta = eta_max - A * (tn ** 2.0) - B * (nn ** 1.6)

        # small low-speed copper penalty (very low speed, higher losses due to high currents)
        eta = np.where((nn < 0.05) & (tn > 0.5),
                       eta - 0.04 * (tn - 0.5), eta)

        # clamp
        eta = np.clip(eta, eta_min, eta_max)
        return eta
    
    return eff_map

# ---------- MOTOR CONSTANTS (compatible with your compute function) ----------
# Each entry includes: k_t, k_e, R, L, pole_pairs, efficiency (scalar fallback),
# nominal_kW and an eff_map callable stored under "eff_map".
MOTOR_CONSTANTS = {
    "PMSM": {
        "k_t": 0.45,            # Nm/A (example)
        "k_e": 0.075,           # V/(rad/s) (example)
        "R": 0.020,             # ohm
        "L": 1.2e-3,            # H
        "pole_pairs": 4,
        "efficiency": 0.92,     # fallback scalar
        "nominal_kW": 100,
        # reference torque & speed (used to normalize inputs in eff_map)
        "t_ref": 160.0,         # Nm (approx. rated torque)
        "n_ref": 6000.0,        # rpm (approx. rated speed)
        "eff_map": make_eff_map(eta_max=0.94, t_ref=160.0, n_ref=6000.0, a=0.6, b=0.55, eta_min=0.6)
    },

    "IPM": {
        "k_t": 0.40,
        "k_e": 0.070,
        "R": 0.015,
        "L": 0.8e-3,
        "pole_pairs": 4,
        "efficiency": 0.93,
        "nominal_kW": 200,
        "t_ref": 320.0,
        "n_ref": 6000.0,
        "eff_map": make_eff_map(eta_max=0.96, t_ref=320.0, n_ref=6000.0, a=0.55, b=0.5, eta_min=0.62)
    },

    "BLDC": {
        "k_t": 0.60,
        "k_e": 0.100,
        "R": 0.050,
        "L": 1.8e-3,
        "pole_pairs": 4,
        "efficiency": 0.88,
        "nominal_kW": 75,
        "t_ref": 30.0,
        "n_ref": 4000.0,
        "eff_map": make_eff_map(eta_max=0.92, t_ref=30.0, n_ref=4000.0, a=0.65, b=0.6, eta_min=0.55)
    },

    "AFPM": {
        "k_t": 0.50,
        "k_e": 0.075,
        "R": 0.018,
        "L": 0.6e-3,
        "pole_pairs": 5,
        "efficiency": 0.96,
        "nominal_kW": 300,
        "t_ref": 450.0,
        "n_ref": 8000.0,
        "eff_map": make_eff_map(eta_max=0.97, t_ref=450.0, n_ref=8000.0, a=0.5, b=0.45, eta_min=0.65)
    },

    # IM uses k_e field as nominal line-line voltage in your previous function;
    # eff_map still added for better power estimates
    "IM": {
        "k_e": 300.0,           # V_ll_rms (used as voltage assumption)
        "efficiency": 0.90,     # fallback scalar
        "nominal_kW": 150,
        "t_ref": 200.0,
        "n_ref": 5000.0,
        "eff_map": make_eff_map(eta_max=0.90, t_ref=200.0, n_ref=5000.0, a=0.7, b=0.6, eta_min=0.6)
    },

    "SRM": {
        "dL_dtheta": 0.004,     # H/rad
        "R": 0.040,
        "L": 3.0e-3,
        "pole_pairs": 4,
        "efficiency": 0.88,
        "nominal_kW": 100,
        "t_ref": 200.0,
        "n_ref": 4000.0,
        "eff_map": make_eff_map(eta_max=0.88, t_ref=200.0, n_ref=4000.0, a=0.75, b=0.7, eta_min=0.55)
    }
}

# ---------- small utility to obtain efficiency (uses eff_map if present) ----------
def get_efficiency_for(motor_type, torque, rpm):
    """
    Returns efficiency in [0..1]. Supports scalar or array-like torque/rpm.
    """
    m = MOTOR_CONSTANTS[motor_type]
    eff_map = m.get("eff_map", None)
    if eff_map is not None:
        return eff_map(torque, rpm)
    else:
        # fallback scalar (broadcast)
        return np.full_like(np.asarray(torque, dtype=float), fill_value=m.get("efficiency", 0.9), dtype=float)

def calculate_pmsm_electrical(df, Vdc):

    # Known motor params
    Rs = 0.05        # ohm
    Ld = 0.0002      # H
    Lq = 0.0002      # H  # surface PMSM assumption
    lam = 0.06       # Wb (flux linkage)
    p = 4            # pole pairs


    # Kinematics
    omega_m = 2 * np.pi * df["Motor Speed [rpm]"] / 60.0
    omega_e = p * omega_m

    # Currents (surface PMSM, i_d = 0)
    iq = (2.0/3.0) * (df["Motor Torque [Nm]"] / (p * lam))
    id_curr = np.zeros_like(iq)

    # Voltages
    vd = Rs * id_curr - omega_e * Lq * iq
    vq = Rs * iq + omega_e * Ld * id_curr + omega_e * lam
    Vph = np.sqrt(vd**2 + vq**2)
    Iph = np.sqrt(id_curr**2 + iq**2)

    # DC bus current (average)
    P_elec = Vph * Iph # airgap electrical power
    Idc = P_elec / Vdc                      # inverter DC current

    df["Invertor Current [A]"] = Idc

    # Feasibility check (illustrative threshold)
    # Note: achievable phase voltage depends on modulation; compare against your inverter’s AC capability.
    feasible = Vph < (Vdc / np.sqrt(3))  # rough line-line rms to phase rms relationship (strategy-dependent)

    # Add to DataFrame
    df["Motor Voltage [V]"] = Vph
    df["Motor Current [A]"] = Iph


def calculate_srm_electrical(df, Vdc):
    """
    Calculate SRM current and voltage using simplified inductance-based model.
    
    Expected columns in df:
        - Motor Speed [rpm]
        - Motor Torque [Nm]
    
    Returns:
        DataFrame with added columns: Iph, Vph
    """
    # Known motor params (example values)
    Rs = 0.05        # ohm (phase resistance)
    Lmin = 0.0001    # H (minimum inductance)
    Lmax = 0.0010    # H (maximum inductance)
    p = 4            # pole pairs


    # Kinematics
    omega_m = 2 * np.pi * df["Motor Speed [rpm]"] / 60.0   # mechanical rad/s
    omega_e = p * omega_m                                 # electrical rad/s
    
    # Approximate inductance slope (dL/dθ)
    dL_dtheta = (Lmax - Lmin) / (np.pi / p)   # per electrical rad
    
    # Current estimation from torque equation: T = 0.5 * i^2 * dL/dθ
    Iph = np.sqrt(2 * df["Motor Torque [Nm]"] / dL_dtheta)
    
    # Voltage estimation: v = Rs*i + ω_e*L*i
    # Use average inductance for approximation
    Lavg = 0.5 * (Lmin + Lmax)
    Vph = Rs * Iph + omega_e * Lavg * Iph
    
    df["Motor Current [A]"] = Iph
    df["Motor Voltage [V]"] = Vph

    # DC bus current (average)
    P_elec = Iph * Vph  # airgap electrical power
    Idc = P_elec / Vdc  # inverter DC current

    df["Invertor Current [A]"] = Idc

    