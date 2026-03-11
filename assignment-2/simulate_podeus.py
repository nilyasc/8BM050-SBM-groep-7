import podeus
import numpy as np
import matplotlib.pyplot as plt

<<<<<<< HEAD
def make_liver_scenario(params, adh_factor=1.0, cyp_factor=1.0):
    p = params.copy()
    p[12] *= adh_factor   # vmax_adh
    p[13] *= cyp_factor   # vmax_cyp2e1
    return p


def get_highest_stage_reached(bac):
    peak = np.max(bac)

    # stages gebaseerd op promille
    if peak < 0.2:
        return 1
    elif peak < 0.5:
        return 2
    elif peak < 0.8:
        return 3
    else:
        return 4

=======
>>>>>>> 56c4a07abdd463e290e1b93208e6e2c86ada0e85
# define drinks
beer = podeus.Drink(volume_dl=5, kcal=120, alcohol_percentage=5, time_start_min=0, time_end_min=30)

# (optional) define meals
meal = podeus.Meal(kcal=500, time_start_min=0)  # meal at t=0, or set to later time if you want to simulate meal effects

drinks = [beer]
meals = [meal]  # or []

# simulate
t_sim = np.arange(0, 240, 0.1)  # simulate for 4 hours with 1000 time points
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

<<<<<<< HEAD
_, out_base = podeus.simulate_podeus(
    t_sim, 'male', 70.0, 1.75, drinks, meals, params=params_base
)
plt.plot(t_sim, out_base['promille'], label='baseline', linewidth=2)
=======
#sensitivity analysis.
sex = 'female'
weight = 70.0
height = 1.75
>>>>>>> 56c4a07abdd463e290e1b93208e6e2c86ada0e85

idx_adh = 12
idx_cyp = 13

<<<<<<< HEAD
for name, i in zip(param_names, indices):
    params_high = params_base.copy()
    params_high[i] *= 1.1
    _, out_high = podeus.simulate_podeus(
        t_sim, 'male', 70.0, 1.75, drinks, meals, params=params_high
    )
    plt.plot(t_sim, out_high['promille'], label=f'{name} +10%')

    params_low = params_base.copy()
    params_low[i] *= 0.9
    _, out_low = podeus.simulate_podeus(
        t_sim, 'male', 70.0, 1.75, drinks, meals, params=params_low
    )
    plt.plot(t_sim, out_low['promille'], linestyle='--', label=f'{name} -10%')

=======
vmax_adh_base = params_base[idx_adh]
vmax_cyp_base = params_base[idx_cyp]


cyp_factors = [1.0, 2.0,3.25]
adh_factors = [1.0, 0.7071, 0.5547]

plt.figure(figsize=(10, 6))

for cyp_factor, adh_factor in zip(cyp_factors, adh_factors):
    params = params_base.copy()
    params[idx_cyp] = vmax_cyp_base * cyp_factor
    params[idx_adh] = vmax_adh_base * adh_factor

    _, out = podeus.simulate_podeus(t_sim, sex=sex, weight=weight, height=height,drinks=drinks, meals=meals, params=params)

    plt.plot(t_sim,out['promille'],linewidth=2,label=f'CYP x{cyp_factor}, ADH x{adh_factor:.4f}')

>>>>>>> 56c4a07abdd463e290e1b93208e6e2c86ada0e85
plt.xlabel('Time (min)')
plt.ylabel('BAC (‰)')
plt.title('BAC for CYP-ADH scenarios')
plt.legend()
plt.show()

<<<<<<< HEAD
for name, i in zip(param_names, indices):
    params_high = params_base.copy()
    params_high[i] *= 1.3
    _, out_high = podeus.simulate_podeus(
        t_sim, 'male', 70.0, 1.75, drinks, meals, params=params_high
    )
    plt.plot(t_sim, out_high['promille'], label=f'{name} +30%')

    params_low = params_base.copy()
    params_low[i] *= 0.7
    _, out_low = podeus.simulate_podeus(
        t_sim, 'male', 70.0, 1.75, drinks, meals, params=params_low
    )
    plt.plot(t_sim, out_low['promille'], linestyle='--', label=f'{name} -30%')

plt.xlabel('Time (min)')
plt.ylabel('BAC (‰)')
plt.title('Local sensitivity analysis of BAC')
plt.legend()
plt.show()

# Onderzoeksvraag beantwoorden BMI stage berekenen
bmi_values = [20, 25, 30, 35]
height = 1.80
weights = [bmi * height**2 for bmi in bmi_values]

liver_scenarios = {
    "Healthy liver": (1.0, 1.0),
    "Mild impaired liver": (0.75, 0.75),
    "Damaged liver": (0.50, 0.50)
}

# lege dictionary voor resultaten
stage_table = {}

for bmi, weight in zip(bmi_values, weights):
    stage_table[bmi] = {}

    for liver_name, (adh_factor, cyp_factor) in liver_scenarios.items():

        params_new = make_liver_scenario(params_base, adh_factor, cyp_factor)

        solution, outputs = podeus.simulate_podeus(
            t_sim,
            sex="male",
            weight=weight,
            height=height,
            drinks=drinks,
            meals=meals,
            params=params_new
        )

        bac = outputs['promille']
        stage = get_highest_stage_reached(bac)

        stage_table[bmi][liver_name] = stage

#Waardes in tabel zetten
print("\nHighest stage reached table:\n")

header = f"{'BMI':<8}{'Healthy liver':<20}{'Mild impaired liver':<24}{'Damaged liver':<20}"
print(header)
print("-" * len(header))

for bmi in bmi_values:
    healthy = stage_table[bmi]["Healthy liver"]
    mild = stage_table[bmi]["Mild impaired liver"]
    damaged = stage_table[bmi]["Damaged liver"]

    row = f"{bmi:<8}{healthy:<20}{mild:<24}{damaged:<20}"
    print(row)

#BAC Curves plotten
for liver_name, (adh_factor, cyp_factor) in liver_scenarios.items():
    plt.figure()

    for bmi, weight in zip(bmi_values, weights):
        params_new = make_liver_scenario(params_base, adh_factor, cyp_factor)

        solution, outputs = podeus.simulate_podeus(
            t_sim,
            sex="male",
            weight=weight,
            height=height,
            drinks=drinks,
            meals=meals,
            params=params_new
        )

        plt.plot(t_sim, outputs['promille'], label=f'BMI {bmi}')

    plt.xlabel('Time (min)')
    plt.ylabel('BAC (‰)')
    plt.title(f'BAC curves - {liver_name}')
    plt.legend()
=======
for cyp_factor, adh_factor in zip(cyp_factors, adh_factors):

    params_mid = params_base.copy()
    params_mid[idx_cyp] = vmax_cyp_base * cyp_factor
    params_mid[idx_adh] = vmax_adh_base * adh_factor

    params_low = params_mid.copy()
    params_low[idx_adh] *= 0.9

    params_high = params_mid.copy()
    params_high[idx_adh] *= 1.1

    _, out_mid = podeus.simulate_podeus(t_sim, sex=sex, weight=weight, height=height,drinks=drinks, meals=meals, params=params_mid)
    _, out_low = podeus.simulate_podeus(t_sim, sex=sex, weight=weight, height=height,drinks=drinks, meals=meals, params=params_low)
    _, out_high = podeus.simulate_podeus(t_sim, sex=sex, weight=weight, height=height,drinks=drinks, meals=meals, params=params_high)

    bac_mid = np.asarray(out_mid['promille'])
    bac_low = np.asarray(out_low['promille'])
    bac_high = np.asarray(out_high['promille'])

    plt.figure(figsize=(9, 5))
    plt.plot(t_sim, bac_mid, linewidth=2, label='baseline')
    plt.plot(t_sim, bac_low, '--', linewidth=2, label='ADH -10%')
    plt.plot(t_sim, bac_high, ':', linewidth=2, label='ADH +10%')

    plt.xlabel('Time (min)')
    plt.ylabel('BAC (‰)')
    plt.title(f'ADH sensitivity analysis for CYP factor {cyp_factor}')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
>>>>>>> 56c4a07abdd463e290e1b93208e6e2c86ada0e85
    plt.show()