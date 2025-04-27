from PIL import Image, ImageTk
import tkinter as tk
from tkinter import messagebox  # On importe messagebox pour afficher des boîtes de dialogue

def create_main_window():
    w = tk.Tk()
    w.title("Heat Exchanger Simulator")
    w.geometry("800x600")  # Ajuste la taille de la fenêtre
    w.config(bg="#f0f0f0")  # Donne une couleur de fond plus moderne

    # Charger l'image du logo EPFL avec Pillow et ajuster la taille
    img = Image.open("src/heat_exchanger_simulator/epfl_logo.png")  # Remplace par le bon chemin de ton logo
    img = img.resize((100, 60), Image.Resampling.LANCZOS)  # Taille du logo plus adaptée, largeur 100px, hauteur 60px
    logo = ImageTk.PhotoImage(img)

    # Afficher l'image du logo dans l'interface en haut à gauche
    label_logo = tk.Label(w, image=logo, bg="#f0f0f0")  # Fond transparent pour le logo
    label_logo.image = logo  # Référence pour ne pas que l'image disparaisse
    label_logo.place(x=10, y=10)  # Positionne le logo en haut à gauche

    # Ajouter le titre principal "Heat Exchanger Simulator" centré
    title = tk.Label(w, text="Heat Exchanger Simulator", font=('Helvetica', 24, 'bold'), bg="#f0f0f0")
    title.pack(pady=(50, 10))  # Décale le titre avec un padding

    # Ajouter le sous-titre "Choose your TP" centré
    subtitle = tk.Label(w, text="Choose your TP", font=('Helvetica', 16), bg="#f0f0f0")
    subtitle.pack(pady=10)

    # Créer la liste des TP à choisir avec des cases à cocher
    tp_buttons_frame = tk.Frame(w, bg="#f0f0f0")
    tp_buttons_frame.pack(pady=20)

    # Variables pour les cases à cocher (utilisées pour vérifier si l'utilisateur a sélectionné un TP)
    tp1_var = tk.BooleanVar()
    tp2_var = tk.BooleanVar()
    tp3_var = tk.BooleanVar()
    tp4_var = tk.BooleanVar()
    tp5_var = tk.BooleanVar()

    # Boutons de sélection pour les TP
    tp1 = tk.Checkbutton(tp_buttons_frame, text="TP1: Flow Impact", font=('Helvetica', 14), variable=tp1_var, bg="#f0f0f0")
    tp2 = tk.Checkbutton(tp_buttons_frame, text="TP2: Temperature Impact", font=('Helvetica', 14), variable=tp2_var, bg="#f0f0f0")
    tp3 = tk.Checkbutton(tp_buttons_frame, text="TP3: Counterflow vs Parallelflow", font=('Helvetica', 14), variable=tp3_var, bg="#f0f0f0")
    tp4 = tk.Checkbutton(tp_buttons_frame, text="TP4: Different Fluids Impact", font=('Helvetica', 14), variable=tp4_var, bg="#f0f0f0")
    tp5 = tk.Checkbutton(tp_buttons_frame, text="TP5: Lenght and Diameter Impact", font=('Helvetica', 14), variable=tp5_var, bg="#f0f0f0")

    tp1.grid(row=0, column=0, pady=5, sticky="w")
    tp2.grid(row=1, column=0, pady=5, sticky="w")
    tp3.grid(row=2, column=0, pady=5, sticky="w")
    tp4.grid(row=3, column=0, pady=5, sticky="w")
    tp5.grid(row=4, column=0, pady=5, sticky="w")

    # Ajouter un bouton pour passer à la page suivante
    button_continue = tk.Button(w, text="Continue", font=('Helvetica', 16, 'bold'), command=lambda: next_step(tp1_var, tp2_var, tp3_var, tp4_var, tp5_var, w), bg="#4CAF50", fg="white", relief="flat")
    button_continue.pack(pady=30)

    w.mainloop()

def next_step(tp1_var, tp2_var, tp3_var, tp4_var, tp5_var, window):
    # Vérifie si un TP a été sélectionné
    if not (tp1_var.get() or tp2_var.get() or tp3_var.get() or tp4_var.get() or tp5_var.get()):
        # Affiche une boîte de dialogue d'erreur si aucun TP n'est sélectionné
        messagebox.showerror("Error", "Please select a TP before continuing.")
    else:
        # Si un TP est sélectionné, continue avec l'étape suivante
        print("Next step: Proceeding with selected TP.")

# Appeler la fonction pour créer la fenêtre
create_main_window()
