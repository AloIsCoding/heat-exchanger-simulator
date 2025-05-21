import time
import os
import subprocess
from pathlib import Path
import pandas as pd
from plotting import generate_plot
import tkinter as tk
from tkinter import filedialog, messagebox

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

def ecriture_table(file, tp_name, results):
    """
    Écrit une table LaTeX avec les résultats de la simulation.
    
    Parameters:
        file: Fichier LaTeX ouvert
        tp_name (str): Nom du TP
        results (dict): Résultats de la simulation
    """
    if tp_name == "TP1":
        df = pd.DataFrame({
            "Flow Rate (L/min)": results["flow_rates"],
            "Outlet Temp (°C)": [round(t, 2) for t in results["T_out"]],
            "Heat Transferred (W)": [round(q, 2) for q in results["Q"]],
            "Efficiency (%)": [round(e * 100, 2) for e in results["efficiency"]]
        })
        caption = "Results for TP1: Flow Impact"
    elif tp_name == "TP2":
        df = pd.DataFrame({
            "Hot Fluid Temp (°C)": results["T_hot_in"],
            "Outlet Temp (°C)": [round(t, 2) for t in results["T_out"]],
            "Heat Transferred (W)": [round(q, 2) for q in results["Q"]],
            "Efficiency (%)": [round(e * 100, 2) for e in results["efficiency"]]
        })
        caption = "Results for TP2: Temperature Impact"
    elif tp_name == "TP3":
        df = pd.DataFrame({
            "Hot Fluid": results["hot_fluids"],
            "Outlet Temp (°C)": [round(t, 2) for t in results["T_out"]],
            "Heat Transferred (W)": [round(q, 2) for q in results["Q"]],
            "Efficiency (%)": [round(e * 100, 2) for e in results["efficiency"]]
        })
        caption = "Results for TP3: Different Fluids Impact"
    elif tp_name == "TP4":
        df = pd.DataFrame({
            f"{results['dimension_type'].capitalize()} (m)": results["dimensions"],
            "Outlet Temp (°C)": [round(t, 2) for t in results["T_out"]],
            "Heat Transferred (W)": [round(q, 2) for q in results["Q"]],
            "Efficiency (%)": [round(e * 100, 2) for e in results["efficiency"]]
        })
        caption = f"Results for TP4: {results['dimension_type'].capitalize()} Impact"
    
    table_content = "\\begin{tabular}{|l" + "|c" * (len(df.columns) - 1) + "|}\n\\hline\n"
    table_content += " & ".join(df.columns) + " \\\\\n\\hline\n"
    for _, row in df.iterrows():
        table_content += " & ".join(str(val) for val in row) + " \\\\\n\\hline\n"
    table_content += "\\end{tabular}"
    
    file.write(f'''\\begin{{table}}[ht!]
        \\centering
        {table_content}
        \\caption{{{caption}}}
        \\label{{tab:{tp_name.lower()}_results}}
\\end{{table}}\\n''')

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
    
    # Ajouter les paramètres spécifiques à chaque TP
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

    # Ajouter les paramètres calculés (U, Re)
    items.extend([
        f"\\item Overall Heat Transfer Coefficient (U): {results.get('U', ['N/A'])[0]} W/m²·K",
        f"\\item Internal Reynolds Number: {results.get('Re_internal', ['N/A'])[0]} ({results.get('Re_internal_regime', ['Unknown'])[0]})",
        f"\\item External Reynolds Number: {results.get('Re_external', ['N/A'])[0]} ({results.get('Re_external_regime', ['Unknown'])[0]})"
    ])

    file.write(f'''\\begin{{itemize}}
    \\setlength\\itemsep{{-0.5em}}
    {"\n".join(items)}
\\end{{itemize}}\\n''')

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

\\section{{Introduction}}
This report presents the results of the {tp_name} simulation for a heat exchanger.

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
        ecriture_table(file, tp_name, results)
        
        file.write(f'''
\\section{{Conclusion}}
The simulation results show the impact of the varied parameter on the outlet temperature, heat transferred, and efficiency.

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