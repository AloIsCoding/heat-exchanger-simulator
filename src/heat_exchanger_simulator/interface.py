import os
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import ttk, messagebox
from core import simulate_tp1, simulate_tp2, simulate_tp3, simulate_tp4
from utils import specific_heat_capacity, thermal_conductivity
from report import write_tex
from plotting import generate_plot

class HeatExchangerSimulator:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Heat Exchanger Simulator")
        self.window.geometry("800x600")
        self.window.configure(bg="#E6ECEF")

        style = ttk.Style()
        style.configure("TButton", font=("Segoe UI", 12, "bold"), padding=10, background="#003087")
        style.map("TButton", background=[("active", "#005566")])
        style.configure("TLabel", font=("Segoe UI", 12), background="#E6ECEF")
        style.configure("TCombobox", font=("Segoe UI", 10))
        style.configure("Title.TLabel", font=("Segoe UI", 24, "bold"), foreground="#ED1B2F")
        style.configure("Subtitle.TLabel", font=("Segoe UI", 16), foreground="#003087")

        try:
            logo_path = os.path.join(os.path.dirname(__file__), "epfl_logo.png")
            img = Image.open(logo_path)
            img = img.resize((120, 60), Image.Resampling.LANCZOS)
            self.logo = ImageTk.PhotoImage(img)
            label_logo = tk.Label(self.window, image=self.logo, bg="#E6ECEF")
            label_logo.place(x=10, y=10)
        except Exception as e:
            print(f"Erreur de chargement du logo : {e}")

    def create_dropdown(self, parent, label_text, options, default, width=20):
        frame = ttk.Frame(parent)
        frame.pack(pady=5, padx=20, fill="x")
        label = ttk.Label(frame, text=label_text)
        label.pack(side="left", padx=5)
        var = tk.StringVar(value=default)
        menu = ttk.Combobox(frame, textvariable=var, values=list(options), width=width, state="readonly")
        menu.pack(side="right", padx=5)
        return var

    def create_entry(self, parent, label_text, placeholder=None):
        frame = ttk.Frame(parent)
        frame.pack(pady=5, padx=20, fill="x")
        label = ttk.Label(frame, text=label_text)
        label.pack(side="left", padx=5)
        entry = ttk.Entry(frame)
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

    def create_main_window(self):
        ttk.Label(self.window, text="Heat Exchanger Simulator", style="Title.TLabel").pack(pady=(50, 10))
        ttk.Label(self.window, text="Choose your TP", style="Subtitle.TLabel").pack(pady=10)

        tp_options = [
            "TP1: Flow Impact",
            "TP2: Temperature Impact",
            "TP3: Different Fluids Impact",
            "TP4: Length and Diameter Impact"
        ]
        self.tp_var = self.create_dropdown(self.window, "Select TP:", tp_options, tp_options[0], width=30)

        ttk.Button(self.window, text="Continue", command=self.continue_action).pack(pady=20)
        self.window.mainloop()

    def continue_action(self):
        selected_tp = self.tp_var.get()
        self.window.destroy()
        if selected_tp == "TP1: Flow Impact":
            self.tp1_interface()
        elif selected_tp == "TP2: Temperature Impact":
            self.tp2_interface()
        elif selected_tp == "TP3: Different Fluids Impact":
            self.tp3_interface()
        elif selected_tp == "TP4: Length and Diameter Impact":
            self.tp4_interface()

    def draw_exchanger(self, canvas, params):
        canvas.delete("all")
        try:
            img_path = os.path.join(os.path.dirname(__file__), "exchanger.png")
            img = Image.open(img_path)
            img = img.resize((400, 300), Image.Resampling.LANCZOS)
            canvas.image = ImageTk.PhotoImage(img)
            canvas.create_image(200, 150, image=canvas.image)
        except Exception as e:
            print(f"Erreur de chargement de l'image : {e}")
            # Dessin de secours (identique à l'original)
            canvas.create_rectangle(100, 100, 300, 200, outline="black", width=2)
            canvas.create_line(50, 150, 100, 150, arrow=tk.LAST)
            canvas.create_line(300, 150, 350, 150, arrow=tk.LAST)
            canvas.create_line(350, 120, 100, 120, arrow=tk.LAST)
            canvas.create_text(50, 130, text=f"T_in: {params.get('T_cold_in', '')}°C", anchor="e")
            canvas.create_text(350, 130, text=f"T_out: ?", anchor="w")
            canvas.create_text(200, 80, text=f"Hot Fluid: {params.get('hot_fluid', '')}, T_hot: {params.get('T_hot_in', '')}°C")
            canvas.create_text(200, 220, text=f"Pipe: {params.get('material', '')}, L={params.get('length', '')}m, D={params.get('diameter', '')}m")

    def run_simulation(self, progress_bar, callback):
        progress = 0
        def update_progress():
            nonlocal progress
            if progress < 100:
                progress += 5
                progress_bar["value"] = progress
                self.window.after(100, update_progress)
            else:
                callback()
        update_progress()

    def tp1_interface(self):
        window = tk.Tk()
        window.title("TP1: Flow Impact")
        window.geometry("800x600")
        window.configure(bg="#E6ECEF")

        ttk.Label(window, text="TP1: Flow Impact", font=("Segoe UI", 18, "bold"), foreground="#ED1B2F").pack(pady=10)
        ttk.Label(window, text="Study the impact of cold fluid flow rate on outlet temperature.", wraplength=600).pack(pady=10)

        params_frame = ttk.Frame(window)
        params_frame.pack(pady=10, padx=20, fill="both")
        fluid_var = self.create_dropdown(params_frame, "Cold Fluid:", specific_heat_capacity.keys(), "water")
        hot_fluid_var = self.create_dropdown(params_frame, "Hot Fluid:", specific_heat_capacity.keys(), "water")
        material_var = self.create_dropdown(params_frame, "Material:", thermal_conductivity.keys(), "stainless steel")
        t_cold_in_entry = self.create_entry(params_frame, "Cold Inlet Temp (°C):", "20")
        t_hot_in_entry = self.create_entry(params_frame, "Hot Inlet Temp (°C):", "80")
        flow_start_entry = self.create_entry(params_frame, "Start Flow Rate (L/min):", "5")
        flow_end_entry = self.create_entry(params_frame, "End Flow Rate (L/min):", "100")
        flow_steps_entry = self.create_entry(params_frame, "Flow Steps:", "20")
        length_entry = self.create_entry(params_frame, "Pipe Length (m):", "2")
        diameter_entry = self.create_entry(params_frame, "Pipe Diameter (m):", "0.1")
        thickness_entry = self.create_entry(params_frame, "Pipe Thickness (m):", "0.005")

        canvas = tk.Canvas(window, width=400, height=300, bg="white")
        canvas.pack(pady=10)
        params = {
            "T_cold_in": t_cold_in_entry.get(),
            "hot_fluid": hot_fluid_var.get(),
            "T_hot_in": t_hot_in_entry.get(),
            "material": material_var.get(),
            "length": length_entry.get(),
            "diameter": diameter_entry.get()
        }
        self.draw_exchanger(canvas, params)

        progress_bar = ttk.Progressbar(window, length=300, mode="determinate")
        progress_bar.pack(pady=10)

        button_frame = ttk.Frame(window)
        button_frame.pack(pady=10)
        results = {}

        def run_sim():
            try:
                fluid = fluid_var.get()
                hot_fluid = hot_fluid_var.get()
                material = material_var.get()
                T_cold_in = float(t_cold_in_entry.get())
                T_hot_in = float(t_hot_in_entry.get())
                flow_start = float(flow_start_entry.get())
                flow_end = float(flow_end_entry.get())
                flow_steps = int(flow_steps_entry.get())
                length = float(length_entry.get())
                diameter = float(diameter_entry.get())
                thickness = float(thickness_entry.get())
                pipe_properties = {"outer_diameter": diameter, "thickness": thickness, "length": length}
                
                def callback():
                    nonlocal results
                    results = simulate_tp1(fluid, hot_fluid, material, T_cold_in, T_hot_in, flow_start, flow_end, flow_steps, pipe_properties)
                    plot_path = generate_plot("TP1", results)
                    img = Image.open(plot_path)
                    img = img.resize((600, 400), Image.Resampling.LANCZOS)
                    img_tk = ImageTk.PhotoImage(img)
                    plt_window = tk.Toplevel()
                    plt_window.title("TP1 Results")
                    tk.Label(plt_window, image=img_tk).pack()
                    plt_window.image = img_tk
                    download_button["state"] = "normal"
                
                self.run_simulation(progress_bar, callback)
            except ValueError:
                messagebox.showerror("Error", "Please enter valid numbers.")

        def download_report():
            if results:
                write_tex("TP1", results, {
                    "fluid": fluid_var.get(),
                    "hot_fluid": hot_fluid_var.get(),
                    "material": material_var.get(),
                    "T_cold_in": t_cold_in_entry.get(),
                    "T_hot_in": t_hot_in_entry.get(),
                    "pipe_length": length_entry.get(),
                    "pipe_diameter": diameter_entry.get()
                })
                messagebox.showinfo("Success", "Report generated as reports/rapport.pdf")

        ttk.Button(button_frame, text="Run Simulation", command=run_sim).pack(side="left", padx=5)
        download_button = ttk.Button(button_frame, text="Download Report", command=download_report, state="disabled")
        download_button.pack(side="left", padx=5)
        ttk.Button(button_frame, text="Another TP", command=lambda: [window.destroy(), self.create_main_window()]).pack(side="left", padx=5)

        window.mainloop()

    def tp2_interface(self):
        window = tk.Tk()
        window.title("TP2: Temperature Impact")
        window.geometry("800x600")
        window.configure(bg="#E6ECEF")

        ttk.Label(window, text="TP2: Temperature Impact", font=("Segoe UI", 18, "bold"), foreground="#ED1B2F").pack(pady=10)
        ttk.Label(window, text="Study the impact of hot fluid temperature on outlet temperature.", wraplength=600).pack(pady=10)

        params_frame = ttk.Frame(window)
        params_frame.pack(pady=10, padx=20, fill="both")
        fluid_var = self.create_dropdown(params_frame, "Cold Fluid:", specific_heat_capacity.keys(), "water")
        hot_fluid_var = self.create_dropdown(params_frame, "Hot Fluid:", specific_heat_capacity.keys(), "water")
        material_var = self.create_dropdown(params_frame, "Material:", thermal_conductivity.keys(), "stainless steel")
        t_cold_in_entry = self.create_entry(params_frame, "Cold Inlet Temp (°C):", "20")
        flow_cold_entry = self.create_entry(params_frame, "Cold Flow Rate (L/min):", "10")
        t_hot_start_entry = self.create_entry(params_frame, "Start Hot Temp (°C):", "50")
        t_hot_end_entry = self.create_entry(params_frame, "End Hot Temp (°C):", "100")
        t_hot_steps_entry = self.create_entry(params_frame, "Hot Temp Steps:", "20")
        length_entry = self.create_entry(params_frame, "Pipe Length (m):", "2")
        diameter_entry = self.create_entry(params_frame, "Pipe Diameter (m):", "0.1")
        thickness_entry = self.create_entry(params_frame, "Pipe Thickness (m):", "0.005")

        canvas = tk.Canvas(window, width=400, height=300, bg="white")
        canvas.pack(pady=10)
        params = {
            "T_cold_in": t_cold_in_entry.get(),
            "hot_fluid": hot_fluid_var.get(),
            "T_hot_in": t_hot_start_entry.get(),
            "material": material_var.get(),
            "length": length_entry.get(),
            "diameter": diameter_entry.get()
        }
        self.draw_exchanger(canvas, params)

        progress_bar = ttk.Progressbar(window, length=300, mode="determinate")
        progress_bar.pack(pady=10)

        button_frame = ttk.Frame(window)
        button_frame.pack(pady=10)
        results = {}

        def run_sim():
            try:
                fluid = fluid_var.get()
                hot_fluid = hot_fluid_var.get()
                material = material_var.get()
                T_cold_in = float(t_cold_in_entry.get())
                flow_cold = float(flow_cold_entry.get())
                T_hot_start = float(t_hot_start_entry.get())
                T_hot_end = float(t_hot_end_entry.get())
                T_hot_steps = int(t_hot_steps_entry.get())
                length = float(length_entry.get())
                diameter = float(diameter_entry.get())
                thickness = float(thickness_entry.get())
                pipe_properties = {"outer_diameter": diameter, "thickness": thickness, "length": length}
                
                def callback():
                    nonlocal results
                    results = simulate_tp2(fluid, hot_fluid, material, T_cold_in, flow_cold, T_hot_start, T_hot_end, T_hot_steps, pipe_properties)
                    plot_path = generate_plot("TP2", results)
                    img = Image.open(plot_path)
                    img = img.resize((600, 400), Image.Resampling.LANCZOS)
                    img_tk = ImageTk.PhotoImage(img)
                    plt_window = tk.Toplevel()
                    plt_window.title("TP2 Results")
                    tk.Label(plt_window, image=img_tk).pack()
                    plt_window.image = img_tk
                    download_button["state"] = "normal"
                
                self.run_simulation(progress_bar, callback)
            except ValueError:
                messagebox.showerror("Error", "Please enter valid numbers.")

        def download_report():
            if results:
                write_tex("TP2", results, {
                    "fluid": fluid_var.get(),
                    "hot_fluid": hot_fluid_var.get(),
                    "material": material_var.get(),
                    "T_cold_in": t_cold_in_entry.get(),
                    "flow_cold": flow_cold_entry.get(),
                    "pipe_length": length_entry.get(),
                    "pipe_diameter": diameter_entry.get()
                })
                messagebox.showinfo("Success", "Report generated as reports/rapport.pdf")

        ttk.Button(button_frame, text="Run Simulation", command=run_sim).pack(side="left", padx=5)
        download_button = ttk.Button(button_frame, text="Download Report", command=download_report, state="disabled")
        download_button.pack(side="left", padx=5)
        ttk.Button(button_frame, text="Another TP", command=lambda: [window.destroy(), self.create_main_window()]).pack(side="left", padx=5)

        window.mainloop()

    def tp3_interface(self):
        window = tk.Tk()
        window.title("TP3: Different Fluids Impact")
        window.geometry("800x600")
        window.configure(bg="#E6ECEF")

        ttk.Label(window, text="TP3: Different Fluids Impact", font=("Segoe UI", 18, "bold"), foreground="#ED1B2F").pack(pady=10)
        ttk.Label(window, text="Study the impact of hot fluid choice on outlet temperature.", wraplength=600).pack(pady=10)

        params_frame = ttk.Frame(window)
        params_frame.pack(pady=10, padx=20, fill="both")
        fluid_var = self.create_dropdown(params_frame, "Cold Fluid:", specific_heat_capacity.keys(), "water")
        material_var = self.create_dropdown(params_frame, "Material:", thermal_conductivity.keys(), "stainless steel")
        flow_cold_entry = self.create_entry(params_frame, "Cold Flow Rate (L/min):", "10")
        flow_hot_entry = self.create_entry(params_frame, "Hot Flow Rate (L/min):", "10")
        length_entry = self.create_entry(params_frame, "Pipe Length (m):", "2")
        diameter_entry = self.create_entry(params_frame, "Pipe Diameter (m):", "0.1")
        thickness_entry = self.create_entry(params_frame, "Pipe Thickness (m):", "0.005")

        canvas = tk.Canvas(window, width=400, height=300, bg="white")
        canvas.pack(pady=10)
        params = {
            "T_cold_in": "20",
            "hot_fluid": "Multiple",
            "T_hot_in": "80",
            "material": material_var.get(),
            "length": length_entry.get(),
            "diameter": diameter_entry.get()
        }
        self.draw_exchanger(canvas, params)

        progress_bar = ttk.Progressbar(window, length=300, mode="determinate")
        progress_bar.pack(pady=10)

        button_frame = ttk.Frame(window)
        button_frame.pack(pady=10)
        results = {}

        def run_sim():
            try:
                fluid = fluid_var.get()
                material = material_var.get()
                flow_cold = float(flow_cold_entry.get())
                flow_hot = float(flow_hot_entry.get())
                length = float(length_entry.get())
                diameter = float(diameter_entry.get())
                thickness = float(thickness_entry.get())
                pipe_properties = {"outer_diameter": diameter, "thickness": thickness, "length": length}
                
                def callback():
                    nonlocal results
                    results = simulate_tp3(fluid, material, flow_cold, flow_hot, pipe_properties)
                    plot_path = generate_plot("TP3", results)
                    img = Image.open(plot_path)
                    img = img.resize((600, 400), Image.Resampling.LANCZOS)
                    img_tk = ImageTk.PhotoImage(img)
                    plt_window = tk.Toplevel()
                    plt_window.title("TP3 Results")
                    tk.Label(plt_window, image=img_tk).pack()
                    plt_window.image = img_tk
                    download_button["state"] = "normal"
                
                self.run_simulation(progress_bar, callback)
            except ValueError:
                messagebox.showerror("Error", "Please enter valid numbers.")

        def download_report():
            if results:
                write_tex("TP3", results, {
                    "fluid": fluid_var.get(),
                    "material": material_var.get(),
                    "flow_cold": flow_cold_entry.get(),
                    "flow_hot": flow_hot_entry.get(),
                    "pipe_length": length_entry.get(),
                    "pipe_diameter": diameter_entry.get()
                })
                messagebox.showinfo("Success", "Report generated as reports/rapport.pdf")

        ttk.Button(button_frame, text="Run Simulation", command=run_sim).pack(side="left", padx=5)
        download_button = ttk.Button(button_frame, text="Download Report", command=download_report, state="disabled")
        download_button.pack(side="left", padx=5)
        ttk.Button(button_frame, text="Another TP", command=lambda: [window.destroy(), self.create_main_window()]).pack(side="left", padx=5)

        window.mainloop()

    def tp4_interface(self):
        window = tk.Tk()
        window.title("TP4: Length and Diameter Impact")
        window.geometry("800x600")
        window.configure(bg="#E6ECEF")

        ttk.Label(window, text="TP4: Length and Diameter Impact", font=("Segoe UI", 18, "bold"), foreground="#ED1B2F").pack(pady=10)
        ttk.Label(window, text="Study the impact of pipe dimensions on outlet temperature.", wraplength=600).pack(pady=10)

        params_frame = ttk.Frame(window)
        params_frame.pack(pady=10, padx=20, fill="both")
        fluid_var = self.create_dropdown(params_frame, "Cold Fluid:", specific_heat_capacity.keys(), "water")
        hot_fluid_var = self.create_dropdown(params_frame, "Hot Fluid:", specific_heat_capacity.keys(), "water")
        material_var = self.create_dropdown(params_frame, "Material:", thermal_conductivity.keys(), "stainless steel")
        flow_cold_entry = self.create_entry(params_frame, "Cold Flow Rate (L/min):", "10")
        flow_hot_entry = self.create_entry(params_frame, "Hot Flow Rate (L/min):", "10")
        t_cold_in_entry = self.create_entry(params_frame, "Cold Inlet Temp (°C):", "20")
        t_hot_in_entry = self.create_entry(params_frame, "Cold Inlet Temp (°C):", "80")
        dim_type_var = self.create_dropdown(params_frame, "Dimension to Vary:", ["length", "diameter"], "length")
        dim_start_entry = self.create_entry(params_frame, "Start Dimension (m):", "1")
        dim_end_entry = self.create_entry(params_frame, "End Dimension (m):", "5")
        dim_steps_entry = self.create_entry(params_frame, "Dimension Steps:", "20")
        thickness_entry = self.create_entry(params_frame, "Pipe Thickness (m):", "0.005")

        canvas = tk.Canvas(window, width=400, height=300, bg="white")
        canvas.pack(pady=10)
        params = {
            "T_cold_in": t_cold_in_entry.get(),
            "hot_fluid": hot_fluid_var.get(),
            "T_hot_in": t_hot_in_entry.get(),
            "material": material_var.get(),
            "length": "Varies" if dim_type_var.get() == "length" else "2",
            "diameter": "Varies" if dim_type_var.get() == "diameter" else "0.1"
        }
        self.draw_exchanger(canvas, params)

        progress_bar = ttk.Progressbar(window, length=300, mode="determinate")
        progress_bar.pack(pady=10)

        button_frame = ttk.Frame(window)
        button_frame.pack(pady=10)
        results = {}

        def run_sim():
            try:
                fluid = fluid_var.get()
                hot_fluid = hot_fluid_var.get()
                material = material_var.get()
                flow_cold = float(flow_cold_entry.get())
                flow_hot = float(flow_hot_entry.get())
                T_cold_in = float(t_cold_in_entry.get())
                T_hot_in = float(t_hot_in_entry.get())
                dim_type = dim_type_var.get()
                dim_start = float(dim_start_entry.get())
                dim_end = float(dim_end_entry.get())
                dim_steps = int(dim_steps_entry.get())
                thickness = float(thickness_entry.get())
                
                def callback():
                    nonlocal results
                    results = simulate_tp4(fluid, hot_fluid, material, flow_cold, flow_hot, T_cold_in, T_hot_in, dim_type, dim_start, dim_end, dim_steps)
                    plot_path = generate_plot("TP4", results)
                    img = Image.open(plot_path)
                    img = img.resize((600, 400), Image.Resampling.LANCZOS)
                    img_tk = ImageTk.PhotoImage(img)
                    plt_window = tk.Toplevel()
                    plt_window.title("TP4 Results")
                    tk.Label(plt_window, image=img_tk).pack()
                    plt_window.image = img_tk
                    download_button["state"] = "normal"
                
                self.run_simulation(progress_bar, callback)
            except ValueError:
                messagebox.showerror("Error", "Please enter valid numbers.")

        def download_report():
            if results:
                write_tex("TP4", results, {
                    "fluid": fluid_var.get(),
                    "hot_fluid": hot_fluid_var.get(),
                    "material": material_var.get(),
                    "flow_cold": flow_cold_entry.get(),
                    "flow_hot": flow_hot_entry.get(),
                    "T_cold_in": t_cold_in_entry.get(),
                    "T_hot_in": t_hot_in_entry.get(),
                    "dimension_type": dim_type_var.get()
                })
                messagebox.showinfo("Success", "Report generated as reports/rapport.pdf")

        ttk.Button(button_frame, text="Run Simulation", command=run_sim).pack(side="left", padx=5)
        download_button = ttk.Button(button_frame, text="Download Report", command=download_report, state="disabled")
        download_button.pack(side="left", padx=5)
        ttk.Button(button_frame, text="Another TP", command=lambda: [window.destroy(), self.create_main_window()]).pack(side="left", padx=5)

        window.mainloop()

if __name__ == "__main__":
    app = HeatExchangerSimulator()
    app.create_main_window()