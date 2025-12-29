# -*- coding: utf-8 -*-
"""
Created on Mon Dec 29 09:06:57 2025

@author: UMSS-FCYT
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import requests
import os  # Added for folder management

# --- 0. DIRECTORY SETUP ---
output_folder = "Results"
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# --- 1. PARAMETERS ---
LAT, LON = -17.783, -63.182
T_BASE = 24.0      # Comfort Setpoint
GAMMA = 0.5        # Thermal Inertia (BAIT)
EER = 3.2          # Energy Efficiency Ratio
C_AVG = 1.2        # Avg kWe per unit
DIV_FACTOR = 0.4   # Grid Coincidence Factor

# Demographic & Penetration Data [19, 20]
N_2024, ALPHA_2024 = 550000, 0.35
N_2050, ALPHA_SSP1, ALPHA_SSP5 = 780000, 0.50, 0.65

# SSP Monthly Anomalies (2050) [18]
SSP5_DELTAS = {1:2.5, 2:2.5, 3:2.6, 4:2.7, 5:2.8, 6:3.0, 7:3.1, 8:3.2, 9:3.3, 10:2.9, 11:2.7, 12:2.6}
SSP1_DELTAS = {m: d * 0.45 for m, d in SSP5_DELTAS.items()}

# --- 2. DATA ACQUISITION (NASA POWER API) [17] ---
def fetch_nasa_data(lat, lon, year):
    url = "https://power.larc.nasa.gov/api/temporal/hourly/point"
    params = {"start": f"{year}0101", "end": f"{year}1231", "latitude": lat, "longitude": lon,
              "parameters": "T2M", "community": "SB", "format": "JSON", "time-standard": "LST"}
    r = requests.get(url, params=params)
    if r.status_code == 200:
        data = r.json()['properties']['parameter']['T2M']
        series = pd.Series(data)
        series.index = pd.to_datetime(series.index, format='%Y%m%d%H')
        return series
    return None

temp_2024 = fetch_nasa_data(LAT, LON, 2024)
df = pd.DataFrame({'T_ext_2024': temp_2024})
df['month'] = df.index.month

# Apply Scenario Shifts
df['T_SSP1'] = df.apply(lambda x: x['T_ext_2024'] + SSP1_DELTAS[x['month']], axis=1)
df['T_SSP5'] = df.apply(lambda x: x['T_ext_2024'] + SSP5_DELTAS[x['month']], axis=1)

# --- 3. RECURSIVE BAIT & SCALING [21] ---
def compute_grid_mw(temp_series, households, alpha):
    t_int = np.zeros(len(temp_series))
    t_int[0] = temp_series.iloc[0]
    for i in range(1, len(temp_series)):
        t_int[i] = t_int[i-1] + GAMMA * (temp_series.iloc[i] - t_int[i-1])
    
    p_norm = np.maximum(0, t_int - T_BASE) / EER
    S = households * alpha * C_AVG * DIV_FACTOR
    return (p_norm * S) / 1000

df['MW_2024'] = compute_grid_mw(df['T_ext_2024'], N_2024, ALPHA_2024)
df['MW_SSP1'] = compute_grid_mw(df['T_SSP1'], N_2050, ALPHA_SSP1)
df['MW_SSP5'] = compute_grid_mw(df['T_SSP5'], N_2050, ALPHA_SSP5)

# Export full hourly results to CSV in the Results folder
csv_path = os.path.join(output_folder, "bolivia_cooling_results_2050.csv")
df.to_csv(csv_path)
print(f"Data exported successfully to: {csv_path}")

# --- 4. VISUALIZATION ---
plt.style.use('seaborn-v0_8-whitegrid')

def get_bait_temp(temp_series):
    t_int = np.zeros(len(temp_series))
    t_int[0] = temp_series.iloc[0]
    for i in range(1, len(temp_series)):
        t_int[i] = t_int[i-1] + GAMMA * (temp_series.iloc[i] - t_int[i-1])
    return pd.Series(t_int, index=temp_series.index)

def get_p_norm(temp_series):
    t_int = get_bait_temp(temp_series)
    return np.maximum(0, t_int - T_BASE) / EER

periods = {
    "January": ('2024-01-10', '2024-01-16'),
    "June": ('2024-06-15', '2024-06-21')
}

for month_name, (start, end) in periods.items():
    sub = df.loc[start:end]
    
    t_bait_2024 = get_bait_temp(sub['T_ext_2024'])
    t_bait_ssp1 = get_bait_temp(sub['T_SSP1'])
    t_bait_ssp5 = get_bait_temp(sub['T_SSP5'])
    
    p_2024 = get_p_norm(sub['T_ext_2024'])
    p_ssp1 = get_p_norm(sub['T_SSP1'])
    p_ssp5 = get_p_norm(sub['T_SSP5'])

    # A. INTERNAL (BAIT) TEMPERATURE COMPARISON
    plt.figure(figsize=(12, 4))
    plt.plot(sub.index, t_bait_2024, label='Baseline 2024 (Internal)', color='blue', alpha=0.5, ls='--')
    plt.plot(sub.index, t_bait_ssp1, label='SSP1-2.6 (2050) (Internal)', color='orange')
    plt.plot(sub.index, t_bait_ssp5, label='SSP5-8.5 (2050) (Internal)', color='red', lw=2)
    plt.axhline(T_BASE, color='black', ls=':', label=f'Comfort Setpoint ({T_BASE}°C)')
    plt.fill_between(sub.index, T_BASE, t_bait_ssp5, where=(t_bait_ssp5 > T_BASE), 
                     color='red', alpha=0.1, label='Cooling Required (SSP5 Internal)')
    plt.title(f"{month_name}: Hourly Internal (BAIT) Temperature Comparison")
    plt.ylabel("Internal Temp (°C)")
    plt.legend(loc='upper right', frameon=True, fontsize='small')
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%a %d'))
    plt.tight_layout()
    plt.savefig(os.path.join(output_folder, f"BAIT_Temp_{month_name}.png"), dpi=300)
    plt.show()

    # B. NORMALIZED ELECTRICAL DEMAND
    plt.figure(figsize=(12, 4))
    plt.plot(sub.index, p_2024, label='Baseline 2024', color='blue', ls='--')
    plt.plot(sub.index, p_ssp1, label='SSP1-2.6 (2050)', color='orange')
    plt.plot(sub.index, p_ssp5, label='SSP5-8.5 (2050)', color='red', lw=2)
    plt.title(f"{month_name}: Hourly Normalized Electrical Demand for Cooling")
    plt.ylabel("kWe per AC unit")
    plt.legend(loc='upper right', frameon=True, fontsize='small')
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%a %d'))
    plt.tight_layout()
    plt.savefig(os.path.join(output_folder, f"Normalized_Demand_{month_name}.png"), dpi=300)
    plt.show()

    # C. TOTAL GRID DEMAND
    plt.figure(figsize=(12, 4))
    plt.plot(sub.index, sub['MW_2024'], label='Baseline 2024', color='blue', ls='--')
    plt.plot(sub.index, sub['MW_SSP1'], label='SSP1-2.6 (2050)', color='orange')
    plt.plot(sub.index, sub['MW_SSP5'], label='SSP5-8.5 (2050)', color='red', lw=2)
    plt.title(f"{month_name}: Total Grid Cooling Demand")
    plt.ylabel("MW")
    plt.legend(loc='upper right', frameon=True, fontsize='small')
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%a %d'))
    plt.tight_layout()
    plt.savefig(os.path.join(output_folder, f"Grid_Demand_{month_name}.png"), dpi=300)
    plt.show()

print(f"All plots and data have been saved in the '{output_folder}' directory.")