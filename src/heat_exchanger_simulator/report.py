import time
from pathlib import Path

def ecriture_graphique(file,value,data_file=open("C:/Users/rombe/Desktop/BA4/ppc/projet/data.csv","r",encoding='utf-8')):
    # fonction pour ecrire des graphiques en latex
    # TODO : faire fonctionner les {} 
    # TODO : faire des boucle pour chaque "sample"/ chose donnée par l'utilisateur.trice
    # TODO : definir toutes les chose que l'utilisateur veux 
    # pour sa fonction genre des point , des droites , des regression lin etc

    if ... : # l'utilisateur veux des point ou des courbes ?
        data_you_have_to_plot = "\\addplot[color=red,dashed,domain=0:100]{-0.001*x+0.6259};\\addlegendentry{trend line : $-0.001x+0.6259$ ($R^{2}=0.9411$)}" 
        # TODO il y'a toute les valeurs a opti evidement
    elif ... :
        data_you_have_to_plot = ' \\addplot[color=blue] table [x=A,y=B,col sep=comma]{data_file};'
    else:
        data_you_have_to_plot = '''\\addplot[color=blue,mark=*,]
                    coordinates{""};
                    \\addlegendentry{temperature = 30°}'''
    def_axis =f'''\\begin{"axis"}[xlabel={""},ylabel={""},xmin=0, xmax=100,ymin=0, ymax=1,xtick={"{}"},ytick={"{}"},legend pos=north west,grid,grid style=dashed,]'''
    file.write(f'''\\begin{"figure"}[htb!]
                \\centering
                \\begin{"tikzpicture"}
                \\begin{"axis"}[grid,grid style={"dashed"}]
                \\addplot[color=blue] table [x=A,y=B,col sep=comma]{data_file};
                \\addlegendentry{"sample 1"}
                \\end{"axis"}
                \\end{"tikzpicture"}
                \\caption{""}\\label{""}
        \\end{"figure"}''')
    ...

def ecriture_equation(file,value,data_file):
    # fonction pour ecrire une equation (ptt personalisé ?)
    # TODO : ptt généraliser cette fonction ?
    # TODO : décider de l'équation à écrire
    file.write(f'''\\begin{"equation"}\\label{""}
               ...
        \\end{"equation"}\\''')

def ecriture_table(file,value,data_file):
    '''\\begin{table}[ht!]
        \\centering
        \\begin{tabular}{|c||c|c||c| }
            \\hline
            {}&{}&{}&{}\\
            \\hline
            Absorption at 510nm &0.5316&0.4523&$\\setminus$\\
            \\hline
            concentration [mmol/L]&0.05449&0.04636&0.0504$\\pm$0.004\\
            \\hline
        \\end{tabular}
        \\caption{standars solution and measurate value for unknow sample}\\label{table:6}
    \\end{table}\\'''
    ...

def ecritue_doc_extern(file,value,data_file):
    file.write(f'''\\begin{'figure'}[ht!]
            \\centering
            \\caption{''}
            \\includegraphics{''}
            \\label{''}
        \\end{'figure'}''')
    ...
    
def ecriture_itemiz(file,value,data_file):
    file.write(f'''\\begin{'itemize'}
            \\setlength\\itemsep{'-0.5em'}
            \\item[+] {...}
            \\item[+] {...}
            \\item[+] {...}
            \\item[+] {...}
        \\end{'itemize'}''')
    ...

def ecriture_template(file):
    title = str(input("title of the repport : "))
    autor = str(input("autor : "))
    date = time.strftime("%%d.%m.%Y")
    file.write('''\\documentclass[12pt]{article}
\\usepackage[a4paper, total={7in, 8in}]{geometry}
\\usepackage{graphicx,amssymb,dsfont,fourier,xcolor,amsmath,ulem,filecontents,MnSymbol,wasysym}
\\usepackage[colorlinks]{hyperref}
\\hypersetup{colorlinks=True,allcolors=black}
\\usepackage[noabbrev, nameinlink]{cleveref} % to be loaded after hyperref
\\usepackage{pgfplots}\\pgfplotsset{width=12cm,compat=1.9}
\\usepackage[utf8]{inputenc}

\\title{}
\\author{}
\\date{}

\\begin{document}
\\maketitle
\\tableofcontents

\\section{introduction}

\\section{experimental part}

\\section{results and disscution}

\\section{conclusion}

\\section{bibliographie}

\\end{document}''')


def write_tex():
    x = Path('~/report')
    # TODO : demander a l'utilisateur ou est ce qu'il souhaite enregistrer son fichier
    if not x.exists():
        x.mkdir()
    f1 = open("projet/report/rapport.tex","w",encoding='utf-8')
    f2 = open("projet/template_rapport.tex","r",encoding='utf-8')
    for line in f2.readlines():
        f1.write(line)
    f2.close
    f1.close()


write_tex()