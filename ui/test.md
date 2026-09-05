# Beam Analysis Solver

A Python-based engineering application for analyzing statically determinate beams and generating shear force and bending moment diagrams.

This project began as a personal learning project alongside my Mechanical and Aerospace Engineering studies. The project grew from a command-line beam solver into a modular application with an object-oriented architecture. This documentation aligns with the overarching structure detailed in BMD SFD Solver - Final Report Planning.pdf[cite: 1].

> **Project status: Complete**
>
> This project has reached the final version I originally envisioned and is no longer under active feature development.

## Final Release V3.5.0
V3.5.0 is the final release of Beam Analysis Solver. The final version represents the completed development of the project, including beam analysis, graphical interfaces, and automated testing.

### Features
* Support reaction calculation using static equilibrium
* Shear Force Diagram (SFD) generation
* Bending Moment Diagram (BMD) generation
* Point loads
* Concentrated applied moments
* Uniformly Distributed Loads (UDLs)
* Uniformly Varying Loads (UVLs)
* Simply supported beam analysis
* Cantilever beam analysis
* Pinned, roller, and fixed supports
* Numerical SFD/BMD calculation
* Matplotlib-based engineering visualization
* PyQt5 graphical user interface
* Live input-state validation
* Input and calculation error handling
* Automatic identification of maximum absolute shear force
* Automatic identification of maximum absolute bending moment
* Saved analysis history using JSON
* Reconstruction of previously saved beam analyses
* Loading previously saved SFD/BMD results without rerunning the solver
* Graph export through Matplotlib
* Modular, object-oriented beam architecture
* Automated unit testing with pytest

## Example Output
The final GUI combines beam inputs, analysis results, and engineering diagrams into a single interface.

![Beam Analysis Solver GUI](Screenshot%202026-08-13%20214646.png)

## How It Works
The solver uses an event-based beam model to represent the physical entities acting on a beam.

### Beam Model
The beam is represented using:
* **Beam**: stores beam geometry, discrete points, and distributed events
* **Point**: represents discrete locations along the beam
* **Point Events**: point loads, applied moments, supports, and reactions
* **Distributed Events**: UDLs and UVLs

The beam model separates the physical representation of the problem from the numerical analysis. Distributed loads are represented by their actual loading spans in the beam model.

### Analysis Pipeline
The general analysis process is:

```text
User Input
    ↓
Input Validation
    ↓
Beam Construction
    ↓
Load Representation
    ↓
Equivalent Load Calculation
    ↓
Support Reaction Calculation
    ↓
SFD/BMD Calculation
    ↓
Numerical Results
    ↓
Engineering Visualization
    ↓
Optional History / Graph Export
```
For previously saved analyses, the stored beam data and numerical SFD/BMD arrays can be loaded directly. This allows an old analysis to be reconstructed and plotted without rerunning the numerical solver.

## Supported Beam Systems

### Simply Supported Beams
The solver supports simply supported beams using:
* One pinned support
* One roller support
* Two support reactions

Support locations can be specified along the beam provided the validation requirements are satisfied.

### Cantilever Beams
The solver supports cantilever beams using:
* One fixed support
* Fixed support located at `x = 0`
* One vertical reaction force
* One reaction moment

The cantilever implementation uses static equilibrium to determine both the reaction force and reaction moment.

## Supported Loading

### Point Loads
Point loads can be applied at specified beam locations. Loads are entered in `kN`, with the project's sign convention determining their direction.

### Applied Moments
Concentrated applied moments can be applied at discrete beam locations. Moments are entered in `kNm`.

### Uniformly Distributed Loads (UDLs)
UDLs can be defined using `start x, end x, intensity`.
For example: `0.0, 2.5, -10.0` where the intensity is given in `kN/m`.
The resultant force is calculated from the load intensity multiplied by the loaded span, and the resultant acts at the centroid of the loaded region.

### Uniformly Varying Loads (UVLs)
UVLs can be defined using `start x, end x, w1, w2`.
For example: `5.0, 8.0, 0.0, -20.0` where `w1` and `w2` are the load intensities at the beginning and end of the loaded span, respectively.
The UVL is treated as a linearly varying distributed load. Its resultant force and centroid are calculated from the corresponding trapezoidal loading distribution.

## Engineering Sign Convention
The solver follows the sign convention used throughout the project:
* Positive x direction: to the right
* Positive y direction: upward
* Counter-clockwise moments: positive
* Downward forces: negative

The sign convention is applied consistently when calculating reactions, shear force, and bending moment.

## Graphical User Interface
The application uses a PyQt5 graphical interface with Matplotlib embedded for visualization. The GUI provides:
* Beam input fields
* Point-load and moment inputs
* UDL and UVL inputs
* Support location inputs
* Input-state validation
* Calculation and plotting
* Analysis result summary
* Saved-analysis history access
* Graph saving

The plotting interface displays three main engineering views:
1. Beam diagram
2. Shear Force Diagram
3. Bending Moment Diagram

The beam diagram includes graphical representations of supports, applied loads, moments, reactions, UDLs, and UVLs.

## Analysis History
Completed analyses can be stored in `history.json`. Each history entry contains the information required to reconstruct the beam and reproduce its stored analysis, including:
* Beam length
* Support locations and types
* Point loads
* Applied moments
* Distributed loads
* System type
* Calculated reactions
* Summary statistics
* Numerical, shear-force, and bending-moment data
* Execution number
* Timestamp

Saved analyses can be loaded later and plotted without executing the solver again. `history.json` is intentionally excluded from version control through `.gitignore`, so locally saved user analyses are not committed to the repository.

## Graph Export
The generated Matplotlib figure can be saved as an image using the application's graph-saving functionality. This allows completed beam analyses to be retained independently of the application.

## Automated Testing
The project uses `pytest` for automated testing. Tests are organized in the `tests/` directory and cover the project's core beam model, input-data handling, validation, and solver functionality.

Run the complete test suite from the project root with:
```bash
python -m pytest
```
A successful test run confirms that the implemented functionality covered by the test suite continues to behave as expected.

## Project Structure

```text
Beam-Analysis-Solver/
├── main.py               # Application entry point
├── gui.py                # PyQt5 graphical user interface
├── beam.py               # Beam model and event classes
├── get_beam_data.py      # Beam construction and input data handling
├── solvers.py            # Reaction, SFD, and BMD calculations
├── plotting.py           # Beam, SFD, and BMD visualization
├── Validation.py         # Input and typing-state validation
├── history.py            # Analysis history and graph export
├── tests/                # Automated pytest test suite
├── .gitignore            # Git ignore rules
└── README.md             # Project documentation
```
The architecture intentionally separates:
* Data modelling (`beam.py`)
* Input construction (`get_beam_data.py`)
* Numerical analysis (`solvers.py`)
* Validation (`Validation.py`)
* Visualization (`plotting.py`)
* GUI (`gui.py`)
* History and persistence (`history.py`)
* Testing (`tests/`)

This separation made it possible to develop and test individual parts of the application independently.

## Requirements
* Python 3.12+
* NumPy
* Matplotlib
* PyQt5
* pytest (for running the test suite)

## Installation

Clone the repository:
```bash
git clone https://github.com/vvidhukrishna/Beam-Analysis-Solver.git
cd Beam-Analysis-Solver
```

Create a virtual environment:
```bash
python -m venv .venv
```

Activate the virtual environment (Windows):
```bash
.venv\Scripts\activate
```

Install the required packages:
```bash
pip install numpy matplotlib PyQt5 pytest
```

## Running the Application

Launch the application with:
```bash
python main.py
```

The application opens the graphical interface. Enter the beam geometry, loading, moments, and support locations, then use the calculation control to perform the analysis. The program validates the inputs, constructs the beam model, solves the support reactions, calculates the SFD and BMD, and displays the results graphically.

## Engineering Scope and Limitations
The final solver is designed for statically determinate beam problems and currently implements two system types:
* Simply supported beams with two supports
* Cantilever beams with one fixed support at `x = 0`

Supported loading includes:
* Point loads
* Concentrated applied moments
* UDLs
* UVLs

The project is intentionally not a generalized structural-analysis package. It does not attempt to solve statically indeterminate beam systems or provide a generalized finite-element analysis framework. The current implementation is intended primarily as an educational and engineering-learning tool rather than a certified structural-analysis program.

## Development History

### V1.0.0 - Core Solver
The first version established the fundamental beam-analysis functionality:
* Static support reaction calculation
* SFD generation
* BMD generation
* Point loads
* Applied moments
* Basic visualization
* Command-line input
* Object-oriented beam architecture

### V2.1.0 - Distributed Loading
The solver was extended to support distributed loading:
* Uniformly Distributed Loads
* Uniformly Varying Loads
* Improved beam visualization
* Improved numerical SFD/BMD calculation

### V2.2.0 - Graphical Interface
The project evolved from a command-line solver into a graphical application:
* PyQt GUI
* Integrated beam input
* Live input validation
* Integrated reaction calculation
* Integrated SFD/BMD calculation
* Engineering-style visualization
* Analysis result summary
* Improved modular architecture

### V3.x - Expansion and Refinement
The third development phase expanded the solver beyond the original simply supported implementation and introduced the supporting software infrastructure needed for a more complete application. Major developments included:
* Cantilever beam analysis
* Fixed-support reaction force and moment calculation
* Expanded beam and support modelling
* Automated unit testing with pytest
* Persistent analysis history using JSON
* Reconstruction of saved beam analyses
* Loading stored numerical analysis data
* Graph export
* GUI refinement and usability improvements
* Improved engineering visualization
* Expanded validation and error handling

### V3.5.0 - Final Release
The final release consolidated the project's features into the completed application. At this point, the original project scope had been achieved: a beam-analysis program developed from first principles had evolved into a modular, tested, graphical engineering application capable of analyzing both simply supported and cantilever beam systems with multiple loading types. No further feature development is planned.

## Why I Built This
I started this project because I wanted to understand beam analysis beyond solving individual problems by hand. Instead of treating the calculations as isolated equations, I wanted to understand how the engineering problem could be represented computationally:

```text
Physical Beam  →  Mathematical Model  →  Object-Oriented Representation  →  Numerical Solver  →  Engineering Visualization  →  Usable Application
```

The project therefore became much more than a calculator. During its development I worked with:
* Static equilibrium and beam theory
* Numerical computation
* Object-oriented programming
* Data modelling
* Input validation
* GUI development
* Matplotlib visualization
* Persistent data storage
* Automated testing
* Git and GitHub version control

The most important outcome of the project is not simply that it can calculate an SFD or BMD. It is that it gave me practical experience translating an engineering problem into software, designing a computational architecture around it, testing the implementation, and gradually turning the result into a usable engineering tool.

## License
This project is intended as a personal learning and engineering portfolio project.
