"""
Cooling Tower Performance – Exploratory Data Analysis
======================================================
Reproduces every analysis section from the project PPT:
  1. Data overview & descriptive statistics
  2. Boxplots of all parameters
  3. Skewness + QQ-plots
  4. Distribution (histogram + KDE) of parameters
  5. Scatter plots between parameters
  6. Correlation heatmap
  7. Effectiveness analysis (Range vs Approach)
  8. Conclusion summary

Run:  python cooling_tower_eda.py
Outputs are saved to  ./eda_output/<Tower>/  as PNG files.
"""

import os
import warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns
from scipy import stats

warnings.filterwarnings("ignore")

# ── Matplotlib global style ────────────────────────────────────────────────────
plt.rcParams.update({
    "figure.dpi": 120,
    "figure.facecolor": "white",
    "axes.facecolor": "#f8f9fa",
    "axes.grid": True,
    "grid.color": "#e0e0e0",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "font.family": "DejaVu Sans",
    "axes.titlesize": 13,
    "axes.labelsize": 11,
})

PALETTE = "Set2"

# ──────────────────────────────────────────────────────────────────────────────
# 0. LOAD DATA
# ──────────────────────────────────────────────────────────────────────────────

CSV_PATH = "1781884620204_Cooling_tower_performance__1___2_.csv"

df_raw = pd.read_csv(CSV_PATH)

# Standardise column names (strip extra spaces)
df_raw.columns = [c.strip().replace("  ", " ") for c in df_raw.columns]

# Core numeric parameters analysed in the PPT
PARAMS = ["Hot Water Temp", "Cold Water Temp", "Dry Bulb Temp", "Wet Bulb Temp"]
DERIVED = ["Range", "Approach", "Cooling Tower Effectiveness"]

# Identify unique towers (the 'Area' column holds the tower name)
towers = df_raw["Area"].dropna().unique()
print(f"Towers found in data: {list(towers)}")
print(f"Total records: {len(df_raw)}\n")

OUTPUT_ROOT = "eda_output"
os.makedirs(OUTPUT_ROOT, exist_ok=True)


# ──────────────────────────────────────────────────────────────────────────────
# Helper: save figure
# ──────────────────────────────────────────────────────────────────────────────
def save(fig, folder, filename):
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, filename)
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved → {path}")


# ──────────────────────────────────────────────────────────────────────────────
# PER-TOWER ANALYSIS
# ──────────────────────────────────────────────────────────────────────────────
for tower in towers:
    print(f"\n{'='*60}")
    print(f"  TOWER: {tower}")
    print(f"{'='*60}")

    df = df_raw[df_raw["Area"] == tower].copy().reset_index(drop=True)
    out = os.path.join(OUTPUT_ROOT, tower.replace(" ", "_"))

    # ── Recalculate derived columns (ensures consistency) ─────────────────────
    df["Range"]  = df["Hot Water Temp"] - df["Cold Water Temp"]
    df["Approach"] = df["Cold Water Temp"] - df["Wet Bulb Temp"]
    df["Cooling Tower Effectiveness"] = (
        df["Range"] / (df["Range"] + df["Approach"]) * 100
    ).round(2)

    all_cols = PARAMS + DERIVED

    # ── Slide 4 / 13 / 22 – DESCRIPTIVE STATISTICS ────────────────────────────
    print("\n[1] Descriptive Statistics")
    desc = df[all_cols].describe().T
    desc["skewness"] = df[all_cols].skew()
    desc["kurtosis"] = df[all_cols].kurt()
    print(desc.to_string())

    fig, ax = plt.subplots(figsize=(14, 4))
    ax.axis("off")
    tbl_data = desc.round(3).reset_index()
    tbl_data.columns = ["Parameter"] + list(tbl_data.columns[1:])
    table = ax.table(
        cellText=tbl_data.values,
        colLabels=tbl_data.columns,
        cellLoc="center",
        loc="center",
    )
    table.auto_set_font_size(False)
    table.set_fontsize(8)
    table.scale(1, 1.6)
    # colour header
    for j in range(len(tbl_data.columns)):
        table[0, j].set_facecolor("#4472C4")
        table[0, j].set_text_props(color="white", fontweight="bold")
    ax.set_title(f"Descriptive Statistics – {tower}", fontsize=14, pad=12)
    save(fig, out, "01_descriptive_statistics.png")

    # ── Slide 5 / 14 / 23 – BOXPLOTS ──────────────────────────────────────────
    print("[2] Boxplots")
    fig, axes = plt.subplots(1, len(PARAMS), figsize=(14, 5))
    colors = sns.color_palette(PALETTE, len(PARAMS))
    for ax, col, color in zip(axes, PARAMS, colors):
        bp = ax.boxplot(df[col].dropna(), patch_artist=True,
                        medianprops=dict(color="black", linewidth=2))
        bp["boxes"][0].set_facecolor(color)
        ax.set_title(col, fontsize=11)
        ax.set_ylabel("°C")
    fig.suptitle(f"Boxplot of Parameters – {tower}", fontsize=14, y=1.02)
    plt.tight_layout()
    save(fig, out, "02_boxplots.png")

    # ── Slide 6 / 15 / 24 – SKEWNESS + QQ-PLOTS ───────────────────────────────
    print("[3] QQ-plots + Skewness")
    n = len(PARAMS)
    fig, axes = plt.subplots(2, n, figsize=(14, 8))
    for i, col in enumerate(PARAMS):
        data = df[col].dropna()
        sk = data.skew()
        # Top row: bar showing skewness value
        axes[0, i].bar([col], [sk],
                       color=("steelblue" if sk >= 0 else "tomato"), width=0.4)
        axes[0, i].axhline(0, color="black", linewidth=0.8, linestyle="--")
        axes[0, i].set_title(f"Skewness = {sk:.3f}", fontsize=10)
        axes[0, i].set_ylabel("Skewness")
        axes[0, i].set_xticks([])
        axes[0, i].set_xlabel(col)
        # Bottom row: QQ-plot
        (osm, osr), (slope, intercept, r) = stats.probplot(data, dist="norm")
        axes[1, i].scatter(osm, osr, alpha=0.7, s=20, color="steelblue")
        x_line = np.array([osm.min(), osm.max()])
        axes[1, i].plot(x_line, slope * x_line + intercept, "r--", linewidth=1.5)
        axes[1, i].set_title(f"QQ-plot – {col}", fontsize=10)
        axes[1, i].set_xlabel("Theoretical Quantiles")
        axes[1, i].set_ylabel("Sample Quantiles")
    fig.suptitle(f"Skewness & QQ-plots – {tower}", fontsize=14, y=1.01)
    plt.tight_layout()
    save(fig, out, "03_skewness_qqplots.png")

    # ── Slide 7 / 16 / 25 – DISTRIBUTIONS (hist + KDE) ────────────────────────
    print("[4] Distributions")
    fig, axes = plt.subplots(1, n, figsize=(14, 5))
    for ax, col in zip(axes, PARAMS):
        data = df[col].dropna()
        ax.hist(data, bins="auto", density=True,
                color="steelblue", alpha=0.5, edgecolor="white", label="Histogram")
        kde_x = np.linspace(data.min() - 1, data.max() + 1, 200)
        kde = stats.gaussian_kde(data)
        ax.plot(kde_x, kde(kde_x), color="crimson", linewidth=2, label="KDE")
        ax.axvline(data.mean(),   color="green",  linestyle="--", linewidth=1.5,
                   label=f"Mean={data.mean():.1f}")
        ax.axvline(data.median(), color="orange", linestyle=":",  linewidth=1.5,
                   label=f"Median={data.median():.1f}")
        ax.set_title(col, fontsize=11)
        ax.set_xlabel("°C")
        ax.set_ylabel("Density")
        ax.legend(fontsize=7)
    fig.suptitle(f"Distribution of Parameters – {tower}", fontsize=14, y=1.02)
    plt.tight_layout()
    save(fig, out, "04_distributions.png")

    # ── Slide 8 / 17 / 26 – SCATTER PLOTS ─────────────────────────────────────
    print("[5] Scatter plots")
    # Pairwise scatter: each param vs Effectiveness + HWT vs CWT, DBT vs WBT
    pairs = [
        ("Hot Water Temp",  "Cooling Tower Effectiveness"),
        ("Cold Water Temp", "Cooling Tower Effectiveness"),
        ("Wet Bulb Temp",   "Cooling Tower Effectiveness"),
        ("Approach",        "Cooling Tower Effectiveness"),
        ("Range",           "Cooling Tower Effectiveness"),
        ("Hot Water Temp",  "Cold Water Temp"),
    ]
    fig, axes = plt.subplots(2, 3, figsize=(14, 9))
    axes = axes.flatten()
    colors_eff = sns.color_palette(PALETTE, len(df))
    eff_vals = df["Cooling Tower Effectiveness"].values

    for ax, (x_col, y_col) in zip(axes, pairs):
        x = df[x_col]
        y = df[y_col]
        sc = ax.scatter(x, y, c=eff_vals, cmap="RdYlGn",
                        s=60, edgecolors="grey", linewidths=0.5, alpha=0.85)
        # Regression line
        mask = x.notna() & y.notna()
        if mask.sum() > 1:
            m, b, r, p, _ = stats.linregress(x[mask], y[mask])
            xr = np.linspace(x.min(), x.max(), 100)
            ax.plot(xr, m * xr + b, "k--", linewidth=1.2,
                    label=f"R²={r**2:.2f}")
            ax.legend(fontsize=8)
        ax.set_xlabel(x_col, fontsize=9)
        ax.set_ylabel(y_col, fontsize=9)
        ax.set_title(f"{x_col} vs {y_col}", fontsize=10)
    plt.colorbar(sc, ax=axes[-1], label="Effectiveness %")
    fig.suptitle(f"Scatter Plots – {tower}", fontsize=14, y=1.01)
    plt.tight_layout()
    save(fig, out, "05_scatter_plots.png")

    # ── Slide 9 / 18 / 27 – CORRELATION HEATMAP ───────────────────────────────
    print("[6] Correlation heatmap")
    corr = df[all_cols].corr()
    fig, ax = plt.subplots(figsize=(9, 7))
    mask_upper = np.triu(np.ones_like(corr, dtype=bool), k=1)
    sns.heatmap(
        corr, annot=True, fmt=".2f", cmap="coolwarm",
        center=0, linewidths=0.5, linecolor="white",
        ax=ax, square=True, cbar_kws={"shrink": 0.8},
    )
    ax.set_title(f"Correlation Heatmap – {tower}", fontsize=14)
    plt.tight_layout()
    save(fig, out, "06_correlation_heatmap.png")

    # ── Slide 10 / 19 / 28 – EFFECTIVENESS ANALYSIS ───────────────────────────
    print("[7] Effectiveness analysis")
    df["Eff_Category"] = np.where(
        df["Range"] > df["Approach"], "High / Normal (Range > Approach)",
        "Low (Approach ≥ Range)"
    )
    cat_colors = {
        "High / Normal (Range > Approach)": "#2ecc71",
        "Low (Approach ≥ Range)": "#e74c3c",
    }

    fig = plt.figure(figsize=(14, 10))
    gs = gridspec.GridSpec(2, 2, figure=fig, hspace=0.4, wspace=0.35)

    # (a) Range vs Approach scatter coloured by category
    ax1 = fig.add_subplot(gs[0, :])
    for cat, grp in df.groupby("Eff_Category"):
        ax1.scatter(grp["Approach"], grp["Range"],
                    label=cat, color=cat_colors[cat],
                    s=100, edgecolors="black", linewidths=0.5, zorder=3)
    x_diag = np.linspace(0, df[["Range", "Approach"]].max().max() + 1, 100)
    ax1.plot(x_diag, x_diag, "k--", linewidth=1.2, label="Range = Approach (boundary)")
    ax1.set_xlabel("Approach (CWT – WBT) [°C]")
    ax1.set_ylabel("Range (HWT – CWT) [°C]")
    ax1.set_title("Range vs Approach – Effectiveness Boundary")
    ax1.legend(fontsize=9)

    # (b) Effectiveness by category – boxplot
    ax2 = fig.add_subplot(gs[1, 0])
    eff_data = [
        df.loc[df["Eff_Category"] == c, "Cooling Tower Effectiveness"].dropna().values
        for c in cat_colors
    ]
    bp = ax2.boxplot(eff_data, patch_artist=True,
                     medianprops=dict(color="black", linewidth=2))
    for patch, color in zip(bp["boxes"], cat_colors.values()):
        patch.set_facecolor(color)
    ax2.set_xticklabels(["High/Normal", "Low"], rotation=15, fontsize=9)
    ax2.set_ylabel("Effectiveness (%)")
    ax2.set_title("Effectiveness by Category")

    # (c) Approach distribution with optimal zone shaded
    ax3 = fig.add_subplot(gs[1, 1])
    ax3.hist(df["Approach"], bins="auto", color="steelblue",
             alpha=0.6, edgecolor="white", label="Approach")

    # Determine optimal approach range from data (approach values where Eff≥50%)
    good = df[df["Cooling Tower Effectiveness"] >= 50]["Approach"]
    if len(good):
        lo, hi = good.min(), good.max()
        ax3.axvspan(lo, hi, alpha=0.25, color="green",
                    label=f"Optimal zone ({lo}–{hi}°C)")
    ax3.set_xlabel("Approach [°C]")
    ax3.set_ylabel("Count")
    ax3.set_title("Approach Distribution")
    ax3.legend(fontsize=9)

    fig.suptitle(f"Effectiveness Analysis – {tower}\n"
                 "Effectiveness = Range / (Range + Approach) × 100",
                 fontsize=13, y=1.01)
    save(fig, out, "07_effectiveness_analysis.png")

    # ── Slide 11 / 20 / 29 – CONCLUSION SUMMARY TABLE ─────────────────────────
    print("[8] Conclusion summary")
    good_approach = df[df["Cooling Tower Effectiveness"] >= 50]["Approach"]
    lo_ap = good_approach.min() if len(good_approach) else "N/A"
    hi_ap = good_approach.max() if len(good_approach) else "N/A"
    mean_eff = df["Cooling Tower Effectiveness"].mean()
    high_eff_pct = (df["Eff_Category"] == "High / Normal (Range > Approach)").mean() * 100

    summary = {
        "Tower": tower,
        "Records Analysed": len(df),
        "Mean Effectiveness (%)": f"{mean_eff:.2f}",
        "Records: Range > Approach": f"{high_eff_pct:.1f}%",
        "Optimal Approach Range (°C)": f"{lo_ap} – {hi_ap}",
        "Avg Range (HWT-CWT) °C": f"{df['Range'].mean():.1f}",
        "Avg Approach (CWT-WBT) °C": f"{df['Approach'].mean():.1f}",
    }

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.axis("off")
    rows = [[k, v] for k, v in summary.items()]
    tbl = ax.table(cellText=rows, colLabels=["Metric", "Value"],
                   cellLoc="center", loc="center")
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(11)
    tbl.scale(1, 2)
    for j in range(2):
        tbl[0, j].set_facecolor("#4472C4")
        tbl[0, j].set_text_props(color="white", fontweight="bold")
    for i in range(1, len(rows) + 1):
        bg = "#dce6f1" if i % 2 == 0 else "white"
        for j in range(2):
            tbl[i, j].set_facecolor(bg)
    ax.set_title(f"Conclusion – {tower}", fontsize=14, pad=15)
    save(fig, out, "08_conclusion_summary.png")

    print(f"\n  → All plots for '{tower}' saved to: {out}/")


# ──────────────────────────────────────────────────────────────────────────────
# CROSS-TOWER COMPARISON (if multiple towers)
# ──────────────────────────────────────────────────────────────────────────────
if len(towers) > 1:
    print(f"\n{'='*60}")
    print("  CROSS-TOWER COMPARISON")
    print(f"{'='*60}")
    out_cmp = os.path.join(OUTPUT_ROOT, "cross_tower_comparison")

    # Recalculate for full dataset
    df_full = df_raw.copy()
    df_full.columns = [c.strip().replace("  ", " ") for c in df_full.columns]
    df_full["Range"] = df_full["Hot Water Temp"] - df_full["Cold Water Temp"]
    df_full["Approach"] = df_full["Cold Water Temp"] - df_full["Wet Bulb Temp"]
    df_full["Cooling Tower Effectiveness"] = (
        df_full["Range"] / (df_full["Range"] + df_full["Approach"]) * 100
    ).round(2)

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    for ax, col in zip(axes, ["Cooling Tower Effectiveness", "Range", "Approach"]):
        data_by_tower = [
            df_full.loc[df_full["Area"] == t, col].dropna().values
            for t in towers
        ]
        bp = ax.boxplot(data_by_tower, patch_artist=True,
                        medianprops=dict(color="black", linewidth=2))
        colors = sns.color_palette(PALETTE, len(towers))
        for patch, color in zip(bp["boxes"], colors):
            patch.set_facecolor(color)
        ax.set_xticklabels([t.replace(" ", "\n") for t in towers], fontsize=8)
        ax.set_title(col)
        ax.set_ylabel("Value")
    fig.suptitle("Cross-Tower Comparison", fontsize=14, y=1.01)
    plt.tight_layout()
    save(fig, out_cmp, "cross_tower_comparison.png")


print("\n✅  EDA complete. All outputs saved under ./eda_output/")
print("\nFolder structure:")
for root, dirs, files in os.walk(OUTPUT_ROOT):
    level = root.replace(OUTPUT_ROOT, "").count(os.sep)
    indent = "  " * level
    print(f"{indent}{os.path.basename(root)}/")
    for f in sorted(files):
        print(f"{indent}  {f}")
