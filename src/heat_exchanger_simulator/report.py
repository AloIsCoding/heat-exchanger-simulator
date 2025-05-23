import time
import os
import subprocess
from pathlib import Path
import numpy as np
from plotting import generate_plot
import tkinter as tk
from tkinter import filedialog, messagebox
from utils import specific_heat_capacity


def demander_nom_fichier(tp_name, results, params):
    def valider(tp_name, results, params):
        nonlocal nom_de_fichier
        nom_de_fichier = entry.get()
        no.destroy()  # Ferme la fenêtre une fois validé
        save_folder(tp_name, results, params,nom_de_fichier)


    nom_de_fichier = None  # Valeur par défaut
    no = tk.Tk()
    no.geometry("400x250")
    no.title("Nom du fichier")

    label = tk.Label(no, text="Entrez le nom du fichier (sans extension) :")
    label.pack(pady=10)

    entry = tk.Entry(no, width=40)
    entry.pack(pady=10)

    bouton_valider = tk.Button(no, text="Valider", command=lambda :valider(tp_name, results, params))
    bouton_valider.pack(pady=10)

    no.mainloop()



def ecriture_graphique(file, tp_name, results, plo_path):
    """
    Write a graphic to the LaTeX file using a generated PNG image.
    
    Args:
        file: Open LaTeX file.
        tp_name (str): Name of the TP (e.g., "TP1").
        results (dict): Simulation results.
        plo_path (str): Path to the PNG plot.
    """
    caption = f"Simulation results for {tp_name} [H]"
    label = f"fig:{tp_name.lower()}_results"
    file.write(f'''\\begin{{figure}}[htb!]
        \\centering
        \\includegraphics[width=0.8\\textwidth]{{{Path(plo_path).name}}}
        \\caption{{{caption}}}
        \\label{{{label}}}
\\end{{figure}}\n''')

def ecriture_results(file, tp_name, results):
    """
    Write optimal results (maximizing T_out) as sentences and a qualitative analysis.
    
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
For the optimal parameters maximizing the outlet temperature, the simulation yields the following results:
\\begin{{itemize}}
    \\item The outlet temperature is: {T_out} °C
    \\item The heat transferred is: {Q} W
    \\item The efficiency is: {efficiency} \\%
    \\item The overall heat transfer coefficient (U) is: {U} W/m²·K
    \\item The logarithmic mean temperature difference (LMTD) is: {delta_T_lm} °C
    \\item The internal convection coefficient is: {h_internal} W/m²·K
    \\item The external convection coefficient is: {h_external} W/m²·K
    \\item The heat transfer surface area is: {A} m²
\\end{{itemize}}\n''')

    # Qualitative Analysis
    file.write(f'''\\subsection{{Qualitative Analysis}}\n''')
    if tp_name == "TP1":
        analysis = (
            "The results show that increasing the cold fluid flow rate enhances the heat transfer rate due to a higher internal convection coefficient, driven by an increased Reynolds number. "
            "However, beyond a certain point, the outlet temperature decreases because the fluid spends less time in the exchanger, reducing the heat absorbed. "
            "The optimal flow rate balances these effects, maximizing the outlet temperature while maintaining efficient heat transfer."
        )
    elif tp_name == "TP2":
        analysis = (
            "Higher hot fluid inlet temperatures increase the outlet temperature and heat transfer rate by enlarging the logarithmic mean temperature difference, which drives heat transfer. "
            "The efficiency may slightly decrease at very high temperatures due to a larger maximum possible heat transfer, but the overall performance improves with greater temperature gradients."
        )
    elif tp_name == "TP3":
        analysis = (
            "Different hot fluids affect performance through their thermophysical properties, such as specific heat capacity and viscosity. "
            "Fluids with higher specific heat capacities transfer more heat, increasing the outlet temperature and heat transfer rate. "
            "The choice of fluid significantly influences the exchanger's effectiveness, with optimal fluids balancing high heat capacity and favorable flow characteristics."
        )
    elif tp_name == "TP4":
        analysis = (
            "Varying pipe dimensions impacts the heat transfer surface area and flow dynamics. Longer pipes or larger diameters increase the surface area, enhancing heat transfer and outlet temperature."
            "However, larger diameters may reduce flow velocity, affecting convection coefficients. The optimal dimension maximizes heat transfer while maintaining efficient flow regimes."
        )
    file.write(f'{analysis}\n')

def ecriture_equation(file, tp_name):
    """
    Write the key equations used in the simulation with explanations.
    
    Args:
        file: Open LaTeX file.
        tp_name (str): Name of the TP.
    """
    file.write(f'''The simulation relies on the following key equations to model the heat exchanger's performance:

\\begin{{itemize}}
    \\item \\textbf{{Heat transfer by the cold fluid}}:
    \\begin{{equation}}\\label{{eq:{tp_name.lower()}_heat_transfer}}
    Q = \\dot{{m}} \\cdot c_p \\cdot (T_{{out}} - T_{{in}})
    \\end{{equation}}
    This equation calculates the heat transfer rate ($Q$) based on the mass flow rate ($\\dot{{m}}$), specific heat capacity ($c_p$), and temperature difference between the outlet ($T_{{out}}$) and inlet ($T_{{in}}$) of the cold fluid. It quantifies the energy absorbed by the cold fluid.

    \\item \\textbf{{Overall heat transfer}}:
    \\begin{{equation}}\\label{{eq:{tp_name.lower()}_overall_transfer}}
    Q = U \\cdot A \\cdot \\Delta T_{{lm}}
    \\end{{equation}}
    This equation computes the heat transfer rate ($Q$) using the overall heat transfer coefficient ($U$), the heat transfer surface area ($A$), and the logarithmic mean temperature difference ($\\Delta T_{{lm}}$). It describes the total heat exchanged between the fluids.

    \\item \\textbf{{Logarithmic mean temperature difference (LMTD)}}:
    \\begin{{equation}}\\label{{eq:{tp_name.lower()}_lmtd}}
    \\Delta T_{{lm}} = \\frac{{\\Delta T_1 - \\Delta T_2}}{{\\ln(\\Delta T_1 / \\Delta T_2)}}
    \\end{{equation}}
    The LMTD accounts for the temperature gradient along the exchanger, where $\\Delta T_1$ and $\\Delta T_2$ are the temperature differences at the two ends. It is critical for calculating the driving force for heat transfer in counter-flow exchangers.

    \\item \\textbf{{Reynolds number}}:
    \\begin{{equation}}\\label{{eq:{tp_name.lower()}_reynolds}}
    Re = \\frac{{\\rho v D}}{{\\mu}}
    \\end{{equation}}
    The Reynolds number ($Re$) determines the flow regime (laminar or turbulent) using fluid density ($\\rho$), velocity ($v$), characteristic length ($D$), and dynamic viscosity ($\\mu$). It influences the convection coefficients and heat transfer efficiency.

    \\item \\textbf{{Nusselt number (Dittus-Boelter correlation)}}:
    \\begin{{equation}}\\label{{eq:{tp_name.lower()}_nusselt}}
    Nu = 0.023 \\cdot Re^{{0.8}} \\cdot Pr^{{0.4}}
    \\end{{equation}}
    The Nusselt number ($Nu$) relates to the convection coefficient ($h$) via $h = Nu \\cdot k / D$, where $k$ is the thermal conductivity and $D$ is the diameter. The Dittus-Boelter correlation is used for turbulent flow to estimate $h$, which affects $U$.
\\end{{itemize}}\n''')

def ecriture_itemiz(file, params, results):
    """
    Write a list of parameters in an itemize list, including user inputs and defaults.
    
    Args:
        file: Open LaTeX file.
        params (dict): Simulation parameters.
        results (dict): Simulation results.
    """
    # Default values
    defaults = {
        'fluid': 'water',
        'hot_fluid': 'water',
        'material': 'stainless steel',
        'T_cold_in': 20,
        'T_hot_in': 50,
        'pipe_length': 2,
        'pipe_diameter': 0.1,
        'pipe_thickness': 0.005,
        'gap': 0.01,
        'flow_cold': 10,
        'flow_hot': 10,
        'T_hot_start': 50,
        'T_hot_end': 100,
        'T_hot_steps': 20,
        'flow_start': 5,
        'flow_end': 15,
        'flow_steps': 10,
        'dim_start': 0.05,
        'dim_end': 0.15,
        'dim_steps': 10,
        'dimension_type': 'length'
    }
    
    # Nettoyer les paramètres pour éviter les caractères problématiques
    safe_params = {k: str(params.get(k, defaults.get(k, 'N/A'))).replace('_', ' ').replace('%', '\\%').replace('#', '\\#') for k in defaults.keys()}
    
    items = [
        f"\\item Cold Fluid: {safe_params['fluid']}{' (default)' if 'fluid' not in params else ''}",
        f"\\item Hot Fluid: {safe_params['hot_fluid']}{' (default)' if 'hot_fluid' not in params else ''}",
        f"\\item Material: {safe_params['material']}{' (default)' if 'material' not in params else ''}",
        f"\\item Cold Inlet Temperature: {safe_params['T_cold_in']} °C{' (default)' if 'T_cold_in' not in params else ''}",
        f"\\item Hot Inlet Temperature: {safe_params['T_hot_in']} °C{' (default)' if 'T_hot_in' not in params else ''}",
        f"\\item Pipe Length: {safe_params['pipe_length']} m{' (default)' if 'pipe_length' not in params else ''}",
        f"\\item Pipe Diameter: {safe_params['pipe_diameter']} m{' (default)' if 'pipe_diameter' not in params else ''}",
        f"\\item Pipe Thickness: {safe_params['pipe_thickness']} m{' (default)' if 'pipe_thickness' not in params else ''}",
        f"\\item Gap: {safe_params['gap']} m{' (default)' if 'gap' not in params else ''}",
    ]
    
    if "flow_start" in params or 'flow_start' in safe_params:
        items.append(f"\\item Start Flow Rate: {safe_params['flow_start']} L/min{' (default)' if 'flow_start' not in params else ''}")
        items.append(f"\\item End Flow Rate: {safe_params['flow_end']} L/min{' (default)' if 'flow_end' not in params else ''}")
        items.append(f"\\item Flow Steps: {safe_params['flow_steps']}{' (default)' if 'flow_steps' not in params else ''}")
    if "flow_cold" in params or 'flow_cold' in safe_params:
        items.append(f"\\item Cold Flow Rate: {safe_params['flow_cold']} L/min{' (default)' if 'flow_cold' not in params else ''}")
    if "flow_hot" in params or 'flow_hot' in safe_params:
        items.append(f"\\item Hot Flow Rate: {safe_params['flow_hot']} L/min{' (default)' if 'flow_hot' not in params else ''}")
    if "T_hot_start" in params or 'T_hot_start' in safe_params:
        items.append(f"\\item Start Hot Temperature: {safe_params['T_hot_start']} °C{' (default)' if 'T_hot_start' not in params else ''}")
        items.append(f"\\item End Hot Temperature: {safe_params['T_hot_end']} °C{' (default)' if 'T_hot_end' not in params else ''}")
        items.append(f"\\item Hot Temperature Steps: {safe_params['T_hot_steps']}{' (default)' if 'T_hot_steps' not in params else ''}")
    if "dimension_type" in params or 'dimension_type' in safe_params:
        items.append(f"\\item Dimension Type: {safe_params['dimension_type']}{' (default)' if 'dimension_type' not in params else ''}")
        items.append(f"\\item Start Dimension: {safe_params['dim_start']} m{' (default)' if 'dim_start' not in params else ''}")
        items.append(f"\\item End Dimension: {safe_params['dim_end']} m{' (default)' if 'dim_end' not in params else ''}")
        items.append(f"\\item Dimension Steps: {safe_params['dim_steps']}{' (default)' if 'dim_steps' not in params else ''}")

    items.extend([
        f"\\item Average Overall Heat Transfer Coefficient (U): {round(np.mean(results.get('U', [0])), 2)} W/m²·K",
        f"\\item Average Internal Reynolds Number: {round(np.mean(results.get('Re_internal', [0])), 2)} ({results.get('Re_internal_regime', ['Unknown'])[0]})",
        f"\\item Average External Reynolds Number: {round(np.mean(results.get('Re_external', [0])), 2)} ({results.get('Re_external_regime', ['Unknown'])[0]})"
    ])

    file.write(f'''\\begin{{itemize}}
    \\setlength\\itemsep{{-0.5em}}
    {"\n".join(items)}
    \\end{{itemize}}\n''')

def ecriture_introduction(file, tp_name):
    """
    Write a professional introduction with context and specific objectives.
    
    Args:
        file: Open LaTeX file.
        tp_name (str): Name of the TP.
    """
    context = (
        "Heat exchangers are essential devices in industrial and engineering applications, facilitating efficient thermal energy transfer between two fluids without mixing. "
        "Widely used in power plants, HVAC systems, and chemical processing, they optimize energy efficiency by leveraging temperature gradients. "
        "This simulation focuses on a counter-flow concentric tube heat exchanger, where fluids flow in opposite directions to maximize heat transfer efficiency."
    )
    
    if tp_name == "TP1":
        objective = (
            "The objective of TP1 is to study the effect of the cold fluid flow rate on the heat exchanger's performance. "
            "By varying the flow rate while keeping other parameters constant (e.g., pipe dimensions, fluid properties, hot fluid conditions), we aim to evaluate its impact on the outlet temperature, heat transfer rate, and efficiency. "
            "This experiment highlights the trade-off between enhanced convection at higher flow rates and reduced residence time, which affects the heat absorbed."
        )
    elif tp_name == "TP2":
        objective = (
            "The objective of TP2 is to investigate the influence of the hot fluid inlet temperature on the heat exchanger's performance. "
            "By adjusting the inlet temperature with fixed flow rates and pipe geometry, we seek to assess its effect on the outlet temperature, heat transfer rate, and efficiency. "
            "This experiment emphasizes the role of the temperature difference as the primary driving force for heat transfer."
        )
    elif tp_name == "TP3":
        objective = (
            "The objective of TP3 is to analyze the impact of different hot fluids on the heat exchanger's performance. "
            "By testing fluids with varying thermophysical properties (e.g., specific heat capacity, viscosity), we aim to identify which fluid maximizes the outlet temperature and heat transfer rate. "
            "This experiment underscores the critical role of fluid selection in optimizing heat exchanger design."
        )
    elif tp_name == "TP4":
        objective = (
            "The objective of TP4 is to examine the effect of pipe dimensions (length or diameter) on the heat exchanger's performance. "
            "By varying one dimension while keeping other parameters constant, we aim to understand its influence on the outlet temperature, heat transfer rate, and efficiency. "
            "This experiment illustrates the importance of geometry in enhancing heat transfer efficiency."
        )
    
    file.write(f'''\\section{{Introduction}}
{context}

{objective}\n''')

def ecriture_conclusion(file, tp_name, results):
    """
    Write a conclusion indicating the optimal parameters maximizing T_out.
    
    Args:
        file: Open LaTeX file.
        tp_name (str): Name of the TP.
        results (dict): Simulation results.
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
        optimal_param = f"pipe {results.get('dimension_type', 'length')} of {results['dimensions'][max_T_out_idx]} m"

    conclusion = (
        f"This simulation demonstrates how the varied parameter affects the heat exchanger's performance. "
        f"The optimal configuration, yielding the highest outlet temperature of {max_T_out} °C, is achieved with a {optimal_param}. "
        "These results highlight the importance of optimizing the varied parameter to maximize heat transfer efficiency."
    )
    
    file.write(f'''\\section{{Conclusion}}
{conclusion}\n''')

def ecriture_template(tp_name, results, params, output_dir, base_filename):
    """
    Write the complete LaTeX template with all elements.
    
    Args:
        tp_name (str): Name of the TP.
        results (dict): Simulation results.
        params (dict): Simulation parameters.
        output_dir (Path): Output directory.
        base_filename (str): Base filename (without extension).
    
    Returns:
        tuple: Paths to the generated PDF, LaTeX, and PNG files, or None if failed.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)
    tex_file = output_dir / f"{base_filename}.tex"
    
    try:
        plo_path = generate_plot(tp_name, results, output_dir)
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
\\section{{Experimental Setup}}
The following parameters were used in the simulation, with default values applied where user input was not provided:
''')
            ecriture_itemiz(file, params, results)
            file.write(f'''
\\section{{Methodology}}
''')
            ecriture_equation(file, tp_name)
            
            file.write(f'''
\\section{{Results and Discussion}}
''')
            ecriture_graphique(file, tp_name, results, plo_path)  # Correction : ajout de plo_path
            ecriture_results(file, tp_name, results)
            
            ecriture_conclusion(file, tp_name, results)
            
            file.write(f'''
\\end{{document}}
''')
    except Exception as e:
        messagebox.showerror("Erreur", f"Échec de l'écriture du fichier LaTeX : {str(e)}")
        return None
    
    try:
        # Utiliser encoding='utf-8' avec errors='replace' pour gérer les caractères problématiques
        result = subprocess.run(
            ["pdflatex", "-interaction=nonstopmode", "-output-directory", str(output_dir), str(tex_file)],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            check=True
        )
        pdf_file = output_dir / f"{base_filename}.pdf"
        if not pdf_file.exists():
            messagebox.showerror("Erreur", f"Échec de la compilation LaTeX :\n{result.stderr}")
            return None
        return str(pdf_file), str(tex_file), str(plo_path)
    except FileNotFoundError:
        messagebox.showerror("Erreur", "MiKTeX (pdflatex) n'est pas installé ou n'est pas dans le PATH.\nVérifiez votre installation MiKTeX.")
        return None
    except subprocess.CalledProcessError as e:
        # Afficher la sortie avec encodage nettoyé
        stderr_cleaned = e.stderr.encode('utf-8', errors='replace').decode('utf-8')
        messagebox.showerror("Erreur", f"Erreur lors de la compilation LaTeX :\n{stderr_cleaned}")
        return None
    finally:
        # Nettoyage des fichiers auxiliaires
        for ext in [".aux", ".log", ".out", ".toc"]:
            aux_file = output_dir / f"{base_filename}{ext}"
            if aux_file.exists():
                try:
                    aux_file.unlink()
                except Exception:
                    pass

def write_tex(tp_name, results, params):
    """
    Generate a LaTeX report and prompt the user to save it.
    
    Args:
        tp_name (str): Name of the TP.
        results (dict): Simulation results.
        params (dict): Simulation parameters.
    """
    filename = demander_nom_fichier(tp_name, results, params)
    


def save_folder(tp_name, results, params,file_name):
    root = tk.Tk()
    root.withdraw()


    output_dir = filedialog.asksaveasfilename(title=f"Select Output Directory for {tp_name} Report")
    if not output_dir:
        messagebox.showinfo("Annulé",  "Le rapport n'a pas été généré.")
        root.destroy()
        return
    
    base_filename = tp_name.lower()
    result = ecriture_template(tp_name, results, params, output_dir, base_filename,file_name)
    
    if result:
        pdf_path, _, _ = result
        messagebox.showinfo("Succès", f"Rapport généré avec succès : {pdf_path}")
    root.destroy()