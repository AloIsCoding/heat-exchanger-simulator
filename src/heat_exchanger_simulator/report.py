import time
import os
import subprocess
from pathlib import Path
import pandas as pd
from plotting import generate_plot

def ecriture_graphique(file, tp_name, results, plot_path):
    """
    Écrit un graphique dans le fichier LaTeX en utilisant une image PNG générée.
    
    Parameters:
        file: Fichier LaTeX ouvert
        tp_name (str): Nom du TP (ex. "TP1")
        results (dict): Résultats de la simulation
        plot_path (str): Chemin vers l’image PNG du graphe
    """
    caption = f"Simulation results for {tp_name}"
    label = f"fig:{tp_name.lower()}_results"
    file.write(f'''\\begin{{figure}}[htb!]
        \\centering
        \\includegraphics[width=0.8\\textwidth]{{{Path(plot_path).name}}}
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

def ecriture_itemiz(file, params):
    """
    Écrit une liste des paramètres dans une liste itemize.
    """
    file.write(f'''\\begin{{itemize}}
    \\setlength\\itemsep{{-0.5em}}
    \\item Cold Fluid: {params.get('fluid', '')}
    \\item Hot Fluid: {params.get('hot_fluid', '')}
    \\item Material: {params.get('material', '')}
    \\item Cold Inlet Temperature: {params.get('T_cold_in', '')}°C
    \\item Hot Inlet Temperature: {params.get('T_hot_in', '')}°C
    \\item Pipe Length: {params.get('pipe_length', '')} m
    \\item Pipe Diameter: {params.get('pipe_diameter', '')} m
\\end{{itemize}}\\n''')

def ecriture_template(tp_name, results, params):
    """
    Écrit le template LaTeX complet avec tous les éléments.
    
    Parameters:
        tp_name (str): Nom du TP
        results (dict): Résultats de la simulation
        params (dict): Paramètres de la simulation
    """
    output_dir = Path("reports")
    output_dir.mkdir(exist_ok=True)
    tex_file = output_dir / "rapport.tex"
    
    plot_path = generate_plot(tp_name, results, output_dir)
    
    title = f"Heat Exchanger Simulation Report: {tp_name}"
    author = "User"
    date = time.strftime("%d.%m.%Y")
    
    with open(tex_file, "w", encoding="utf-8") as file:
        file.write(f'''\\documentclass[12pt]{{article}}
\\usepackage[a4paper, total={{7in, 8in}}]{{geometry}}
\\usepackage{{graphicx,amssymb,dsfont,fourier,xcolor,amsmath,ulem,filecontents,MnSymbol,wasysym}}
\\usepackage[utf8]{{inputenc}}

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
        ecriture_itemiz(file, params)
        
        file.write(f'''
\\section{{Methodology}}
The simulation uses the following heat transfer equations:
''')
        ecriture_equation(file, tp_name)
        
        file.write(f'''
\\section{{Results and Discussion}}
''')
        ecriture_graphique(file, tp_name, results, plot_path)
        ecriture_table(file, tp_name, results)
        
        file.write(f'''
\\section{{Conclusion}}
The simulation results show the impact of the varied parameter on the outlet temperature, heat transferred, and efficiency.

\\end{{document}}
''')
    
    try:
        subprocess.run([r"C:\Program Files\MiKTeX\miktex\bin\x64\pdflatex.exe", "-interaction=nonstopmode", "-output-directory", str(output_dir), str(tex_file)], check=False)
    except Exception as e:
        print(f"Erreur de compilation LaTeX : {e}\nverifier votre installation MiKTeX")
    
    for ext in [".aux", ".log", ".out"]:
        aux_file = output_dir / f"rapport{ext}"
        if aux_file.exists():
            aux_file.unlink()

def write_tex(tp_name, results, params):
    """
    Fonction principale pour générer le rapport.
    """
    ecriture_template(tp_name, results, params)

def save_tex():
    """
    fonction dont le but est de faire que le rapport s'enregistre au bon endroit
    """
    script_path = Path(os.path.abspath(__file__)[:-10] + '/reports_test')
    print(script_path) 
    if script_path.exists():
        pass
    else:
        script_path.mkdir()
    
print(save_tex())