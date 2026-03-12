import podeus
import numpy as np
import matplotlib.pyplot as plt

def make_liver_scenario(params, adh_factor=1.0, cyp_factor=1.0):
    p = params.copy()
    p[12] *= adh_factor   # vmax_adh
    p[13] *= cyp_factor   # vmax_cyp2e1
    return p

def get_full_recovery_time(t, bac, threshold=0.2):
    peak_idx = np.argmax(bac)

    for i in range(peak_idx, len(bac)):
        if bac[i] < threshold:
            return t[i] - t[peak_idx]   # recovery time vanaf piek

    return np.nan   # niet hersteld binnen simulatietijd


# define drinks
beer = podeus.Drink(volume_dl=10, kcal=240, alcohol_percentage=5, time_start_min=0, time_end_min=60)

# (optional) define meals
meal = podeus.Meal(kcal=500, time_start_min=0)  # meal at t=0, or set to later time if you want to simulate meal effects

drinks = [beer]
meals = [meal]  # or []

# simulate
t_sim = np.arange(0, 720, 0.1)  # simulate for 12 hours with 1000 time points
solution, outputs = podeus.simulate_podeus(t_sim, sex='male', weight=70.0, height=1.75, drinks=drinks, meals=meals)
solution_nomeal, outputs_nomeal = podeus.simulate_podeus(t_sim, sex='male', weight=70.0, height=1.75, drinks=drinks, meals=[])


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

_, out_base = podeus.simulate_podeus(
    t_sim, 'male', 70.0, 1.75, drinks, meals, params=params_base
)
plt.plot(t_sim, out_base['promille'], label='baseline', linewidth=2)

param_names = ["vmax_adh", "vmax_cyp2e1"]
indices = [12, 13]

for name, i in zip(param_names, indices):
    params_high = params_base.copy()
    params_high[i] *= 1.1
    _, out_high = podeus.simulate_podeus(
        t_sim, 'male', 80.0, 1.80, drinks, meals, params=params_high
    )
    plt.plot(t_sim, out_high['promille'], label=f'{name} +10%')

    params_low = params_base.copy()
    params_low[i] *= 0.9
    _, out_low = podeus.simulate_podeus(
        t_sim, 'male', 80.0, 1.80, drinks, meals, params=params_low
    )
    plt.plot(t_sim, out_low['promille'], linestyle='--', label=f'{name} -10%')

plt.xlabel('Time (min)')
plt.ylabel('BAC (‰)')
plt.title('Local sensitivity analysis of BAC')
plt.legend()
plt.show()

for name, i in zip(param_names, indices):
    params_high = params_base.copy()
    params_high[i] *= 1.3
    _, out_high = podeus.simulate_podeus( t_sim, 'male', 80.0, 1.80, drinks, meals, params=params_high)
    plt.plot(t_sim, out_high['promille'], label=f'{name} +30%')

    params_low = params_base.copy()
    params_low[i] *= 0.7
    _, out_low = podeus.simulate_podeus(
        t_sim, 'male', 80.0, 1.80, drinks, meals, params=params_low
    )
    plt.plot(t_sim, out_low['promille'], linestyle='--', label=f'{name} -30%')

plt.xlabel('Time (min)')
plt.ylabel('BAC (‰)')
plt.title('Local sensitivity analysis of BAC')
plt.legend()
plt.show()

# Onderzoeksvraag beantwoorden BMI stage berekenen
bmi_values = [18.5, 23, 27, 32]
height = 1.80 
weights = [bmi * height**2 for bmi in bmi_values]

liver_scenarios = {"Healthy liver": (1.0, 1.0),"Mildly impaired liver": (0.7559 , 1.75),"Damaged liver": (0.6324, 2.75), "Extremely damaged liver": (0.5423, 3.4)}

# lege dictionary voor resultaten
recovery_table = {}

for bmi, weight in zip(bmi_values, weights):
    recovery_table[bmi] = {}

    for liver_name, (adh_factor, cyp_factor) in liver_scenarios.items():

        params_new = make_liver_scenario(params_base, adh_factor, cyp_factor)

        solution, outputs = podeus.simulate_podeus(t_sim,sex="male",weight=weight,height=height,drinks=drinks,meals=meals,params=params_new)

        bac = outputs['promille']
        recovery_time = get_full_recovery_time(t_sim, bac)

        recovery_table[bmi][liver_name] = recovery_time

#Waardes in tabel zetten
print("\nFull recovery time table (minutes):\n")

header = f"{'BMI':<8}{'Healthy liver':<20}{'Mildly damaged liver':<24}{'Damaged liver':<20}{'Extremely damaged liver':<24}"
print(header)
print("-" * len(header))

for bmi in bmi_values:
    healthy = recovery_table[bmi]["Healthy liver"]
    mild = recovery_table[bmi]["Mild impaired liver"]
    damaged = recovery_table[bmi]["Damaged liver"]

    row = f"{bmi:<8}{healthy:<20.1f}{mild:<24.1f}{damaged:<20.1f}"
    print(row)

#BAC Curves plotten
for liver_name, (adh_factor, cyp_factor) in liver_scenarios.items():
    plt.figure()

    for bmi, weight in zip(bmi_values, weights):
        params_new = make_liver_scenario(params_base, adh_factor, cyp_factor)

        solution, outputs = podeus.simulate_podeus(t_sim,sex="male",weight=weight,height=height,drinks=drinks,meals=meals,params=params_new)

        plt.plot(t_sim, outputs['promille'], label=f'BMI {bmi}')

    plt.xlabel('Time (min)')
    plt.ylabel('BAC (‰)')
    plt.title(f'BAC curves - {liver_name}')
    plt.legend()
    plt.show()