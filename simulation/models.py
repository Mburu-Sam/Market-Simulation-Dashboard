import numpy as np

from django.db import models

class SimulationRun(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    buyers = models.IntegerField()
    sellers = models.IntegerField()
    prices = models.JSONField()
    demand = models.JSONField()
    sales = models.JSONField()

def run_simulation(num_buyers=50, num_sellers=5):
    iterations = 100

    buyers_budget = np.random.randint(50, 200, num_buyers)
    buyers_wtp = np.random.randint(20, 150, num_buyers)
    seller_prices = np.random.randint(30, 100, num_sellers)

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
                seller_prices[j] *= 1.05
            else:
                seller_prices[j] *= 0.95

            seller_prices[j] = max(1, seller_prices[j])

        price_history.append(float(np.mean(seller_prices)))
        demand_history.append(int(total_demand))
        sales_history.append(int(np.sum(sales)))

    return {
        "prices": price_history,
        "demand": demand_history,
        "sales": sales_history
    }