# Dictionary of specific heat capacities (J/kg·K)
specific_heat_capacity = {
    "water": 4186,
    "air": 1005,
    "thermal oil": 2200,
    "glycol": 2400,
    "steam": 2010,
    "nitrogen": 1040,
    "carbon dioxide": 844,
    "ammonia": 4700,
    "helium": 5190
}

def calculate_heat_transfer(fluid, mass_flow_rate, temp_in, temp_out):
    """
    Calculate heat transferred using Q = m * cp * (Tin - Tout)

    Parameters:
        fluid (str): name of the fluid
        mass_flow_rate (float): mass flow rate in kg/s
        temp_in (float): inlet temperature in °C
        temp_out (float): outlet temperature in °C

    Returns:
        float: heat transferred in watts (J/s), or None if fluid not found
    """
    cp = specific_heat_capacity.get(fluid.lower())

    if cp is None:
        print(f"Fluid '{fluid}' not found in the database.")
        return None

    Q = mass_flow_rate * cp * (temp_in - temp_out)
    return Q

# Example usage
fluid = input("Enter the fluid used in your heat exchanger: ").strip().lower()
mass_flow_rate = float(input("Enter the mass flow rate (kg/s): "))
temp_in = float(input("Enter the inlet temperature (°C): "))
temp_out = float(input("Enter the outlet temperature (°C): "))

Q = calculate_heat_transfer(fluid, mass_flow_rate, temp_in, temp_out)

if Q is not None:
    print(f"The heat transferred is {Q:.2f} watts.")


# Detailed thermal conductivities (W·m⁻¹·K⁻¹)
thermal_conductivity = {
    "stainless steel": 16,     # AISI 304
    "mild steel": 50,          # Low carbon steel
    "iron": 80,                # Pure iron
    "aluminum (pure)": 237,    # 99.9% Al
    "aluminum (alloy)": 120,   # Common alloy
    "copper (pure)": 401,      # 99.9% Cu
    "copper (annealed)": 385,  # Softer, lower purity copper
}

# Ask the user to enter a specific type of metal
metal = input("Enter a metal (e.g., stainless steel, aluminum (alloy)): ").strip().lower()

# Get the thermal conductivity
k = thermal_conductivity.get(metal)

if k:
    print(f"The thermal conductivity of {metal} is {k} W·m⁻¹·K⁻¹.")
else:
    print(f"Metal '{metal}' not found in the database.")




def ask_fluid_properties():
    """
    Asks the user for the fluid they want to heat or cool, 
    and its specific heat capacity (in J·kg⁻¹·K⁻¹).

    Returns:
        tuple: (fluid name, specific heat capacity)
    """
    fluid_name = input("Enter the name of the fluid you want to heat or cool: ").strip()
    while True:
        try:
            specific_heat = float(input(f"Enter the specific heat capacity of {fluid_name} (in J·kg⁻¹·K⁻¹): "))
            break
        except ValueError:
            print("Invalid input. Please enter a numerical value for the specific heat capacity.")

    return fluid_name, specific_heat

# Example usage
fluid, cp = ask_fluid_properties()
print(f"You entered: {fluid} with a specific heat capacity of {cp} J·kg⁻¹·K⁻¹.")


def ask_pipe_properties():
    """
    Asks the user for the pipe characteristics: 
    outer diameter, wall thickness, and length (in meters).

    Returns:
        dict: with keys 'outer_diameter', 'thickness', 'length'
    """
    while True:
        try:
            outer_diameter = float(input("Enter the outer diameter of the pipe (in meters): "))
            if outer_diameter <= 0:
                raise ValueError
            break
        except ValueError:
            print("Invalid input. Please enter a positive number for the outer diameter.")

    while True:
        try:
            thickness = float(input("Enter the wall thickness of the pipe (in meters): "))
            if thickness <= 0 or thickness >= outer_diameter / 2:
                print("Invalid input. Thickness must be positive and less than half the outer diameter.")
                continue
            break
        except ValueError:
            print("Invalid input. Please enter a positive number for the wall thickness.")

    while True:
        try:
            length = float(input("Enter the length of the pipe (in meters): "))
            if length <= 0:
                raise ValueError
            break
        except ValueError:
            print("Invalid input. Please enter a positive number for the length.")

    return {
        "outer_diameter": outer_diameter,
        "thickness": thickness,
        "length": length
    }

# Example usage
pipe_properties = ask_pipe_properties()
print(f"You entered: {pipe_properties}")