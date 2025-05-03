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

#FIN DU PROJET NORMALEMENT Les fomules sont a ranger correctement dans les differents TP dispo

def ask_external_pipe_properties():
    """
    Asks the user for the characteristics of the external pipe:
    internal diameter, wall thickness, and length (in meters).
    
    Returns:
        dict: with 'inter_diameter', 'thickness', 'length'
    """
    print("\nEnter characteristics for the **external pipe**:")

    while True:
        try:
            inter_diameter = float(input("Internal diameter of the external pipe (in meters): "))
            if inter_diameter <= 0:
                raise ValueError
            break
        except ValueError:
            print("Please enter a valid positive number for the internal diameter.")

    while True:
        try:
            thickness = float(input("Wall thickness of the external pipe (in meters): "))
            if thickness <= 0:
                raise ValueError
            break
        except ValueError:
            print("Please enter a valid positive number for the thickness.")

    while True:
        try:
            length = float(input("Length of the external pipe (in meters): "))
            if length <= 0:
                raise ValueError
            break
        except ValueError:
            print("Please enter a valid positive number for the length.")

    return {
        "inter_diameter": inter_diameter,
        "thickness": thickness,
        "length": length
    }

def validate_pipe_dimensions(internal_pipe, external_pipe):
    """
    Checks if the external pipe is physically larger than the internal pipe.
    If not, prints an error and returns False.
    
    Parameters:
        internal_pipe (dict): internal pipe properties
        external_pipe (dict): external pipe properties
    
    Returns:
        bool: True if dimensions are valid, False otherwise
    """
    internal_outer_diameter = internal_pipe["inter_diameter"] + 2 * internal_pipe["thickness"]
    external_inner_diameter = external_pipe["inter_diameter"]

    if external_inner_diameter <= internal_outer_diameter:
        print("\n ERROR: The internal pipe is too large to fit inside the external pipe.")
        print(f"→ Internal pipe outer diameter: {internal_outer_diameter:.4f} m")
        print(f"→ External pipe inner diameter: {external_inner_diameter:.4f} m")
        return False

    return True


#REYNOLDS Formule

def ask_for_Re(fluid_position="internal"):
    """
    Ask the user for fluid properties needed to calculate Reynolds number.
    
    Parameters:
        fluid_position (str): 'internal' or 'external'
    
    Returns:
        dict: with 'density', 'velocity', 'viscosity'
    """
    print(f"\nEnter fluid properties for the {fluid_position} fluid:")

    while True:
        try:
            density = float(input("Density (in kg/m³): "))
            if density <= 0:
                raise ValueError
            break
        except ValueError:
            print("Please enter a positive number for density.")

    while True:
        try:
            velocity = float(input("Flow velocity (in m/s): "))
            if velocity <= 0:
                raise ValueError
            break
        except ValueError:
            print("Please enter a positive number for velocity.")

    while True:
        try:
            viscosity = float(input("Dynamic viscosity (in Pa·s or kg/(m·s)): "))
            if viscosity <= 0:
                raise ValueError
            break
        except ValueError:
            print("Please enter a positive number for viscosity.")

    return {
        "density": density,
        "velocity": velocity,
        "viscosity": viscosity
    }

def calculate_reynolds_number(fluid_properties, pipe_diameter):
    """
    Calculates the Reynolds number.
    
    Parameters:
        fluid_properties (dict): with 'density', 'velocity', 'viscosity'
        pipe_diameter (float): internal diameter of the pipe (m)
    
    Returns:
        float: Reynolds number (dimensionless)
    """
    rho = fluid_properties["density"]
    v = fluid_properties["velocity"]
    mu = fluid_properties["viscosity"]

    Re = (rho * v * pipe_diameter) / mu
    return Re


external_pipe = ask_external_pipe_properties()
internal_fluid = ask_for_Re("internal")
external_fluid = ask_for_Re("external")

Re_internal = calculate_reynolds_number(internal_fluid, pipe["inter_diameter"])
Re_external = calculate_reynolds_number(external_fluid, external_pipe["inter_diameter"])

print(f"\nReynolds number (internal fluid): {Re_internal:.2f}")
print(f"Reynolds number (external fluid): {Re_external:.2f}")


def interpret_reynolds_number(Re):
    """
    Returns a string describing the flow regime based on the Reynolds number,
    using a simplified threshold at Re = 5000.
    
    Parameters:
        Re (float): Reynolds number
    
    Returns:
        str: description of flow regime
    """
    if Re < 5000:
        return "Laminar flow"
    else:
        return "Turbulent flow"

print(f"\nReynolds number (internal fluid): {Re_internal:.2f} → {interpret_reynolds_number(Re_internal)}")
print(f"Reynolds number (external fluid): {Re_external:.2f} → {interpret_reynolds_number(Re_external)}")


#PRANDT formule 

def ask_fluid_conductivity(fluid_position="internal"):
    """
    Ask the user for the thermal conductivity of a fluid in W/(m·K).
    
    Parameters:
        fluid_position (str): 'internal' or 'external'
    
    Returns:
        float: thermal conductivity (k)
    """
    while True:
        try:
            k = float(input(f"Enter thermal conductivity of the {fluid_position} fluid (W/m·K): "))
            if k <= 0:
                raise ValueError
            return k
        except ValueError:
            print("Please enter a valid positive number.")

def calculate_prandtl_number(mu, cp, k):
    """
    Calculate Prandtl number from dynamic viscosity, specific heat, and conductivity.

    Parameters:
        mu (float): dynamic viscosity (Pa·s)
        cp (float): specific heat capacity (J/kg·K)
        k (float): thermal conductivity (W/m·K)

    Returns:
        float: Prandtl number (dimensionless)
    """
    return mu * cp / k

cp_internal = float(input("Enter specific heat capacity (cp) of internal fluid in J/kg·K: "))
cp_external = float(input("Enter specific heat capacity (cp) of external fluid in J/kg·K: "))

# k : conductivité thermique des fluides
k_internal = ask_fluid_conductivity("internal")
k_external = ask_fluid_conductivity("external")

# Calcul des Prandtl
Pr_internal = calculate_prandtl_number(internal_fluid["viscosity"], cp_internal, k_internal)
Pr_external = calculate_prandtl_number(external_fluid["viscosity"], cp_external, k_external)


#CALCUL des coef de convection

def calculate_convection_coefficient(fluid_side, fluid_props, pipe_props, Re, Pr):
    """
    Calculate the convection heat transfer coefficient for internal or external fluid.
    
    Parameters:
        fluid_side (str): "internal" or "external"
        fluid_props (dict): must include 'k' (thermal conductivity)
        pipe_props (dict): must include 'inter_diameter'
        Re (float): Reynolds number
        Pr (float): Prandtl number
    
    Returns:
        float: convection coefficient h in W/(m²·K)
    """
    D = pipe_props["inter_diameter"]
    k = fluid_props["k"]

    print(f"\nHow would you like to compute the convection coefficient for the {fluid_side} fluid?")
    print("1. Manually enter the value")
    print("2. Let the program compute it")

    choice = input("Enter your choice (1 or 2): ")

    if choice == "1":
        while True:
            try:
                h_manual = float(input(f"Enter the convection coefficient h for the {fluid_side} fluid (W/m²·K): "))
                if h_manual > 0:
                    return h_manual
                else:
                    raise ValueError
            except ValueError:
                print("Please enter a valid positive number.")
    
    elif choice == "2":
        if Re < 5000:  # Laminar
            print("\nLaminar regime detected.")
            print("Select approximation method:")
            print("1. Constant outer fluid temperature (h = 4.36 * k / D), as long the external fluid has a very high flow rate compared to the internal fluid or the external pipe is much larger than the internal pipe")
            print("2. Constant wall surface temperature (h = 3.66 * k / D), as long as the metal wall is thin or the two fluids are very close in temperature")
            while True:
                laminar_choice = input("Enter your choice (1 or 2): ")
                if laminar_choice == "1":
                    return 4.36 * k / D
                elif laminar_choice == "2":
                    return 3.66 * k / D
                else:
                    print("Invalid input. Please choose 1 or 2.")
        else:  # Turbulent
            print("\nTurbulent regime detected.")
            h = 0.023 * (Re ** 0.8) * (Pr ** 0.33) * k / D
            return h
    
    else:
        print("Invalid input. Defaulting to program calculation with constant wall temperature.")
        return 3.66 * k / D

# Compute h for each fluid
h_internal = calculate_convection_coefficient("internal", internal_fluid, pipe, Re_internal, Pr_internal)
h_external = calculate_convection_coefficient("external", external_fluid, external_pipe, Re_external, Pr_external)

print(f"\nConvection coefficient (internal fluid): {h_internal:.2f} W/m²·K")
print(f"Convection coefficient (external fluid): {h_external:.2f} W/m²·K")

#CALCUL DE U

def calculate_overall_heat_transfer_coefficient( pipe, k, h_internal, h_external):
    """
    Calculates the overall heat transfer coefficient U (W/m²·K),
    adjusted with division by outer radius (r_o).
    
    Parameters:
        internal_pipe (dict): must include 'inter_diameter' and 'thickness' (in meters)
        k (float): thermal conductivity of pipe material (W/m·K)
        h_internal (float): convection coefficient of internal fluid (W/m²·K)
        h_external (float): convection coefficient of external fluid (W/m²·K)
        length (float): lenght of the pipe (m)
    
    Returns:
        float: overall heat transfer coefficient U (W/m²·K)
    """
    ri = pipe["inter_diameter"] / 2
    thickness = pipe["thickness"]
    ro = ri + thickness
    length=pipe["length"]

    # Thermal resistances
    resistance_internal = 1 / (2* math.pi* length* ri * h_internal )
    resistance_wall = math.log(ro / ri) / (2 * math.pi * length * k )
    resistance_external = 1 / ( 2* math.pi * length * ro * h_external )

    total_resistance = resistance_internal + resistance_wall + resistance_external

    # Final formula with division by ro
    U = 1 / ( 2 * math.pi * length * ro * total_resistance )
    return U
U= calculate_overall_heat_transfer_coefficient(pipe, k, h_internal, h_external)

# Energie recu ou enlever au fluide necessaire

def calculate_fluid_heat_energy():
    """
    Calculates the amount of heat required or received by a fluid using:
    Q = mass_flow_rate * cp * (T_out - T_in)

    Returns:
        float: heat energy in Watts (J/s)
    """
    fluid = ask_fluid_properties()

    while True:
        try:
            T_in = float(input(f"Enter the inlet temperature of {fluid['name']} (in °C): "))
            break
        except ValueError:
            print("Invalid input. Please enter a numerical value for inlet temperature.")

    while True:
        try:
            T_out = float(input(f"Enter the outlet temperature of {fluid['name']} (in °C): "))
            break
        except ValueError:
            print("Invalid input. Please enter a numerical value for outlet temperature.")

    delta_T = T_out - T_in
    Q = fluid["mass_flow_rate"] * fluid["cp"] * delta_T

    print(f"\nThe heat {'required' if Q > 0 else 'removed'} by {fluid['name']} is {abs(Q):.2f} Watts.")

    return Q
Q = calculate_fluid_heat_energy()

def calculate_log_mean_temperature_difference():
    """
    Calculates the logarithmic mean temperature difference (Tlm) using:
    Tlm = Q / (U * A)

    Returns:
        float: Tlm in Kelvin
    """
    # Compute Tlm
    Tlm = Q / (U * A)

    print(f"\nLogarithmic Mean Temperature Difference (Tlm) = {Tlm:.2f} K")
    return Tlm
