import podeus
import numpy as np
import matplotlib.pyplot as plt

# define drinks
beer = podeus.Drink(volume_dl=5, kcal=120, alcohol_percentage=5, time_start_min=0, time_end_min=30)

# (optional) define meals
meal = podeus.Meal(kcal=500, time_start_min=0)  # meal at t=0, or set to later time if you want to simulate meal effects

drinks = [beer]
meals = [meal]  # or []

# simulate
t_sim = np.arange(0, 240, 0.1)  # simulate for 4 hours with 1000 time points
solution, outputs = podeus.simulate_podeus(t_sim, sex='female', weight=70.0, height=1.75, drinks=drinks, meals=meals)
solution_nomeal, outputs_nomeal = podeus.simulate_podeus(t_sim, sex='female', weight=70.0, height=1.75, drinks=drinks, meals=[])

with_meal, = plt.plot(t_sim, outputs['promille'], color='red', alpha=0.5, label='With Meal')
without_meal, = plt.plot(t_sim, outputs_nomeal['promille'], color='blue', alpha=0.5, label='Without Meal')
beer_times = plt.vlines([beer.time_start_min, beer.time_end_min], ymin=0, ymax=0.25, colors='gray', linestyles='dashed', label='Drink Timing')
beer_duration = plt.fill_betweenx([0, 0.25], beer.time_start_min, beer.time_end_min, color='gray', alpha=0.2, label='Drink Timing')
plt.xlabel('Time (min)')
plt.ylabel('BAC (‰)') 
plt.legend([with_meal, without_meal, (beer_times, beer_duration)], ['With Meal', 'Without Meal', 'Drink Timing'])
plt.show()