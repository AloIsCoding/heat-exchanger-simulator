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
        self.dim_x = 500
        self.dim_y = 500
        self.window = tk.Tk()
        self.window.title("Heat Exchanger Simulator")
        self.window.geometry(f"{self.dim_x}x{self.dim_y}")
        self.window.configure(bg="#EEEEEE")

        style = ttk.Style()
        style.configure("TButton", font=("Segoe UI", 12, "bold"), padding=10, background="#003087")
        style.map("TButton", background=[("active", "#005566")])
        style.configure("TLabel", font=("Segoe UI", 12), background="#EEEEEE")
        style.configure("TCombobox", font=("Segoe UI", 10))
        style.configure("Title.TLabel", font=("Segoe UI", 24, "bold"), foreground="#ED1B2F")
        style.configure("Subtitle.TLabel", font=("Segoe UI", 16), foreground="#003087")

        try:
            logo_path = os.path.join(os.path.dirname(__file__), "epfl_logo.png")
            img = Image.open(logo_path)
            img = img.resize((120, 60), Image.Resampling.LANCZOS)
            self.logo = ImageTk.PhotoImage(img)
            label_logo = tk.Label(self.window, image=self.logo, bg="#EEEEEE")
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
        for widget in self.window.winfo_children():
            widget.destroy()
        self.window.geometry(f"{self.dim_x}x{self.dim_y}")
        ttk.Label(self.window, text="Heat Exchanger Simulator", style="Title.TLabel").pack(pady=(50, 10))
        ttk.Label(self.window, text="Choose your TP", style="Subtitle.TLabel").pack(pady=10)

        tp_options = [
            "TP1: Flow Impact",
            "TP2: Temperature Impact",
            "TP3: Different Fluids Impact",
            "TP4: Length and Diameter Impact"
        ]
        self.tp_var = self.create_dropdown(self.window, "Select TP:", tp_options, tp_options[0], width=40)

        continu_buton = ttk.Button(self.window, text="Continue", command=self.continue_action)
        continu_buton.pack(pady=100)
        self.window.mainloop()

    def continue_action(self):
        selected_tp = self.tp_var.get()
        for elem in self.window.winfo_children():
            elem.destroy()
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
        self.window.title("TP1: Flow Impact")
        self.window.geometry(f"{self.dim_x+700}x{self.dim_y+100}")
        self.window.configure(bg="#EEEEEE")

        # Titre
        title_frame = ttk.Frame(self.window)
        title_frame.pack(fill='x', pady=10)
        ttk.Label(title_frame, text="TP1: Flow Impact", font=("Segoe UI", 18, "bold"), foreground="#ED1B2F").pack()
        ttk.Label(title_frame, text="Study the impact of cold fluid flow rate on outlet temperature.", wraplength=600).pack()

        # Conteneur principal pour les 3 parties
        main_frame = ttk.Frame(self.window)
        main_frame.pack(expand=True, fill='both', padx=10, pady=10)

        # Partie 1 : Paramètres (colonne 0)
        params_frame = ttk.Frame(main_frame)
        params_frame.grid(row=0, column=0, sticky="nsew", padx=10)
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
        gap_entry = self.create_entry(params_frame, "Gap (m):", "0.01")

        # Partie 2 : Schéma (colonne 1)
        canvas = tk.Canvas(main_frame, bg="#EEEEEE")
        canvas.grid(row=0, column=1, sticky="nsew", padx=10)
        params = {
            "T_cold_in": t_cold_in_entry.get(),
            "hot_fluid": hot_fluid_var.get(),
            "T_hot_in": t_hot_in_entry.get(),
            "material": material_var.get(),
            "length": length_entry.get(),
            "diameter": diameter_entry.get(),
            "gap": gap_entry.get()
        }
        self.draw_exchanger(canvas, params)

        # Partie 3 : Boutons et progress bar (colonne 2)
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=0, column=2, sticky="nsew", padx=10)

        # Progress bar
        progress_bar = ttk.Progressbar(button_frame, length=200, mode="determinate")
        progress_bar.pack(pady=20)

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
                gap = float(gap_entry.get())
                pipe_properties = {"outer_diameter": diameter, "thickness": thickness, "length": length}

                def callback():
                    nonlocal results
                    results = simulate_tp1(fluid, hot_fluid, material, T_cold_in, T_hot_in,flow_start, flow_end, flow_steps, pipe_properties, gap)
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
                    "flow_start" : flow_start_entry.get(),
                    "flow_end" : flow_end_entry.get(),
                    "flow_steps" : flow_steps_entry.get(),
                    "pipe_length": length_entry.get(),
                    "pipe_diameter": diameter_entry.get(),
                    "pipe_thickness" : thickness_entry.get(),
                    "gap": gap_entry.get()
                })

        ttk.Button(button_frame, text="Run Simulation", command=run_sim).pack(pady=10)
        download_button = ttk.Button(button_frame, text="Download Report", command=download_report, state="disabled")
        download_button.pack(pady=10)
        ttk.Button(button_frame, text="Another TP", command=lambda: self.create_main_window()).pack(pady=10)

        # Rendre les colonnes équitablement redimensionnables
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.columnconfigure(2, weight=1)
        main_frame.rowconfigure(0, weight=1)

        self.window.mainloop()


    def tp2_interface(self):
        self.window.title("TP2: Temperature Impact")
        self.window.geometry(f"{self.dim_x+700}x{self.dim_y+100}")
        self.window.configure(bg="#EEEEEE")


        params_frame = ttk.Frame(self.window)
        params_frame.pack(fill="x",pady=10)
        ttk.Label(self.window, text="TP2: Temperature Impact", font=("Segoe UI", 18, "bold"), foreground="#ED1B2F").pack(pady=10)
        ttk.Label(self.window, text="Study the impact of hot fluid temperature on outlet temperature.", wraplength=600).pack(pady=10)


        main_frame = ttk.Frame(self.window)
        main_frame.pack(expand=True,fill='both',padx=10,pady=10)

        params_frame = ttk.Frame(main_frame)
        params_frame.grid(row=0, column=0, sticky="nsew", padx=10)

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
        gap_entry = self.create_entry(params_frame, "Gap (m):", "0.01")

        canvas = tk.Canvas(main_frame, bg="#EEEEEE")
        canvas.grid(row=0, column=1, sticky="nsew", padx=10)
        params = {
            "T_cold_in": t_cold_in_entry.get(),
            "hot_fluid": hot_fluid_var.get(),
            "T_hot_in": t_hot_start_entry.get(),
            "material": material_var.get(),
            "length": length_entry.get(),
            "diameter": diameter_entry.get(),
            "gap" : gap_entry.get()
        }
        self.draw_exchanger(canvas, params)


        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=0, column=2, sticky="nsew", padx=10)

        progress_bar = ttk.Progressbar(button_frame, length=200, mode="determinate")
        progress_bar.pack(pady=20)

        # button_frame = ttk.Frame(self.window)
        # button_frame.pack(pady=10)s
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
                gap = float(gap_entry.get())
                pipe_properties = {"outer_diameter": diameter + 2*thickness, "thickness": thickness, "length": length}
                
                def callback():
                    nonlocal results
                    results = simulate_tp2(fluid, hot_fluid, material, T_cold_in, flow_cold, T_hot_start, T_hot_end, T_hot_steps, pipe_properties,gap)
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
                    "T_hot_start": t_hot_start_entry.get(),
                    "T_hot_end": t_hot_end_entry.get(),
                    "T_hot_steps": t_hot_steps_entry.get(),
                    "pipe_length": length_entry.get(),
                    "pipe_diameter": diameter_entry.get(),
                    "pipe_thickness": thickness_entry.get(),
                    "gap" : gap_entry.get()
                })
                

        ttk.Button(button_frame, text="Run Simulation", command=run_sim).pack(pady=10)
        download_button = ttk.Button(button_frame, text="Download Report", command=download_report, state="disabled")
        download_button.pack(pady=10)
        ttk.Button(button_frame, text="Another TP", command=lambda: self.create_main_window()).pack(pady=10)

        # Rendre les colonnes équitablement redimensionnables
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.columnconfigure(2, weight=1)
        main_frame.rowconfigure(0, weight=1)


        self.window.mainloop()

    def tp3_interface(self):
        self.window.title("TP3: Different Fluids Impact")
        self.window.geometry(f"{self.dim_x+700}x{self.dim_y+100}")
        self.window.configure(bg="#EEEEEE")


        title_frame = ttk.Frame(self.window)
        title_frame.pack(fill='x', pady=10)
        ttk.Label(self.window, text="TP3: Different Fluids Impact", font=("Segoe UI", 18, "bold"), foreground="#ED1B2F").pack(pady=10)
        ttk.Label(self.window, text="Study the impact of hot fluid choice on outlet temperature.", wraplength=600).pack(pady=10)

        main_frame = ttk.Frame(self.window)
        main_frame.pack(expand=True, fill='both', padx=10, pady=10)

        params_frame = ttk.Frame(main_frame)
        params_frame.grid(row=0, column=0, sticky="nsew", padx=10)

        fluid_var = self.create_dropdown(params_frame, "Cold Fluid:", specific_heat_capacity.keys(), "water")
        material_var = self.create_dropdown(params_frame, "Material:", thermal_conductivity.keys(), "stainless steel")
        flow_cold_entry = self.create_entry(params_frame, "Cold Flow Rate (L/min):", "10")
        flow_hot_entry = self.create_entry(params_frame, "Hot Flow Rate (L/min):", "10")
        length_entry = self.create_entry(params_frame, "Pipe Length (m):", "2")
        diameter_entry = self.create_entry(params_frame, "Pipe Diameter (m):", "0.1")
        thickness_entry = self.create_entry(params_frame, "Pipe Thickness (m):", "0.005")
        gap_entry = self.create_entry(params_frame, "Gap (m):", "0.01")

        canvas = tk.Canvas(main_frame, bg="#EEEEEE")
        canvas.grid(row=0, column=1, sticky="nsew", padx=10)
        params = {
            "T_cold_in": "20",
            "hot_fluid": "Multiple",
            "T_hot_in": "80",
            "material": material_var.get(),
            "length": length_entry.get(),
            "diameter": diameter_entry.get(),
            "gap" : gap_entry.get()
        }
        self.draw_exchanger(canvas, params)

        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=0, column=2, sticky="nsew", padx=10)

        
        progress_bar = ttk.Progressbar(button_frame, length=200, mode="determinate")
        progress_bar.pack(pady=20)

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
                    results = simulate_tp3(fluid, material, flow_cold, flow_hot, pipe_properties,float(gap_entry.get()))
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
                    "pipe_diameter": diameter_entry.get(),
                    "pipe_thickness": thickness_entry.get(),
                    "gap" : gap_entry.get()
                })
                

        ttk.Button(button_frame, text="Run Simulation", command=run_sim).pack(pady=10)
        download_button = ttk.Button(button_frame, text="Download Report", command=download_report, state="disabled")
        download_button.pack(pady=10)
        ttk.Button(button_frame, text="Another TP", command=lambda: self.create_main_window()).pack(pady=10)

        # Rendre les colonnes équitablement redimensionnables
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.columnconfigure(2, weight=1)
        main_frame.rowconfigure(0, weight=1)
        
        self.window.mainloop()

    def tp4_interface(self):
        self.window.title("TP4: Length and Diameter Impact")
        self.window.geometry(f"{self.dim_x+700}x{self.dim_y+100}")
        self.window.configure(bg="#EEEEEE")


        title_frame = ttk.Frame(self.window)
        title_frame.pack(fill='x', pady=10)
        ttk.Label(self.window, text="TP4: Length and Diameter Impact", font=("Segoe UI", 18, "bold"), foreground="#ED1B2F").pack(pady=10)
        ttk.Label(self.window, text="Study the impact of pipe dimensions on outlet temperature.", wraplength=600).pack(pady=10)


        main_frame = ttk.Frame(self.window)
        main_frame.pack(expand=True, fill='both', padx=10, pady=10)

        params_frame = ttk.Frame(main_frame)
        params_frame.grid(row=0, column=0, sticky="nsew", padx=10)

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
        gap_entry = self.create_entry(params_frame, "Gap (m):", "0.01")

        canvas = tk.Canvas(main_frame, bg="#EEEEEE")
        canvas.grid(row=0, column=1, sticky="nsew", padx=10)
        params = {
            "T_cold_in": t_cold_in_entry.get(),
            "hot_fluid": hot_fluid_var.get(),
            "T_hot_in": t_hot_in_entry.get(),
            "material": material_var.get(),
            "length": "Varies" if dim_type_var.get() == "length" else "2",
            "diameter": "Varies" if dim_type_var.get() == "diameter" else "0.1",
            "gap" : gap_entry.get()
        }
        self.draw_exchanger(canvas, params)

        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=0, column=2, sticky="nsew", padx=10)

        # Progress bar
        progress_bar = ttk.Progressbar(button_frame, length=200, mode="determinate")
        progress_bar.pack(pady=20)

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
                    results = simulate_tp4(fluid, hot_fluid, material, flow_cold, flow_hot, T_cold_in, T_hot_in, dim_type, dim_start, dim_end, dim_steps,float(gap_entry.get()))
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
                    "dimension_type": dim_type_var.get(),
                    "dim_start": dim_start_entry.get(),
                    "dim_end": dim_end_entry.get(),
                    "dim_steps": dim_steps_entry.get(),
                    "pipe_thickness": thickness_entry.get(),
                    "gap" : gap_entry.get()
                })
               
               
        ttk.Button(button_frame, text="Run Simulation", command=run_sim).pack(pady=10)
        download_button = ttk.Button(button_frame, text="Download Report", command=download_report, state="disabled")
        download_button.pack(pady=10)
        ttk.Button(button_frame, text="Another TP", command=lambda: self.create_main_window()).pack(pady=10)

        # Rendre les colonnes équitablement redimensionnables
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.columnconfigure(2, weight=1)
        main_frame.rowconfigure(0, weight=1)

        self.window.mainloop()
