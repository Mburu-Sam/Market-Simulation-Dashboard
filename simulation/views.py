import json
import csv
from io import BytesIO, StringIO
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.db.models import Q, Avg, Max, Min
from openpyxl import Workbook
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.units import inch
from reportlab.lib import colors
import numpy as np

from .models import (
    run_simulation, SimulationRun, SimulationParameters, 
    SimulationScenario, MarketType
)


# ==================== Authentication Views ====================

def register(request):
    """User registration"""
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        
        if password != password_confirm:
            return render(request, 'simulation/register.html', {'error': 'Passwords do not match'})
        
        if User.objects.filter(username=username).exists():
            return render(request, 'simulation/register.html', {'error': 'Username already exists'})
        
        user = User.objects.create_user(username=username, email=email, password=password)
        login(request, user)
        return redirect('dashboard')
    
    return render(request, 'simulation/register.html')


def user_login(request):
    """User login"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            return render(request, 'simulation/login.html', {'error': 'Invalid credentials'})
    
    return render(request, 'simulation/login.html')


def user_logout(request):
    """User logout"""
    logout(request)
    return redirect('dashboard')


# ==================== Dashboard & Core Views ====================

def dashboard(request):
    """Main dashboard with simulation controls"""
    scenarios = SimulationScenario.objects.filter(is_active=True)
    parameters_list = SimulationParameters.objects.all()[:10]
    market_types = MarketType.objects.all()
    
    if request.method == "POST":
        buyers = int(request.POST.get("buyers", 50))
        sellers = int(request.POST.get("sellers", 5))
        scenario_id = request.POST.get('scenario')
        market_type_id = request.POST.get('market_type')
        
        scenario = None
        market_type = None
        
        if scenario_id:
            scenario = get_object_or_404(SimulationScenario, id=scenario_id)
        if market_type_id:
            market_type = get_object_or_404(MarketType, id=market_type_id)
        
        data = run_simulation(buyers, sellers)
        
        # Save to DB
        sim = SimulationRun.objects.create(
            owner=request.user if request.user.is_authenticated else None,
            buyers=buyers,
            sellers=sellers,
            scenario=scenario,
            market_type=market_type,
            iterations=200,
            prices=data["prices"],
            demand=data["demand"],
            sales=data["sales"]
        )
        sim.calculate_analytics()
    else:
        data = run_simulation()
    
    # Get user's simulations or recent ones
    if request.user.is_authenticated:
        history = SimulationRun.objects.filter(owner=request.user).order_by('-created_at')[:10]
    else:
        history = SimulationRun.objects.order_by('-created_at')[:10]
    
    return render(request, "simulation/dashboard.html", {
        "data": data,
        "history": history,
        "scenarios": scenarios,
        "parameters_list": parameters_list,
        "market_types": market_types,
    })


@login_required(login_url='login')
def simulations_list(request):
    """List all user simulations"""
    simulations = SimulationRun.objects.filter(owner=request.user).order_by('-created_at')
    
    # Filter by market type
    market_type_id = request.GET.get('market_type')
    if market_type_id:
        simulations = simulations.filter(market_type_id=market_type_id)
    
    # Filter by date range
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    if start_date:
        simulations = simulations.filter(created_at__gte=start_date)
    if end_date:
        simulations = simulations.filter(created_at__lte=end_date)
    
    # Search
    search_q = request.GET.get('q')
    if search_q:
        simulations = simulations.filter(Q(id__icontains=search_q))
    
    market_types = MarketType.objects.all()
    
    return render(request, 'simulation/simulations_list.html', {
        'simulations': simulations,
        'market_types': market_types,
    })


def simulation_detail(request, sim_id):
    """View simulation details with analytics"""
    simulation = get_object_or_404(SimulationRun, id=sim_id)
    
    # Check permissions
    if simulation.owner and simulation.owner != request.user and not request.user.is_staff:
        if not request.user.is_authenticated:
            return redirect('login')
        return HttpResponse('Unauthorized', status=403)
    
    return render(request, 'simulation/simulation_detail.html', {
        'simulation': simulation
    })


@require_http_methods(["GET", "POST"])
def compare(request):
    """Compare two or more simulations side by side"""
    if request.user.is_authenticated:
        simulations = SimulationRun.objects.filter(owner=request.user)
    else:
        simulations = SimulationRun.objects.all()
    
    sim1 = None
    sim2 = None
    sim3 = None
    
    if request.method == 'POST':
        sim1_id = request.POST.get('sim1')
        sim2_id = request.POST.get('sim2')
        sim3_id = request.POST.get('sim3')
        
        if sim1_id:
            sim1 = get_object_or_404(SimulationRun, id=sim1_id)
        if sim2_id:
            sim2 = get_object_or_404(SimulationRun, id=sim2_id)
        if sim3_id:
            sim3 = get_object_or_404(SimulationRun, id=sim3_id)
    else:
        sim1_id = request.GET.get('sim1')
        sim2_id = request.GET.get('sim2')
        
        if sim1_id:
            sim1 = get_object_or_404(SimulationRun, id=sim1_id)
        if sim2_id:
            sim2 = get_object_or_404(SimulationRun, id=sim2_id)
    
    def calc_stats(sim):
        if not sim:
            return None
        prices = sim.prices if isinstance(sim.prices, list) else json.loads(sim.prices)
        demand = sim.demand if isinstance(sim.demand, list) else json.loads(sim.demand)
        sales = sim.sales if isinstance(sim.sales, list) else json.loads(sim.sales)
        
        return {
            'avg_price': sum(prices) / len(prices) if prices else 0,
            'total_demand': sum(demand) if demand else 0,
            'total_sales': sum(sales) if sales else 0,
            'max_price': max(prices) if prices else 0,
            'min_price': min(prices) if prices else 0,
            'volatility': float(np.std(prices)) if prices else 0,
        }
    
    stats1 = calc_stats(sim1)
    stats2 = calc_stats(sim2)
    stats3 = calc_stats(sim3)
    
    return render(request, 'simulation/compare.html', {
        'simulations': simulations[:20],
        'sim1': sim1,
        'sim2': sim2,
        'sim3': sim3,
        'stats1': stats1,
        'stats2': stats2,
        'stats3': stats3,
    })


# ==================== Scenario Management ====================

@login_required(login_url='login')
def scenarios(request):
    """Manage simulation scenarios"""
    scenario_list = SimulationScenario.objects.filter(is_active=True)
    
    if request.method == 'POST':
        name = request.POST.get('name')
        scenario_type = request.POST.get('scenario_type')
        description = request.POST.get('description')
        
        SimulationScenario.objects.create(
            name=name,
            scenario_type=scenario_type,
            description=description,
            parameters={}
        )
        return redirect('scenarios')
    
    return render(request, 'simulation/scenarios.html', {
        'scenarios': scenario_list
    })


@login_required(login_url='login')
def scenario_detail(request, scenario_id):
    """View scenario details"""
    scenario = get_object_or_404(SimulationScenario, id=scenario_id)
    return render(request, 'simulation/scenario_detail.html', {
        'scenario': scenario
    })


# ==================== Parameters Management ====================

@login_required(login_url='login')
def parameters(request):
    """Manage simulation parameters"""
    params_list = SimulationParameters.objects.filter(created_by=request.user)
    market_types = MarketType.objects.all()
    
    if request.method == 'POST':
        SimulationParameters.objects.create(
            name=request.POST.get('name'),
            num_buyers=int(request.POST.get('num_buyers', 50)),
            num_sellers=int(request.POST.get('num_sellers', 5)),
            iterations=int(request.POST.get('iterations', 200)),
            buyer_budget_min=int(request.POST.get('buyer_budget_min', 50)),
            buyer_budget_max=int(request.POST.get('buyer_budget_max', 200)),
            buyer_wtp_min=int(request.POST.get('buyer_wtp_min', 20)),
            buyer_wtp_max=int(request.POST.get('buyer_wtp_max', 150)),
            seller_price_min=int(request.POST.get('seller_price_min', 30)),
            seller_price_max=int(request.POST.get('seller_price_max', 100)),
            price_adjustment_factor=float(request.POST.get('price_adjustment_factor', 0.05)),
            market_type_id=request.POST.get('market_type') or None,
            created_by=request.user
        )
        return redirect('parameters')
    
    return render(request, 'simulation/parameters.html', {
        'parameters': params_list,
        'market_types': market_types
    })


# ==================== Export Functions ====================

def export_csv(request, sim_id):
    """Export simulation as CSV"""
    simulation = get_object_or_404(SimulationRun, id=sim_id)
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="simulation_{sim_id}.csv"'
    
    prices = simulation.prices if isinstance(simulation.prices, list) else json.loads(simulation.prices)
    demand = simulation.demand if isinstance(simulation.demand, list) else json.loads(simulation.demand)
    sales = simulation.sales if isinstance(simulation.sales, list) else json.loads(simulation.sales)
    
    writer = csv.writer(response)
    writer.writerow(['Step', 'Price', 'Demand', 'Sales'])
    
    for i in range(len(prices)):
        writer.writerow([i, prices[i], demand[i], sales[i]])
    
    return response


def export_excel(request, sim_id=None):
    """Export simulation as Excel"""
    if sim_id:
        simulation = get_object_or_404(SimulationRun, id=sim_id)
        prices = simulation.prices if isinstance(simulation.prices, list) else json.loads(simulation.prices)
        demand = simulation.demand if isinstance(simulation.demand, list) else json.loads(simulation.demand)
        sales = simulation.sales if isinstance(simulation.sales, list) else json.loads(simulation.sales)
        filename = f"simulation_{sim_id}.xlsx"
    else:
        data = run_simulation()
        prices = data["prices"]
        demand = data["demand"]
        sales = data["sales"]
        filename = "simulation.xlsx"

    wb = Workbook()
    ws = wb.active
    ws.title = "Simulation Data"

    # Headers
    ws.append(["Step", "Price", "Demand", "Sales"])

    for i in range(len(prices)):
        ws.append([i, prices[i], demand[i], sales[i]])

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response['Content-Disposition'] = f'attachment; filename={filename}'

    wb.save(response)
    return response


def export_pdf(request, sim_id):
    """Export simulation report as PDF"""
    simulation = get_object_or_404(SimulationRun, id=sim_id)
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1f77b4'),
        spaceAfter=30,
    )
    elements.append(Paragraph(f"Simulation Report #{simulation.id}", title_style))
    elements.append(Spacer(1, 0.3*inch))
    
    # Basic Info
    info_data = [
        ['Parameter', 'Value'],
        ['Simulation ID', str(simulation.id)],
        ['Date', simulation.created_at.strftime('%Y-%m-%d %H:%M:%S')],
        ['Buyers', str(simulation.buyers)],
        ['Sellers', str(simulation.sellers)],
        ['Iterations', str(simulation.iterations)],
        ['Market Type', simulation.market_type.get_name_display() if simulation.market_type else 'N/A'],
    ]
    
    info_table = Table(info_data)
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 0.5*inch))
    
    # Analytics
    elements.append(Paragraph("Analytics", styles['Heading2']))
    analytics_data = [
        ['Metric', 'Value'],
        ['Average Price', f"${simulation.avg_price:.2f}"],
        ['Max Price', f"${simulation.max_price:.2f}"],
        ['Min Price', f"${simulation.min_price:.2f}"],
        ['Price Volatility', f"{simulation.price_volatility:.2f}"],
        ['Total Demand', str(simulation.total_demand)],
        ['Total Sales', str(simulation.total_sales)],
        ['Market Efficiency', f"{simulation.market_efficiency*100:.1f}%"],
    ]
    
    analytics_table = Table(analytics_data)
    analytics_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.lightblue),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(analytics_table)
    
    doc.build(elements)
    buffer.seek(0)
    
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="simulation_{sim_id}_report.pdf"'
    return response


# ==================== AJAX/API Views ====================

@require_http_methods(["GET"])
def get_simulation_data(request, sim_id):
    """Get simulation data as JSON for real-time visualization"""
    simulation = get_object_or_404(SimulationRun, id=sim_id)
    
    prices = simulation.prices if isinstance(simulation.prices, list) else json.loads(simulation.prices)
    demand = simulation.demand if isinstance(simulation.demand, list) else json.loads(simulation.demand)
    sales = simulation.sales if isinstance(simulation.sales, list) else json.loads(simulation.sales)
    
    return JsonResponse({
        'id': simulation.id,
        'prices': prices,
        'demand': demand,
        'sales': sales,
        'avg_price': simulation.avg_price,
        'max_price': simulation.max_price,
        'min_price': simulation.min_price,
        'total_demand': simulation.total_demand,
        'total_sales': simulation.total_sales,
        'market_efficiency': simulation.market_efficiency,
    })


@require_http_methods(["GET"])
def get_analytics(request):
    """Get analytics data for dashboard"""
    if request.user.is_authenticated:
        simulations = SimulationRun.objects.filter(owner=request.user)
    else:
        simulations = SimulationRun.objects.all()
    
    stats = simulations.aggregate(
        avg_price=Avg('avg_price'),
        max_price=Max('max_price'),
        min_price=Min('min_price'),
        total_simulations=Count('id')
    )
    
    # Market type distribution
    market_distribution = simulations.values('market_type__name').count()
    
    return JsonResponse({
        'stats': stats,
        'market_distribution': market_distribution,
    })


from django.db.models import Count

# Re-enable the import at the top if not already there
