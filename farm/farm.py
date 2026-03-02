import numpy as np
import math
from farm.artifact import *
from farm.prices import *

class Farm:
    def __init__(self, egg, cr=None, er=None, silos=None, habs=None, vehicles=None, se=0, pe=0, te=0, colleggtibles=None, pop=None, artifact_set=None, video_doubler=False, cash=0):
        self.egg = egg
        self.cr = cr if cr is not None else np.zeros(56)
        self.er = er if er is not None else list(max_er)
        self.silos = silos if silos is not None else 1
        self.habs = habs if habs is not None else [1,0,0,0]
        self.vehicles = vehicles if vehicles is not None else [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        self.se = se
        self.pe = pe
        self.te = te
        self.colleggtibles = colleggtibles if colleggtibles is not None else np.ones(11)*4
        self.pop = pop if pop is not None else 0
        self.artf = artifact_set if artifact_set is not None else Artifact_set()
        self.video_doubler = video_doubler
        self.cash = cash
        self.event_effects = {
            "cash": 1,
            "drone": 1,
            "cr": 1,
            "hab": 1,
            "veh": 1,
            "gift": 1
            }

        
        if self.egg not in egg_specs:
            raise KeyError(f"Unknown egg key: {self.egg}")
        for i in range(len(self.cr)):
            if self.cr[i] > max_cr[i]: raise Exception(f"{self.cr[i]} exceeds maximum CR{i} level")
        for i in range(len(self.er)):
            if self.er[i] > max_er[i]: raise Exception(f"{self.er[i]} exceeds maximum ER{i} level")
        if self.silos > 10: raise Exception("Number of silos exceeds maximum")
        for i in range(len(self.colleggtibles)):
            if self.colleggtibles[i] > 4: raise Exception(f"Colleggtible {i} level exceeds maximum")
        for i in range(len(self.vehicles)):
            if i>=self.max_vehicle_number:
                if self.vehicles[i] != 0: raise Exception(f"Vehicle {i} not unlocked")
            if self.vehicles[i] > self.max_vehicle_level: raise Exception(f"Vehicle {i} exceeds maximum level")
        for i in range(len(self.habs)):
            if self.habs[i] > 19: raise Exception(f"Hab {i} exceeds maximum level")
        if self.pop > self.hab_size: raise Exception(f"Population larger than hab space!")


    def on_enlightenment(self):
        return self.egg=="enlightenment"

    def on_virtue(self):
        return self.egg in {"curiosity", "kindness", "resilience", "humility", "integrity"}

    def coll_effect(self, c):
        if c not in coll_specs:
            raise KeyError(f"Unknown colleggtible key: {c}")
        return coll_specs[c][int(self.colleggtibles[coll_index[c]])]


    @property
    def egg_value(self):
        # egg value is just the bare value times a ton of common research
        return self.artf.egg_value * egg_specs[self.egg][1] * (1+0.25*self.cr[1]) * (1+0.25*self.cr[6]) * (2**self.cr[8]) * (3**self.cr[15]) * (1+0.25*self.cr[17]) * (1+0.15*self.cr[23]) * (1+0.15*self.cr[27]) * (2**self.cr[30]) * (1+0.1*self.cr[33]) * (2**self.cr[37]) * (1+0.25*self.cr[39]) * (1+0.25*self.cr[42]) * (1+0.1*self.cr[45]) * (10**self.cr[46]) * (1+0.05*self.cr[49]) * (1+0.01*self.cr[52]) * (10**self.cr[53])
    
    @property
    def laying_chick(self):
        #laying rate per chicken is 2 times a factor from epic research times
        return 2/60*self.artf.laying * (1+0.05*self.er[15]) * self.coll_effect("silicon") * (1+0.1*self.cr[0]) * (1+0.05*self.cr[16]) * (1+0.15*self.cr[23]) * (1+0.10*self.cr[35]) * (1+0.02*self.cr[47]) * (1+0.1*self.cr[55])
    
    @property
    def max_vehicle_number(self):
        return int(4+self.cr[11]+self.cr[21]+self.cr[24]+self.cr[28]+self.cr[40])

    @property
    def max_vehicle_level(self):
        return int(16 + self.cr[50])
  
    @property
    def max_shipping(self):
        # shipping rate is vehicle capacity times a factor from epic research, two colleggtibles and some common research
        total_capacity = 0
        for i in range(len(self.vehicles)):
            if(self.vehicles[i]>7):
                if(self.vehicles[i]>11):
                    total_capacity += vehicle_capacities[int(self.vehicles[i])]* (1+0.05*self.cr[36]) * (1+0.05*self.cr[54]) 
                else:
                    total_capacity += vehicle_capacities[int(self.vehicles[i])]* (1+0.1*self.cr[36])
            else: 
                total_capacity += vehicle_capacities[int(self.vehicles[i])]
        return total_capacity/60 * self.artf.shipping * (1+0.05*self.er[16]) * self.coll_effect("carbon") * self.coll_effect("pumpkin") * (1+0.05*self.cr[10]) * (1+0.1*self.cr[20]) * (1+0.05*self.cr[26]) * (1+0.05*self.cr[29]) * (1+0.05*self.cr[32]) * (1+0.05*self.cr[44]) * (1+0.05*self.cr[51]) 
    
    
    @property
    def ihr(self): # in seconds
        # ihr is calculated from cr, er and the easter colleggtible, as well as TE
        total_ihr = (1+0.05*self.er[4]) * self.coll_effect("easter") *(2*self.cr[5] + 5*self.cr[9] + 10*self.cr[22] + 25*self.cr[31] + 5*self.cr[34] + 50*self.cr[41])
        if self.on_virtue(): total_ihr = total_ihr * (1.1**self.te)
        else: total_ihr = total_ihr * (1.01**self.te)
        return total_ihr / 60 * 4 * self.artf.ihr # assuming max internal hatchery sharing or 4 habs!!

    @property
    def ihr_away(self):
        return self.ihr * (1+0.1*self.er[12])

    @property
    def eb(self): #in percent change!
        if self.on_virtue(): return 100*(1.1**self.te -1)
        else: 
            return ((10+1*self.er[13]+100*self.artf.se_bonus) * self.se * (1.05 + 0.01*self.er[19] + self.artf.pe_effect)**self.pe * 1.01**self.te)
   
    @property
    def max_rcb(self):
        # base rcb is 5, increased by cr and er
        return 5 + self.artf.max_rcb + 2*self.er[9] + 0.2*self.cr[13] + 0.5*self.cr[25] + 2*self.cr[43]
    
    @property
    def max_away_time(self):
        return (60+6*self.er[2])*self.silos
    
    @property
    def hab_size(self): # ceil has been tested extensively
        total_capacity = 0
        for i in range(len(self.habs)):
            if self.habs[i]==19:
                single_capacity = hab_capacities[int(self.habs[i])] * (1+0.02*self.cr[48])
            else:
                single_capacity = hab_capacities[int(self.habs[i])]
            single_capacity = single_capacity * self.coll_effect("pegg") * self.artf.hab_capacity * (1+0.05*self.cr[4]) * (1+0.05*self.cr[18]) * (1+0.02*self.cr[38])
            if single_capacity==round(single_capacity) and single_capacity>0 and self.coll_effect("pegg") != 1 and (self.artf.hab_capacity == 1.1 or self.artf.hab_capacity == 1.12):
                single_capacity += 1
            total_capacity += math.ceil(single_capacity)
        return total_capacity
    

    def farm_value(self, p=None): # All without colleggtible effects
        if p is None: p = self.pop
        laying_chick_naked = self.laying_chick/self.coll_effect("silicon")/self.artf.laying

        def hab_size_effective(p): 
            total_capacity = 0
            for i in range(len(self.habs)):
                if self.habs[i]==19: total_capacity += hab_capacities[int(self.habs[i])] * (1+0.02*self.cr[48])
                else: total_capacity += hab_capacities[int(self.habs[i])]
            total_capacity *= (1+0.05*self.cr[4]) * (1+0.05*self.cr[18]) * (1+0.02*self.cr[38])
            if p <= total_capacity:
                return total_capacity
            elif p <= self.hab_size:
                return p
            raise ValueError("Population must be smaller than Hab capacity")
        def max_shipping_naked():
            # shipping rate is vehicle capacity times a factor from epic research, two colleggtibles and some common research
            total_capacity = 0
            for i in range(len(self.vehicles)):
                if(self.vehicles[i]>7):
                    if(self.vehicles[i]>11):
                        total_capacity += vehicle_capacities[int(self.vehicles[i])]* (1+0.05*self.cr[36]) * (1+0.05*self.cr[54]) 
                    else:
                        total_capacity += vehicle_capacities[int(self.vehicles[i])]* (1+0.1*self.cr[36])
                else: 
                    total_capacity += vehicle_capacities[int(self.vehicles[i])]
            return total_capacity/60 * (1+0.05*self.er[16]) * (1+0.05*self.cr[10]) * (1+0.1*self.cr[20]) * (1+0.05*self.cr[26]) * (1+0.05*self.cr[29]) * (1+0.05*self.cr[32]) * (1+0.05*self.cr[44]) * (1+0.05*self.cr[51]) 
        def ihr_naked():
            total_ihr = (1+0.05*self.er[4]) *(2*self.cr[5] + 5*self.cr[9] + 10*self.cr[22] + 25*self.cr[31] + 5*self.cr[34] + 50*self.cr[41])
            return total_ihr / 60 * 4 # assuming max internal hatchery sharing or 4 habs!!

        return (30000 * self.artf.farm_value # Lens
                * (1+0.05*self.er[3]) # Accounting Tricks
                * egg_specs[self.egg][0] # Egg Coefficient
                * laying_chick_naked # Laying Rate per chicken
                * (1+self.eb/100) # Earning Bonus
                * self.egg_value/self.artf.egg_value # Naked egg value
                * (self.max_rcb-self.artf.max_rcb-4)**(0.25) # Naked max Running Chicken Bonus
                * (0.2*p
                   + 0.8*math.floor(p*min(1, max_shipping_naked()/laying_chick_naked/max(p,1)))
                   + (hab_size_effective(p)-p)**(0.6) 
                   + ihr_naked()*self.max_away_time))


    def set_event(self, e, x):
        if e not in self.event_effects:
            raise KeyError(f"Unknown event type: {e}")
        self.event_effects[e] = x

    def reset_events(self):
        for e in self.event_effects:
            self.event_effects[e] = 1

    def event(self,e):
        if e not in self.event_effects:
            raise KeyError(f"Unknown event type: {e}")
        return float(self.event_effects[e])



    def earnings(self, p=None):
        if p is None: p = self.pop
        p = int(p)
        if(self.laying_chick*p < self.max_shipping):
            return self.event("cash") * ((1+int(self.video_doubler)) * self.laying_chick*p*self.egg_value*self.coll_effect("firework")*(1+self.eb/100))
        else:
            return self.event("cash") * (1+int(self.video_doubler)) * self.max_shipping*self.egg_value*self.coll_effect("firework")*(1+self.eb/100)

    def earnings_away(self, p=None):
        if p is None: p = self.pop
        return self.earnings(p) * self.artf.away_earnings * self.coll_effect("chocolate") * self.coll_effect("wood")
    
    def earnings_active(self, p=None): # RCB, drones, boxes
        if p is None: p = self.pop
        # online earnings running chickens
        earnings = self.earnings(p)
        if p < self.hab_size:
            earnings *= self.effective_rcb
        return earnings + self.gifts_and_drones(p)

    def gifts_and_drones(self, pop):
        # gift boxes and video gifts (differ on contract farms)
        # farm value * (percentage of farm value it drops) * occurance chance * boxes per second
        gifts = self.farm_value(pop) * (0.0125 * 0.3578 / 325 + 0.0375 * 0.1351 / 325
            + 0.0125 * 0.0868 / 285 + 0.0375 * 0.4208 / 285)
        gifts *= self.event("gift")
        if pop <= 100 or self.on_virtue():
            gifts /= 2.5

        # drones
        # occurances per hour / 3600 * farm value * percentage of tier
        m = (1 + 0.1*self.er[10])/100
        drones = (142.690/3600 * self.farm_value(pop) * (0.0001*(1-10*m) + 0.0005*7*m + 0.0025*3*m) 
                + 12.321/3600 * self.farm_value(pop) * 0.05)

        drones *= (1 - 0.3 * self.artf.drone_gold_chance/self.artf.drone_cash_chance)
        drones *= self.event("drone")

        if pop <=100 or self.on_virtue(): # Drone value decreased
            drones = drones / 2.5

        if pop < self.hab_size: # RCB when habs not full
            drones *= (self.max_rcb)**0.5

        if self.on_virtue(): # More time between drones on virtue
            drones *= 0.75

        return gifts + drones

    @property
    def elite_drone_value(self):
        value = self.event("drone") * self.farm_value() * 0.05
        if self.pop <=100 or self.on_virtue():
            value = value/2.5

        if self.pop < self.hab_size:
            value *= (self.max_rcb)**0.5

        return value



    @property
    def hatchery_capacity(self):
        return 250 + 10 * self.cr[7] + 50 * self.cr[14] + 10 * self.cr[19]

    @property
    def hatchery_refill(self):
        return 3 * (1 + 0.1 * self.cr[2]) * (1 + 0.05 * self.cr[12]) * (1 + 0.1 * self.er[1])

    @property
    def hatchery_output(self):
        return 3 + 2*self.er[0] + self.artf.hold_to_hatch

    @property
    def manual_hatchery_rate(self): # this has been tested to good confidence
        return 1/(1/self.hatchery_output + 1/self.hatchery_refill)

    @property
    def effective_rcb(self):
        return min(self.max_rcb,self.manual_hatchery_rate*self.rcb_chicken)

    @property
    def rcb_chicken(self):
        return 1 + 0.001*self.cr[3] + 0.001*self.er[8]
