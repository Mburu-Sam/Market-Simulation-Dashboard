from django.urls import path
from .views import dashboard, export_excel, compare

urlpatterns = [
    path('', dashboard, name='dashboard'),
    path('export/', export_excel, name='export_excel'),
    path('compare/', compare, name='compare'),
]