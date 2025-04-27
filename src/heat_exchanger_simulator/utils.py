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