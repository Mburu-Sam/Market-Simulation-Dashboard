from rest_framework import serializers
from django.contrib.auth.models import User
from .models import SimulationRun, SimulationParameters, SimulationScenario, MarketType


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class MarketTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarketType
        fields = ['id', 'name', 'description']


class SimulationScenarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = SimulationScenario
        fields = ['id', 'name', 'scenario_type', 'description', 'parameters', 'is_active', 'created_at']


class SimulationParametersSerializer(serializers.ModelSerializer):
    market_type_name = serializers.CharField(source='market_type.get_name_display', read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = SimulationParameters
        fields = [
            'id', 'name', 'num_buyers', 'num_sellers', 'iterations',
            'buyer_budget_min', 'buyer_budget_max', 'buyer_wtp_min', 'buyer_wtp_max',
            'seller_price_min', 'seller_price_max', 'price_adjustment_factor',
            'market_type', 'market_type_name', 'created_by', 'created_by_name', 'created_at'
        ]


class SimulationRunSerializer(serializers.ModelSerializer):
    owner_name = serializers.CharField(source='owner.username', read_only=True)
    market_type_name = serializers.CharField(source='market_type.get_name_display', read_only=True)
    scenario_name = serializers.CharField(source='scenario.name', read_only=True)
    
    class Meta:
        model = SimulationRun
        fields = [
            'id', 'owner', 'owner_name', 'parameters', 'scenario', 'scenario_name',
            'market_type', 'market_type_name', 'created_at', 'updated_at',
            'buyers', 'sellers', 'iterations', 'prices', 'demand', 'sales',
            'avg_price', 'max_price', 'min_price', 'price_volatility',
            'total_demand', 'total_sales', 'market_efficiency', 'price_elasticity'
        ]
        read_only_fields = ['created_at', 'updated_at', 'avg_price', 'max_price', 'min_price',
                          'price_volatility', 'total_demand', 'total_sales', 'market_efficiency',
                          'price_elasticity']


class SimulationRunDetailSerializer(SimulationRunSerializer):
    """Extended serializer with related objects"""
    parameters_data = SimulationParametersSerializer(source='parameters', read_only=True)
    scenario_data = SimulationScenarioSerializer(source='scenario', read_only=True)
    
    class Meta(SimulationRunSerializer.Meta):
        fields = SimulationRunSerializer.Meta.fields + ['parameters_data', 'scenario_data']
