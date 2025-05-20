# 🧪 Heat Exchanger Simulator

## 🔍 Overview

This project is a Python-based heat exchanger simulator designed for educational purposes in chemistry and chemical engineering at EPFL. It models thermal exchanges between two fluids using principles of heat transfer and fluid dynamics, focusing on **co-current and counter-current configurations**.

The tool aims to deepen understanding of heat exchanger behavior by allowing users to customize parameters such as:

- Flow rates  
- Fluid types  
- Pipe dimensions  
- Materials  

It also generates **professional lab reports** in PDF format for analysis.

---

## 👥 Authors

- Robin Elkaim – BSc in Chemistry and Chemical Engineering, EPFL  
- Roméo Bedague – BSc in Chemistry and Chemical Engineering, EPFL  
- Aloïsse Dantant-Cochet – BSc in Chemistry and Chemical Engineering, EPFL

---

## ⚙️ Functionalities

The simulator supports four practical sessions (TPs) to study the impact of:

- **TP1**: Cold fluid flow rate on outlet temperature  
- **TP2**: Hot fluid temperature on outlet temperature  
- **TP3**: Hot fluid choice on outlet temperature  
- **TP4**: Pipe dimensions (length or diameter) on outlet temperature  

### ✅ Key Features

- Calculation of key parameters:  
  - Heat transfer rate (Q)  
  - Overall heat transfer coefficient (U)  
  - Logarithmic mean temperature difference (ΔT<sub>lm</sub>)  
  - Heat exchanger efficiency  

- Interactive GUI built with **Tkinter**  
- Built-in database of fluid and material properties  
- **Automated LaTeX-based PDF report** generation  
- Result visualization with **Matplotlib**  

---

## 📦 Installation

1. **Clone the repository**  
```bash
git clone https://github.com/your-repo/heat-exchanger-simulator.git
```

2. **Navigate to the project directory**  
```bash
cd heat-exchanger-simulator
```

3. **Install the required dependencies**  
```bash
pip install -r requirements.txt
```

---

## 📋 Requirements

- Python **3.8+**
- Required Python packages:
  - `numpy`
  - `matplotlib`
  - `pandas`
  - `pillow`
- **LaTeX distribution** (e.g., MiKTeX or TeX Live) for PDF generation
- Optional: image files for the GUI:
  - `epfl_logo.png`
  - `exchanger.png`

---

## ▶️ Usage

To launch the simulator:

```bash
python src/heat_exchanger_simulator/interface.py
```

### From the GUI:

1. Select a TP from the dropdown menu  
2. Configure parameters (fluids, flow rates, dimensions, etc.)  
3. Click **"Run Simulation"** to view results  
4. Click **"Download Report"** to save a PDF lab report  

➡️ For a full example, check the Jupyter notebook:  
`notebooks/exploration.ipynb`

---

## 📁 Project Structure

```
heat-exchanger-simulator/
├── src/
│   └── heat_exchanger_simulator/
│       ├── __init__.py
│       ├── core.py          # Core simulation logic
│       ├── utils.py         # Fluid and material properties
│       ├── interface.py     # GUI with Tkinter
│       ├── simulation.py    # Animations (to be implemented)
│       ├── report.py        # PDF report generation
├── notebooks/
│   └── exploration.ipynb    # Pedagogical example
├── tests/
│   ├── test_core.py         # Unit tests for core
│   ├── test_utils.py        # Unit tests for utils
├── README.md
```

---

## 🖼 Interface

The GUI includes:

- TP selection dropdown  
- Fields for entering parameters (flow, temperature, etc.)  
- Image of the heat exchanger  
- Progress bar  
- Buttons to:
  - Run simulations  
  - Download reports  
  - Change TP  

---

## 🙏 Acknowledgments

This project was developed as part of the **EPFL course: Practical Programming for Chemistry**.  
Special thanks to the teaching staff for their support and guidance.
