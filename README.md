# Market Simulation

A Django-based market simulation that models buyer/seller interactions and tracks price, demand, and sales over time.

## Overview

This project simulates a market where buyers with budgets and willingness-to-pay (WTP) interact with sellers who set prices. The simulation runs iteratively, adjusting seller prices based on sales performance.

## Features

- **Interactive Dashboard**: Web interface to configure and run simulations
- **Configurable Parameters**: Set number of buyers and sellers
- **Simulation Engine**: Models market dynamics with price adjustments
- **Data Persistence**: Stores simulation results in SQLite database
- **Excel Export**: Download simulation data as Excel files

## Tech Stack

- **Backend**: Django 6.0
- **Database**: SQLite
- **Frontend**: HTML templates
- **Data Processing**: NumPy
- **Excel Export**: openpyxl

## Installation

1. Create and activate virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # or
   venv\Scripts\activate  # Windows
   ```

2. Install dependencies:
   ```bash
   pip install django numpy openpyxl
   ```

3. Run migrations:
   ```bash
   python manage.py migrate
   ```

4. Start the development server:
   ```bash
   python manage.py runserver
   ```

5. Open http://localhost:8000 in your browser

## Usage

1. Visit the dashboard at the root URL
2. Enter number of buyers and sellers
3. Click "Run Simulation" to execute
4. View recent simulation history
5. Click "Export to Excel" to download results

## Simulation Logic

- **Buyers**: Each has a random budget (50-200) and willingness-to-pay (20-150)
- **Sellers**: Each has a random initial price (30-100)
- **Matching**: Buyers purchase from the seller offering the lowest price they can afford
- **Price Adjustment**: 
  - Sellers with >5 sales increase prices by 5%
  - Sellers with ≤5 sales decrease prices by 5%
- **Iterations**: 100 time steps per simulation

## Project Structure

```
Simulation/
├── manage.py
├── db.sqlite3
├── market_app/          # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── simulation/          # Main app
    ├── models.py        # SimulationRun model & run_simulation()
    ├── views.py         # Dashboard & export views
    ├── urls.py          # URL routing
    └── templates/
        └── simulation/
            └── dashboard.html
```