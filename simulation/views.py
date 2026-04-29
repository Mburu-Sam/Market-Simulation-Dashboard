from django.http import HttpResponse
from django.shortcuts import render
from openpyxl import Workbook
from .models import run_simulation

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
from .models import SimulationRun

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
