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

# Dictionary of densities (kg/L)
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
    "copper (annealed)": 385,  # Softer, lower purity copper
}

#il faudrait ajouter une liste qui s'appelle "material" et qui aurait toutes les key de "thermal conductivity" dedans