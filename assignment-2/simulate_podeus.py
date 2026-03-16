import podeus
import numpy as np
import matplotlib.pyplot as plt


# define drinks
beer = podeus.Drink(volume_dl=10, alcohol_percentage=5, kcal=240, time_start_min=0, time_end_min=60)

# define meals
meal = podeus.Meal(kcal=500, time_start_min=0)  # meal at t=0

drinks = [beer]
meals = [meal]  

# simulate
t_sim = np.arange(0, 720, 0.1)  # for 720 minutes (12 hours) with small time steps
solution, outputs = podeus.simulate_podeus(t_sim, sex='male', height=1.75, weight=70.0, drinks=drinks, meals=meals)
solution_nomeal, outputs_nomeal = podeus.simulate_podeus(t_sim, sex='male', height=1.75, weight=70.0, drinks=drinks, meals=[])


with_meal, = plt.plot(t_sim, outputs['promille'], color='red', alpha=0.5, label='With Meal')
without_meal, = plt.plot(t_sim, outputs_nomeal['promille'], color='blue', alpha=0.5, label='Without Meal')
beer_times = plt.vlines([beer.time_start_min, beer.time_end_min], ymin=0, ymax=0.25, colors='gray', linestyles='dashed', label='Drink Timing')
beer_duration = plt.fill_betweenx([0, 0.25], beer.time_start_min, beer.time_end_min, color='gray', alpha=0.2, label='Drink Timing')
plt.xlabel('Time (min)')
plt.ylabel('BAC (‰)')
plt.legend([with_meal, without_meal, (beer_times, beer_duration)], ['With Meal', 'Without Meal', 'Drink Timing'])
plt.show()

params_base = [
1.4599e4,
1.5695e2,
1.7416e4,
5.8081e-3,
1.0155e1,
4.0227e-1,
2.1545e3,
1.7793e4,
1.5843e2,
8.4172e1,
8.3001e2,
1.3079e-1,
9.6381e-1,
1.7148e-1,
9.2200e0,
3.6880e1,
6.1804e-3
]

plt.figure()

# new parameter for the formation of new liver scenarios by adjusting the Vmax of ADH and CYP2E1
def make_liver_scenario(params, adh_factor=1.0, cyp_factor=1.0):
    new_param= params.copy()
    new_param[12] *= adh_factor   # vmax_adh
    new_param[13] *= cyp_factor   # vmax_cyp2e1
    return new_param

# calculate the time it takes for the BAC to drop below the threshold, after the BAC peak has been reached. 
def get_full_recovery_time(t, bac, threshold=0.2):
    peak_index = np.argmax(bac)

    for i in range(peak_index, len(bac)):
        if bac[i] < threshold:
            return t[i] - t[peak_index]   

    return np.nan   

#plot baseline simulation with given parameters. 
solution_base, outputs_base = podeus.simulate_podeus(t_sim, sex='male', height=1.75, weight=70.0, drinks=drinks, meals=meals, params=params_base)
plt.plot(t_sim, outputs_base['promille'], label='baseline')

param_names = ["vmax_adh", "vmax_cyp2e1"]
indices = [12, 13]

# calculate the local sensitivity of ADH at 10% (to confirm chosen factors)
for name, i in zip(param_names, indices):
    params_high = params_base.copy()
    params_high[i] *= 1.1
    solution_high, output_high = podeus.simulate_podeus(t_sim, sex='male', height=1.80, weight=80.0, drinks=drinks, meals=meals, params=params_high)
    plt.plot(t_sim, output_high['promille'], label=name + ' +10%')

    params_low = params_base.copy()
    params_low[i] *= 0.9
    solution_low, output_low = podeus.simulate_podeus(t_sim, sex='male', height=1.80, weight=80.0, drinks=drinks, meals=meals, params=params_low)
    plt.plot(t_sim, output_low['promille'], linestyle='--', label=name + ' -10%')

#plot the local sensitivity analysis for ADH at 10%
plt.xlabel('Time (min)')
plt.ylabel('BAC (‰)')
plt.title('Local sensitivity analysis of BAC')
plt.legend()
plt.show()

#Use of BMI to answer the research question.
bmi_values = [18.5, 23, 27, 32]
height = 1.80 
weights = []

#look at each BMI
for bmi in bmi_values:
    weight = bmi* height**2
    weights.append(weight)

# linking the CYP2E1 and ADH to different scenarios    
liver_scenarios = {"Healthy liver": (1.0, 1.0),
                   "Mildly damaged liver": (0.7559 , 1.75),
                   "Damaged liver": (0.6324, 2.75), 
                   "Extremely damaged liver": (0.5423, 3.4)}

# empty dictionary for our results
recovery_table = {}

# calculating recovery time for each BMI and liver condition
for bmi, weight in zip(bmi_values, weights):
    recovery_table[bmi] = {}

    for liver_name, (adh_factor, cyp_factor) in liver_scenarios.items():
        params_new = make_liver_scenario(params_base, adh_factor, cyp_factor)
        solution, outputs = podeus.simulate_podeus(t_sim,sex="male", height=height, weight=weight, drinks=drinks, meals=meals, params=params_new)
        bac = outputs['promille']
        recovery_time = get_full_recovery_time(t_sim, bac)
        recovery_table[bmi][liver_name] = recovery_time

# add values to table.
print("\nFull recovery time table (minutes):\n")

header = f"{'BMI':<8}{'Healthy liver':<20}{'Mildly damaged liver':<24}{'Damaged liver':<20}{'Extremely damaged liver':<20}"
print(header)
print("-" * len(header))

for bmi in bmi_values:
    healthy_liver = recovery_table[bmi]["Healthy liver"]
    mildly_damaged_liver = recovery_table[bmi]["Mildly damaged liver"]
    damaged_liver = recovery_table[bmi]["Damaged liver"]
    extremely_damaged_liver = recovery_table[bmi]["Extremely damaged liver"]

    row = f"{bmi:<8}{healthy_liver:<20.2f}{mildly_damaged_liver:<24.2f}{damaged_liver:<20.2f}{extremely_damaged_liver:<20.2f}"
    print(row)

#plot BAC curves 
for liver_name, (adh_factor, cyp_factor) in liver_scenarios.items():
    plt.figure()

    for bmi, weight in zip(bmi_values, weights):
        params_new = make_liver_scenario(params_base, adh_factor, cyp_factor)

        solution, outputs = podeus.simulate_podeus(t_sim, sex="male", height=height, weight=weight, drinks=drinks, meals=meals, params=params_new)

        plt.plot(t_sim, outputs['promille'], label='BMI ' + str(bmi))

    plt.xlabel('Time (min)')
    plt.ylabel('BAC (‰)')
    plt.title('BAC curves - ' + liver_name)
    plt.legend()
    plt.show()