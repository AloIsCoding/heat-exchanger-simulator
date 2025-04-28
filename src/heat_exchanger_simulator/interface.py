import os
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from core import simulate_tp1  # Importer la simulation

# Importer utils.py
try:
    from utils import specific_heat_capacity, thermal_conductivity
except ImportError:
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from utils import specific_heat_capacity, thermal_conductivity

# Créer un menu déroulant
def create_dropdown(parent, label_text, options, default, width=20):
    frame = ttk.Frame(parent, borderwidth=1, relief="solid")
    frame.pack(pady=8, padx=20, fill="x")
    label = ttk.Label(frame, text=label_text, font=("Segoe UI", 10))
    label.pack(side="left", padx=5)
    var = tk.StringVar(value=default)
    menu = ttk.Combobox(frame, textvariable=var, values=list(options), width=width, state="readonly", font=("Segoe UI", 10))
    menu.pack(side="right", padx=5)
    return var

# Créer un champ de saisie
def create_entry(parent, label_text, placeholder=None):
    frame = ttk.Frame(parent, borderwidth=1, relief="solid")
    frame.pack(pady=8, padx=20, fill="x")
    label = ttk.Label(frame, text=label_text, font=("Segoe UI", 10))
    label.pack(side="left", padx=5)
    entry = ttk.Entry(frame, font=("Segoe UI", 10))
    if placeholder:
        entry.insert(0, placeholder)
        entry.config(foreground="grey")
        def on_focus_in(event):
            if entry.get() == placeholder:
                entry.delete(0, tk.END)
                entry.config(foreground="black")
        def on_focus_out(event):
            if not entry.get():
                entry.insert(0, placeholder)
                entry.config(foreground="grey")
        entry.bind("<FocusIn>", on_focus_in)
        entry.bind("<FocusOut>", on_focus_out)
    entry.pack(side="right", padx=5, fill="x", expand=True)
    return entry

# Fenêtre principale
def create_main_window():
    window = tk.Tk()
    window.title("Heat Exchanger Simulator")
    window.geometry("800x600")
    window.configure(bg="#E6ECEF")

    # Style moderne
    style = ttk.Style()
    style.configure("TButton", font=("Segoe UI", 12, "bold"), padding=10, background="#003087", foreground="white")
    style.map("TButton", background=[("active", "#005566")])
    style.configure("TLabel", font=("Segoe UI", 12), background="#E6ECEF")
    style.configure("TCombobox", font=("Segoe UI", 12))
    style.configure("Title.TLabel", font=("Segoe UI", 24, "bold"), foreground="#ED1B2F")
    style.configure("Subtitle.TLabel", font=("Segoe UI", 16), foreground="#003087")

    # Logo EPFL
    try:
        logo_path = r"C:\Users\aloisse\Desktop\projet de prog\heat-exchanger-simulator\src\heat_exchanger_simulator\epfl_logo.png"
        img = Image.open(logo_path)
        img = img.resize((120, 60), Image.Resampling.LANCZOS)
        logo = ImageTk.PhotoImage(img)
        label_logo = tk.Label(window, image=logo, bg="#E6ECEF")
        label_logo.image = logo
        label_logo.place(x=10, y=10)
    except FileNotFoundError:
        print(f"Erreur : 'epfl_logo.png' non trouvé à {logo_path}. Assurez-vous qu'il est dans C:\\Users\\aloisse\\Desktop\\projet de prog\\heat-exchanger-simulator\\src\\heat_exchanger_simulator")
    except Exception as e:
        print(f"Erreur de chargement du logo : {e}. Continue sans logo.")

    # Titre
    ttk.Label(window, text="Heat Exchanger Simulator", style="Title.TLabel").pack(pady=(50, 10))

    # Sous-titre
    ttk.Label(window, text="Choose your TP", style="Subtitle.TLabel").pack(pady=10)

    # Menu déroulant pour choisir le TP
    tp_options = [
        "TP1: Flow Impact",
        "TP2: Temperature Impact",
        "TP3: Counterflow vs Parallelflow",
        "TP4: Different Fluids Impact",
        "TP5: Length and Diameter Impact",
    ]
    tp_var = create_dropdown(window, "Select TP:", tp_options, tp_options[0], width=30)

    # Bouton Continuer
    def continue_action():
        selected_tp = tp_var.get()
        window.destroy()
        if selected_tp == "TP1: Flow Impact":
            tp1_interface()
        elif selected_tp == "TP2: Temperature Impact":
            tp2_interface()
        elif selected_tp == "TP3: Counterflow vs Parallelflow":
            tp3_interface()
        elif selected_tp == "TP4: Different Fluids Impact":
            tp4_interface()
        elif selected_tp == "TP5: Length and Diameter Impact":
            tp5_interface()

    ttk.Button(window, text="Continue", command=continue_action).pack(pady=20)

    window.mainloop()

# TP1 : Flow Impact
def tp1_interface():
    window = tk.Tk()
    window.title("TP1: Flow Impact")
    window.geometry("600x600")
    window.configure(bg="#E6ECEF")

    ttk.Label(window, text="TP1: Flow Impact", font=("Segoe UI", 18, "bold"), foreground="#ED1B2F").pack(pady=10)
    ttk.Label(window, text="Vary the flow rate to observe the impact on outlet temperature.", wraplength=500, font=("Segoe UI", 12)).pack(pady=10)

    params_frame = ttk.Frame(window, borderwidth=2, relief="groove")
    params_frame.pack(pady=10, padx=20, fill="both", expand=True)

    fluid_var = create_dropdown(params_frame, "Choose a fluid:", specific_heat_capacity.keys(), "water")
    material_var = create_dropdown(params_frame, "Choose a material:", thermal_conductivity.keys(), "stainless steel")
    tin_entry = create_entry(params_frame, "Inlet temperature (°C):", "e.g., 20")
    flow_start_entry = create_entry(params_frame, "Start flow rate (L/min):", "e.g., 5")
    flow_end_entry = create_entry(params_frame, "End flow rate (L/min):", "e.g., 100")
    flow_steps_entry = create_entry(params_frame, "Number of flow steps:", "e.g., 20")

    button_frame = ttk.Frame(window)
    button_frame.pack(pady=10)

    def continue_action():
        fluid = fluid_var.get()
        material = material_var.get()
        tin = tin_entry.get()
        flow_start = flow_start_entry.get()
        flow_end = flow_end_entry.get()
        flow_steps = flow_steps_entry.get()
        if not tin or tin == "e.g., 20" or not flow_start or flow_start == "e.g., 5" or not flow_end or flow_end == "e.g., 100" or not flow_steps or flow_steps == "e.g., 20":
            messagebox.showerror("Error", "Please fill all fields.")
            return
        try:
            tin = float(tin)
            flow_start = float(flow_start)
            flow_end = float(flow_end)
            flow_steps = int(flow_steps)
            if flow_start >= flow_end or flow_steps < 1:
                messagebox.showerror("Error", "Start flow must be less than end flow, and steps must be positive.")
                return
            results = simulate_tp1(fluid, material, tin, flow_start, flow_end, flow_steps)
            # Afficher le graphe
            plt.figure(figsize=(8, 6))
            plt.plot(results["flow_rates"], results["T_out"], marker="o", color="#ED1B2F")
            plt.xlabel("Flow Rate (L/min)")
            plt.ylabel("Outlet Temperature (°C)")
            plt.title(f"TP1: Flow Impact (Fluid: {fluid}, Material: {material}, T_in: {tin}°C)")
            plt.grid(True)
            plt.show()
            messagebox.showinfo("Results", f"Simulation completed for {flow_steps} flow rates from {flow_start} to {flow_end} L/min.")
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers for temperature, flow rates, and steps.")

    def reset_action():
        fluid_var.set("water")
        material_var.set("stainless steel")
        tin_entry.delete(0, tk.END)
        tin_entry.insert(0, "e.g., 20")
        tin_entry.config(foreground="grey")
        flow_start_entry.delete(0, tk.END)
        flow_start_entry.insert(0, "e.g., 5")
        flow_start_entry.config(foreground="grey")
        flow_end_entry.delete(0, tk.END)
        flow_end_entry.insert(0, "e.g., 100")
        flow_end_entry.config(foreground="grey")
        flow_steps_entry.delete(0, tk.END)
        flow_steps_entry.insert(0, "e.g., 20")
        flow_steps_entry.config(foreground="grey")

    ttk.Button(button_frame, text="Continue", command=continue_action).pack(side="left", padx=5)
    ttk.Button(button_frame, text="Reset", command=reset_action).pack(side="left", padx=5)

    def back_action():
        window.destroy()
        create_main_window()

    ttk.Button(window, text="Back", command=back_action).pack(pady=10)

    window.mainloop()

# TP2 : Temperature Impact
def tp2_interface():
    window = tk.Tk()
    window.title("TP2: Temperature Impact")
    window.geometry("600x600")
    window.configure(bg="#E6ECEF")

    ttk.Label(window, text="TP2: Temperature Impact", font=("Segoe UI", 18, "bold"), foreground="#ED1B2F").pack(pady=10)
    ttk.Label(window, text="Vary the desired outlet temperature to observe the required flow rate.", wraplength=500, font=("Segoe UI", 12)).pack(pady=10)

    params_frame = ttk.Frame(window, borderwidth=2, relief="groove")
    params_frame.pack(pady=10, padx=20, fill="both", expand=True)

    fluid_var = create_dropdown(params_frame, "Choose a fluid:", specific_heat_capacity.keys(), "water")
    material_var = create_dropdown(params_frame, "Choose a material:", thermal_conductivity.keys(), "stainless steel")
    tin_entry = create_entry(params_frame, "Inlet temperature (°C):", "e.g., 20")
    tout_entry = create_entry(params_frame, "Outlet temperature (°C):", "e.g., 30")

    button_frame = ttk.Frame(window)
    button_frame.pack(pady=10)

    def continue_action():
        fluid = fluid_var.get()
        material = material_var.get()
        tin = tin_entry.get()
        tout = tout_entry.get()
        if not tin or tin == "e.g., 20" or not tout or tout == "e.g., 30":
            messagebox.showerror("Error", "Please fill all fields.")
            return
        try:
            tin = float(tin)
            tout = float(tout)
            messagebox.showinfo("Results", f"Fluid: {fluid}\nMaterial: {material}\nT_in: {tin}°C\nT_out: {tout}°C\nSimulation not implemented yet.")
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers for temperatures.")

    def reset_action():
        fluid_var.set("water")
        material_var.set("stainless steel")
        tin_entry.delete(0, tk.END)
        tin_entry.insert(0, "e.g., 20")
        tin_entry.config(foreground="grey")
        tout_entry.delete(0, tk.END)
        tout_entry.insert(0, "e.g., 30")
        tout_entry.config(foreground="grey")

    ttk.Button(button_frame, text="Continue", command=continue_action).pack(side="left", padx=5)
    ttk.Button(button_frame, text="Reset", command=reset_action).pack(side="left", padx=5)

    def back_action():
        window.destroy()
        create_main_window()

    ttk.Button(window, text="Back", command=back_action).pack(pady=10)

    window.mainloop()

# TP3 : Counterflow vs Parallelflow
def tp3_interface():
    window = tk.Tk()
    window.title("TP3: Counterflow vs Parallelflow")
    window.geometry("600x600")
    window.configure(bg="#E6ECEF")

    ttk.Label(window, text="TP3: Counterflow vs Parallelflow", font=("Segoe UI", 18, "bold"), foreground="#ED1B2F").pack(pady=10)
    ttk.Label(window, text="Compare counterflow and parallelflow configurations.", wraplength=500, font=("Segoe UI", 12)).pack(pady=10)

    params_frame = ttk.Frame(window, borderwidth=2, relief="groove")
    params_frame.pack(pady=10, padx=20, fill="both", expand=True)

    fluid_var = create_dropdown(params_frame, "Choose a fluid:", specific_heat_capacity.keys(), "water")
    material_var = create_dropdown(params_frame, "Choose a material:", thermal_conductivity.keys(), "stainless steel")
    flow_entry = create_entry(params_frame, "Flow rate (L/min):", "e.g., 10")

    button_frame = ttk.Frame(window)
    button_frame.pack(pady=10)

    def continue_action():
        fluid = fluid_var.get()
        material = material_var.get()
        flow = flow_entry.get()
        if not flow or flow == "e.g., 10":
            messagebox.showerror("Error", "Please fill all fields.")
            return
        try:
            flow = float(flow)
            messagebox.showinfo("Results", f"Fluid: {fluid}\nMaterial: {material}\nFlow rate: {flow} L/min\nSimulation not implemented yet.")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number for flow rate.")

    def reset_action():
        fluid_var.set("water")
        material_var.set("stainless steel")
        flow_entry.delete(0, tk.END)
        flow_entry.insert(0, "e.g., 10")
        flow_entry.config(foreground="grey")

    ttk.Button(button_frame, text="Continue", command=continue_action).pack(side="left", padx=5)
    ttk.Button(button_frame, text="Reset", command=reset_action).pack(side="left", padx=5)

    def back_action():
        window.destroy()
        create_main_window()

    ttk.Button(window, text="Back", command=back_action).pack(pady=10)

    window.mainloop()

# TP4 : Different Fluids Impact
def tp4_interface():
    window = tk.Tk()
    window.title("TP4: Different Fluids Impact")
    window.geometry("600x600")
    window.configure(bg="#E6ECEF")

    ttk.Label(window, text="TP4: Different Fluids Impact", font=("Segoe UI", 18, "bold"), foreground="#ED1B2F").pack(pady=10)
    ttk.Label(window, text="Observe the impact of different fluids on the outlet temperature.", wraplength=500, font=("Segoe UI", 12)).pack(pady=10)

    params_frame = ttk.Frame(window, borderwidth=2, relief="groove")
    params_frame.pack(pady=10, padx=20, fill="both", expand=True)

    fluid_var = create_dropdown(params_frame, "Choose a fluid:", specific_heat_capacity.keys(), "water")
    material_var = create_dropdown(params_frame, "Choose a material:", thermal_conductivity.keys(), "stainless steel")
    flow_entry = create_entry(params_frame, "Flow rate (L/min):", "e.g., 10")

    button_frame = ttk.Frame(window)
    button_frame.pack(pady=10)

    def continue_action():
        fluid = fluid_var.get()
        material = material_var.get()
        flow = flow_entry.get()
        if not flow or flow == "e.g., 10":
            messagebox.showerror("Error", "Please fill all fields.")
            return
        try:
            flow = float(flow)
            messagebox.showinfo("Results", f"Fluid: {fluid}\nMaterial: {material}\nFlow rate: {flow} L/min\nSimulation not implemented yet.")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number for flow rate.")

    def reset_action():
        fluid_var.set("water")
        material_var.set("stainless steel")
        flow_entry.delete(0, tk.END)
        flow_entry.insert(0, "e.g., 10")
        flow_entry.config(foreground="grey")

    ttk.Button(button_frame, text="Continue", command=continue_action).pack(side="left", padx=5)
    ttk.Button(button_frame, text="Reset", command=reset_action).pack(side="left", padx=5)

    def back_action():
        window.destroy()
        create_main_window()

    ttk.Button(window, text="Back", command=back_action).pack(pady=10)

    window.mainloop()

# TP5 : Length and Diameter Impact
def tp5_interface():
    window = tk.Tk()
    window.title("TP5: Length and Diameter Impact")
    window.geometry("600x600")
    window.configure(bg="#E6ECEF")

    ttk.Label(window, text="TP5: Length and Diameter Impact", font=("Segoe UI", 18, "bold"), foreground="#ED1B2F").pack(pady=10)
    ttk.Label(window, text="Study the impact of the exchanger length and diameter on the outlet temperature.", wraplength=500, font=("Segoe UI", 12)).pack(pady=10)

    params_frame = ttk.Frame(window, borderwidth=2, relief="groove")
    params_frame.pack(pady=10, padx=20, fill="both", expand=True)

    fluid_var = create_dropdown(params_frame, "Choose a fluid:", specific_heat_capacity.keys(), "water")
    material_var = create_dropdown(params_frame, "Choose a material:", thermal_conductivity.keys(), "stainless steel")
    length_entry = create_entry(params_frame, "Length of exchanger (m):", "e.g., 2")
    diameter_entry = create_entry(params_frame, "Diameter of exchanger (m):", "e.g., 0.1")

    button_frame = ttk.Frame(window)
    button_frame.pack(pady=10)

    def continue_action():
        fluid = fluid_var.get()
        material = material_var.get()
        length = length_entry.get()
        diameter = diameter_entry.get()
        if not length or length == "e.g., 2" or not diameter or diameter == "e.g., 0.1":
            messagebox.showerror("Error", "Please fill all fields.")
            return
        try:
            length = float(length)
            diameter = float(diameter)
            messagebox.showinfo("Results", f"Fluid: {fluid}\nMaterial: {material}\nLength: {length} m\nDiameter: {diameter} m\nSimulation not implemented yet.")
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers for length and diameter.")

    def reset_action():
        fluid_var.set("water")
        material_var.set("stainless steel")
        length_entry.delete(0, tk.END)
        length_entry.insert(0, "e.g., 2")
        length_entry.config(foreground="grey")
        diameter_entry.delete(0, tk.END)
        diameter_entry.insert(0, "e.g., 0.1")
        diameter_entry.config(foreground="grey")

    ttk.Button(button_frame, text="Continue", command=continue_action).pack(side="left", padx=5)
    ttk.Button(button_frame, text="Reset", command=reset_action).pack(side="left", padx=5)

    def back_action():
        window.destroy()
        create_main_window()

    ttk.Button(window, text="Back", command=back_action).pack(pady=10)

    window.mainloop()

# Lancer le programme
if __name__ == "__main__":
    create_main_window()