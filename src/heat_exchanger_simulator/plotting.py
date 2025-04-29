import matplotlib.pyplot as plt
from pathlib import Path

def generate_plot(tp_name, results, output_dir="reports"):
    """
    Generate and save a plot for the given TP.

    Parameters:
        tp_name (str): Name of the TP (e.g., "TP1", "TP2")
        results (dict): Simulation results
        output_dir (str): Directory to save the plot

    Returns:
        str: Path to the saved plot
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)
    plot_path = output_dir / f"{tp_name.lower()}_plot.png"

    plt.figure(figsize=(8, 6), dpi=100)
    
    if tp_name == "TP1":
        plt.plot(results["flow_rates"], results["T_out"], marker="o", color="#ED1B2F", linestyle="-", linewidth=2)
        plt.xlabel("Flow Rate (L/min)", fontsize=12)
        plt.ylabel("Outlet Temperature (°C)", fontsize=12)
        plt.title("TP1: Impact of Flow Rate on Outlet Temperature", fontsize=14, pad=10)
    elif tp_name == "TP2":
        plt.plot(results["T_hot_in"], results["T_out"], marker="o", color="#ED1B2F", linestyle="-", linewidth=2)
        plt.xlabel("Hot Fluid Temperature (°C)", fontsize=12)
        plt.ylabel("Outlet Temperature (°C)", fontsize=12)
        plt.title("TP2: Impact of Hot Fluid Temperature on Outlet Temperature", fontsize=14, pad=10)
    elif tp_name == "TP3":
        plt.bar(results["hot_fluids"], results["T_out"], color="#ED1B2F", edgecolor="black")
        plt.xlabel("Hot Fluid", fontsize=12)
        plt.ylabel("Outlet Temperature (°C)", fontsize=12)
        plt.title("TP3: Impact of Hot Fluid Choice on Outlet Temperature", fontsize=14, pad=10)
        plt.xticks(rotation=45, ha="right")
    elif tp_name == "TP4":
        plt.plot(results["dimensions"], results["T_out"], marker="o", color="#ED1B2F", linestyle="-", linewidth=2)
        plt.xlabel(f"{results['dimension_type'].capitalize()} (m)", fontsize=12)
        plt.ylabel("Outlet Temperature (°C)", fontsize=12)
        plt.title(f"TP4: Impact of {results['dimension_type'].capitalize()} on Outlet Temperature", fontsize=14, pad=10)
    
    plt.grid(True, linestyle="--", alpha=0.7)
    plt.tight_layout()
    plt.savefig(plot_path, bbox_inches="tight")
    plt.close()
    
    return str(plot_path)