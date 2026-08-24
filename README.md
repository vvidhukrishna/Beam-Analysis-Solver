# Beam Analysis Solver

A Python-based beam analysis program that computes support reactions, Shear Force Diagrams (SFD), and Bending Moment Diagrams (BMD) for statically determinate beams.

This project was developed as a personal learning project alongside my Mechanical and Aerospace Engineering coursework to better understand structural analysis while improving my Python software design skills.

## Features

### Version 1

* Support reaction calculation using static equilibrium
* Shear Force Diagram (SFD) generation
* Bending Moment Diagram (BMD) generation
* Point loads
* Concentrated applied moments
* Pinned and roller supports
* Interactive command-line input
* Automatic input validation
* Matplotlib visualization
* Modular, object-oriented architecture

## Project Structure

```
main.py              # Program entry point
beam.py              # Beam and event classes
get_beam_data.py     # User input and beam construction
solvers.py           # Reaction, SFD and BMD solvers
plotting.py          # Diagram plotting
Validation.py        # Input and equilibrium validation
```

## Example Output

### Shear Force Diagram

*(Insert screenshot here)*

### Bending Moment Diagram

*(Insert screenshot here)*

## Requirements

* Python 3.12+
* Matplotlib

Install dependencies:

```bash
pip install matplotlib
```

## Running the Project

```bash
python main.py
```

The program can be run using interactive input or with the built-in default test case.

## Current Limitations

Version 1 currently supports:

* Two supports (pinned + roller)
* Point loads
* Applied moments

Distributed loads, graphical user interface, and report generation are planned for future versions.

## Planned Features

### Version 2

* Uniformly Distributed Loads (UDL)
* Uniformly Varying Loads (UVL)
* Improved engineering-style diagrams
* PyQt GUI
* Export to PDF/PNG
* Automated unit tests

## Why I Built This

Rather than solving beam problems manually every time, I wanted to build the solver from first principles. The goal was not only to automate structural calculations but also to practice software engineering concepts such as modular design, object-oriented programming, validation, plotting, and version control.
