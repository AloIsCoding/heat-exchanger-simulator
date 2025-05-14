#data : (fluids, constants,..)

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

# Dictionary of density (kg/L)
density = {
    "water": 1.0,
    "air": 0.001225,
    "thermal oil": 0.9,
    "glycol": 1.11,
    "steam": 0.000598,
    "nitrogen": 0.001251,
    "carbon dioxide": 0.001977,
    "ammonia": 0.000682,
    "helium": 0.000179
}

# Detailed thermal conductivities (W·m⁻¹·K⁻¹)
thermal_conductivity = {
    "stainless steel": 16,     # AISI 304
    "mild steel": 50,          # Low carbon steel
    "iron": 80,                # Pure iron
    "aluminum (pure)": 237,    # 99.9% Al
    "aluminum (alloy)": 120,   # Common alloy
    "copper (pure)": 401,      # 99.9% Cu
    "copper (annealed)": 385  # Softer, lower purity copper
}

# List of materials (keys of thermal_conductivity)
material = list(thermal_conductivity.keys())

# Dictionary of dynamic viscosity (Pa·s)
viscosity = {
    "water": 0.001,        # At 20°C
    "air": 1.81e-5,       # At 20°C
    "thermal oil": 0.05,   # Approx. for common thermal oils
    "glycol": 0.02,        # Approx. for ethylene glycol
    "steam": 1.2e-5,       # At 100°C
    "nitrogen": 1.78e-5,   # At 20°C
    "carbon dioxide": 1.48e-5,  # At 20°C
    "ammonia": 1.0e-5,     # At 20°C
    "helium": 1.96e-5      # At 20°C
}

# Dictionary of thermal conductivity for fluids (W/m·K)
thermal_conductivity_fluid = {
    "water": 0.6,          # At 20°C
    "air": 0.026,         # At 20°C
    "thermal oil": 0.15,   # Approx.
    "glycol": 0.25,        # Approx. for ethylene glycol
    "steam": 0.026,        # At 100°C
    "nitrogen": 0.026,     # At 20°C
    "carbon dioxide": 0.016,  # At 20°C
    "ammonia": 0.022,      # At 20°C
    "helium": 0.15         # At 20°C
}