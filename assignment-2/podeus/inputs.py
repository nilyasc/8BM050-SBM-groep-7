import numpy as np

class Drink:

    def __init__(self, volume_dl, kcal, alcohol_percentage, time_start_min, time_end_min):
        self.volume_dl = volume_dl
        self.alcohol_percentage = alcohol_percentage
        self.time_start_min = time_start_min
        self.time_end_min = time_end_min
        self.kcal = kcal      

    @property
    def concentration_g_per_ml(self):
        return self.alcohol_percentage * 789.1  #mg/dl
    
    @property
    def kcal_per_dl(self):
        return self.kcal / self.volume_dl
    
    def vol_drink_per_time(self, t):
        if self.time_start_min <= t <= self.time_end_min:
            duration = self.time_end_min - self.time_start_min
            return self.volume_dl / duration  # dl/min
        else:
            return 0.0

class Meal:

    def __init__(self, kcal, time_start_min):
        self.kcal = kcal
        self.time_start_min = time_start_min


    def r_kcal(self, t):
        if t <= self.time_start_min:
            return 0.0
        else:
            R_kcal_solid = self.kcal * -1.88 * 0.010* (0.010*(t-self.time_start_min))**0.86  * np.exp(-(0.010*(t-self.time_start_min))**1.86)
            return R_kcal_solid