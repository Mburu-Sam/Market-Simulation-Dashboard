from django.core.management.base import BaseCommand
from simulation.models import MarketType, SimulationScenario

class Command(BaseCommand):
    help = 'Create default market types and scenarios'

    def handle(self, *args, **options):
        default_markets = [
            {'name': 'competitive', 'description': 'Perfect Competition market with many buyers and sellers.'},
            {'name': 'oligopoly', 'description': 'Oligopoly market with a few dominant sellers.'},
            {'name': 'monopoly', 'description': 'Monopoly market with a single seller.'},
            {'name': 'auction', 'description': 'Auction market where buyers bid for goods.'},
        ]

        for market in default_markets:
            MarketType.objects.get_or_create(name=market['name'], defaults={'description': market['description']})

        default_scenarios = [
            {'name': 'Bull Market', 'scenario_type': 'bull_market', 'description': 'Growing demand and rising prices.'},
            {'name': 'Bear Market', 'scenario_type': 'bear_market', 'description': 'Falling prices and low demand.'},
            {'name': 'Recession', 'scenario_type': 'recession', 'description': 'Weak buyer activity and challenging competition.'},
            {'name': 'Boom', 'scenario_type': 'boom', 'description': 'High demand with strong price growth.'},
            {'name': 'Stable Market', 'scenario_type': 'stable', 'description': 'Balanced conditions and predictable activity.'},
            {'name': 'Volatile Market', 'scenario_type': 'volatile', 'description': 'Sharp fluctuations in demand and pricing.'},
        ]

        for scenario in default_scenarios:
            SimulationScenario.objects.get_or_create(
                name=scenario['name'],
                defaults={
                    'scenario_type': scenario['scenario_type'],
                    'description': scenario['description'],
                    'parameters': {}
                }
            )

        self.stdout.write(self.style.SUCCESS('Default market types and scenarios created.'))
