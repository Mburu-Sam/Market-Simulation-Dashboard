import numpy as np
import json
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class MarketType(models.Model):
    """Different market simulation types"""
    MARKET_CHOICES = [
        ('competitive', 'Perfect Competition'),
        ('oligopoly', 'Oligopoly'),
        ('monopoly', 'Monopoly'),
        ('auction', 'Auction Market'),
    ]
    
    name = models.CharField(max_length=50, choices=MARKET_CHOICES, unique=True)
    description = models.TextField()
    
    class Meta:
        verbose_name_plural = "Market Types"
    
    def __str__(self):
        return self.get_name_display()


class SimulationScenario(models.Model):
    """Preset scenarios for simulations"""
    SCENARIO_TYPES = [
        ('bull_market', 'Bull Market'),
        ('bear_market', 'Bear Market'),
        ('recession', 'Recession'),
        ('boom', 'Economic Boom'),
        ('stable', 'Stable Market'),
        ('volatile', 'Volatile Market'),
    ]
    
    name = models.CharField(max_length=100)
    scenario_type = models.CharField(max_length=20, choices=SCENARIO_TYPES)
    description = models.TextField()
    parameters = models.JSONField(default=dict)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.get_scenario_type_display()})"


class SimulationParameters(models.Model):
    """Customizable simulation parameters"""
    name = models.CharField(max_length=100)
    num_buyers = models.IntegerField(default=50)
    num_sellers = models.IntegerField(default=5)
    iterations = models.IntegerField(default=200)
    buyer_budget_min = models.IntegerField(default=50)
    buyer_budget_max = models.IntegerField(default=200)
    buyer_wtp_min = models.IntegerField(default=20)
    buyer_wtp_max = models.IntegerField(default=150)
    seller_price_min = models.IntegerField(default=30)
    seller_price_max = models.IntegerField(default=100)
    price_adjustment_factor = models.FloatField(default=0.05)
    market_type = models.ForeignKey(MarketType, on_delete=models.SET_NULL, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Simulation Parameters"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.num_buyers}B, {self.num_sellers}S)"


class SimulationRun(models.Model):
    """Records of simulation runs with analytics"""
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='simulations')
    parameters = models.ForeignKey(SimulationParameters, on_delete=models.SET_NULL, null=True, blank=True)
    scenario = models.ForeignKey(SimulationScenario, on_delete=models.SET_NULL, null=True, blank=True)
    market_type = models.ForeignKey(MarketType, on_delete=models.SET_NULL, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Basic data
    buyers = models.IntegerField()
    sellers = models.IntegerField()
    iterations = models.IntegerField(default=200)
    
    # Time series data
    prices = models.JSONField()
    demand = models.JSONField()
    sales = models.JSONField()
    
    # Analytics
    avg_price = models.FloatField(null=True, blank=True)
    max_price = models.FloatField(null=True, blank=True)
    min_price = models.FloatField(null=True, blank=True)
    price_volatility = models.FloatField(null=True, blank=True)
    total_demand = models.IntegerField(null=True, blank=True)
    total_sales = models.IntegerField(null=True, blank=True)
    market_efficiency = models.FloatField(null=True, blank=True)
    price_elasticity = models.FloatField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['owner', '-created_at']),
            models.Index(fields=['market_type', '-created_at']),
        ]
    
    def calculate_analytics(self):
        """Calculate analytics from simulation data"""
        prices = self.prices if isinstance(self.prices, list) else json.loads(self.prices)
        demand = self.demand if isinstance(self.demand, list) else json.loads(self.demand)
        sales = self.sales if isinstance(self.sales, list) else json.loads(self.sales)
        
        if prices:
            self.avg_price = float(np.mean(prices))
            self.max_price = float(np.max(prices))
            self.min_price = float(np.min(prices))
            self.price_volatility = float(np.std(prices))
        
        if demand:
            self.total_demand = int(np.sum(demand))
        
        if sales:
            self.total_sales = int(np.sum(sales))
        
        # Market efficiency (ratio of total sales to total demand)
        if self.total_demand and self.total_demand > 0:
            self.market_efficiency = (self.total_sales / self.total_demand) if self.total_sales else 0
        
        self.save()
    
    def __str__(self):
        return f"Simulation {self.id} - {self.buyers}B/{self.sellers}S ({self.created_at.strftime('%Y-%m-%d')})"


def run_simulation(num_buyers=50, num_sellers=5, iterations=200, params=None):
    """
    Run market simulation with configurable parameters
    
    Args:
        num_buyers: Number of buyers in market
        num_sellers: Number of sellers in market
        iterations: Number of simulation steps
        params: Optional SimulationParameters instance or dict with custom settings
    """
    if params and isinstance(params, SimulationParameters):
        num_buyers = params.num_buyers
        num_sellers = params.num_sellers
        iterations = params.iterations
        buyer_budget_min = params.buyer_budget_min
        buyer_budget_max = params.buyer_budget_max
        buyer_wtp_min = params.buyer_wtp_min
        buyer_wtp_max = params.buyer_wtp_max
        seller_price_min = params.seller_price_min
        seller_price_max = params.seller_price_max
        adjustment_factor = params.price_adjustment_factor
    else:
        buyer_budget_min = 50
        buyer_budget_max = 200
        buyer_wtp_min = 20
        buyer_wtp_max = 150
        seller_price_min = 30
        seller_price_max = 100
        adjustment_factor = 0.05

    buyers_budget = np.random.randint(buyer_budget_min, buyer_budget_max, num_buyers)
    buyers_wtp = np.random.randint(buyer_wtp_min, buyer_wtp_max, num_buyers)
    seller_prices = np.random.randint(seller_price_min, seller_price_max, num_sellers)

    price_history = []
    demand_history = []
    sales_history = []

    for t in range(iterations):
        sales = np.zeros(num_sellers)
        total_demand = 0

        for i in range(num_buyers):
            scores = buyers_wtp[i] - seller_prices
            seller_index = np.argmax(scores)

            if buyers_wtp[i] >= seller_prices[seller_index] and buyers_budget[i] >= seller_prices[seller_index]:
                buyers_budget[i] -= seller_prices[seller_index]
                sales[seller_index] += 1
                total_demand += 1

        for j in range(num_sellers):
            if sales[j] > 5:
                seller_prices[j] *= (1 + adjustment_factor)
            else:
                seller_prices[j] *= (1 - adjustment_factor)

            seller_prices[j] = max(1, seller_prices[j])

        price_history.append(float(np.mean(seller_prices)))
        demand_history.append(int(total_demand))
        sales_history.append(int(np.sum(sales)))

    return {
        "prices": price_history,
        "demand": demand_history,
        "sales": sales_history
    }