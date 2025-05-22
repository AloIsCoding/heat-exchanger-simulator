import numpy as np
import math
from utils import specific_heat_capacity, thermal_conductivity, density, viscosity, thermal_conductivity_fluid

def calculate_heat_transfer(fluid, mass_flow_rate, temp_in, temp_out):
    """
    Calculate heat transferred using Q = m * cp * (Tin - Tout)
    """
    cp = specific_heat_capacity.get(fluid.lower())
    if cp is None:
        raise ValueError(f"Fluid '{fluid}' not found in the database.")
    Q = mass_flow_rate * cp * (temp_in - temp_out)
    return Q

def calculate_outer_surface(pipe_properties):
    """
    Calculates the outer contact surface area of a pipe.
    """
    outer_diameter = pipe_properties["outer_diameter"]
    length = pipe_properties["length"]
    return math.pi * outer_diameter * length

def calculate_log_mean_temperature_difference(Q,U,A):
    """
    Calculates the logarithmic mean temperature difference (Tlm) using:
    Tlm = Q / (U * A)
    """
    Tlm = Q / (U * A)
    return Tlm

def calculate_efficiency(Q, m_dot_cold, Cp_cold, T_hot_in, T_cold_in):
    """
    Calculate heat exchanger efficiency.
    """
    Q_max = m_dot_cold * Cp_cold * (T_hot_in - T_cold_in)
    if Q_max == 0:
        return 0
    return Q / Q_max

def validate_pipe_dimensions(internal_pipe, external_pipe):
    """
    Checks if the external pipe is physically larger than the internal pipe.
    """
    internal_outer_diameter = internal_pipe["outer_diameter"]
    external_inner_diameter = external_pipe["inter_diameter"]
    if external_inner_diameter <= internal_outer_diameter:
        raise ValueError(
            f"Internal pipe outer diameter ({internal_outer_diameter:.4f} m) "
            f"is too large for external pipe inner diameter ({external_inner_diameter:.4f} m)."
        )
    return True

def calculate_reynolds_number(fluid, mass_flow_rate, pipe_diameter):
    """
    Calculates the Reynolds number.
    """
    rho = density.get(fluid.lower(), 1.0)
    mu = viscosity.get(fluid.lower(), 0.001)
    area = math.pi * (pipe_diameter / 2) ** 2
    velocity = mass_flow_rate / (rho * area)
    Re = (rho * velocity * pipe_diameter) / mu
    return Re

def interpret_reynolds_number(Re):
    """
    Returns a string describing the flow regime based on the Reynolds number.
    """
    return "Laminar" if Re < 5000 else "Turbulent"

def calculate_prandtl_number(fluid):
    """
    Calculate Prandtl number from dynamic viscosity, specific heat, and conductivity.
    """
    mu = viscosity.get(fluid.lower(), 0.001)
    cp = specific_heat_capacity.get(fluid.lower(), 4186)
    k = thermal_conductivity_fluid.get(fluid.lower(), 0.6)
    return mu * cp / k

def calculate_convection_coefficient(fluid, pipe_diameter, Re, Pr):
    """
    Calculate the convection heat transfer coefficient.
    """
    k = thermal_conductivity_fluid.get(fluid.lower(), 0.6)
    if Re < 5000:  # Laminar
        return 3.66 * k / pipe_diameter  # Constant wall temperature
    else:  # Turbulent
        return 0.023 * (Re ** 0.8) * (Pr ** 0.33) * k / pipe_diameter

def calculate_overall_heat_transfer_coefficient(pipe, material, h_internal, h_external):
    """
    Calculates the overall heat transfer coefficient U (W/m²·K).
    """
    ri = pipe["outer_diameter"] / 2 - pipe["thickness"]
    ro = pipe["outer_diameter"] / 2
    length = pipe["length"]
    k = thermal_conductivity.get(material.lower(), 16.0)

    resistance_internal = 1 / (2 * math.pi * length * ri * h_internal)
    resistance_wall = math.log(ro / ri) / (2 * math.pi * length * k)
    resistance_external = 1 / (2 * math.pi * length * ro * h_external)

    total_resistance = resistance_internal + resistance_wall + resistance_external
    U = 1 / (2 * math.pi * length * ro * total_resistance)
    return U

def simulate_tp1(fluid, hot_fluid, material, T_cold_in, T_hot_in, flow_start, flow_end, flow_steps, pipe_properties,gap=0.01):
    """
    Simulate TP1: Impact of cold fluid flow rate on outlet temperature.
    """
    A = calculate_outer_surface(pipe_properties)
    flow_rates = np.linspace(flow_start, flow_end, flow_steps)
    T_outs = []
    Qs = []
    efficiencies = []
    Re_internals = []
    Re_externals = []
    Re_internal_regimes = []
    Re_external_regimes = []
    Us = []

    fluid_density = density.get(fluid.lower(), 1.0)
    hot_fluid_density = density.get(hot_fluid.lower(), 1.0)
    Cp_cold = specific_heat_capacity.get(fluid.lower(), 4186)
    Cp_hot = specific_heat_capacity.get(hot_fluid.lower(), 4186)
    m_dot_hot = (10 * hot_fluid_density) / 60  # Fixed hot flow rate: 10 L/min

    external_pipe = {
        "inter_diameter": pipe_properties["outer_diameter"] + gap,
        "thickness": pipe_properties["thickness"],
        "length": pipe_properties["length"]
    }
    validate_pipe_dimensions(pipe_properties, external_pipe)

    Re_external = calculate_reynolds_number(hot_fluid, m_dot_hot, external_pipe["inter_diameter"])
    Pr_external = calculate_prandtl_number(hot_fluid)
    h_external = calculate_convection_coefficient(hot_fluid, external_pipe["inter_diameter"], Re_external, Pr_external)

    for flow in flow_rates:
        m_dot_cold = (flow * fluid_density) / 60
        Re_internal = calculate_reynolds_number(fluid, m_dot_cold, pipe_properties["outer_diameter"] - 2 * pipe_properties["thickness"])
        Pr_internal = calculate_prandtl_number(fluid)
        h_internal = calculate_convection_coefficient(fluid, pipe_properties["outer_diameter"] - 2 * pipe_properties["thickness"], Re_internal, Pr_internal)
        U = calculate_overall_heat_transfer_coefficient(pipe_properties, material, h_internal, h_external)

        T_hot_out = T_hot_in - 10
        T_cold_out_guess = T_cold_in + 10
        for _ in range(5):
            delta_T_lm = calculate_delta_T_lm(T_hot_in, T_hot_out, T_cold_in, T_cold_out_guess)
            Q = U * A * delta_T_lm
            T_cold_out_guess = T_cold_in + Q / (m_dot_cold * Cp_cold)
        T_outs.append(T_cold_out_guess)
        Qs.append(Q)
        efficiencies.append(calculate_efficiency(Q, m_dot_cold, Cp_cold, T_hot_in, T_cold_in))
        Re_internals.append(Re_internal)
        Re_externals.append(Re_external)
        Re_internal_regimes.append(interpret_reynolds_number(Re_internal))
        Re_external_regimes.append(interpret_reynolds_number(Re_external))
        Us.append(U)

    return {
        "flow_rates": flow_rates.tolist(),
        "T_out": T_outs,
        "Q": Qs,
        "efficiency": efficiencies,
        "U": Us,
        "Re_internal": Re_internals,
        "Re_external": Re_externals,
        "Re_internal_regime": Re_internal_regimes,
        "Re_external_regime": Re_external_regimes
    }

def simulate_tp2(fluid, hot_fluid, material, T_cold_in, flow_cold, T_hot_start, T_hot_end, T_hot_steps, pipe_properties,gap=0.01):
    """
    Simulate TP2: Impact of hot fluid temperature on outlet temperature.
    """
    A = calculate_outer_surface(pipe_properties)
    T_hot_ins = np.linspace(T_hot_start, T_hot_end, T_hot_steps)
    T_outs = []
    Qs = []
    efficiencies = []
    Re_internals = []
    Re_externals = []
    Re_internal_regimes = []
    Re_external_regimes = []
    Us = []

    fluid_density = density.get(fluid.lower(), 1.0)
    hot_fluid_density = density.get(hot_fluid.lower(), 1.0)
    Cp_cold = specific_heat_capacity.get(fluid.lower(), 4186)
    Cp_hot = specific_heat_capacity.get(hot_fluid.lower(), 4186)
    m_dot_cold = (flow_cold * fluid_density) / 60
    m_dot_hot = (10 * hot_fluid_density) / 60

    external_pipe = {
        "inter_diameter": pipe_properties["outer_diameter"] + gap,
        "thickness": pipe_properties["thickness"],
        "length": pipe_properties["length"]
    }
    validate_pipe_dimensions(pipe_properties, external_pipe)

    Re_internal = calculate_reynolds_number(fluid, m_dot_cold, pipe_properties["outer_diameter"] - 2 * pipe_properties["thickness"])
    Pr_internal = calculate_prandtl_number(fluid)
    h_internal = calculate_convection_coefficient(fluid, pipe_properties["outer_diameter"] - 2 * pipe_properties["thickness"], Re_internal, Pr_internal)
    Re_external = calculate_reynolds_number(hot_fluid, m_dot_hot, external_pipe["inter_diameter"])
    Pr_external = calculate_prandtl_number(hot_fluid)
    h_external = calculate_convection_coefficient(hot_fluid, external_pipe["inter_diameter"], Re_external, Pr_external)
    U = calculate_overall_heat_transfer_coefficient(pipe_properties, material, h_internal, h_external)

    for T_hot_in in T_hot_ins:
        T_hot_out = T_hot_in - 10
        T_cold_out_guess = T_cold_in + 10
        for _ in range(5):
            delta_T_lm = calculate_delta_T_lm(T_hot_in, T_hot_out, T_cold_in, T_cold_out_guess)
            Q = U * A * delta_T_lm
            T_cold_out_guess = T_cold_in + Q / (m_dot_cold * Cp_cold)
        T_outs.append(T_cold_out_guess)
        Qs.append(Q)
        efficiencies.append(calculate_efficiency(Q, m_dot_cold, Cp_cold, T_hot_in, T_cold_in))
        Re_internals.append(Re_internal)
        Re_externals.append(Re_external)
        Re_internal_regimes.append(interpret_reynolds_number(Re_internal))
        Re_external_regimes.append(interpret_reynolds_number(Re_external))
        Us.append(U)

    return {
        "T_hot_in": T_hot_ins.tolist(),
        "T_out": T_outs,
        "Q": Qs,
        "efficiency": efficiencies,
        "U": Us,
        "Re_internal": Re_internals,
        "Re_external": Re_externals,
        "Re_internal_regime": Re_internal_regimes,
        "Re_external_regime": Re_external_regimes
    }

def simulate_tp3(fluid, material, flow_cold, flow_hot, pipe_properties,gap=0.01):
    """
    Simulate TP3: Impact of hot fluid choice on outlet temperature.
    """
    A = calculate_outer_surface(pipe_properties)
    hot_fluids = list(specific_heat_capacity.keys())
    T_outs = []
    Qs = []
    efficiencies = []
    Re_internals = []
    Re_externals = []
    Re_internal_regimes = []
    Re_external_regimes = []
    Us = []

    fluid_density = density.get(fluid.lower(), 1.0)
    Cp_cold = specific_heat_capacity.get(fluid.lower(), 4186)
    m_dot_cold = (flow_cold * fluid_density) / 60
    T_hot_in = 80
    T_cold_in = 20

    external_pipe = {
        "inter_diameter": pipe_properties["outer_diameter"] + gap,
        "thickness": pipe_properties["thickness"],
        "length": pipe_properties["length"]
    }
    validate_pipe_dimensions(pipe_properties, external_pipe)

    Re_internal = calculate_reynolds_number(fluid, m_dot_cold, pipe_properties["outer_diameter"] - 2 * pipe_properties["thickness"])
    Pr_internal = calculate_prandtl_number(fluid)
    h_internal = calculate_convection_coefficient(fluid, pipe_properties["outer_diameter"] - 2 * pipe_properties["thickness"], Re_internal, Pr_internal)

    for hot_fluid in hot_fluids:
        hot_fluid_density = density.get(hot_fluid.lower(), 1.0)
        Cp_hot = specific_heat_capacity.get(hot_fluid.lower(), 4186)
        m_dot_hot = (flow_hot * hot_fluid_density) / 60
        Re_external = calculate_reynolds_number(hot_fluid, m_dot_hot, external_pipe["inter_diameter"])
        Pr_external = calculate_prandtl_number(hot_fluid)
        h_external = calculate_convection_coefficient(hot_fluid, external_pipe["inter_diameter"], Re_external, Pr_external)
        U = calculate_overall_heat_transfer_coefficient(pipe_properties, material, h_internal, h_external)

        T_hot_out = T_hot_in - 10
        T_cold_out_guess = T_cold_in + 10
        for _ in range(5):
            delta_T_lm = calculate_delta_T_lm(T_hot_in, T_hot_out, T_cold_in, T_cold_out_guess)
            Q = U * A * delta_T_lm
            T_cold_out_guess = T_cold_in + Q / (m_dot_cold * Cp_cold)
        T_outs.append(T_cold_out_guess)
        Qs.append(Q)
        efficiencies.append(calculate_efficiency(Q, m_dot_cold, Cp_cold, T_hot_in, T_cold_in))
        Re_internals.append(Re_internal)
        Re_externals.append(Re_external)
        Re_internal_regimes.append(interpret_reynolds_number(Re_internal))
        Re_external_regimes.append(interpret_reynolds_number(Re_external))
        Us.append(U)

    return {
        "hot_fluids": hot_fluids,
        "T_out": T_outs,
        "Q": Qs,
        "efficiency": efficiencies,
        "U": Us,
        "Re_internal": Re_internals,
        "Re_external": Re_externals,
        "Re_internal_regime": Re_internal_regimes,
        "Re_external_regime": Re_external_regimes
    }

def simulate_tp4(fluid, hot_fluid, material, flow_cold, flow_hot, T_cold_in, T_hot_in, dimension_type, dim_start, dim_end, dim_steps,gap=0.01):
    """
    Simulate TP4: Impact of pipe dimensions on outlet temperature.
    """
    T_outs = []
    Qs = []
    efficiencies = []
    Re_internals = []
    Re_externals = []
    Re_internal_regimes = []
    Re_external_regimes = []
    Us = []

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
        external_pipe = {
            "inter_diameter": pipe_properties["outer_diameter"] + gap,
            "thickness": pipe_properties["thickness"],
            "length": pipe_properties["length"]
        }
        validate_pipe_dimensions(pipe_properties, external_pipe)

        Re_internal = calculate_reynolds_number(fluid, m_dot_cold, pipe_properties["outer_diameter"] - 2 * pipe_properties["thickness"])
        Pr_internal = calculate_prandtl_number(fluid)
        h_internal = calculate_convection_coefficient(fluid, pipe_properties["outer_diameter"] - 2 * pipe_properties["thickness"], Re_internal, Pr_internal)
        Re_external = calculate_reynolds_number(hot_fluid, m_dot_hot, external_pipe["inter_diameter"])
        Pr_external = calculate_prandtl_number(hot_fluid)
        h_external = calculate_convection_coefficient(hot_fluid, external_pipe["inter_diameter"], Re_external, Pr_external)
        U = calculate_overall_heat_transfer_coefficient(pipe_properties, material, h_internal, h_external)

        T_hot_out = T_hot_in - 10
        T_cold_out_guess = T_cold_in + 10
        for _ in range(5):
            delta_T_lm = calculate_delta_T_lm(T_hot_in, T_hot_out, T_cold_in, T_cold_out_guess)
            Q = U * A * delta_T_lm
            T_cold_out_guess = T_cold_in + Q / (m_dot_cold * Cp_cold)
        T_outs.append(T_cold_out_guess)
        Qs.append(Q)
        efficiencies.append(calculate_efficiency(Q, m_dot_cold, Cp_cold, T_hot_in, T_cold_in))
        Re_internals.append(Re_internal)
        Re_externals.append(Re_external)
        Re_internal_regimes.append(interpret_reynolds_number(Re_internal))
        Re_external_regimes.append(interpret_reynolds_number(Re_external))
        Us.append(U)

    return {
        "dimensions": dims.tolist(),
        "T_out": T_outs,
        "Q": Qs,
        "efficiency": efficiencies,
        "dimension_type": dimension_type,
        "U": Us,
        "Re_internal": Re_internals,
        "Re_external": Re_externals,
        "Re_internal_regime": Re_internal_regimes,
        "Re_external_regime": Re_external_regimes
    }