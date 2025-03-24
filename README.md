# Temperature Probe Analysis Tool

This tool analyzes thermal data from temperature probes, specifically designed for processing and visualizing temperature fluctuations and recovery times.

## Features

- Processes CSV files containing temperature probe data
- Analyzes temperature drops and recovery times
- Visualizes temperature data with matplotlib
- Calculates minimum temperatures during aspiration
- Supports multiple probe locations (inlet, middle, outlet)

## Requirements

- Python 3.x
- Required packages:
  - numpy
  - pandas
  - matplotlib
  - scipy

## Installation

1. Clone this repository:
```bash
git clone [your-repository-url]
```

2. Install required packages:
```bash
pip install numpy pandas matplotlib scipy
```

## Usage

1. Place your temperature data CSV file in an accessible location
2. Update the file path in `Thermal_temp_analysis.py`:
```python
file = "path/to/your/data.csv"
```
3. Run the script:
```bash
python Thermal_temp_analysis.py
```

4. Follow the interactive prompts to analyze specific datasets and probes

## Data Format

The input CSV file should contain:
- Temperature values for different probe locations
- Time stamps in HH:MM:SS format
- Values should be organized in columns with headers containing 'value'

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. 