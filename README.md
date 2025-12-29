# Bolivia-Cooling-Demand-2050: Residential Cooling Demand Projections for Santa Cruz, Bolivia (2050)
## Overview
This repository contains the Python implementation of a study evaluating the impact of climate change and demographic growth on residential cooling demand in Santa Cruz, Bolivia. Using the **Recursive Building Adjusted Internal Temperature (BAIT)** model, the project simulates hourly grid loads for the year 2050 under two Shared Socioeconomic Pathways: **SSP1-2.6** and **SSP5-8.5**.

## Abstract
This work evaluates the impact of climate change on residential cooling demand in Santa Cruz, Bolivia, using NASA POWER data and the Recursive BAIT model. Results indicate that peak demand could reach approximately **973.7 MW** by 2050, representing a significant increase over current baselines. 

However, this regional analysis is intended as a foundational component for a comprehensive study of all regions in Bolivia. The ultimate objective is a national-scale analysis considering how climate change will affect the overall energy panorama. This includes not only the escalating demand for residential cooling but also the climate-driven availability of water for hydroelectric generation and biomass production. Such a multi-sectoral approach is essential to address energy security and climate vulnerability across Bolivia's diverse geographic regions.

## Key Features
* **Climatic Data Integration:** Automated retrieval of hourly temperature data via the NASA POWER API.
* **BAIT Model Implementation:** A recursive algorithm that accounts for thermal inertia ($\gamma = 0.5$) to simulate internal building temperatures.
* **Scenario Projections:** Comparison of current baselines against 2050 temperature deltas for SSP1 and SSP5 scenarios.
* **Multi-Sectoral Focus:** Structured to eventually incorporate hydroelectric and biomass resource assessments.
* **Automated Output:** Generates a comprehensive CSV of results and high-resolution visualization plots in a dedicated `/Results` folder.

## Methodology
The model calculates cooling loads based on a comfort threshold of **24°C**. The transition from seasonal to year-round cooling demand is analyzed by tracking winter afternoon excursions above this threshold. The electrical load is scaled according to projected household growth and air conditioning penetration rates.

## Installation and Usage
1. **Clone the repository:**
   ```bash
   git clone [https://github.com/JVISchneider/Bolivia-Cooling-Demand-2050.git](https://github.com/JVISchneider/Bolivia-Cooling-Demand-2050.git)
2. **Install dependencies:**
pip install -r requirements.txt
3. **Run the analysis:**
   python "Santa Cruz Cooling Demand Project.py"
