import numpy as np

def _dvol_stomach_dt(vol_stomach, kcal_liquid, vmax, km, vss, k_kcal, drinks, t):
    R_emptying = vmax * ( (vol_stomach-vss)/((vol_stomach-vss) + km) ) * np.exp( -kcal_liquid/k_kcal )
    vol_drink_per_time = sum([drink.vol_drink_per_time(t) for drink in drinks])
    return vol_drink_per_time - R_emptying

def _dkcal_liquid_dt(kcal_liquid, k_kcal_clearance, drinks, t):
    kcal_clearance = kcal_liquid * k_kcal_clearance
    kcal_drink_per_time = sum([drink.vol_drink_per_time(t) * drink.kcal_per_dl for drink in drinks])
    return kcal_drink_per_time - kcal_clearance

def _kcal_solid_dt(meals, t):
    return sum([meal.r_kcal(t) for meal in meals])

def _detoh_pool_dt(etoh_pool, vol_stomach, conc_etoh_stomach, kcal_solid, k_pool_in, k_pool_out):
    kcal_solid_vol = max(1.0, kcal_solid) / 400
    r_pool_in = max(0, conc_etoh_stomach - etoh_pool/kcal_solid_vol) * k_pool_in
    r_pool_out = etoh_pool * k_pool_out
    return r_pool_in*vol_stomach - r_pool_out

def _dconc_etoh_stomach_dt(conc_etoh_stomach, vol_stomach, etoh_pool, kcal_solid_vol, 
                          k_pool_in, k_pool_out, drinks, t):
    r_pool_in = max(0, conc_etoh_stomach - etoh_pool/kcal_solid_vol) * k_pool_in
    r_pool_out = etoh_pool * k_pool_out
    R_drink_etoh = (1/vol_stomach)*sum([
        drink.vol_drink_per_time(t) * (drink.concentration_g_per_ml - 
                                       conc_etoh_stomach) for drink in drinks])
    return R_drink_etoh - r_pool_in + r_pool_out/vol_stomach

def _dmass_etoh_intestine_dt(mass_etoh_intestine, conc_etoh_stomach, vol_stomach, 
                            vmax, vss, km, kcal_liquid, k_kcal, k3, k4):
    R_emptying = vmax * ( (vol_stomach-vss)/((vol_stomach-vss) + km) ) * np.exp( -kcal_liquid/k_kcal )
    r3 = mass_etoh_intestine * k3
    r4 = mass_etoh_intestine * k4
    return R_emptying*conc_etoh_stomach - r3 - r4

def _dconc_blood_alcohol_dt(conc_blood, k_m_cyp2e1, k_m_adh, v_liver, v_max_adh, v_max_cyp2e1, mass_etoh_intestine, a, b, c, h, w, k3):
    v_adh = v_max_adh * (conc_blood)/(k_m_adh + conc_blood)
    v_cyp2e1 = v_max_cyp2e1 * (conc_blood)/(k_m_cyp2e1 + conc_blood)
    v_blood = (a * h^3 + b * w + c) * 10 #dl 
    r3 = mass_etoh_intestine * k3
    r5 = v_adh + v_cyp2e1
    return (r3/v_blood) - r5 * (v_liver/v_blood)

def _dplasma_acetate_dt(v_adh, v_cyp2e1, k6, plasma_acetate):
    r5 = v_adh + v_cyp2e1
    r6 = k6 * plasma_acetate
    return r5 - r6

def _dpeth_dt(k_peth, blood_conc, k_peth_out, peth, k_peth_bind, peth_bound, k_peth_release):
    r_peth = k_peth * blood_conc
    r_peth_clear = k_peth_out * peth
    r_peth_bind = k_peth_bind * peth_bound
    r_peth_release = max(0, k_peth_release * (peth_bound - peth))
    return r_peth - r_peth_bind + r_peth_release - r_peth_clear

def _dpeth_bound_dt (k_peth_bind, peth_bound, k_peth_release, peth):
    r_peth_bind = k_peth_bind * peth_bound
    r_peth_release = max(0, k_peth_release * (peth_bound - peth))
    return r_peth_bind - r_peth_release
    


def podeus_model(y, t, params, sex, weight, height, drinks, meals):

    # unpack variables
    (vol_stomach, kcal_liquid, kcal_solid, etoh_pool, conc_etoh_stomach, 
     mass_etoh_intestine, blood_conc, plasma_acetate, peth, peth_bound) = y
    
    (k_peth, k_peth_out, k_peth_bind, k_peth_release, k_pool_in, k_pool_out,
    vmax, km, k_kcal, k3, k4, k6, vmax_adh, vmax_cyp2e1, km_adh, km_cyp2e1, k_kcal_clearance) = params

    # Variables
    ss_vol = 0.001

    # stomach volume 
    dvol_stomach_dt = _dvol_stomach_dt(vol_stomach, kcal_liquid, vmax, km, ss_vol, k_kcal, drinks, t)
    dkcal_liquid_dt = _dkcal_liquid_dt(kcal_liquid, k_kcal_clearance, drinks, t)
    
    # solid kcal
    dkcal_solid_dt = _kcal_solid_dt(meals, t)
    # ethanol pool and concentration
    detoh_pool_dt = _detoh_pool_dt(etoh_pool, vol_stomach, conc_etoh_stomach, kcal_solid,
                                   k_pool_in, k_pool_out)
    dconc_etoh_stomach_dt = _dconc_etoh_stomach_dt(conc_etoh_stomach, vol_stomach, 
                                                  etoh_pool, max(1.0, kcal_solid) / 400, 
                                                  k_pool_in, k_pool_out, drinks, t)
    dmass_etoh_intestine_dt = _dmass_etoh_intestine_dt(mass_etoh_intestine, 
                                                      conc_etoh_stomach, vol_stomach, 
                                                      vmax, ss_vol, km, kcal_liquid, k_kcal, k3, k4)
    
    # blood concentrations 
    # ------- START OF OWN IMPLEMENTATION -------
    # You can implement the remaining equations here! 
    dblood_conc_dt = 5
    dplasma_acetate_dt = 0.0
    dpeth_dt = 0.0
    dpeth_bound_dt = 0.0
    # ------- END OF OWN IMPLEMENTATION -------
    return [dvol_stomach_dt, dkcal_liquid_dt, dkcal_solid_dt, detoh_pool_dt, 
            dconc_etoh_stomach_dt, dmass_etoh_intestine_dt, dblood_conc_dt, 
            dplasma_acetate_dt, dpeth_dt, dpeth_bound_dt]