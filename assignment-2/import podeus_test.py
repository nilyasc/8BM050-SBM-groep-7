import podeus
import numpy as np
import matplotlib.pyplot as plt

# drinks and meal
beer = podeus.Drink(volume_dl=5, kcal=120, alcohol_percentage=5, time_start_min=0, time_end_min=30)
meal = podeus.Meal(kcal=500, time_start_min=0)

drinks = [beer]
meals = [meal]
t_sim = np.arange(0, 240, 0.1)

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
    9.6381e-1,   # vmax_adh
    1.7148e-1,   # vmax_cyp2e1
    9.2200e0,
    3.6880e1,
    6.1804e-3
]

idx_adh = 12
idx_cyp = 13

vmax_adh_base = params_base[idx_adh]
vmax_cyp_base = params_base[idx_cyp]

cyp_factors = [1.0, 1.75, 2.5, 3.25]
adh_factors = [1.0, 0.7559, 0.6325, 0.5547]

plt.figure(figsize=(10,6))

for cyp_factor, adh_factor in zip(cyp_factors, adh_factors):
    params = params_base.copy()
    params[idx_cyp] = vmax_cyp_base * cyp_factor
    params[idx_adh] = vmax_adh_base * adh_factor

    _, out = podeus.simulate_podeus(
        t_sim, sex='female', weight=70.0, height=1.75,
        drinks=drinks, meals=meals, params=params
    )

    plt.plot(
        t_sim,
        out['promille'],
        label=f'CYP x{cyp_factor}, ADH x{adh_factor:.4f}'
    )

plt.xlabel('Time (min)')
plt.ylabel('BAC (‰)')
plt.title('BAC for CYP-ADH scenarios')
plt.legend()
plt.show()