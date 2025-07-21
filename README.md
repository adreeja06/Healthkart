# HealthKart Influencer Campaign ROI Dashboard

This project is an open-source dashboard built with Python and Streamlit to analyze the performance and return on investment (ROI) of HealthKart's influencer marketing campaigns. It includes advanced filtering, time-series analysis, and automated PDF reporting.

## 🚀 Overview

The dashboard provides a comprehensive view of campaign performance by ingesting and processing data related to influencers, posts, sales, and payouts. It allows marketing managers to make data-driven decisions by visualizing key metrics and uncovering actionable insights.

**Working demo available at:** [https://adreeja06-healthkart-app-izvayg.streamlit.app/](https://adreeja06-healthkart-app-izvayg.streamlit.app/)

## 📸 Dashboard Preview

Here is a preview of the dashboard's features:

**Overview Tab:**
*Displays high-level KPIs and analyzes influencer personas and platform performance.*
![Overview Tab](assets/image_654a45.jpg)

**Influencer Deep Dive Tab:**
*Identifies top-performing and underperforming influencers.*
![Influencer Deep Dive](assets/image_65475a.jpg)

**Temporal Analysis Tab:**
*Tracks weekly revenue trends over the course of the campaign.*
![Temporal Analysis](assets/image_654703.jpg)

## 📝 Key Assumptions

A crucial part of this analysis is the calculation of **Incremental ROAS**. The following assumption was made to estimate the true impact of the influencer campaigns:

-   **Baseline Organic Sales:** It is assumed that **15%** of the revenue attributed to an influencer would have been generated organically through other channels regardless of the campaign. Therefore, Incremental Revenue is calculated as `Attributed Revenue * (1 - 0.15)`.

## 🛠️ How to Run the Dashboard

1.  **Clone the Repository:**
    ```bash
    git clone [https://github.com/adreeja06/Healthkart](https://github.com/adreeja06/Healthkart)
    cd Healthkart
    ```

2.  **Set up Environment & Install Dependencies:**
    ```bash
    # Create and activate a virtual environment
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate

    # Install required packages
    pip install -r requirements.txt
    ```

3.  **Generate Sample Data:**
    Run the data generation script once to create the necessary CSV files.
    ```bash
    python generate_data.py
    ```

4.  **Launch the Streamlit App:**
    ```bash
    streamlit run app.py
    ```

5.  **Use the Dashboard:**
    Open the local URL in your browser and use the sidebar to upload the four CSV files. The dashboard will load automatically.

## ✨ Features

-   **Dynamic Data Ingestion:** Upload campaign data via four separate CSV files.
-   **Core Metrics:** Calculates total payouts, ROI (ROAS), and Incremental ROAS.
-   **Advanced Filtering:** Dynamically filter by Platform, Influencer Category, Campaign, Product, Date Range, and ROAS.
-   **Multi-Tab Analysis:**
    -   **Overview:** High-level KPIs and persona/platform analysis.
    -   **Influencer Deep Dive:** Top and underperforming influencers.
    -   **Temporal Analysis:** Weekly revenue trends.
    -   **Data Explorer:** A complete, sortable dataset.
-   **Automated Reporting:** Generate a comprehensive PDF report with key metrics, charts, and data tables.
-   **Data Export:** Download the filtered dataset as a CSV file.
