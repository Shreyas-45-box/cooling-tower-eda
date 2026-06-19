# Cooling Tower Performance – EDA

Exploratory Data Analysis of cooling tower performance data (Hirakud Smelter).  
Reproduces all analyses from the project presentation:

## Tower Covered
- IR Cooling Tower

> The script auto-detects all towers present in the CSV and runs every analysis for each one.

## Parameters Analysed

| Parameter | Description |
|---|---|
| Hot Water Temp (HWT) | Water temperature entering the tower (°C) |
| Cold Water Temp (CWT) | Water temperature leaving the tower (°C) |
| Dry Bulb Temp (DBT) | Ambient air dry bulb temperature (°C) |
| Wet Bulb Temp (WBT) | Ambient air wet bulb temperature (°C) |
| Range | HWT − CWT |
| Approach | CWT − WBT |
| Effectiveness | Range / (Range + Approach) × 100 (%) |


## Setup

```bash
pip install pandas numpy matplotlib seaborn scipy
```

## Usage

```bash
# Place your CSV in the same folder as the script, then:
python cooling_tower_eda.py
```

Plots are saved to `./eda_output/<Tower_Name>/`.

## Key Insight

Cooling tower effectiveness is computed as:

```
Effectiveness = Range / (Range + Approach) × 100
```

When **Range > Approach**, effectiveness is high/normal.  
When **Approach ≥ Range**, effectiveness drops.

Based on the analysis:
- **IR Cooling Tower** – optimal approach: 4 to 6 °C
- **Screw Compressor CT** – optimal approach: 4 to 8 °C  
- **235 KA Cooling Tower** – optimal approach: 5 to 7 °C
