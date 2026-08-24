# Beam Analysis Solver

A Python-based beam analysis program for calculating support reactions, Shear Force Diagrams (SFD), and Bending Moment Diagrams (BMD) for statically determinate beams.

This project was developed as a personal learning project alongside my Mechanical and Aerospace Engineering coursework. The goal was to build a beam solver from first principles while developing practical skills in numerical methods, object-oriented programming, input validation, data modelling, visualization, and GUI development.

## Current Release — V2.2.0

V2.2.0 is the current stable release and represents the transition from a command-line beam solver into a functional graphical analysis tool.

### Features

* Support reaction calculation using static equilibrium
* Shear Force Diagram (SFD) generation
* Bending Moment Diagram (BMD) generation
* Point loads
* Concentrated applied moments
* Uniformly Distributed Loads (UDLs)
* Uniformly Varying Loads (UVLs)
* Pinned and roller supports
* Interactive graphical user interface
* Live input validation
* Numerical SFD/BMD calculation
* Matplotlib-based engineering visualization
* Automatic identification of maximum absolute shear force
* Automatic identification of maximum absolute bending moment
* Modular, object-oriented beam architecture

## Example Output

The V2.2 GUI combines beam inputs, analysis results, and engineering diagrams into a single interface.

![Beam Analysis Solver GUI](Screenshot%202026-08-13%20214646.png)

## How It Works

The solver uses an event-based beam model to represent the physical entities acting on a beam.

### Beam Model

The beam is represented using:

* **Beam** — stores beam geometry and all applied events
* **Point** — represents discrete locations along the beam
* **Point Events** — point loads, applied moments, supports, and reactions
* **Distributed Events** — UDLs and UVLs

Distributed loads are converted into equivalent resultant forces at their centroid locations for reaction calculations.

### Analysis Pipeline

The general analysis process is:

```text
User Input
    ↓
Input Validation
    ↓
Beam Construction
    ↓
Equivalent Load Representation
    ↓
Support Reaction Calculation
    ↓
SFD / BMD Calculation
    ↓
Numerical Results
    ↓
Engineering Visualization
```

The GUI provides the interface for entering beam geometry, loads, moments, distributed loads, and support locations before passing the validated data into the beam model and solver.

## Project Structure

```text
Beam-Analysis-Solver/
│
├── main.py              # Program entry point
├── gui.py               # PyQt-based graphical user interface
├── beam.py              # Beam, point, load, support, and event classes
├── get_beam_data.py     # Beam construction and input data handling
├── solvers.py           # Reaction, SFD, and BMD calculations
├── plotting.py          # Beam, SFD, and BMD visualization
├── Validation.py        # Input and analysis validation
├── .gitignore           # Git ignore rules
└── README.md            # Project documentation
```

The code is intentionally divided into separate modules so that the beam model, numerical solver, validation, plotting, and GUI can be developed and tested independently.

## Requirements

* Python 3.12+
* NumPy
* Matplotlib
* PyQt5 or PyQt6

### Installation

Clone the repository and create a virtual environment:

```bash
git clone https://github.com/vvidhukrishna/Beam-Analysis-Solver.git
cd Beam-Analysis-Solver
python -m venv .venv
```

Activate the virtual environment.

**Windows:**

```bash
.venv\Scripts\activate
```

Install the required packages:

```bash
pip install numpy matplotlib PyQt5
```

## Running the Application

Launch the graphical interface with:

```bash
python gui.py
```

The application opens with the beam input panel on the left and the analysis visualization on the right.

Enter the beam geometry, loading, moments, and support locations, then select **Calculate & Plot** to perform the analysis.

## Supported Loading

### Point Loads

Point loads can be applied at specified beam locations.

### Applied Moments

Concentrated moments can be applied at discrete beam locations.

### Uniformly Distributed Loads

UDLs can be defined using:

```text
start_x, end_x, intensity
```

### Uniformly Varying Loads

UVLs can be defined using:

```text
start_x, end_x, w1, w2
```

where `w1` and `w2` define the load intensities at the beginning and end of the load span.

## Engineering Scope

The current solver is designed for **statically determinate beam problems**.

V2.2 currently focuses on beams with:

* Two supports
* Pinned and roller support conditions
* Point loads
* Applied moments
* Uniformly distributed loads
* Uniformly varying loads

The current release does not yet implement cantilever beam analysis or a generalized support system.

## Development History

### V1.0.0

The first version established the core beam analysis functionality:

* Static support reaction calculation
* SFD generation
* BMD generation
* Point loads
* Applied moments
* Basic visualization
* Command-line input
* Object-oriented beam architecture

### V2.1.0

The solver was extended with distributed loading and improved visualization:

* Uniformly Distributed Loads
* Uniformly Varying Loads
* Improved beam visualization
* Improved numerical SFD/BMD calculation

### V2.2.0

The project evolved into a functional graphical analysis application:

* PyQt GUI
* Integrated beam input
* Live input validation
* Integrated reaction calculation
* Integrated SFD/BMD calculation
* Engineering-style visualization
* Analysis result summary
* Improved modular architecture

## Roadmap

### V3 — In Development

The next development phase will focus on expanding the solver and improving the user experience.

Planned features include:

* Cantilever beam analysis
* Improved GUI and user interaction
* Further UI/UX refinement
* Expanded beam/support modelling

Future versions may extend the solver toward additional beam configurations, loading conditions, analysis capabilities, and export functionality.

## Why I Built This

Rather than solving beam problems manually every time, I wanted to build a solver from first principles.

The project started as a way to better understand structural analysis while learning Python. It gradually developed into a larger software engineering project involving object-oriented design, numerical computation, validation, visualization, GUI development, version control, and testing.

The aim is not simply to automate beam calculations, but to understand how an engineering problem can be translated into a structured computational model and then developed into a usable engineering tool.

## License

This project is currently intended as a personal learning and engineering portfolio project.
