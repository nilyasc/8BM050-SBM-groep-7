import podeus
import numpy as np
import matplotlib.pyplot as plt

# Sluit oude figuren
plt.close('all')

# =============================
# 1. INPUTS
# =============================

# Define drink
beer = podeus.Drink(
    volume_dl=5,
    kcal=120,
    alcohol_percentage=5,
    time_start_min=0,
    time_end_min=30
)

# Define meal
meal = podeus.Meal(
    kcal=500,
    time_start_min=0
)

drinks = [beer]
meals = [meal]

# Simulation time
t_sim = np.arange(0, 240, 0.1)

# Base parameters
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

# Parameter indices
idx_adh = 12
idx_cyp = 13

# Baseline values
vmax_adh_base = params_base[idx_adh]
vmax_cyp_base = params_base[idx_cyp]

# Predefined CYP scenarios and corresponding ADH factors
cyp_factors = [1.0, 1.75, 2.5, 3.25]
adh_factors = [1.0, 0.7559, 0.6325, 0.5547]

# =============================
# 2. HELPER FUNCTION
# =============================

def get_metrics(t, bac):
    peak_bac = np.max(bac)
    time_to_peak = t[np.argmax(bac)]
    auc = np.trapz(bac, t)
    return peak_bac, time_to_peak, auc

# =============================
# 3. CHECK BASE MODEL
# =============================

print("=== Base model check ===")
try:
    _, out_check = podeus.simulate_podeus(
        t_sim, 'female', 70.0, 1.75, drinks, meals, params=params_base
    )
    print("Base simulation successful.")
    print("Output keys:", out_check.keys())
    print("Max BAC base:", np.max(out_check['promille']))
except Exception as e:
    print("ERROR in base simulation:")
    print(e)
    raise

# =============================
# 4. PLOT BASELINE CYP-ADH SCENARIOS
# =============================

print("\n=== Plotting baseline CYP-ADH scenarios ===")

successful_baseline_runs = 0
plt.figure(figsize=(10, 6))

for cyp_factor, adh_factor in zip(cyp_factors, adh_factors):
    params = params_base.copy()
    params[idx_cyp] = vmax_cyp_base * cyp_factor
    params[idx_adh] = vmax_adh_base * adh_factor

    print(f"\nScenario baseline: CYP factor = {cyp_factor}, ADH factor = {adh_factor}")
    print(f"  vmax_cyp2e1 = {params[idx_cyp]:.6f}")
    print(f"  vmax_adh    = {params[idx_adh]:.6f}")

    try:
        _, out = podeus.simulate_podeus(
            t_sim, 'female', 70.0, 1.75, drinks, meals, params=params
        )

        bac = np.asarray(out['promille'])

        print(f"  BAC max = {np.max(bac):.6f}")
        print(f"  BAC min = {np.min(bac):.6f}")
        print(f"  NaNs?   = {np.isnan(bac).any()}")

        plt.plot(
            t_sim,
            bac,
            linewidth=2,
            label=f'CYP x{cyp_factor}, ADH x{adh_factor:.4f}'
        )
        successful_baseline_runs += 1

    except Exception as e:
        print("  ERROR in baseline scenario:")
        print(" ", e)

if successful_baseline_runs > 0:
    plt.xlabel('Time (min)')
    plt.ylabel('BAC (‰)')
    plt.title('BAC for CYP-ADH scenarios')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()
else:
    plt.close()
    print("No successful baseline scenarios were plotted.")

# =============================
# 5. ADH SENSITIVITY ANALYSIS
# =============================

print("\n=== ADH sensitivity analysis (±10%) ===")
print("CYP_factor | ADH_base | Peak_base | Peak_-10% | Peak_+10% | AUC_base | AUC_-10% | AUC_+10%")

for cyp_factor, adh_factor in zip(cyp_factors, adh_factors):

    print(f"\n--- Sensitivity for CYP factor {cyp_factor} ---")

    # Baseline scenario
    params_mid = params_base.copy()
    params_mid[idx_cyp] = vmax_cyp_base * cyp_factor
    params_mid[idx_adh] = vmax_adh_base * adh_factor

    # ADH -10%
    params_low = params_mid.copy()
    params_low[idx_adh] *= 0.9

    # ADH +10%
    params_high = params_mid.copy()
    params_high[idx_adh] *= 1.1

    try:
        _, out_mid = podeus.simulate_podeus(
            t_sim, 'female', 70.0, 1.75, drinks, meals, params=params_mid
        )
        _, out_low = podeus.simulate_podeus(
            t_sim, 'female', 70.0, 1.75, drinks, meals, params=params_low
        )
        _, out_high = podeus.simulate_podeus(
            t_sim, 'female', 70.0, 1.75, drinks, meals, params=params_high
        )

        bac_mid = np.asarray(out_mid['promille'])
        bac_low = np.asarray(out_low['promille'])
        bac_high = np.asarray(out_high['promille'])

        peak_mid, tpeak_mid, auc_mid = get_metrics(t_sim, bac_mid)
        peak_low, tpeak_low, auc_low = get_metrics(t_sim, bac_low)
        peak_high, tpeak_high, auc_high = get_metrics(t_sim, bac_high)

        print(f"{cyp_factor:10.2f} | {adh_factor:8.4f} | {peak_mid:9.4f} | {peak_low:9.4f} | {peak_high:9.4f} | {auc_mid:8.4f} | {auc_low:8.4f} | {auc_high:8.4f}")

        # Plot separate figure for this CYP scenario
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

    except Exception as e:
        print(f"ERROR in sensitivity scenario for CYP factor {cyp_factor}:")
        print(e)

# =============================
# 6. OPTIONAL: SUMMARY TABLE OF SENSITIVITY EFFECTS
# =============================

print("\n=== Relative effect of ADH ±10% on peak BAC ===")
print("CYP_factor | % change peak BAC for ADH -10% | % change peak BAC for ADH +10%")

for cyp_factor, adh_factor in zip(cyp_factors, adh_factors):

    params_mid = params_base.copy()
    params_mid[idx_cyp] = vmax_cyp_base * cyp_factor
    params_mid[idx_adh] = vmax_adh_base * adh_factor

    params_low = params_mid.copy()
    params_low[idx_adh] *= 0.9

    params_high = params_mid.copy()
    params_high[idx_adh] *= 1.1

    try:
        _, out_mid = podeus.simulate_podeus(
            t_sim, 'male', 85.0, 1.80, drinks, meals, params=params_mid
        )
        _, out_low = podeus.simulate_podeus(
            t_sim, 'male', 85.0, 1.80, drinks, meals, params=params_low
        )
        _, out_high = podeus.simulate_podeus(
            t_sim, 'male', 85.0, 1.80, drinks, meals, params=params_high
        )

        peak_mid = np.max(np.asarray(out_mid['promille']))
        peak_low = np.max(np.asarray(out_low['promille']))
        peak_high = np.max(np.asarray(out_high['promille']))

        rel_low = 100 * (peak_low - peak_mid) / peak_mid
        rel_high = 100 * (peak_high - peak_mid) / peak_mid

        print(f"{cyp_factor:10.2f} | {rel_low:27.3f} | {rel_high:27.3f}")

    except Exception as e:
        print(f"ERROR in summary calculation for CYP factor {cyp_factor}:")
        print(e)