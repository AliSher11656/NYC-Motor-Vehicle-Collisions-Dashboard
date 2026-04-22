
---

# 🚗 NYC Motor Vehicle Collisions Dashboard

An interactive data analytics dashboard built using **Shiny for Python** to explore, analyze, and visualize motor vehicle collision data in New York City.

---

## 📌 Overview

This project provides a comprehensive platform for analyzing crash data sourced from NYC Open Data. It enables users to explore patterns in traffic collisions through interactive visualizations, geospatial mapping, and risk-based insights.

The dashboard is designed to support **data-driven decision making** in areas such as urban safety, transportation analysis, and public policy.

---

## ✨ Key Features

* 🔄 **Real-time data integration** using Socrata API (NYC Open Data)
* 📅 **Dynamic date filtering** for customized analysis
* ⚡ **Efficient caching (10-minute TTL)** to improve performance
* 📊 **Interactive visualizations** powered by Plotly
* 🗺️ **Geospatial mapping** of crash locations
* ⏱️ **Time-based analysis** (hourly, daily, weekday trends)
* 🚨 **Severity classification** (Fatal, Injury, No Injury)
* 📍 **Street-level risk insights** with derived risk scoring
* 🚗 **Vehicle type & contributing factor analysis**
* 🧩 **Modular architecture** for scalability and maintainability

---

## 📊 Dashboard Sections

* **Overview** → Key metrics and high-level trends
* **Map View** → Interactive crash location visualization
* **Time Analysis** → Temporal patterns and heatmaps
* **Risk & Streets** → High-risk areas and dangerous streets
* **Causes & Vehicles** → Analysis of contributing factors and vehicle types

---

## 🛠️ Tech Stack

* **Python**
* **Shiny for Python**
* **Pandas & NumPy**
* **Plotly**
* **Requests**
* **Socrata Open Data API**

---

## 📁 Project Structure

```
nyc_crash_dashboard/
│
├── app.py          # Application entry point
├── backend.py      # Data fetching, processing, caching
├── frontend.py     # UI layout and dashboard design
├── utils.py        # Helper functions and feature engineering
├── requirements.txt
└── README.md
```

---

## ⚙️ Installation & Setup

### 1. Clone the repository

```bash
git clone https://github.com/AliSher11656/NYC-Motor-Vehicle-Collisions-Dashboard.git
cd NYC-Motor-Vehicle-Collisions-Dashboard
```

---

### 2. Create virtual environment

```bash
python -m venv .venv
```

Activate it:

**Windows**

```bash
.venv\Scripts\activate
```

**macOS/Linux**

```bash
source .venv/bin/activate
```

---

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## ▶️ Running the Application

```bash
shiny run --reload app.py
```

Open the local URL displayed in the terminal.

---


## 📈 Data Processing Highlights

* Real-time API data ingestion
* Feature engineering (severity classification, risk scoring)
* Time-based feature extraction (hour, weekday)
* Data cleaning and transformation using Pandas

---

## 🚀 Use Cases

* Data Analytics Portfolio Project
* Urban Safety & Traffic Analysis
* Interactive Dashboard Development
* Real-time Data Application Design

---

## 🔮 Future Enhancements

* Cloud deployment (Render / AWS / Azure)
* Advanced geospatial clustering
* Predictive crash-risk modeling
* Export/download functionality
* User authentication

---


## 👤 Author

**Ali Sher**
🔗 GitHub: [https://github.com/AliSher11656](https://github.com/AliSher11656)

---

## 📄 License

This project is open-source and available for learning and portfolio use.

---

