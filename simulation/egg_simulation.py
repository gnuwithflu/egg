from farm.farm import *
from methods import *
from simulation.wait import *
from simulation.commands import *



def curiosity(state, s, printout=True):
    simulate_egg(state, s, "curiosity", printout)
def kindness(state, s, printout=True):
    simulate_egg(state, s, "kindness", printout)
def resilience(state, s, printout=True):
    simulate_egg(state, s, "resilience", printout)
def humility(state, s, printout=True):
    simulate_egg(state, s, "humility", printout)
def integrity(state, s, printout=True):
    simulate_egg(state, s, "integrity", printout)


def simulate_egg(state, s, egg, printout=True):
    if s.endswith("te"):
        mode_time = False
        s = s.removesuffix("te")
        lay = te_treshholds(int(s))
        if lay <= state.eggs_layed[virtue_egg_index[egg]]:
            return
    else:
        if isinstance(s, str): time=read_time(s)
        else: time = s
        lay=0
        mode_time = True
        
    f = state.farm
    if f.egg != egg:
        shift(state, egg, printout=False)
        
    time_zero = state.time_elapsed
    counter = 0
    layed0 = state.eggs_layed[virtue_egg_index[egg]]
    
    def cond():
        if mode_time: 
            return state.time_elapsed-time_zero<time
        return state.eggs_layed[virtue_egg_index[egg]]<lay

    def enough(t):
        if mode_time:
            return state.time_elapsed - time_zero + t < time
        return state.eggs_layed[virtue_egg_index[f.egg]] + wait_offline(state, t, False, False) < lay

    def time_max():
        if mode_time:
            return time-state.time_elapsed + time_zero
        return time_layed_active(state, lay-state.eggs_layed[virtue_egg_index[f.egg]])

    while cond():
        if not mode_time: time = (lay - layed0) / min(f.laying_chick*f.hab_size, f.max_shipping)

        min_index, min_price = find_cheapest(state, mode_time, time-state.time_elapsed + time_zero, lay)
        
        if min_index is None:
            break

        if f.cash >= min_price:
            if not buy(state, min_index, printout=False):
                print(f"You should not see this")
                break
            counter += 1
            continue
       
        if f.pop < f.hab_size and f.ihr == 0:
            wait_active(state, t=min((f.hab_size-f.pop)/(f.ihr + f.manual_hatchery_rate), time/10, time_max()), printout=False)      
            continue  
      
        if enough(time_cash_away(state, min_price)):
            if f.earnings_active()>f.earnings_away():
                wait_active(state, 1.01*time_cash_active(state, min_price, False), printout=False)
            else:
                wait_offline(state, 1.001*time_cash_away(state, min_price, False), printout=False)

            if not buy(state, min_index, printout=False):
                print(f"You should not see this at all ({f.egg})")
                break            
            counter += 1
            continue
        break
    if mode_time:
        wait_offline(state, time - state.time_elapsed + time_zero, printout=False)
    else:
        if f.earnings_active()>f.earnings_away() and not (f.pop == 0 and f.ihr != 0):
            wait_active(state, time_layed_active(state, lay-state.eggs_layed[virtue_egg_index[egg]]), printout=False)
        else:
            wait_offline(state, time_layed(state, lay-state.eggs_layed[virtue_egg_index[egg]]), printout=False)
    buy_all(state)

    if printout:      
        index(state)
        print(f"Spent {format_time(state.time_elapsed-time_zero)} on {egg}.")
        print(f"Bought {counter} upgrades")
        print(f"Eggs layed {format(layed0)} -> {format(state.eggs_layed[virtue_egg_index[egg]])}")    
    return


def find_cheapest(state, mode_time=None, time_rest=0, lay=0):
    f = state.farm
    min_index = None
    min_price = np.inf

    def enough(t):
        if mode_time:
            return t < time_rest
        return state.eggs_layed[virtue_egg_index[f.egg]] + wait_offline(state, t, False, False) < lay

    if f.egg == "resilience":
        if f.silos < 10:
            min_index = 1
            min_price = silo_price[f.silos]
    elif f.egg == "integrity":
        for i in range(len(f.habs)):
            if f.habs[i]==19:
                continue
            same_habs = 0
            for j in range(4):
                if f.habs[j] == f.habs[i]+1: same_habs+=1
            upgrade_cost = hab_prices[f.habs[i]][same_habs] * (1-0.05*f.er[5]) * f.coll_effect("flame") * f.event("hab")
            if upgrade_cost < min_price:
                min_price = upgrade_cost
                min_index = i

    elif f.egg == "kindness":
        for i in range(f.max_vehicle_number):
            if f.vehicles[i]<f.max_vehicle_level:
                same_vehicles = 0
                for j in range(f.max_vehicle_number):
                    if f.vehicles[j] == f.vehicles[i]+1:
                        same_vehicles += 1
                upgrade_cost = vehicle_prices[int(f.vehicles[i])][same_vehicles] * (1-0.05*f.er[6]) * f.coll_effect("lithium") * f.event("veh")
                if upgrade_cost < min_price:
                    min_price = upgrade_cost
                    min_index = i
    
    elif f.egg == "curiosity":
        min_price_eff = np.inf
        for i in range(len(f.cr)):
            if research_available(state=state, cr_index=i):
                upgrade_cost = cr_prices[i][int(f.cr[i])] * f.artf.cr_cost * (1-0.05*f.er[7]) * f.coll_effect("waterballoon") * f.event("cr")
                if upgrade_cost / cr_priority(state, i) < min_price_eff and enough(time_cash_away(state, upgrade_cost)):
                    min_price_eff = upgrade_cost / cr_priority(state, i)
                    min_price = upgrade_cost
                    min_index = i

    return min_index, min_price    