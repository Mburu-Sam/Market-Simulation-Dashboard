from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views_api import SimulationViewSet, ScenarioViewSet, ParametersViewSet, MarketTypeViewSet

router = DefaultRouter()
router.register(r'api/simulations', SimulationViewSet, basename='api-simulation')
router.register(r'api/scenarios', ScenarioViewSet, basename='api-scenario')
router.register(r'api/parameters', ParametersViewSet, basename='api-parameters')
router.register(r'api/market-types', MarketTypeViewSet, basename='api-market-type')

urlpatterns = [
    # Authentication
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    
    # Core Views
    path('', views.dashboard, name='dashboard'),
    path('simulations/', views.simulations_list, name='simulations_list'),
    path('simulations/<int:sim_id>/', views.simulation_detail, name='simulation_detail'),
    path('compare/', views.compare, name='compare'),
    
    # Scenarios
    path('scenarios/', views.scenarios, name='scenarios'),
    path('scenarios/<int:scenario_id>/', views.scenario_detail, name='scenario_detail'),
    
    # Parameters
    path('parameters/', views.parameters, name='parameters'),
    
    # Export
    path('export/csv/<int:sim_id>/', views.export_csv, name='export_csv'),
    path('export/excel/', views.export_excel, name='export_excel'),
    path('export/excel/<int:sim_id>/', views.export_excel, name='export_excel_sim'),
    path('export/pdf/<int:sim_id>/', views.export_pdf, name='export_pdf'),
    
    # AJAX/API
    path('api/simulation-data/<int:sim_id>/', views.get_simulation_data, name='api_simulation_data'),
    path('api/analytics/', views.get_analytics, name='api_analytics'),
    
    # REST API
    path('', include(router.urls)),
]