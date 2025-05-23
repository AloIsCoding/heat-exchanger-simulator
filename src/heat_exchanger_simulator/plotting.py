import matplotlib.pyplot as plt
from pathlib import Path

def generate_plot(tp_name, results, output_dir, filename=None):
    """
    Generate a plot of simulation results and save it as a PNG file.
    
    Args:
        tp_name (str): Name of the TP (e.g., "TP1").
        results (dict): Simulation results.
        output_dir (str or Path): Directory to save the plot.
        filename (str, optional): Custom filename for the plot (e.g., "graphe_tp1.png").
    
    Returns:
        str: Path to the generated PNG file.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)
    if filename is None:
        filename = f"{tp_name.lower()}_plot.png"
    plo_path = output_dir / filename
    
    plt.figure(figsize=(8, 6))
    
    if tp_name == "TP1":
        plt.plot(results["flow_rates"], results["T_out"], 'b-', label="Outlet Temperature")
        plt.xlabel("Cold Fluid Flow Rate (L/min)")
        plt.ylabel("Outlet Temperature (°C)")
        plt.title("Effect of Flow Rate on Outlet Temperature")
    elif tp_name == "TP2":
        plt.plot(results["T_hot_in"], results["T_out"], 'r-', label="Outlet Temperature")
        plt.xlabel("Hot Fluid Inlet Temperature (°C)")
        plt.ylabel("Outlet Temperature (°C)")
        plt.title("Effect of Hot Fluid Temperature on Outlet Temperature")
    elif tp_name == "TP3":
        plt.bar(results["hot_fluids"], results["T_out"])
        plt.xlabel("Hot Fluid")
        plt.ylabel("Outlet Temperature (°C)")
        plt.title("Effect of Hot Fluid on Outlet Temperature")
        plt.xticks(rotation=45)
    elif tp_name == "TP4":
        plt.plot(results["dimensions"], results["T_out"], 'g-', label="Outlet Temperature")
        plt.xlabel(f"Pipe {results.get('dimension_type', 'Dimension')} (m)")
        plt.ylabel("Outlet Temperature (°C)")
        plt.title(f"Effect of Pipe {results.get('dimension_type', 'Dimension')} on Outlet Temperature")
    
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(plo_path, dpi=300)
    plt.close()
    
    return str(plo_path)