import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

class InventorySimulation:
    def __init__(self, forecast_data_file, errors_data_file, lead_time_data_file, total_periods, review_period, service_level):
        self.forecast_data = pd.read_csv(forecast_data_file)
        self.errors_data = pd.read_csv(errors_data_file)
        self.lead_time_data = pd.read_csv(lead_time_data_file)
        self.total_periods = total_periods
        self.review_period = review_period
        self.service_level = service_level
        
        # Estimate the distribution of total demand during lead time using historical data
        self.lead_time_demand_distribution = self.estimate_lead_time_demand_distribution()
        
        # Determine the safety stock
        self.safety_stock = self.calculate_safety_stock(service_level)

    def estimate_lead_time_demand_distribution(self):
        # Using historical data to calculate total demand during each historical lead time period
        total_demand_during_lead_time = []
        for lead_time in self.lead_time_data['lead_time']:
            total_demand = sum(np.random.choice(self.errors_data['errors'], size=lead_time) + self.forecast_data['forecast'].sample(lead_time, replace=True))
            total_demand_during_lead_time.append(total_demand)
        return np.array(total_demand_during_lead_time)

    def calculate_safety_stock(self, service_level):
        # Determine the safety stock level required to achieve the desired service level
        return np.percentile(self.lead_time_demand_distribution, 100 * (1 - service_level))

    def simulate_replenishment(self):
        inventory_levels = []  # List to keep track of inventory levels
        order_quantities = []  # List to keep track of order quantities
        inventory_level = self.safety_stock  # Start with safety stock level
        
        # Simulation loop
        for period in range(self.total_periods):
            demand = self.forecast_data.loc[period, 'forecast'] + np.random.choice(self.errors_data['errors'])
            inventory_level = max(0, inventory_level - demand)  # Update inventory level after demand
            inventory_levels.append(inventory_level)
            
            # Check if it's a review period and place an order if necessary
            order_quantity = 0  # Reset order quantity for each period
            if period % self.review_period == 0:
                order_up_to_level = self.safety_stock + sum(self.forecast_data.loc[period:period + self.review_period - 1, 'forecast'])
                order_quantity = max(0, order_up_to_level - inventory_level)  # Order up to the target level
            order_quantities.append(order_quantity)
            inventory_level += order_quantity  # Update inventory level after order
        
        return inventory_levels, order_quantities

    def plot_simulation(self, inventory_levels, order_quantities):
        plt.figure(figsize=(10, 6))
        plt.plot(inventory_levels, label='Inventory Level')
        plt.plot(order_quantities, label='Order Quantity')
        plt.xlabel('Period')
        plt.ylabel('Quantity')
        plt.legend()
        plt.show()

# Usage example:
sim = InventorySimulation('forecast_data.csv', 'errors_data.csv', 'lead_time_data.csv', total_periods=10, review_period=2, service_level=0.95)
inventory_levels, order_quantities = sim.simulate_replenishment()
sim.plot_simulation(inventory_levels, order_quantities)