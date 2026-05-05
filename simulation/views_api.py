from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from .models import SimulationRun, SimulationParameters, SimulationScenario, MarketType
from .serializers import (
    SimulationRunSerializer, SimulationRunDetailSerializer,
    SimulationParametersSerializer, SimulationScenarioSerializer,
    MarketTypeSerializer
)


class IsOwnerOrReadOnly(permissions.BasePermission):
    """Permission to only allow owners to edit their simulations"""
    
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.owner == request.user or request.user.is_staff


class SimulationViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing simulations
    List, create, retrieve, update, delete simulations
    """
    serializer_class = SimulationRunSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['market_type', 'scenario', 'buyers', 'sellers']
    search_fields = ['id', 'owner__username']
    ordering_fields = ['created_at', 'avg_price', 'total_sales']
    ordering = ['-created_at']
    
    def get_queryset(self):
        if self.request.user.is_authenticated:
            return SimulationRun.objects.filter(owner=self.request.user)
        return SimulationRun.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return SimulationRunDetailSerializer
        return SimulationRunSerializer
    
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
    
    @action(detail=True, methods=['get'])
    def analytics(self, request, pk=None):
        """Get detailed analytics for a simulation"""
        simulation = self.get_object()
        return Response({
            'id': simulation.id,
            'avg_price': simulation.avg_price,
            'max_price': simulation.max_price,
            'min_price': simulation.min_price,
            'price_volatility': simulation.price_volatility,
            'total_demand': simulation.total_demand,
            'total_sales': simulation.total_sales,
            'market_efficiency': simulation.market_efficiency,
            'price_elasticity': simulation.price_elasticity,
        })
    
    @action(detail=True, methods=['get'])
    def time_series(self, request, pk=None):
        """Get time series data for visualization"""
        simulation = self.get_object()
        import json
        prices = simulation.prices if isinstance(simulation.prices, list) else json.loads(simulation.prices)
        demand = simulation.demand if isinstance(simulation.demand, list) else json.loads(simulation.demand)
        sales = simulation.sales if isinstance(simulation.sales, list) else json.loads(simulation.sales)
        
        return Response({
            'prices': prices,
            'demand': demand,
            'sales': sales,
        })
    
    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        """Create multiple simulations at once"""
        simulations_data = request.data
        if not isinstance(simulations_data, list):
            return Response(
                {'error': 'Expected a list of simulations'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        simulations = []
        for data in simulations_data:
            serializer = self.get_serializer(data=data)
            if serializer.is_valid():
                serializer.save(owner=request.user)
                simulations.append(serializer.data)
        
        return Response(simulations, status=status.HTTP_201_CREATED)


class ScenarioViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing simulation scenarios
    """
    queryset = SimulationScenario.objects.filter(is_active=True)
    serializer_class = SimulationScenarioSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'scenario_type']
    ordering = ['-created_at']
    
    @action(detail=False, methods=['get'])
    def by_type(self, request):
        """Get scenarios filtered by type"""
        scenario_type = request.query_params.get('type')
        if not scenario_type:
            return Response(
                {'error': 'type parameter required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        scenarios = self.queryset.filter(scenario_type=scenario_type)
        serializer = self.get_serializer(scenarios, many=True)
        return Response(serializer.data)


class ParametersViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing simulation parameters
    """
    serializer_class = SimulationParametersSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['market_type']
    search_fields = ['name']
    ordering_fields = ['created_at', 'num_buyers', 'num_sellers']
    ordering = ['-created_at']
    
    def get_queryset(self):
        return SimulationParameters.objects.filter(created_by=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def use_for_simulation(self, request, pk=None):
        """Use this parameter set to run a simulation"""
        from .models import run_simulation, SimulationRun
        
        params = self.get_object()
        data = run_simulation(
            num_buyers=params.num_buyers,
            num_sellers=params.num_sellers,
            iterations=params.iterations,
            params=params
        )
        
        sim = SimulationRun.objects.create(
            owner=request.user,
            parameters=params,
            market_type=params.market_type,
            buyers=params.num_buyers,
            sellers=params.num_sellers,
            iterations=params.iterations,
            prices=data['prices'],
            demand=data['demand'],
            sales=data['sales']
        )
        sim.calculate_analytics()
        
        return Response(
            SimulationRunSerializer(sim).data,
            status=status.HTTP_201_CREATED
        )


class MarketTypeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for viewing market types (read-only)
    """
    queryset = MarketType.objects.all()
    serializer_class = MarketTypeSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description']
