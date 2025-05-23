import numpy as np
import math
from utils import specific_heat_capacity, thermal_conductivity, density, viscosity, thermal_conductivity_fluid

def calculate_heat_transfer(fluid, mass_flow_rate, temp_in, temp_out):
    """
    Calculate heat transferred using Q = m * cp * (Tin - Tout).
    
    Args:
        fluid (str): Name of the fluid.
        mass_flow_rate (float): Mass flow rate (kg/s).
        temp_in (float): Inlet temperature (°C).
        temp_out (float): Outlet temperature (°C).
    
    Returns:
        float: Heat transfer rate (W).
    
    Raises:
        ValueError: If fluid is not in the database.
    """
    cp = specific_heat_capacity.get(fluid.lower())
    if cp is None:
        raise ValueError(f"Fluid '{fluid}' not found in the database.")
    Q = mass_flow_rate * cp * (temp_in - temp_out)
    return Q

def calculate_outer_surface(pipe_properties):
    """
    Calculates the outer contact surface area of a pipe.
    
    Args:
        pipe_properties (dict): Dictionary with 'outer_diameter' and 'length' (m).
    
    Returns:
        float: Surface area (m²).
    """
    outer_diameter = pipe_properties["outer_diameter"]
    length = pipe_properties["length"]
    return math.pi * outer_diameter * length

def calculate_delta_T_lm(T_hot_in, T_hot_out, T_cold_in, T_cold_out):
    """
    Calculate logarithmic mean temperature difference (delta_T_lm).
    
    Args:
        T_hot_in (float): Inlet temperature of hot fluid (°C).
        T_hot_out (float): Outlet temperature of hot fluid (°C).
        T_cold_in (float): Inlet temperature of cold fluid (°C).
        T_cold_out (float): Outlet temperature of cold fluid (°C).
    
    Returns:
        float: Logarithmic mean temperature difference (°C).
    
    Raises:
        ValueError: If inputs lead to invalid LMTD calculation.
    """
    dT1 = T_hot_in - T_cold_out
    dT2 = T_hot_out - T_cold_in
    
    # Vérifier les valeurs négatives ou nulles
    if dT1 <= 0 or dT2 <= 0:
        raise ValueError(
            f"Invalid temperature differences: dT1 = {dT1}, dT2 = {dT2}. "
            "Ensure temperatures are physically valid (T_hot_in > T_cold_out and T_hot_out > T_cold_in)."
        )
    
    # Cas où dT1 ≈ dT2 pour éviter division par zéro
    if abs(dT1 - dT2) < 1e-6:
        return dT1
    
    try:
        return (dT1 - dT2) / math.log(dT1 / dT2)
    except ValueError as e:
        raise ValueError(f"Error calculating LMTD: {str(e)}. Check input temperatures.")

def calculate_log_mean_temperature_difference(Q, U, A):
    """
    Calculates the logarithmic mean temperature difference (Tlm) using:
    Tlm = Q / (U * A).
    
    Args:
        Q (float): Heat transfer rate (W).
        U (float): Overall heat transfer coefficient (W/m²·K).
        A (float): Surface area (m²).
    
    Returns:
        float: Logarithmic mean temperature difference (°C).
    """
    if U * A == 0:
        raise ValueError("U * A cannot be zero.")
    Tlm = Q / (U * A)
    return Tlm

def calculate_efficiency(Q, m_dot_cold, Cp_cold, T_hot_in, T_cold_in):
    """
    Calculate heat exchanger efficiency.
    
    Args:
        Q (float): Heat transfer rate (W).
        m_dot_cold (float): Mass flow rate of cold fluid (kg/s).
        Cp_cold (float): Specific heat capacity of cold fluid (J/kg·K).
        T_hot_in (float): Inlet temperature of hot fluid (°C).
        T_cold_in (float): Inlet temperature of cold fluid (°C).
    
    Returns:
        float: Efficiency (fraction).
    """
    Q_max = m_dot_cold * Cp_cold * (T_hot_in - T_cold_in)
    if Q_max == 0:
        return 0
    return Q / Q_max

def validate_pipe_dimensions(internal_pipe, external_pipe):
    """
    Checks if the external pipe is physically larger than the internal pipe.
    
    Args:
        internal_pipe (dict): Properties of the internal pipe.
        external_pipe (dict): Properties of the external pipe.
    
    Raises:
        ValueError: If external pipe inner diameter is too small.
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
    
    Args:
        fluid (str): Name of the fluid.
        mass_flow_rate (float): Mass flow rate (kg/s).
        pipe_diameter (float): Pipe diameter (m).
    
    Returns:
        float: Reynolds number.
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
    
    Args:
        Re (float): Reynolds number.
    
    Returns:
        str: Flow regime ("Laminar" or "Turbulent").
    """
    return "Laminar" if Re < 5000 else "Turbulent"

def calculate_prandtl_number(fluid):
    """
    Calculate Prandtl number from dynamic viscosity, specific heat, and conductivity.
    
    Args:
        fluid (str): Name of the fluid.
    
    Returns:
        float: Prandtl number.
    """
    mu = viscosity.get(fluid.lower(), 0.001)
    cp = specific_heat_capacity.get(fluid.lower(), 4186)
    k = thermal_conductivity_fluid.get(fluid.lower(), 0.6)
    return mu * cp / k

def calculate_convection_coefficient(fluid, pipe_diameter, Re, Pr):
    """
    Calculate the convection heat transfer coefficient.
    
    Args:
        fluid (str): Name of the fluid.
        pipe_diameter (float): Pipe diameter (m).
        Re (float): Reynolds number.
        Pr (float): Prandtl number.
    
    Returns:
        float: Convection coefficient (W/m²·K).
    """
    k = thermal_conductivity_fluid.get(fluid.lower(), 0.6)
    if Re < 5000:  # Laminar
        return 3.66 * k / pipe_diameter  # Constant wall temperature
    else:  # Turbulent
        return 0.023 * (Re ** 0.8) * (Pr ** 0.33) * k / pipe_diameter

def calculate_overall_heat_transfer_coefficient(pipe, material, h_internal, h_external):
    """
    Calculates the overall heat transfer coefficient U (W/m²·K).
    
    Args:
        pipe (dict): Pipe properties.
        material (str): Pipe material.
        h_internal (float): Internal convection coefficient (W/m²·K).
        h_external (float): External convection coefficient (W/m²·K).
    
    Returns:
        float: Overall heat transfer coefficient (W/m²·K).
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

def simulate_tp1(fluid, hot_fluid, material, T_cold_in, T_hot_in, flow_start, flow_end, flow_steps, pipe_properties, gap=0.01):
    """
    Simulate TP1: Impact of cold fluid flow rate on outlet temperature.
    
    Args:
        fluid (str): Cold fluid name.
        hot_fluid (str): Hot fluid name.
        material (str): Pipe material.
        T_cold_in (float): Cold fluid inlet temperature (°C).
        T_hot_in (float): Hot fluid inlet temperature (°C).
        flow_start (float): Starting flow rate (L/min).
        flow_end (float): Ending flow rate (L/min).
        flow_steps (int): Number of flow steps.
        pipe_properties (dict): Pipe properties (outer_diameter, thickness, length).
        gap (float): Gap between pipes (m).
    
    Returns:
        dict: Simulation results including additional parameters for reporting.
    """
    try:
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
        delta_T_lms = []
        h_internals = []
        h_externals = []

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
            delta_T_lms.append(delta_T_lm)
            h_internals.append(h_internal)
            h_externals.append(h_external)

        return {
            "flow_rates": flow_rates.tolist(),
            "T_out": T_outs,
            "Q": Qs,
            "efficiency": efficiencies,
            "U": Us,
            "Re_internal": Re_internals,
            "Re_external": Re_externals,
            "Re_internal_regime": Re_internal_regimes,
            "Re_external_regime": Re_external_regimes,
            "delta_T_lm": delta_T_lms,
            "h_internal": h_internals,
            "h_external": h_externals,
            "A": [A] * len(flow_rates)
        }
    except Exception as e:
        raise ValueError(f"Erreur lors de la simulation TP1 : {str(e)}")

def simulate_tp2(fluid, hot_fluid, material, T_cold_in, flow_cold, T_hot_start, T_hot_end, T_hot_steps, pipe_properties, gap=0.01):
    """
    Simulate TP2: Impact of hot fluid temperature on outlet temperature.
    
    Args:
        fluid (str): Cold fluid name.
        hot_fluid (str): Hot fluid name.
        material (str): Pipe material.
        T_cold_in (float): Cold fluid inlet temperature (°C).
        flow_cold (float): Cold fluid flow rate (L/min).
        T_hot_start (float): Starting hot fluid temperature (°C).
        T_hot_end (float): Ending hot fluid temperature (°C).
        T_hot_steps (int): Number of temperature steps.
        pipe_properties (dict): Pipe properties (outer_diameter, thickness, length).
        gap (float): Gap between pipes (m).
    
    Returns:
        dict: Simulation results including additional parameters for reporting.
    """
    try:
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
        delta_T_lms = []
        h_internals = []
        h_externals = []

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
            delta_T_lms.append(delta_T_lm)
            h_internals.append(h_internal)
            h_externals.append(h_external)

        return {
            "T_hot_in": T_hot_ins.tolist(),
            "T_out": T_outs,
            "Q": Qs,
            "efficiency": efficiencies,
            "U": Us,
            "Re_internal": Re_internals,
            "Re_external": Re_externals,
            "Re_internal_regime": Re_internal_regimes,
            "Re_external_regime": Re_external_regimes,
            "delta_T_lm": delta_T_lms,
            "h_internal": h_internals,
            "h_external": h_externals,
            "A": [A] * len(T_hot_ins)
        }
    except Exception as e:
        raise ValueError(f"Erreur lors de la simulation TP2 : {str(e)}")

def simulate_tp3(fluid, material, flow_cold, flow_hot, pipe_properties, gap=0.01):
    """
    Simulate TP3: Impact of hot fluid choice on outlet temperature.
    
    Args:
        fluid (str): Cold fluid name.
        material (str): Pipe material.
        flow_cold (float): Cold fluid flow rate (L/min).
        flow_hot (float): Hot fluid flow rate (L/min).
        pipe_properties (dict): Pipe properties (outer_diameter, thickness, length).
        gap (float): Gap between pipes (m).
    
    Returns:
        dict: Simulation results including additional parameters for reporting.
    """
    try:
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
        delta_T_lms = []
        h_internals = []
        h_externals = []

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
            delta_T_lms.append(delta_T_lm)
            h_internals.append(h_internal)
            h_externals.append(h_external)

        return {
            "hot_fluids": hot_fluids,
            "T_out": T_outs,
            "Q": Qs,
            "efficiency": efficiencies,
            "U": Us,
            "Re_internal": Re_internals,
            "Re_external": Re_externals,
            "Re_internal_regime": Re_internal_regimes,
            "Re_external_regime": Re_external_regimes,
            "delta_T_lm": delta_T_lms,
            "h_internal": h_internals,
            "h_external": h_externals,
            "A": [A] * len(hot_fluids)
        }
    except Exception as e:
        raise ValueError(f"Erreur lors de la simulation TP3 : {str(e)}")

def simulate_tp4(fluid, hot_fluid, material, flow_cold, flow_hot, T_cold_in, T_hot_in, dimension_type, dim_start, dim_end, dim_steps, gap=0.01):
    """
    Simulate TP4: Impact of pipe dimensions on outlet temperature.
    
    Args:
        fluid (str): Cold fluid name.
        hot_fluid (str): Hot fluid name.
        material (str): Pipe material.
        flow_cold (float): Cold fluid flow rate (L/min).
        flow_hot (float): Hot fluid flow rate (L/min).
        T_cold_in (float): Cold fluid inlet temperature (°C).
        T_hot_in (float): Hot fluid inlet temperature (°C).
        dimension_type (str): Dimension to vary ("length" or "diameter").
        dim_start (float): Starting dimension (m).
        dim_end (float): Ending dimension (m).
        dim_steps (int): Number of dimension steps.
        gap (float): Gap between pipes (m).
    
    Returns:
        dict: Simulation results including additional parameters for reporting.
    """
    try:
        T_outs = []
        Qs = []
        efficiencies = []
        Re_internals = []
        Re_externals = []
        Re_internal_regimes = []
        Re_external_regimes = []
        Us = []
        delta_T_lms = []
        h_internals = []
        h_externals = []
        As = []

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
            delta_T_lms.append(delta_T_lm)
            h_internals.append(h_internal)
            h_externals.append(h_external)
            As.append(A)

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
            "Re_external_regime": Re_external_regimes,
            "delta_T_lm": delta_T_lms,
            "h_internal": h_internals,
            "h_external": h_externals,
            "A": As
        }
    except Exception as e:
        raise ValueError(f"Erreur lors de la simulation TP4 : {str(e)}")