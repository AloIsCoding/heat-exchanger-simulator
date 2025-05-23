# report.py
# ---------
import time
import os
import subprocess
from pathlib import Path
import numpy as np
from plotting import generate_plot
import tkinter as tk
from tkinter import filedialog, messagebox
from utils import specific_heat_capacity

def ecriture_graphique(file, tp_name, results, plo_path):
    """
    Write a graphic to the LaTeX file using a generated PNG image.
    
    Args:
        file: Open LaTeX file.
        tp_name (str): Name of the TP (e.g., "TP1").
        results (dict): Simulation results.
        plo_path (str): Path to the PNG plot.
    """
    caption = f"Simulation results for {tp_name}"
    label = f"fig:{tp_name.lower()}_results"
    file.write(f'''\\begin{{figure}}[H]
        \\centering
        \\includegraphics[width=0.8\\textwidth]{{{Path(plo_path).name}}}
        \\caption{{{caption}}}
        \\label{{{label}}}
\\end{{figure}}\\n''')

def ecriture_results(file, tp_name, results):
    """
    Write optimal results (maximizing T_out) as an itemize list.
    
    Args:
        file: Open LaTeX file.
        tp_name (str): Name of the TP.
        results (dict): Simulation results.
    """
    required_keys = ["T_out", "Q", "efficiency", "U", "delta_T_lm", "h_internal", "h_external", "A"]
    if not all(key in results for key in required_keys):
        file.write(f'''\\subsection{{Optimal Results}}
Les résultats optimaux n'ont pas pu être calculés en raison de données manquantes.
''')
        return

    max_T_out_idx = np.argmax(results["T_out"])
    T_out = round(results["T_out"][max_T_out_idx], 2)
    Q = round(results["Q"][max_T_out_idx], 2)
    efficiency = round(results["efficiency"][max_T_out_idx] * 100, 2)
    U = round(results["U"][max_T_out_idx], 2)
    delta_T_lm = round(results["delta_T_lm"][max_T_out_idx], 2)
    h_internal = round(results["h_internal"][max_T_out_idx], 2)
    h_external = round(results["h_external"][max_T_out_idx], 2)
    A = round(results["A"][max_T_out_idx], 4)

    file.write(f'''\\subsection{{Optimal Results}}
The simulation identifies the following optimal parameters maximizing the outlet temperature:
\\begin{{itemize}}
    \\item Outlet temperature: {T_out} °C
    \\item Heat transferred: {Q} W
    \\item Efficiency: {efficiency} \\%
    \\item Overall heat transfer coefficient (U): {U} W/m²·K
    \\item Logarithmic mean temperature difference (LMTD): {delta_T_lm} °C
    \\item Internal convection coefficient: {h_internal} W/m²·K
    \\item External convection coefficient: {h_external} W/m²·K
    \\item Heat transfer surface area: {A} m²
\\end{{itemize}}

Qualitative analysis: For {tp_name}, the optimal outlet temperature is achieved through a balance of flow conditions, temperature gradients, or geometric parameters, as detailed in Section \\ref{{sec:methodology}}. The efficiency reflects effective use of the temperature difference, with convection coefficients indicating the flow regime's impact (laminar or turbulent).
''')

def ecriture_equation(file, tp_name):
    """
    Write the key equations used in the simulation with explanations.
    
    Args:
        file: Open LaTeX file.
        tp_name (str): Name of the TP.
    """
    file.write(f'''\\section{{Methodology}}\\label{{sec:methodology}}
The simulation models a counter-flow concentric tube heat exchanger using the following key equations:

\\begin{{align}}
Q &= \\dot{{m}} \\cdot c_p \\cdot (T_{{out}} - T_{{in}}) & \\text{{(Heat transfer rate)}} \\label{{eq:{tp_name.lower()}_q}} \\\\
\\end{{align}}
This equation calculates the heat transfer rate ($Q$) based on the mass flow rate ($\\dot{{m}}$), specific heat capacity ($c_p$), 
and the temperature difference between the outlet ($T_{{out}}$) and inlet ($T_{{in}}$) of the cold fluid. It quantifies the energy 
transferred from the hot fluid to the cold fluid.

\\begin{{align}}
Q &= U \\cdot A \\cdot \\Delta T_{{lm}} & \\text{{(Overall heat transfer)}} \\label{{eq:{tp_name.lower()}_u}} \\\\
\\end{{align}}
This equation relates the heat transfer rate to the overall heat transfer coefficient ($U$), the heat transfer surface area ($A$), 
and the logarithmic mean temperature difference ($\\Delta T_{{lm}}$). It accounts for the convective and conductive resistances 
across the exchanger.

\\begin{{align}}
\\Delta T_{{lm}} &= \\frac{{\\Delta T_1 - \\Delta T_2}}{{\\ln(\\Delta T_1 / \\Delta T_2)}} & \\text{{(LMTD)}} \\label{{eq:{tp_name.lower()}_lmtd}} \\\\
\\end{{align}}
The LMTD is calculated as the logarithmic average of the temperature differences at the two ends of the exchanger 
($\\Delta T_1 = T_{{hot,in}} - T_{{cold,out}}$, $\\Delta T_2 = T_{{hot,out}} - T_{{cold,in}}$). It provides an effective 
temperature driving force for heat transfer in counter-flow configurations.

\\begin{{align}}
\\frac{{1}}{{U}} &= \\frac{{1}}{{h_{{internal}}}} + \\frac{{e}}{{k}} + \\frac{{1}}{{h_{{external}}}} & \\text{{(Overall U)}} \\label{{eq:{tp_name.lower()}_u_coeff}} \\\\
\\end{{align}}
The overall heat transfer coefficient ($U$) is determined by the internal and external convection coefficients 
($h_{{internal}}$, $h_{{external}}$), the pipe thickness ($e$), and the thermal conductivity of the material ($k$). 
This equation models the total thermal resistance across the exchanger.

These equations are solved iteratively to determine the outlet temperatures and heat transfer rates, with convection coefficients 
calculated based on flow properties (e.g., Reynolds number) and empirical correlations.
''')

def ecriture_itemiz(file, params, results):
    """
    Write a list of parameters in an itemize list, including user inputs and defaults.
    
    Args:
        file: Open LaTeX file.
        params (dict): Simulation parameters.
        results (dict): Simulation results.
    """
    default_params = {
        'fluid': 'water',
        'hot_fluid': 'water',
        'material': 'stainless steel',
        'pipe_length': 2.0,
        'pipe_diameter': 0.1,
        'pipe_thickness': 0.005,
        'gap': 0.01,
        'flow_cold': 10.0,
        'flow_hot': 10.0,
        'T_cold_in': 20.0,
        'T_hot_in': 80.0,
    }
    
    safe_params = {k: str(v).replace('_', ' ').replace('%', '\\%').replace('#', '\\#').replace('&', '\\&') for k, v in params.items()}
    
    items = []
    for key, default_value in default_params.items():
        value = safe_params.get(key, default_value)
        note = "(default)" if key not in params and value == str(default_value) else ""
        param_name = {
            'fluid': 'Cold Fluid',
            'hot_fluid': 'Hot Fluid',
            'material': 'Material',
            'T_cold_in': 'Cold Inlet Temperature',
            'T_hot_in': 'Hot Inlet Temperature',
            'pipe_length': 'Pipe Length',
            'pipe_diameter': 'Pipe Diameter',
            'pipe_thickness': 'Pipe Thickness',
            'gap': 'Gap',
            'flow_cold': 'Cold Flow Rate',
            'flow_hot': 'Hot Flow Rate',
        }[key]
        unit = '°C' if 'Temperature' in param_name else 'm' if 'Pipe' in param_name or key == 'gap' else 'L/min' if 'Flow' in param_name else ''
        items.append(f"\\item {param_name}: {value} {unit} {note}")
    
    if "flow_start" in safe_params:
        items.extend([
            f"\\item Start Flow Rate: {safe_params.get('flow_start', 'N/A')} L/min",
            f"\\item End Flow Rate: {safe_params.get('flow_end', 'N/A')} L/min",
            f"\\item Flow Steps: {safe_params.get('flow_steps', 'N/A')}",
        ])
    if "T_hot_start" in safe_params:
        items.extend([
            f"\\item Start Hot Temperature: {safe_params.get('T_hot_start', 'N/A')} °C",
            f"\\item End Hot Temperature: {safe_params.get('T_hot_end', 'N/A')} °C",
            f"\\item Hot Temperature Steps: {safe_params.get('T_hot_steps', 'N/A')}",
        ])
    if "dimension_type" in safe_params:
        items.extend([
            f"\\item Dimension Type: {safe_params.get('dimension_type', 'N/A')}",
            f"\\item Start Dimension: {safe_params.get('dim_start', 'N/A')} m",
            f"\\item End Dimension: {safe_params.get('dim_end', 'N/A')} m",
            f"\\item Dimension Steps: {safe_params.get('dim_steps', 'N/A')}",
        ])
    
    items.extend([
        f"\\item Average Overall Heat Transfer Coefficient (U): {round(np.mean(results.get('U', [0])), 2)} W/m²·K",
        f"\\item Average Internal Reynolds Number: {round(np.mean(results.get('Re_internal', [0])), 2)} ({results.get('Re_internal_regime', ['Unknown'])[0]})",
        f"\\item Average External Reynolds Number: {round(np.mean(results.get('Re_external', [0])), 2)} ({results.get('Re_external_regime', ['Unknown'])[0]})",
    ])

    file.write(f'''\\section{{Experimental Setup}}
The following parameters were used in the simulation, with default values indicated where applicable:
\\begin{{itemize}}
    \\setlength\\itemsep{{-0.5em}}
    {"\n".join(items)}
\\end{{itemize}}\\n''')

def ecriture_introduction(file, tp_name):
    """
    Write a professional introduction with context and specific objectives.
    
    Args:
        file: Open LaTeX file.
        tp_name (str): Name of the TP.
    """
    context = (
        "Heat exchangers are critical components in industrial and engineering applications, enabling efficient thermal energy transfer between two fluids without mixing. "
        "Used in power generation, HVAC systems, and chemical processing, they optimize energy use through temperature gradients. "
        "This simulation examines a counter-flow concentric tube heat exchanger, where fluids flow in opposite directions to maximize heat transfer."
    )
    
    if tp_name == "TP1":
        objective = (
            "TP1 investigates the effect of the cold fluid flow rate on the heat exchanger's performance. "
            "By varying the flow rate while keeping other parameters constant (e.g., pipe dimensions, fluid properties, hot fluid conditions), we aim to assess its impact on outlet temperature, heat transfer rate, and efficiency. "
            "This study explores the balance between enhanced convection at higher flow rates and reduced residence time."
        )
    elif tp_name == "TP2":
        objective = (
            "TP2 examines the influence of the hot fluid inlet temperature on the heat exchanger's performance. "
            "By adjusting the inlet temperature with fixed flow rates and pipe geometry, we seek to evaluate its effect on outlet temperature, heat transfer rate, and efficiency. "
            "This experiment highlights the temperature difference as the driving force for heat transfer."
        )
    elif tp_name == "TP3":
        objective = (
            "TP3 assesses the impact of different hot fluids on the heat exchanger's performance. "
            "By testing fluids with varying thermophysical properties (e.g., specific heat capacity, viscosity), we aim to identify the fluid that maximizes outlet temperature and heat transfer rate. "
            "This study emphasizes fluid selection in heat exchanger design."
        )
    elif tp_name == "TP4":
        objective = (
            "TP4 focuses on the effect of pipe dimensions (length or diameter) on the heat exchanger's performance. "
            "By varying one dimension while keeping other parameters constant, we aim to understand its influence on outlet temperature, heat transfer rate, and efficiency. "
            "This experiment illustrates the role of geometry in heat transfer."
        )
    
    file.write(f'''\\section{{Introduction}}
{context}

{objective}\\n''')

def ecriture_conclusion(file, tp_name, results):
    """
    Write a conclusion summarizing the TP's purpose and main results.
    
    Args:
        file: Open LaTeX file.
        tp_name (str): Name of the TP.
        results (dict): Simulation results.
    """
    max_T_out_idx = np.argmax(results["T_out"])
    max_T_out = round(results["T_out"][max_T_out_idx], 2)
    
    if tp_name == "TP1":
        purpose = "investigate the effect of the cold fluid flow rate on the heat exchanger's performance"
        key_result = f"achieving a maximum outlet temperature of {max_T_out} °C at a flow rate of {results['flow_rates'][max_T_out_idx]} L/min"
    elif tp_name == "TP2":
        purpose = "analyze the impact of the hot fluid inlet temperature on the heat exchanger's performance"
        key_result = f"achieving a maximum outlet temperature of {max_T_out} °C at an inlet temperature of {results['T_hot_in'][max_T_out_idx]} °C"
    elif tp_name == "TP3":
        purpose = "assess the influence of different hot fluids on the heat exchanger's performance"
        key_result = f"achieving a maximum outlet temperature of {max_T_out} °C with {results['hot_fluids'][max_T_out_idx]}"
    elif tp_name == "TP4":
        purpose = f"examine the effect of pipe {results.get('dimension_type', 'dimension')} on the heat exchanger's performance"
        key_result = f"achieving a maximum outlet temperature of {max_T_out} °C at a {results.get('dimension_type', 'dimension')} of {results['dimensions'][max_T_out_idx]} m"
    
    conclusion = (
        f"This simulation aimed to {purpose}. The results show an optimal configuration {key_result}. "
        f"These findings underscore the importance of optimizing the varied parameter to enhance heat transfer efficiency and outlet temperature."
    )
    
    file.write(f'''\\section{{Conclusion}}
{conclusion}\\n''')

def ecriture_template(tp_name, results, params, output_dir, pdf_filename, tex_filename, plot_filename):
    """
    Write the complete LaTeX template with all elements.
    
    Args:
        tp_name (str): Name of the TP.
        results (dict): Simulation results.
        params (dict): Simulation parameters.
        output_dir (Path): Output directory.
        pdf_filename (str): Name of the PDF file.
        tex_filename (str): Name of the LaTeX file.
        plot_filename (str): Name of the plot file.
    
    Returns:
        tuple: Paths to the generated PDF, LaTeX, and PNG files, or None if failed.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)
    tex_file = output_dir / tex_filename
    log_file = output_dir / "pdflatex_output.txt"
    
    try:
        plo_path = generate_plot(tp_name, results, output_dir, filename=plot_filename)
        if not Path(plo_path).exists():
            raise FileNotFoundError(f"Le fichier graphique {plo_path} n'a pas été généré.")
    except Exception as e:
        messagebox.showerror("Erreur", f"Échec de la génération du graphique : {str(e)}")
        return None
    
    title = f"Heat Exchanger Simulation Report: {tp_name}"
    author = params.get("author", "User")
    date = time.strftime("%d.%m.%Y")
    
    try:
        with open(tex_file, "w", encoding="utf-8") as file:
            file.write(f'''\\documentclass[12pt]{{article}}
\\usepackage[a4paper, margin=1in]{{geometry}}
\\usepackage{{graphicx,amsmath,fancyhdr,float}}
\\usepackage[utf8]{{inputenc}}
\\graphicspath{{{{{output_dir.as_posix()}/}}}} % Chemin pour les images
\\pagestyle{{fancy}}
\\fancyhf{{}}
\\fancyhead[L]{{{title}}}
\\fancyhead[R]{{\\today}}
\\fancyfoot[C]{{\\thepage}}
\\renewcommand{{\\headrulewidth}}{{0.4pt}}

\\title{{{title}}}
\\author{{{author}}}
\\date{{{date}}}

\\begin{{document}}
\\maketitle
\\vspace{{10pt}}
\\tableofcontents
\\vspace{{20pt}}

''')
            ecriture_introduction(file, tp_name)
            ecriture_itemiz(file, params, results)
            ecriture_equation(file, tp_name)
            file.write(f'''
\\section{{Results and Discussion}}
''')
            ecriture_graphique(file, tp_name, results, plo_path)
            ecriture_results(file, tp_name, results)
            ecriture_conclusion(file, tp_name, results)
            
            file.write(f'''
\\end{{document}}
''')
    except Exception as e:
        messagebox.showerror("Erreur", f"Échec de l'écriture du fichier LaTeX : {str(e)}")
        return None
    
    with open(log_file, "w", encoding="utf-8") as f:
        f.write(f"Commande: pdflatex -interaction=nonstopmode -output-directory {output_dir} {tex_file}\n")
    
    try:
        result = subprocess.run(
            ["pdflatex", "-interaction=nonstopmode", "-output-directory", str(output_dir), str(tex_file)],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"\nSTDOUT:\n{result.stdout}\n")
            f.write(f"\nSTDERR:\n{result.stderr}\n")
            f.write(f"\nReturn code: {result.returncode}\n")
        
        pdf_file = output_dir / pdf_filename
        if not pdf_file.exists():
            messagebox.showerror("Erreur", f"Échec de la compilation LaTeX. Vérifiez {log_file} pour plus de détails.")
            return None
        return str(pdf_file), str(tex_file), str(plo_path)
    except FileNotFoundError:
        messagebox.showerror("Erreur", "MiKTeX (pdflatex) n'est pas installé ou n'est pas dans le PATH.\nVérifiez votre installation MiKTeX.")
        return None
    except subprocess.CalledProcessError as e:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"\nException: {str(e)}\n")
        messagebox.showerror("Erreur", f"Erreur lors de la compilation LaTeX. Vérifiez {log_file} pour plus de détails.")
        return None
    finally:
        for ext in [".aux", ".log", ".out", ".toc"]:
            aux_file = output_dir / f"{tex_filename.rsplit('.', 1)[0]}{ext}"
            if aux_file.exists():
                try:
                    aux_file.unlink()
                except Exception:
                    pass

def write_tex(tp_name, results, params):
    """
    Generate a LaTeX report and prompt the user to create a directory and name the files.
    
    Args:
        tp_name (str): Name of the TP.
        results (dict): Simulation results.
        params (dict): Simulation parameters.
    """
    root = tk.Tk()
    root.withdraw()
    
    # Ask user to select a parent directory
    parent_dir = filedialog.askdirectory(title=f"Select Parent Directory for {tp_name} Report")
    if not parent_dir:
        messagebox.showinfo("Annulé", "Aucun dossier sélectionné. Le rapport n'a pas été généré.")
        root.destroy()
        return
    
    # Ask user for a folder name
    folder_name = tk.simpledialog.askstring(
        "Folder Name", 
        f"Enter a name for the report folder (e.g., {tp_name}_Report):",
        initialvalue=f"{tp_name}_Report_{time.strftime('%Y-%m-%d')}"
    )
    if not folder_name:
        messagebox.showinfo("Annulé", "Aucun nom de dossier saisi. Le rapport n'a pas été généré.")
        root.destroy()
        return
    
    # Create the report directory
    output_dir = Path(parent_dir) / folder_name
    try:
        output_dir.mkdir(exist_ok=True)
    except Exception as e:
        messagebox.showerror("Erreur", f"Échec de la création du dossier : {str(e)}")
        root.destroy()
        return
    
    # Ask user for a base filename
    base_filename = tk.simpledialog.askstring(
        "File Name", 
        f"Enter a base name for the report files (e.g., rapport_{tp_name.lower()}):",
        initialvalue=f"rapport_{tp_name.lower()}"
    )
    if not base_filename:
        messagebox.showinfo("Annulé", "Aucun nom de fichier saisi. Le rapport n'a pas été généré.")
        root.destroy()
        return
    
    pdf_filename = f"{base_filename}.pdf"
    tex_filename = f"{base_filename}.tex"
    plot_filename = f"{base_filename}_plot.png"
    
    result = ecriture_template(tp_name, results, params, output_dir, pdf_filename, tex_filename, plot_filename)
    
    if result:
        pdf_path, _, _ = result
        messagebox.showinfo("Succès", f"Rapport généré avec succès dans {output_dir}:\n- {pdf_filename}\n- {tex_filename}\n- {plot_filename}")
    else:
        messagebox.showerror("Erreur", f"Échec de la génération du rapport. Vérifiez {output_dir}/pdflatex_output.txt pour plus de détails.")
    root.destroy()