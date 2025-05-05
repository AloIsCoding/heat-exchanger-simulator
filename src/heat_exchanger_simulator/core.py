import numpy as np
import math
from utils import specific_heat_capacity, thermal_conductivity, density

def calculate_heat_transfer(fluid, mass_flow_rate, temp_in, temp_out):
    """
    Calculate heat transferred using Q = m * cp * (Tin - Tout)
    """
    cp = specific_heat_capacity.get(fluid.lower())
    if cp is None:
        print(f"Fluid '{fluid}' not found in the database.")
        return None
    Q = mass_flow_rate * cp * (temp_in - temp_out)
    return Q

def calculate_outer_surface(pipe_properties):
    """
    Calculates the outer contact surface area of a pipe.
    """
    outer_diameter = pipe_properties["outer_diameter"]
    length = pipe_properties["length"]
    return math.pi * outer_diameter * length

def calculate_conduction_resistance(pipe_properties, k):
    """
    Calculates the conduction thermal resistance through the pipe wall.
    """
    r_inner = pipe_properties["outer_diameter"] / 2 - pipe_properties["thickness"]
    r_outer = pipe_properties["outer_diameter"] / 2
    length = pipe_properties["length"]
    R_cond = math.log(r_outer / r_inner) / (2 * math.pi * k * length)
    return R_cond

def calculate_delta_T_lm(T_hot_in, T_hot_out, T_cold_in, T_cold_out):
    """
    Calculate logarithmic mean temperature difference (ΔT_lm).
    """
    dT1 = T_hot_in - T_cold_out
    dT2 = T_hot_out - T_cold_in
    if abs(dT1 - dT2) < 1e-6:
        return dT1
    return (dT1 - dT2) / math.log(dT1 / dT2)

def calculate_efficiency(Q, m_dot_cold, Cp_cold, T_hot_in, T_cold_in):
    """
    Calculate heat exchanger efficiency.
    """
    Q_max = m_dot_cold * Cp_cold * (T_hot_in - T_cold_in)
    if Q_max == 0:
        return 0
    return Q / Q_max

def simulate_tp1(fluid, hot_fluid, material, T_cold_in, T_hot_in, flow_start, flow_end, flow_steps, pipe_properties):
    """
    Simulate TP1: Impact of cold fluid flow rate on outlet temperature.
    """
    U = 100  # W/m²·K
    A = calculate_outer_surface(pipe_properties)
    flow_rates = np.linspace(flow_start, flow_end, flow_steps)
    T_outs = []
    Qs = []
    efficiencies = []
    
    fluid_density = density.get(fluid.lower(), 1.0)
    hot_fluid_density = density.get(hot_fluid.lower(), 1.0)
    Cp_cold = specific_heat_capacity.get(fluid.lower(), 4186)
    Cp_hot = specific_heat_capacity.get(hot_fluid.lower(), 4186)
    m_dot_hot = (10 * hot_fluid_density) / 60  # Fixed hot flow rate: 10 L/min
    
    for flow in flow_rates:
        m_dot_cold = (flow * fluid_density) / 60
        T_hot_out = T_hot_in - 10
        T_cold_out_guess = T_cold_in + 10
        for _ in range(5):
            ΔT_lm = calculate_delta_T_lm(T_hot_in, T_hot_out, T_cold_in, T_cold_out_guess)
            Q = U * A * ΔT_lm
            T_cold_out_guess = T_cold_in + Q / (m_dot_cold * Cp_cold)
        T_outs.append(T_cold_out_guess)
        Qs.append(Q)
        efficiencies.append(calculate_efficiency(Q, m_dot_cold, Cp_cold, T_hot_in, T_cold_in))
    
    return {
        "flow_rates": flow_rates.tolist(),
        "T_out": T_outs,
        "Q": Qs,
        "efficiency": efficiencies
    }

def simulate_tp2(fluid, hot_fluid, material, T_cold_in, flow_cold, T_hot_start, T_hot_end, T_hot_steps, pipe_properties):
    """
    Simulate TP2: Impact of hot fluid temperature on outlet temperature.
    """
    U = 100
    A = calculate_outer_surface(pipe_properties)
    T_hot_ins = np.linspace(T_hot_start, T_hot_end, T_hot_steps)
    T_outs = []
    Qs = []
    efficiencies = []
    
    fluid_density = density.get(fluid.lower(), 1.0)
    hot_fluid_density = density.get(hot_fluid.lower(), 1.0)
    Cp_cold = specific_heat_capacity.get(fluid.lower(), 4186)
    Cp_hot = specific_heat_capacity.get(hot_fluid.lower(), 4186)
    m_dot_cold = (flow_cold * fluid_density) / 60
    m_dot_hot = (10 * hot_fluid_density) / 60
    
    for T_hot_in in T_hot_ins:
        T_hot_out = T_hot_in - 10
        T_cold_out_guess = T_cold_in + 10
        for _ in range(5):
            ΔT_lm = calculate_delta_T_lm(T_hot_in, T_hot_out, T_cold_in, T_cold_out_guess)
            Q = U * A * ΔT_lm
            T_cold_out_guess = T_cold_in + Q / (m_dot_cold * Cp_cold)
        T_outs.append(T_cold_out_guess)
        Qs.append(Q)
        efficiencies.append(calculate_efficiency(Q, m_dot_cold, Cp_cold, T_hot_in, T_cold_in))
    
    return {
        "T_hot_in": T_hot_ins.tolist(),
        "T_out": T_outs,
        "Q": Qs,
        "efficiency": efficiencies
    }

def simulate_tp3(fluid, material, flow_cold, flow_hot, pipe_properties):
    """
    Simulate TP3: Impact of hot fluid choice on outlet temperature.
    """
    U = 100
    A = calculate_outer_surface(pipe_properties)
    hot_fluids = list(specific_heat_capacity.keys())
    T_outs = []
    Qs = []
    efficiencies = []
    
    fluid_density = density.get(fluid.lower(), 1.0)
    Cp_cold = specific_heat_capacity.get(fluid.lower(), 4186)
    m_dot_cold = (flow_cold * fluid_density) / 60
    T_hot_in = 80
    T_cold_in = 20
    
    for hot_fluid in hot_fluids:
        hot_fluid_density = density.get(hot_fluid.lower(), 1.0)
        Cp_hot = specific_heat_capacity.get(hot_fluid.lower(), 4186)
        m_dot_hot = (flow_hot * hot_fluid_density) / 60
        T_hot_out = T_hot_in - 10
        T_cold_out_guess = T_cold_in + 10
        for _ in range(5):
            ΔT_lm = calculate_delta_T_lm(T_hot_in, T_hot_out, T_cold_in, T_cold_out_guess)
            Q = U * A * ΔT_lm
            T_cold_out_guess = T_cold_in + Q / (m_dot_cold * Cp_cold)
        T_outs.append(T_cold_out_guess)
        Qs.append(Q)
        efficiencies.append(calculate_efficiency(Q, m_dot_cold, Cp_cold, T_hot_in, T_cold_in))
    
    return {
        "hot_fluids": hot_fluids,
        "T_out": T_outs,
        "Q": Qs,
        "efficiency": efficiencies
    }

def simulate_tp4(fluid, hot_fluid, material, flow_cold, flow_hot, T_cold_in, T_hot_in, dimension_type, dim_start, dim_end, dim_steps):
    """
    Simulate TP4: Impact of pipe dimensions on outlet temperature.
    """
    U = 100
    T_outs = []
    Qs = []
    efficiencies = []
    
    fluid_density = density.get(fluid.lower(), 1.0)
    hot_fluid_density = density.get(hot_fluid.lower(), 1.0)
    Cp_cold = specific_heat_capacity.get(fluid.lower(), 4186)
    Cp_hot = specific_heat_capacity.get(hot_fluid.lower(), 4186)
    m_dot_cold = (flow_cold * fluid_density) / 60
    m_dot_hot = (flow_hot * hot_fluid_density) / 60
    
    dims = np.linspace(dim_start, dim_end, dim_steps)
    for dim in dims:
        pipe_properties = {"outer_diameter": 0.1, "thickness": 0.005, "length": 2.0}
        if dimension_type == "length":
            pipe_properties["length"] = dim
        else:
            pipe_properties["outer_diameter"] = dim
        A = calculate_outer_surface(pipe_properties)
        T_hot_out = T_hot_in - 10
        T_cold_out_guess = T_cold_in + 10
        for _ in range(5):
            ΔT_lm = calculate_delta_T_lm(T_hot_in, T_hot_out, T_cold_in, T_cold_out_guess)
            Q = U * A * ΔT_lm
            T_cold_out_guess = T_cold_in + Q / (m_dot_cold * Cp_cold)
        T_outs.append(T_cold_out_guess)
        Qs.append(Q)
        efficiencies.append(calculate_efficiency(Q, m_dot_cold, Cp_cold, T_hot_in, T_cold_in))
    
    return {
        "dimensions": dims.tolist(),
        "T_out": T_outs,
        "Q": Qs,
        "efficiency": efficiencies,
        "dimension_type": dimension_type
    }

