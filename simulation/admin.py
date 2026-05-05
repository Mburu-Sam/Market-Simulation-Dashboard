from django.contrib import admin
from .models import SimulationRun, SimulationParameters, SimulationScenario, MarketType


@admin.register(MarketType)
class MarketTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']


@admin.register(SimulationScenario)
class SimulationScenarioAdmin(admin.ModelAdmin):
    list_display = ['name', 'scenario_type', 'is_active', 'created_at']
    list_filter = ['scenario_type', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at']


@admin.register(SimulationParameters)
class SimulationParametersAdmin(admin.ModelAdmin):
    list_display = ['name', 'num_buyers', 'num_sellers', 'market_type', 'created_by', 'created_at']
    list_filter = ['market_type', 'created_at', 'created_by']
    search_fields = ['name']
    readonly_fields = ['created_at']
    fieldsets = (
        ('Basic Info', {
            'fields': ('name', 'market_type', 'created_by', 'created_at')
        }),
        ('Market Participants', {
            'fields': ('num_buyers', 'num_sellers')
        }),
        ('Simulation Settings', {
            'fields': ('iterations', 'price_adjustment_factor')
        }),
        ('Buyer Parameters', {
            'fields': ('buyer_budget_min', 'buyer_budget_max', 'buyer_wtp_min', 'buyer_wtp_max')
        }),
        ('Seller Parameters', {
            'fields': ('seller_price_min', 'seller_price_max')
        }),
    )


@admin.register(SimulationRun)
class SimulationRunAdmin(admin.ModelAdmin):
    list_display = ['id', 'owner', 'buyers', 'sellers', 'market_type', 'avg_price', 'market_efficiency', 'created_at']
    list_filter = ['market_type', 'created_at', 'owner']
    search_fields = ['owner__username', 'id']
    readonly_fields = ['created_at', 'updated_at', 'avg_price', 'max_price', 'min_price',
                      'price_volatility', 'total_demand', 'total_sales', 'market_efficiency']
    fieldsets = (
        ('Ownership & Settings', {
            'fields': ('owner', 'parameters', 'scenario', 'market_type')
        }),
        ('Participants', {
            'fields': ('buyers', 'sellers', 'iterations')
        }),
        ('Time Series Data', {
            'fields': ('prices', 'demand', 'sales'),
            'classes': ('collapse',)
        }),
        ('Analytics', {
            'fields': ('avg_price', 'max_price', 'min_price', 'price_volatility',
                      'total_demand', 'total_sales', 'market_efficiency', 'price_elasticity')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
