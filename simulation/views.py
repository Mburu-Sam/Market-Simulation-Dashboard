from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from openpyxl import Workbook
from .models import run_simulation, SimulationRun

def export_excel(request):
    data = run_simulation()

    wb = Workbook()
    ws = wb.active
    ws.title = "Simulation Data"

    # Headers
    ws.append(["Step", "Price", "Demand", "Sales"])

    for i in range(len(data["prices"])):
        ws.append([
            i,
            data["prices"][i],
            data["demand"][i],
            data["sales"][i]
        ])

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response['Content-Disposition'] = 'attachment; filename=simulation.xlsx'

    wb.save(response)
    return response


def compare(request):
    """Compare two simulations side by side"""
    sim1_id = request.GET.get('sim1')
    sim2_id = request.GET.get('sim2')
    
    simulations = SimulationRun.objects.order_by('-created_at')[:10]
    
    sim1 = None
    sim2 = None
    
    if sim1_id:
        sim1 = get_object_or_404(SimulationRun, id=sim1_id)
    if sim2_id:
        sim2 = get_object_or_404(SimulationRun, id=sim2_id)
    
    # Calculate stats for comparison
    def calc_stats(sim):
        if not sim:
            return None
        return {
            'avg_price': sum(sim.prices) / len(sim.prices),
            'total_demand': sum(sim.demand),
            'total_sales': sum(sim.sales),
            'max_price': max(sim.prices),
            'min_price': min(sim.prices),
        }
    
    stats1 = calc_stats(sim1)
    stats2 = calc_stats(sim2)
    
    return render(request, 'simulation/compare.html', {
        'simulations': simulations,
        'sim1': sim1,
        'sim2': sim2,
        'stats1': stats1,
        'stats2': stats2,
    })


def dashboard(request):
    if request.method == "POST":
        buyers = int(request.POST.get("buyers"))
        sellers = int(request.POST.get("sellers"))

        data = run_simulation(buyers, sellers)

        # Save to DB
        SimulationRun.objects.create(
            buyers=buyers,
            sellers=sellers,
            prices=data["prices"],
            demand=data["demand"],
            sales=data["sales"]
        )
    else:
        data = run_simulation()

    history = SimulationRun.objects.order_by('-created_at')[:5]

    return render(request, "simulation/dashboard.html", {
        "data": data,
        "history": history
    })
