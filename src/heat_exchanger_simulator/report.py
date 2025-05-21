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
    Écrit un graphique dans le fichier LaTeX en utilisant une image PNG générée.
    
    Parameters:
        file: Fichier LaTeX ouvert
        tp_name (str): Nom du TP (ex. "TP1")
        results (dict): Résultats de la simulation
        plo_path (str): Chemin vers l’image PNG du graphe
    """
    caption = f"Simulation results for {tp_name}"
    label = f"fig:{tp_name.lower()}_results"
    file.write(f'''\\begin{{figure}}[htb!]
        \\centering
        \\includegraphics[width=0.8\\textwidth]{{{Path(plo_path).name}}}
        \\caption{{{caption}}}
        \\label{{{label}}}
\\end{{figure}}\\n''')

def ecriture_results(file, tp_name, results):
    """
    Écrit les résultats pour les paramètres idéaux (maximisant T_out) sous forme de phrases.
    
    Parameters:
        file: Fichier LaTeX ouvert
        tp_name (str): Nom du TP
        results (dict): Résultats de la simulation
    """
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
For the optimal parameters maximizing the outlet temperature, the simulation yields the following results:
\\begin{{itemize}}
    \\item The outlet temperature is: {T_out} °C
    \\item The heat transferred is: {Q} W
    \\item The efficiency is: {efficiency} \%
    \\item The overall heat transfer coefficient (U) is: {U} W/m²·K
    \\item The logarithmic mean temperature difference (LMTD) is: {delta_T_lm} °C
    \\item The internal convection coefficient is: {h_internal} W/m²·K
    \\item The external convection coefficient is: {h_external} W/m²·K
    \\item The heat transfer surface area is: {A} m²
\\end{{itemize}}\\n''')

def ecriture_equation(file, tp_name):
    """
    Écrit les équations utilisées dans la simulation.
    """
    equation = """
    Q = \\dot{m} \\cdot c_p \\cdot (T_{out} - T_{in}) \\quad \\text{(Heat transfer)} \\\\
    Q = U \\cdot A \\cdot \\Delta T_{lm} \\quad \\text{(Overall heat transfer)}
    """
    file.write(f'''\\begin{{equation}}\\label{{eq:{tp_name.lower()}_heat_transfer}}
{equation}
\\end{{equation}}\\n''')

def ecriture_itemiz(file, params, results):
    """
    Écrit une liste des paramètres dans une liste itemize, incluant toutes les entrées utilisateur.
    """
    items = [
        f"\\item Cold Fluid: {params.get('fluid', 'N/A')}",
        f"\\item Hot Fluid: {params.get('hot_fluid', 'N/A')}",
        f"\\item Material: {params.get('material', 'N/A')}",
        f"\\item Cold Inlet Temperature: {params.get('T_cold_in', 'N/A')} °C",
        f"\\item Hot Inlet Temperature: {params.get('T_hot_in', 'N/A')} °C",
        f"\\item Pipe Length: {params.get('pipe_length', 'N/A')} m",
        f"\\item Pipe Diameter: {params.get('pipe_diameter', 'N/A')} m",
        f"\\item Pipe Thickness: {params.get('pipe_thickness', 'N/A')} m",
        f"\\item Gap: {params.get('gap', 'N/A')} m",
    ]
    
    if "flow_start" in params:
        items.append(f"\\item Start Flow Rate: {params.get('flow_start', 'N/A')} L/min")
        items.append(f"\\item End Flow Rate: {params.get('flow_end', 'N/A')} L/min")
        items.append(f"\\item Flow Steps: {params.get('flow_steps', 'N/A')}")
    if "flow_cold" in params:
        items.append(f"\\item Cold Flow Rate: {params.get('flow_cold', 'N/A')} L/min")
    if "flow_hot" in params:
        items.append(f"\\item Hot Flow Rate: {params.get('flow_hot', 'N/A')} L/min")
    if "T_hot_start" in params:
        items.append(f"\\item Start Hot Temperature: {params.get('T_hot_start', 'N/A')} °C")
        items.append(f"\\item End Hot Temperature: {params.get('T_hot_end', 'N/A')} °C")
        items.append(f"\\item Hot Temperature Steps: {params.get('T_hot_steps', 'N/A')}")
    if "dimension_type" in params:
        items.append(f"\\item Dimension Type: {params.get('dimension_type', 'N/A')}")
        items.append(f"\\item Start Dimension: {params.get('dim_start', 'N/A')} m")
        items.append(f"\\item End Dimension: {params.get('dim_end', 'N/A')} m")
        items.append(f"\\item Dimension Steps: {params.get('dim_steps', 'N/A')}")

    items.extend([
        f"\\item Average Overall Heat Transfer Coefficient (U): {round(np.mean(results.get('U', [0])), 2)} W/m²·K",
        f"\\item Average Internal Reynolds Number: {round(np.mean(results.get('Re_internal', [0])), 2)} ({results.get('Re_internal_regime', ['Unknown'])[0]})",
        f"\\item Average External Reynolds Number: {round(np.mean(results.get('Re_external', [0])), 2)} ({results.get('Re_external_regime', ['Unknown'])[0]})"
    ])

    file.write(f'''\\begin{{itemize}}
    \\setlength\\itemsep{{-0.5em}}
    {"nn".join(items)}
    \\end{{itemize}}\\n''')

def ecriture_introduction(file, tp_name):
    """
    Écrit une introduction expliquant le but du TP.
    
    Parameters:
        file: Fichier LaTeX ouvert
        tp_name (str): Nom du TP
    """
    if tp_name == "TP1":
        purpose = (
            "The purpose of TP1 is to study the effect of the cold fluid flow rate on the performance of a heat exchanger. "
            "By varying the flow rate, we aim to understand how it influences the outlet temperature, heat transfer rate, "
            "and efficiency, while keeping other parameters such as pipe dimensions and fluid properties constant. This "
            "experiment highlights the trade-off between increased convection and reduced residence time."
        )
    elif tp_name == "TP2":
        purpose = (
            "The purpose of TP2 is to investigate the impact of the hot fluid inlet temperature on the heat exchanger's "
            "performance. By varying the inlet temperature of the hot fluid, we seek to determine its effect on the outlet "
            "temperature, heat transfer rate, and efficiency. This experiment emphasizes the role of the temperature "
            "difference as a driving force for heat transfer."
        )
    elif tp_name == "TP3":
        purpose = (
            "The purpose of TP3 is to explore the influence of different hot fluids on the heat exchanger's performance. "
            "By testing various fluids with distinct thermal properties (e.g., specific heat capacity, viscosity), we aim "
            "to identify which fluid maximizes the outlet temperature and heat transfer rate. This experiment illustrates "
            "the importance of fluid selection in heat exchanger design."
        )
    elif tp_name == "TP4":
        purpose = (
            "The purpose of TP4 is to examine the effect of pipe dimensions (length or diameter) on the heat exchanger's "
            "performance. By varying one dimension while keeping other parameters constant, we aim to understand how the "
            "heat transfer surface area and flow dynamics affect the outlet temperature, heat transfer rate, and efficiency. "
            "This experiment underscores the role of geometry in optimizing heat exchanger performance."
        )
    
    file.write(f'''\\section{{Introduction}}
{purpose}\\n''')

def ecriture_interpretation(file, tp_name, results, params):
    """
    Écrit une interprétation claire et concise des résultats, avec une analyse physique.
    
    Parameters:
        file: Fichier LaTeX ouvert
        tp_name (str): Nom du TP
        results (dict): Résultats de la simulation
        params (dict): Paramètres de la simulation
    """
    max_T_out_idx = np.argmax(results["T_out"])
    max_T_out = round(results["T_out"][max_T_out_idx], 2)

    if tp_name == "TP1":
        flow_rate = results["flow_rates"][max_T_out_idx]
        h_internal = round(results["h_internal"][max_T_out_idx], 2)
        delta_T_lm = round(results["delta_T_lm"][max_T_out_idx], 2)
        interpretation = (
            "In TP1, we varied the cold fluid flow rate to observe its impact on the heat exchanger's performance. "
            "Higher flow rates increase the internal convection coefficient (h_internal) by boosting the Reynolds number, "
            "which enhances the overall heat transfer coefficient (U). For instance, at the optimal flow rate, "
            f"h_internal reaches {h_internal} W/m²·K. However, increased flow reduces the fluid's residence time in the "
            "exchanger, leading to a lower outlet temperature (T_out) at very high flows. The logarithmic mean temperature "
            f"difference (LMTD), such as {delta_T_lm} °C at the optimal point, decreases as T_out rises, reflecting a smaller "
            "temperature gradient. The optimal flow rate balances enhanced convection with sufficient residence time, "
            f"achieving a maximum T_out of {max_T_out} °C at {flow_rate} L/min."
        )
    elif tp_name == "TP2":
        T_hot_in = results["T_hot_in"][max_T_out_idx]
        delta_T_lm = round(results["delta_T_lm"][max_T_out_idx], 2)
        interpretation = (
            "In TP2, we adjusted the hot fluid inlet temperature to study its effect on the heat exchanger. A higher T_hot_in "
            "increases the logarithmic mean temperature difference (LMTD), which acts as the driving force for heat transfer. "
            f"For example, at the optimal T_hot_in, LMTD is {delta_T_lm} °C. This leads to a higher heat transfer rate (Q) and "
            "a higher outlet temperature (T_out). Since the flow rates and fluid properties are fixed, the convection coefficients "
            "and U remain constant. The efficiency may slightly decrease at higher T_hot_in due to a larger maximum possible heat "
            f"transfer. The maximum T_out of {max_T_out} °C is achieved at T_hot_in = {T_hot_in} °C, where the temperature "
            "gradient is maximized."
        )
    elif tp_name == "TP3":
        hot_fluid = results["hot_fluids"][max_T_out_idx]
        cp_hot = specific_heat_capacity.get(hot_fluid.lower(), 4186)
        h_external = round(results["h_external"][max_T_out_idx], 2)
        interpretation = (
            "In TP3, we tested different hot fluids to evaluate their impact on the heat exchanger's performance. Each fluid's "
            "specific heat capacity (c_p), density, and viscosity affect the external convection coefficient (h_external) and "
            f"the overall heat transfer coefficient (U). For instance, with {hot_fluid} (c_p = {cp_hot} J/kg·K), h_external is "
            f"{h_external} W/m²·K. Fluids with higher c_p store and transfer more heat, increasing T_out and Q. The internal "
            "convection coefficient remains constant, as the cold fluid is unchanged. The LMTD adjusts slightly based on T_out. "
            f"The maximum T_out of {max_T_out} °C is achieved with {hot_fluid}, due to its superior thermal properties."
        )
    elif tp_name == "TP4":
        dimension = results["dimensions"][max_T_out_idx]
        dimension_type = results.get('dimension_type', 'length')
        A = round(results["A"][max_T_out_idx], 4)
        interpretation = (
            f"In TP4, we varied the pipe {dimension_type} to assess its effect on the heat exchanger's performance. Increasing "
            f"the {dimension_type} expands the heat transfer surface area (A), such as {A} m² at the optimal point, which boosts "
            "the heat transfer rate (Q). For length variations, longer pipes increase residence time, further raising T_out. For "
            "diameter variations, larger diameters alter flow dynamics, affecting the internal convection coefficient. The LMTD "
            "decreases as T_out rises, indicating a smaller temperature gradient. Efficiency improves with larger dimensions due "
            f"to enhanced heat transfer capacity. The maximum T_out of {max_T_out} °C is achieved at {dimension_type} = {dimension} m."
        )
    
    file.write(f'''\\section{{Interpretation}}
{interpretation}\\n''')

def ecriture_conclusion(file, tp_name, results):
    """
    Écrit une conclusion indiquant les paramètres idéaux maximisant T_out.
    
    Parameters:
        file: Fichier LaTeX ouvert
        tp_name (str): Nom du TP
        results (dict): Résultats de la simulation
    """
    max_T_out_idx = np.argmax(results["T_out"])
    max_T_out = round(results["T_out"][max_T_out_idx], 2)

    if tp_name == "TP1":
        optimal_param = f"cold fluid flow rate of {results['flow_rates'][max_T_out_idx]} L/min"
    elif tp_name == "TP2":
        optimal_param = f"hot fluid inlet temperature of {results['T_hot_in'][max_T_out_idx]} °C"
    elif tp_name == "TP3":
        optimal_param = f"hot fluid '{results['hot_fluids'][max_T_out_idx]}'"
    elif tp_name == "TP4":
        optimal_param = f"pipe {results['dimension_type']} of {results['dimensions'][max_T_out_idx]} m"

    conclusion = (
        f"This simulation demonstrates how the varied parameter affects the heat exchanger's performance. "
        f"The optimal configuration, yielding the highest outlet temperature of {max_T_out} °C, is achieved with a {optimal_param}. "
        "These results highlight the importance of optimizing the varied parameter to maximize heat transfer efficiency."
    )
    
    file.write(f'''\\section{{Conclusion}}
{conclusion}\\n''')

def ecriture_template(tp_name, results, params, output_dir, base_filename):
    """
    Écrit le template LaTeX complet avec tous les éléments.
    
    Parameters:
        tp_name (str): Nom du TP
        results (dict): Résultats de la simulation
        params (dict): Paramètres de la simulation
        output_dir (Path): Dossier de sortie
        base_filename (str): Nom de base pour les fichiers (sans extension)
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)
    tex_file = output_dir / f"{base_filename}.tex"
    plo_path = generate_plot(tp_name, results, output_dir)
    
    title = f"Heat Exchanger Simulation Report: {tp_name}"
    author = params.get("author", "User")
    date = time.strftime("%d.%m.%Y")
    
    with open(tex_file, "w", encoding="utf-8") as file:
        file.write(f'''\\documentclass[12pt]{{article}}
\\usepackage[a4paper, total={{7in, 8in}}]{{geometry}}
\\usepackage{{graphicx,amssymb,dsfont,fourier,xcolor,amsmath,ulem,filecontents,MnSymbol,wasysym}}
\\usepackage[utf8]{{inputenc}}
\\graphicspath{{{{{output_dir.as_posix()}/}}}} % Chemin pour les images

\\title{{{title}}}
\\author{{{author}}}
\\date{{{date}}}

\\begin{{document}}
\\maketitle
\\tableofcontents

''')
        ecriture_introduction(file, tp_name)
        file.write(f'''
\\section{{Experimental Parameters}}
''')
        ecriture_itemiz(file, params, results)
        file.write(f'''
\\section{{Methodology}}
The simulation uses the following heat transfer equations:
''')
        ecriture_equation(file, tp_name)
        
        file.write(f'''
\\section{{Results and Discussion}}
''')
        ecriture_graphique(file, tp_name, results, plo_path)
        ecriture_results(file, tp_name, results)
        
        ecriture_interpretation(file, tp_name, results, params)
        ecriture_conclusion(file, tp_name, results)
        
        file.write(f'''
\\end{{document}}
''')
    
    try:
        result = subprocess.run(["pdflatex", "-interaction=nonstopmode", "-output-directory", str(output_dir), str(tex_file)], capture_output=True, text=True)
        pdf_file = output_dir / f"{base_filename}.pdf"
        if not pdf_file.exists():
            messagebox.showerror("Erreur", f"Échec de la compilation LaTeX :\n{result.stderr}")
            return None
        return str(pdf_file), str(tex_file), str(plo_path)
    except FileNotFoundError:
        messagebox.showerror("Erreur", "MiKTeX (pdflatex) n'est pas installé ou n'est pas dans le PATH.\nVérifiez votre installation MiKTeX.")
        return None
    finally:
        for ext in [".aux", ".log", ".out", ".toc"]:
            aux_file = output_dir / f"{base_filename}{ext}"
            if aux_file.exists():
                aux_file.unlink()

def write_tex(tp_name, results, params):
    """
    Fonction principale pour générer le rapport PDF, LaTeX et PNG dans un dossier.
    """
    folder_path = filedialog.askdirectory(
        title="Choisir un dossier pour sauvegarder le rapport"
    )
    if not folder_path:
        messagebox.showwarning("Annulé", "Génération du rapport annulée.")
        return

    base_name = f"rapport_{tp_name.lower()}_{time.strftime('%Y%m%d')}"
    output_dir = Path(folder_path) / base_name
    counter = 1
    while output_dir.exists():
        output_dir = Path(folder_path) / f"{base_name}_{counter}"
        counter += 1

    result = ecriture_template(tp_name, results, params, output_dir, f"rapport_{tp_name.lower()}")
    if result:
        pdf_path, tex_path, png_path = result
        messagebox.showinfo("Succès", f"Rapport généré dans : {output_dir}\n"
                                     f"- PDF : {pdf_path}\n"
                                     f"- LaTeX : {tex_path}\n"
                                     f"- Graphique : {png_path}")