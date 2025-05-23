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
        """
        Create a dropdown menu with a label.
        
        Args:
            parent: Parent widget.
            label_text (str): Label text.
            options (list): List of options for the dropdown.
            default (str): Default selected option.
            width (int): Width of the dropdown.
        
        Returns:
            tk.StringVar: Variable holding the selected value.
        """
        frame = ttk.Frame(parent)
        frame.pack(pady=5, padx=20, fill="x")
        label = ttk.Label(frame, text=label_text)
        label.pack(side="left", padx=5)
        var = tk.StringVar(value=default)
        menu = ttk.Combobox(frame, textvariable=var, values=list(options), width=width, state="readonly")
        menu.pack(side="right", padx=5)
        return var

    def create_entry(self, parent, label_text, placeholder=None):
        """
        Create an entry field with a label and optional placeholder.
        
        Args:
            parent: Parent widget.
            label_text (str): Label text.
            placeholder (str): Placeholder text for the entry.
        
        Returns:
            ttk.Entry: Entry widget.
        """
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

    def draw_exchanger(self, canvas, params):
        """
        Draw the heat exchanger schematic on the canvas.
        
        Args:
            canvas: Tkinter Canvas widget.
            params (dict): Parameters to display on the schematic.
        """
        canvas.delete("all")
        try:
            img_path = os.path.join(os.path.dirname(__file__), "exchanger.png")
            img = Image.open(img_path)
            img = img.resize((400, 300), Image.Resampling.LANCZOS)
            canvas.image = ImageTk.PhotoImage(img)
            canvas.create_image(200, 150, image=canvas.image)
        except Exception as e:
            print(f"Erreur de chargement de l'image : {e}")
            canvas.create_rectangle(100, 100, 300, 200, outline="black", width=2)
            canvas.create_line(50, 150, 100, 150, arrow=tk.LAST)
            canvas.create_line(300, 150, 350, 150, arrow=tk.LAST)
            canvas.create_line(350, 120, 100, 120, arrow=tk.LAST)
            canvas.create_text(50, 130, text=f"T_in: {params.get('T_cold_in', '')}°C", anchor="e")
            canvas.create_text(350, 130, text=f"T_out: ?", anchor="w")
            canvas.create_text(200, 80, text=f"Hot Fluid: {params.get('hot_fluid', '')}, T_hot: {params.get('T_hot_in', '')}°C")
            canvas.create_text(200, 220, text=f"Pipe: {params.get('material', '')}, L={params.get('length', '')}m, D={params.get('diameter', '')}m")

    def run_simulation(self, progress_bar, callback):
        """
        Simulate a progress bar animation and execute the callback.
        
        Args:
            progress_bar: Tkinter Progressbar widget.
            callback: Function to call after progress completes.
        """
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

    def create_main_window(self):
        """
        Create the main window for selecting a TP.
        """
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

        continue_button = ttk.Button(self.window, text="Continue", command=self.continue_action)
        continue_button.pack(pady=100)
        self.window.mainloop()

    def continue_action(self):
        """
        Handle the selection of a TP and create the corresponding interface.
        """
        selected_tp = self.tp_var.get()
        for elem in self.window.winfo_children():
            elem.destroy()
        fields = []
        title = ""
        description = ""
        if selected_tp == "TP1: Flow Impact":
            fields = [
                ("fluid", "dropdown", "water", specific_heat_capacity.keys()),
                ("hot_fluid", "dropdown", "water", specific_heat_capacity.keys()),
                ("material", "dropdown", "stainless steel", thermal_conductivity.keys()),
                ("T_cold_in", "entry", "20", None),
                ("T_hot_in", "entry", "80", None),
                ("flow_start", "entry", "5", None),
                ("flow_end", "entry", "100", None),
                ("flow_steps", "entry", "20", None),
                ("pipe_length", "entry", "2", None),
                ("pipe_diameter", "entry", "0.1", None),
                ("pipe_thickness", "entry", "0.005", None),
                ("gap", "entry", "0.01", None)
            ]
            title = "Flow Impact"
            description = "Study the impact of cold fluid flow rate on outlet temperature."
        elif selected_tp == "TP2: Temperature Impact":
            fields = [
                ("fluid", "dropdown", "water", specific_heat_capacity.keys()),
                ("hot_fluid", "dropdown", "water", specific_heat_capacity.keys()),
                ("material", "dropdown", "stainless steel", thermal_conductivity.keys()),
                ("T_cold_in", "entry", "20", None),
                ("flow_cold", "entry", "10", None),
                ("T_hot_start", "entry", "50", None),
                ("T_hot_end", "entry", "100", None),
                ("T_hot_steps", "entry", "20", None),
                ("pipe_length", "entry", "2", None),
                ("pipe_diameter", "entry", "0.1", None),
                ("pipe_thickness", "entry", "0.005", None),
                ("gap", "entry", "0.01", None)
            ]
            title = "Temperature Impact"
            description = "Study the impact of hot fluid temperature on outlet temperature."
        elif selected_tp == "TP3: Different Fluids Impact":
            fields = [
                ("fluid", "dropdown", "water", specific_heat_capacity.keys()),
                ("material", "dropdown", "stainless steel", thermal_conductivity.keys()),
                ("flow_cold", "entry", "10", None),
                ("flow_hot", "entry", "10", None),
                ("pipe_length", "entry", "2", None),
                ("pipe_diameter", "entry", "0.1", None),
                ("pipe_thickness", "entry", "0.005", None),
                ("gap", "entry", "0.01", None)
            ]
            title = "Different Fluids Impact"
            description = "Study the impact of hot fluid choice on outlet temperature."
        elif selected_tp == "TP4: Length and Diameter Impact":
            fields = [
                ("fluid", "dropdown", "water", specific_heat_capacity.keys()),
                ("hot_fluid", "dropdown", "water", specific_heat_capacity.keys()),
                ("material", "dropdown", "stainless steel", thermal_conductivity.keys()),
                ("flow_cold", "entry", "10", None),
                ("flow_hot", "entry", "10", None),
                ("T_cold_in", "entry", "20", None),
                ("T_hot_in", "entry", "80", None),
                ("dimension_type", "dropdown", "length", ["length", "diameter"]),
                ("dim_start", "entry", "1", None),
                ("dim_end", "entry", "5", None),
                ("dim_steps", "entry", "20", None),
                ("pipe_thickness", "entry", "0.005", None),
                ("gap", "entry", "0.01", None)
            ]
            title = "Length and Diameter Impact"
            description = "Study the impact of pipe dimensions on outlet temperature."
        self.create_tp_interface(selected_tp.split(":")[0], fields, title, description)
        self.window.mainloop()

    def create_tp_interface(self, tp_name, fields, title, description):
        """
        Create a generic interface for a TP.
        
        Args:
            tp_name (str): Name of the TP (e.g., "TP1").
            fields (list): List of (field_name, field_type, default, options) tuples.
            title (str): Title of the TP.
            description (str): Description of the TP.
        """
        self.window.title(f"{tp_name}: {title}")
        self.window.geometry(f"{self.dim_x+700}x{self.dim_y+100}")
        self.window.configure(bg="#EEEEEE")

        params_frame = ttk.Frame(self.window)
        params_frame.pack(fill="x", pady=10)
        ttk.Label(self.window, text=f"{tp_name}: {title}", font=("Segoe UI", 18, "bold"), foreground="#ED1B2F").pack(pady=10)
        ttk.Label(self.window, text=description, wraplength=600).pack(pady=10)

        main_frame = ttk.Frame(self.window)
        main_frame.pack(expand=True, fill='both', padx=10, pady=10)

        params_frame = ttk.Frame(main_frame)
        params_frame.grid(row=0, column=0, sticky="nsew", padx=10)

        entries = {}
        for field_name, field_type, default, options in fields:
            if field_type == "dropdown":
                entries[field_name] = self.create_dropdown(params_frame, f"{field_name.replace('_', ' ').title()}:", options, default)
            else:
                entries[field_name] = self.create_entry(params_frame, f"{field_name.replace('_', ' ').title()}:", default)

        canvas = tk.Canvas(main_frame, bg="#EEEEEE")
        canvas.grid(row=0, column=1, sticky="nsew", padx=10)
        canvas_params = {
            "T_cold_in": entries.get("T_cold_in", tk.Entry()).get() or "20",
            "hot_fluid": entries.get("hot_fluid", tk.StringVar(value="water")).get() or "Multiple" if tp_name == "TP3" else "water",
            "T_hot_in": entries.get("T_hot_in", tk.Entry()).get() or entries.get("T_hot_start", tk.Entry()).get() or "80",
            "material": entries.get("material", tk.StringVar(value="stainless steel")).get(),
            "length": entries.get("pipe_length", tk.Entry()).get() or "Varies" if tp_name == "TP4" and entries.get("dimension_type", tk.StringVar()).get() == "length" else "2",
            "diameter": entries.get("pipe_diameter", tk.Entry()).get() or "Varies" if tp_name == "TP4" and entries.get("dimension_type", tk.StringVar()).get() == "diameter" else "0.1",
            "gap": entries.get("gap", tk.Entry()).get() or "0.01"
        }
        self.draw_exchanger(canvas, canvas_params)

        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=0, column=2, sticky="nsew", padx=10)

        progress_bar = ttk.Progressbar(button_frame, length=200, mode="determinate")
        progress_bar.pack(pady=20)

        results = {}

        def validate_inputs():
            """
            Validate user inputs before running the simulation.
            
            Returns:
                bool: True if inputs are valid, False otherwise.
            """
            try:
                for field_name, field_type, _, _ in fields:
                    if field_type == "entry":
                        value = entries[field_name].get()
                        if field_name in ["T_hot_steps", "flow_steps", "dim_steps"]:
                            value = int(value)
                            if value < 1:
                                raise ValueError(f"{field_name.replace('_', ' ').title()} doit être au moins 1.")
                        else:
                            value = float(value)
                            if value <= 0 and field_name not in ["T_cold_in", "T_hot_in", "T_hot_start", "T_hot_end"]:
                                raise ValueError(f"{field_name.replace('_', ' ').title()} doit être positif.")
                        if field_name == "T_hot_in" and "T_cold_in" in entries:
                            if value <= float(entries["T_cold_in"].get()):
                                raise ValueError("La température d'entrée du fluide chaud doit être supérieure à celle du fluide froid.")
                        if field_name == "T_hot_start" and "T_cold_in" in entries:
                            if value <= float(entries["T_cold_in"].get()):
                                raise ValueError("La température de départ du fluide chaud doit être supérieure à celle du fluide froid.")
                        if field_name == "T_hot_end" and "T_hot_start" in entries:
                            if value < float(entries["T_hot_start"].get()):
                                raise ValueError("La température de fin du fluide chaud doit être supérieure ou égale à la température de départ.")
                        if field_name == "flow_end" and "flow_start" in entries:
                            if value < float(entries["flow_start"].get()):
                                raise ValueError("Le débit de fin doit être supérieur ou égal au débit de départ.")
                        if field_name == "dim_end" and "dim_start" in entries:
                            if value < float(entries["dim_start"].get()):
                                raise ValueError("La dimension de fin doit être supérieure ou égale à la dimension de départ.")
                        if field_name == "pipe_thickness" and "pipe_diameter" in entries:
                            if value >= float(entries["pipe_diameter"].get()) / 2:
                                raise ValueError("L'épaisseur du tuyau est trop grande par rapport au diamètre.")
                return True
            except ValueError as e:
                if str(e).startswith("invalid literal"):
                    messagebox.showerror("Erreur", "Veuillez entrer des nombres valides pour tous les champs numériques.")
                else:
                    messagebox.showerror("Erreur", str(e))
                return False

        def run_sim():
            """
            Run the simulation for the selected TP.
            """
            if not validate_inputs():
                return
            try:
                params = {field_name: entries[field_name].get() for field_name, _, _, _ in fields}
                if "pipe_diameter" in params and "pipe_thickness" in params:
                    params["pipe_properties"] = {
                        "outer_diameter": float(params["pipe_diameter"]) + 2 * float(params["pipe_thickness"]),
                        "thickness": float(params["pipe_thickness"]),
                        "length": float(params.get("pipe_length", "2"))
                    }
                for key in ["T_cold_in", "T_hot_in", "T_hot_start", "T_hot_end", "flow_cold", "flow_hot", "flow_start", "flow_end", "dim_start", "dim_end", "gap"]:
                    if key in params:
                        params[key] = float(params[key])
                for key in ["T_hot_steps", "flow_steps", "dim_steps"]:
                    if key in params:
                        params[key] = int(params[key])

                def callback():
                    nonlocal results
                    try:
                        if tp_name == "TP1":
                            results = simulate_tp1(
                                params["fluid"], params["hot_fluid"], params["material"],
                                params["T_cold_in"], params["T_hot_in"],
                                params["flow_start"], params["flow_end"], params["flow_steps"],
                                params["pipe_properties"], params["gap"]
                            )
                        elif tp_name == "TP2":
                            results = simulate_tp2(
                                params["fluid"], params["hot_fluid"], params["material"],
                                params["T_cold_in"], params["flow_cold"],
                                params["T_hot_start"], params["T_hot_end"], params["T_hot_steps"],
                                params["pipe_properties"], params["gap"]
                            )
                        elif tp_name == "TP3":
                            results = simulate_tp3(
                                params["fluid"], params["material"],
                                params["flow_cold"], params["flow_hot"],
                                params["pipe_properties"], params["gap"]
                            )
                        elif tp_name == "TP4":
                            results = simulate_tp4(
                                params["fluid"], params["hot_fluid"], params["material"],
                                params["flow_cold"], params["flow_hot"],
                                params["T_cold_in"], params["T_hot_in"],
                                params["dimension_type"], params["dim_start"], params["dim_end"], params["dim_steps"],
                                params["gap"]
                            )
                        plot_path = generate_plot(tp_name, results)
                        img = Image.open(plot_path)
                        img = img.resize((600, 400), Image.Resampling.LANCZOS)
                        img_tk = ImageTk.PhotoImage(img)
                        plt_window = tk.Toplevel()
                        plt_window.title(f"{tp_name} Results")
                        tk.Label(plt_window, image=img_tk).pack()
                        plt_window.image = img_tk
                        download_button["state"] = "normal"
                    except Exception as e:
                        messagebox.showerror("Erreur", f"Erreur lors de la simulation : {str(e)}")
                
                self.run_simulation(progress_bar, callback)
            except ValueError as e:
                messagebox.showerror("Erreur", f"Erreur lors de la préparation de la simulation : {str(e)}")

        def download_report():
            """
            Generate and download the report for the simulation.
            """
            if results:
                try:
                    write_tex(tp_name, results, {
                        field_name: entries[field_name].get() for field_name, _, _, _ in fields
                    })
                except Exception as e:
                    messagebox.showerror("Erreur", f"Échec de la génération du rapport : {str(e)}")

        ttk.Button(button_frame, text="Run Simulation", command=run_sim).pack(pady=10)
        download_button = ttk.Button(button_frame, text="Download Report", command=download_report, state="disabled")
        download_button.pack(pady=10)
        ttk.Button(button_frame, text="Another TP", command=lambda: self.create_main_window()).pack(pady=10)

        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.columnconfigure(2, weight=1)
        main_frame.rowconfigure(0, weight=1)