# Market Simulation

A Django-based market simulation platform that models dynamic buyer and seller market interactions. The application lets users run market scenarios, save simulation runs, compare results, and export data in multiple formats.

## What This Project Does

This project simulates a market where buyers with budgets and willingness-to-pay interact with sellers that set prices. The system runs through multiple market iterations, tracking price, demand, sales, and market efficiency as sellers adjust their prices based on performance.

## Key Features

- **Interactive Dashboard**: Run simulations from a web interface and view results immediately
- **User Authentication**: Register, log in, and save simulations per user
- **Preset Scenarios**: Use or create scenarios like Bull Market, Bear Market, Recession, and more
- **Custom Parameters**: Define reusable parameter sets for buyers, sellers, pricing, and market settings
- **Simulation History**: Store and browse previous simulation runs
- **Export Options**: Download simulation outputs as CSV, Excel, or PDF reports
- **REST API**: Access simulations, scenarios, parameters, and market types programmatically
- **Data Visualization**: Charts for prices, demand, sales, and efficiency using Chart.js
- **Advanced Analytics**: Calculate average price, volatility, total demand, total sales, efficiency, and more
- **Multi-market Support**: Support for different market types like competition, oligopoly, monopoly, and auction markets

## Tech Stack

- **Backend**: Django
- **REST API**: Django REST Framework
- **Database**: SQLite
- **Frontend**: Django templates + Tailwind CSS + Chart.js
- **Data Processing**: NumPy
- **Exports**: openpyxl for Excel and ReportLab for PDF

## Installation

1. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run database migrations:
   ```bash
   python manage.py migrate
   ```

4. Seed default market types and scenarios:
   ```bash
   python manage.py populate_defaults
   ```

5. Start the development server:
   ```bash
   python manage.py runserver
   ```

6. Open `http://127.0.0.1:8000/` in your browser.

## Usage

1. Register or log in.
2. Run a new simulation from the dashboard.
3. Select market models, scenarios, or saved parameter sets.
4. View simulation analytics, charts, and history.
5. Export results as CSV, Excel, or PDF.
6. Compare simulation runs side by side.

## Simulation Logic

- **Buyers**: Generated with random budgets and willingness-to-pay.
- **Sellers**: Set initial prices and adjust them each iteration.
- **Matching**: Buyers choose the seller they can afford based on price and WTP.
- **Price adjustment**:
  - Successful sellers increase price.
  - Less successful sellers decrease price.
- **Analytics**: Average price, price volatility, total demand, total sales, and market efficiency are computed after each run.

## Project Structure

```
Simulation/
├── manage.py
├── README.md
├── db.sqlite3
├── market_app/
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
└── simulation/
    ├── admin.py
    ├── models.py
    ├── views.py
    ├── urls.py
    ├── views_api.py
    ├── serializers.py
    ├── templates/
    │   └── simulation/
    │       ├── dashboard.html
    │       ├── login.html
    │       ├── register.html
    │       ├── scenarios.html
    │       ├── parameters.html
    │       ├── simulation_detail.html
    │       ├── simulations_list.html
    │       ├── compare.html
    │       └── scenario_detail.html
    └── management/
        └── commands/
            └── populate_defaults.py
```

## API Endpoints

- `/api/simulations/`
- `/api/scenarios/`
- `/api/parameters/`
- `/api/market-types/`

## Notes

- This application is for development and experimentation, not for production use.
- The export and visualization features are designed for rapid analysis of market simulation results.
