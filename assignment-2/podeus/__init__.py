from .equations import podeus_model
from .inputs import Drink, Meal
from scipy.integrate import odeint
import numpy as np


def simulate_podeus(t, sex, weight, height, drinks, meals, params=None):

    # Initial conditions
    y0 = [0.001,  # vol_stomach
          0.0,  # kcal_liquid
          0.0,  # kcal_solid
          0.0,  # etoh_pool
          0.0,  # conc_etoh_stomach
          0.0,  # mass_etoh_intestine
          0.0,  # blood_conc
          0.0,  # plasma_acetate
          0.0,  # peth
          0.0]  # peth_bound

    if params is None:    
        params = [
            1.4599e4,  # k_peth
            1.5695e2,  # k_peth_out
            1.7416e4,  # k_peth_bind
            5.8081e-3,  # k_peth_release
            1.0155e1,  # k_pool_in
            4.0227e-1,  # k_pool_out
            2.1545e3,  # vmax
            1.7793e4,  # km
            1.5843e2,  # k_kcal
            8.4172e1,  # k3
            8.3001e2,  # k4
            1.3079e-1,  # k6
            9.6381e-1,  # vmax_adh
            1.7148e-1,  # vmax_cyp2e1
            9.2200e0,  # km_adh
            3.6880e1,  # km_cyp2e1
            6.1804e-3,  # k_kcal_clearance
        ]

    # find meal times
    if meals:

        y_out = []


        meal_times = sorted(set([meal.time_start_min for meal in meals]))
        # if t0 not in meal times, simulate until first meal
        if meal_times[0] > t[0]:
            t_meal = t[t < meal_times[0]]
            sol = odeint(podeus_model, y0, t_meal, args=(params, sex, weight, height, drinks, meals))
            y_out.append(sol)
            y0 = sol[-1]  # update state for next interval
        # solve from one meal to the next, adding the meal kcal at the start of each meal
        
        for i in range(len(meal_times)):
            meal_time = meal_times[i]

            # get time interval from supplied t to next meal time (or end of simulation if last meal)
            if i < len(meal_times) - 1:
                t_meal = t[np.logical_and(t >= meal_time, t < meal_times[i+1])]
            else:
                t_meal = t[t >= meal_time]
            y0[2] += meals[i].kcal  # add meal kcal to solid kcal at start of meal
            sol = odeint(podeus_model, y0, t_meal, args=(params, sex, weight, height, drinks, meals))
            y0 = sol[-1]  # update state for next interval
            y_out.append(sol)
        y = np.vstack(y_out)  # combine results from all intervals
    else:    
        y = odeint(podeus_model, y0, t, args=(params, sex, weight, height, drinks, meals))

    blood_conc = y[:,6]
    plasma_acetate = y[:,7]
    peth = y[:,8]
    vol_stomach = y[:,0]
    solid_kcal = y[:,2]

    outputs = {
        'blood_conc_mg_per_dl': blood_conc,
        'plasma_acetate_mM': plasma_acetate / 10.2,  # convert mg/dl to mM
        'promille': blood_conc / 100.0, # convert mg/dl to g/L (promille: 1 mg/dl = 0.01 g/L)
        'brac': 0.840 * blood_conc / 1000.0 + 0.00367,  # convert mg/dl to g/dl 
        'peth': peth,
        'gastric_volume': vol_stomach,
        'solid_kcal': solid_kcal
    }

    return y, outputs