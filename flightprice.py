# -*- coding: utf-8 -*-
"""
Created on Sat Sep 28 15:59:31 2024

@author: Asus
"""

## Loading all the required libraries 

import pandas as pd
from pulp import * # Import all the module from pulp
import warnings
warnings.filterwarnings('ignore')


# Load datasets individually
manvar_costs  = pd.read_excel('datasets/variable_costs.xlsx', index_col=0)
freight_costs = pd.read_excel('datasets/freight_costs.xlsx', index_col=0)
fixed_cost = pd.read_excel('datasets/fixed_cost.xlsx', index_col=0)
plant_capacity = pd.read_excel('datasets/capacity.xlsx', index_col=0)
demand = pd.read_excel('datasets/demand.xlsx')

# Display the first 5 rows of each dataset
print("--- Manufacturing Cost ---")
print(manvar_costs .head(), "\n")

print("--- Freight Costs ---")
print(freight_costs.head(), "\n")

print("--- Fixed Cost ---")
print(fixed_cost.head(), "\n")

print("--- Plant Capacity ---")
print(plant_capacity.head(), "\n")

print("--- Demand ---")
print(demand.head(), "\n")

# Variable Costs
var_cost = freight_costs/1000 + manvar_costs 

# Define Decision Variables
loc = ['USA', 'Germany', 'Japan', 'Brazil', 'India']
size = ['Low', 'High']

# Initialize Class
model = LpProblem("Capacitated Plant Location Model", LpMinimize)


# Create Decision Variables
x = LpVariable.dicts("production_", [(i,j) for i in loc for j in loc],
                     lowBound=0, upBound=None, cat='continuous')
y = LpVariable.dicts("plant_", 
                     [(i,s) for s in size for i in loc], cat='Binary')

# Define Objective Function
model += (lpSum([fixed_cost.loc[i,s] * y[(i,s)] * 1000 for s in size for i in loc])
          + lpSum([var_cost.loc[i,j] * x[(i,j)]   for i in loc for j in loc]))

# Add Constraints
for j in loc:
    model += lpSum([x[(i, j)] for i in loc]) == demand.loc[j,'Demand']
for i in loc:
    model += lpSum([x[(i, j)] for j in loc]) <= lpSum([cap.loc[i,s]*y[(i,s)] * 1000
                                                       for s in size])
                                                    
                                                       
# Solve Model
model.solve()
print("Total Costs = {:,} ($/Month)".format(int(value(model.objective))))
print('\n' + "Status: {}".format(LpStatus[model.status]))

# Dictionnary
dict_plant = {}
dict_prod = {}
for v in model.variables():
    if 'plant' in v.name:
        name = v.name.replace('plant__', '').replace('_', '')
        dict_plant[name] = int(v.varValue)
        p_name = name
    else:
        name = v.name.replace('production__', '').replace('_', '')
        dict_prod[name] = v.varValue
    print(name, "=", v.varValue)

# Capacity Plant
list_low, list_high = [], []
for l in loc:
    for cap in ['Low', 'High']:
        x = "('{}','{}')".format(l, cap)
        if cap == 'Low':
            list_low.append(dict_plant[x])
        else:
            list_high.append(dict_plant[x])
df_capacity = pd.DataFrame({'Location': loc, 'Low': list_low, 'High': list_high}).set_index('Location')
    
df_capacity
