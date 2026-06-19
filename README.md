# Cooling Tower Performance – EDA

Exploratory Data Analysis of cooling tower performance data (Hirakud Smelter).  
Reproduces all analyses from the project presentation:

## Towers Covered
- Screw Compressor Cooling Tower
- IR Cooling Tower
- 235 KA Cooling Tower

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

## Output Plots (per tower)

| File | Description | PPT Slide |
|---|---|---|
| `01_descriptive_statistics.png` | Count, mean, std, min/max, skewness, kurtosis | Slide 4/13/22 |
| `02_boxplots.png` | Boxplot for each parameter | Slide 5/14/23 |
| `03_skewness_qqplots.png` | Skewness bar + QQ-plot per parameter | Slide 6/15/24 |
| `04_distributions.png` | Histogram + KDE with mean/median lines | Slide 7/16/25 |
| `05_scatter_plots.png` | Pairwise scatter plots with regression lines | Slide 8/17/26 |
| `06_correlation_heatmap.png` | Pearson correlation heatmap | Slide 9/18/27 |
| `07_effectiveness_analysis.png` | Range vs Approach boundary, effectiveness boxplot, approach distribution | Slide 10/19/28 |
| `08_conclusion_summary.png` | Summary table with optimal approach range | Slide 11/20/29 |

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
