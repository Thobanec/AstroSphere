# 🌌 AstroSphere

AstroSphere is a Python-based Solar System Analysis Platform that calculates and visualizes astronomical relationships between Solar System bodies.

The project combines astronomy, Python software engineering, web development, automated testing, and cloud-ready architecture.

## Features

- Solar System overview
- Planetary distance calculations
- Distance from the Sun
- Distance from Earth
- Relative velocity calculations
- Orbital distance analysis over time
- Closest and farthest approach analysis
- Distance statistics
- Relative velocity statistics
- Interactive web interface
- Individual planetary detail pages
- Automated test suite
- JPL DE440S ephemeris support

## Technology Stack

### Backend

- Python
- Flask
- Skyfield
- NumPy

### Astronomy

- JPL DE440S ephemeris
- Skyfield
- Astronomical position calculations

### Visualization

- Plotly
- Matplotlib

### Testing

- pytest

### Development

- Git
- GitHub
- Python virtual environment

## Project Structure

```text
AstroSphere/
│
├── src/
│   └── astrosphere/
│       ├── astronomy/
│       ├── models/
│       ├── analysis_config.py
│       ├── overview.py
│       ├── overview_report.py
│       ├── reporting.py
│       ├── visualization.py
│       └── ...
│
├── tests/
│   ├── test_calculations.py
│   ├── test_overview.py
│   ├── test_orbital_analysis.py
│   └── test_web.py
│
├── web/
│   ├── app.py
│   ├── templates/
│   └── static/
│
├── pyproject.toml
├── requirements.txt
├── README.md
└── .gitignore
## Version

0.1.0

## Author

Thobane Cele

