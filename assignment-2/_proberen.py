import podeus
import numpy as np
import matplotlib.pyplot as plt

sex = 'female'
weight = 70.0
height = 1.75

# define drinks
beer = podeus.Drink(volume_dl=5,kcal=120,alcohol_percentage=5,time_start_min=0,time_end_min=30)

# define meal
meal = podeus.Meal(kcal=500,time_start_min=0)

drinks = [beer]
meals = [meal]

# simulate time
t_sim = np.arange(0, 240, 0.1)


solution, outputs = podeus.simulate_podeus(
    t_sim, sex=sex, weight=weight, height=height, drinks=drinks, meals=meals)

solution_nomeal, outputs_nomeal = podeus.simulate_podeus(t_sim, sex=sex, weight=weight, height=height, drinks=drinks, meals=[])

plt.figure(figsize=(9, 5))
with_meal, = plt.plot(t_sim, outputs['promille'], color='red', alpha=0.5, label='With Meal')
without_meal, = plt.plot(t_sim, outputs_nomeal['promille'], color='blue', alpha=0.5, label='Without Meal')
beer_times = plt.vlines([beer.time_start_min, beer.time_end_min],ymin=0, ymax=0.25,colors='gray', linestyles='dashed',label='Drink Timing')
beer_duration = plt.fill_betweenx([0, 0.25],beer.time_start_min, beer.time_end_min,color='gray', alpha=0.2,label='Drink Timing')

plt.xlabel('Time (min)')
plt.ylabel('BAC (‰)')
plt.title('Original model: with and without meal')
plt.legend([with_meal, without_meal, (beer_times, beer_duration)],['With Meal', 'Without Meal', 'Drink Timing'])
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
    9.6381e-1,   # index 12 = vmax_adh
    1.7148e-1,   # index 13 = vmax_cyp2e1
    9.2200e0,
    3.6880e1,
    6.1804e-3
]

idx_adh = 12
idx_cyp = 13

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

plt.xlabel('Time (min)')
plt.ylabel('BAC (‰)')
plt.title('BAC for CYP-ADH scenarios')
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()


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
    plt.show()