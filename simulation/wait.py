from farm.farm import *
from methods import *
from simulation.commands import virtue_egg_index, index


def wait_online(state, t, printout=True, write=True):
    if isinstance(t, str): t=read_time(t)

    f = state.farm
    if t < 0:
        if printout: print(f"Duration must be positive")
        return 0
    if t < 1: t=1

    growth = f.ihr
    cash = 0
    layed = 0
    pop = f.pop
    pop0 = f.pop

    if growth == 0 or pop == f.hab_size:
        cash += f.earnings() * t
        layed += min(f.pop * f.laying_chick, f.max_shipping) * t
    else:
        t_hab = (f.hab_size - pop)/growth
        t_ship = (f.max_shipping - f.laying_chick*pop)/(f.laying_chick*growth)
        if t_ship < 0: t_ship = 0

        # farm grows unrestricted
        if t_hab>=t and t_ship>=t:
            pop += growth * t
            cash += f.earnings((pop + f.pop)/2) * t
            layed += f.laying_chick * (pop + f.pop)/2 * t

        # shipblocked
        elif t_hab>=t_ship and t_ship<t:
            pop += growth * t_ship
            cash += f.earnings((pop + f.pop)/2) * t_ship
            layed += f.laying_chick * (pop + f.pop)/2 * t_ship

            cash += f.earnings(pop) * (t - t_ship)
            layed += f.max_shipping * (t - t_ship)
            pop = min(pop+growth*(t-t_ship), f.hab_size)

        # habblocked
        elif t_hab<t and t_ship>=t_hab:
            pop = f.hab_size
            cash += f.earnings((pop + f.pop)/2) * t_hab
            layed += f.laying_chick * (pop + f.pop)/2 * t_hab

            cash += f.earnings(pop) * (t - t_hab)
            layed += f.laying_chick * pop * (t - t_hab)

    # update farm stats
    if write:
        state.time_elapsed += t
        state.eggs_layed[virtue_egg_index[f.egg]] += layed
        f.cash += cash
        f.pop = pop

    if printout:
        index(state)
        print(f"Population: {format(pop0)} -> {format(pop)}")
        print(f"Cash: {format(f.cash-cash)} -> {format(f.cash)}")
        print()
    return layed
        

def wait_offline(state, t, printout=True, write=True):
    if isinstance(t, str): t=read_time(t)
    f = state.farm
    if t < 0:
        if printout: print(f"Duration must be positive")
        return 0
    if t < 1: t=1

    growth = f.ihr_away
    cash = 0
    layed = 0
    pop = f.pop
    pop0 = f.pop

    if growth == 0 or pop == f.hab_size:
        cash += f.earnings_away() * t
        layed += min(f.pop * f.laying_chick, f.max_shipping) * t
    else:
        t_hab = (f.hab_size - pop)/growth
        t_ship = (f.max_shipping - f.laying_chick*pop)/(f.laying_chick*growth)
        if t_ship < 0: t_ship = 0
        
        # farm grows unrestricted
        if t_hab>=t and t_ship>=t: 
            pop += growth * t
            cash += f.earnings_away((pop + f.pop)/2) * t
            layed += f.laying_chick * (pop + f.pop)/2 * t

        # shipblocked
        elif t_hab>=t_ship and t_ship<t:
            pop += growth * t_ship
            cash += f.earnings_away((pop + f.pop)/2) * t_ship
            layed += f.laying_chick * (pop + f.pop)/2 * t_ship
            cash += f.earnings_away(pop) * (t - t_ship)
            layed += f.max_shipping * (t - t_ship)
            pop = min(pop+growth*(t-t_ship), f.hab_size)

        # habblocked
        elif t_hab<t and t_ship>=t_hab:
            pop = f.hab_size
            cash += f.earnings_away((pop + f.pop)/2) * t_hab
            layed += f.laying_chick * (pop + f.pop)/2 * t_hab
            cash += f.earnings_away(pop) * (t - t_hab)
            layed += f.laying_chick * pop * (t - t_hab)  
    
    # update farm stats
    if write:
        state.time_elapsed += t
        state.eggs_layed[virtue_egg_index[f.egg]] += layed
        f.cash += cash
        f.pop = pop

    if printout:
        index(state)
        print(f"Population: {format(pop0)} -> {format(pop)}")
        print(f"Cash: {format(f.cash-cash)} -> {format(f.cash)}")
        print()
    return layed


def time_cash_away(state, cash, printout=True): # leaves state unchanged!
    if isinstance(cash, str): cash = egg_read(cash)

    f = state.farm
    growth = f.ihr_away
    cash_to_go = cash - f.cash
    pop = f.pop

    if cash <= f.cash or (pop == 0 and growth == 0):
        return 0

    if growth == 0 or pop == f.hab_size:
        return cash_to_go / f.earnings_away()
    else:
        
        t_hab = (f.hab_size - pop)/growth
        t_ship = (f.max_shipping - f.laying_chick*pop)/(f.laying_chick*growth)
        if t_ship < 0: t_ship = 0
        cash_hab = f.earnings_away(growth*t_hab/2) * t_hab
        cash_ship = f.earnings_away(growth*t_ship/2) * t_ship

        # farm grows unrestricted
        if cash_hab>=cash_to_go and cash_ship>=cash_to_go: 
            return quad_formula(a=0.5*growth*f.earnings_away(1), b=0.5*f.earnings_away(f.pop), c=-cash_to_go)
        
        # shipblocked
        elif cash_hab>=cash_ship and cash_ship<cash_to_go:
            cash_to_go -= cash_ship
            pop += growth * t_ship
            return cash_to_go / f.earnings_away(pop) + t_ship

        # habblocked
        elif cash_hab<cash_to_go and cash_ship>=cash_hab:
            cash_to_go -= cash_hab
            pop = f.hab_size
            return cash_to_go / f.earnings_away(pop) + t_hab
        raise ValueError(f"Nothing works :o")


def time_layed(state, lay): # leaves state unchanged!
    if isinstance(lay, str): lay = egg_read(lay)

    f = state.farm
    growth = f.ihr_away
    lay_to_go = lay
    pop = f.pop

    if lay_to_go <= 0 or (pop == 0 and growth == 0):
        return 0

    if growth == 0 or pop == f.hab_size or f.max_shipping <= f.laying_chick*pop:
        return lay_to_go / min(f.max_shipping, f.laying_chick*pop)
    else:
        t_hab = (f.hab_size - pop)/growth
        t_ship = (f.max_shipping - f.laying_chick*pop)/(f.laying_chick*growth)
        if t_ship < 0: t_ship = 0
        lay_hab = f.laying_chick *growth/2 * t_hab
        lay_ship = f.laying_chick *growth/2 * t_ship

        # farm grows unrestricted
        if lay_hab>=lay_to_go and lay_ship>=lay_to_go: 
            return quad_formula(a=f.laying_chick*growth/2, b=f.laying_chick*pop,  c=-lay_to_go)
        
        # shipblocked
        elif lay_hab>=lay_ship and lay_ship<lay_to_go:
            lay_to_go -= lay_ship
            return lay_to_go / f.max_shipping + t_ship

        # habblocked
        elif lay_hab<lay_to_go and lay_ship>=lay_hab:
            lay_to_go -= lay_hab
            return lay_to_go / (f.laying_chick*f.hab_size) + t_hab
        raise ValueError(f"Nothing works :o")


def wait_active(state, t, printout=True, write=True):
    if isinstance(t, str): t=read_time(t)

    f = state.farm
    if t <= 0:
        if printout: print(f"Duration must be positive")
        return
    if t < 1: t=1
    
    growth = f.ihr + f.manual_hatchery_rate
    cash = 0
    layed = 0
    pop = f.pop
    pop0 = f.pop

    if  pop == f.hab_size:
        cash += f.earnings_active() * t
        layed += min(f.pop * f.laying_chick, f.max_shipping) * t
    else:
        t_hab = (f.hab_size - pop)/growth
        t_ship = (f.max_shipping - f.laying_chick*pop)/(f.laying_chick*growth)
        if t_ship < 0: t_ship = 0
        
        # farm grows unrestricted
        if t_hab>=t and t_ship>=t: 
            pop += growth * t
            cash += f.earnings((pop + f.pop)/2) * f.effective_rcb * t
            cash += (f.gifts_and_drones(pop) + f.gifts_and_drones(f.pop))/2 * t
            layed += f.laying_chick * (pop + f.pop)/2 * t

        # shipblocked
        elif t_hab>=t and t_ship<t:
            pop += growth * t_ship
            cash += f.earnings((pop + f.pop)/2) * f.effective_rcb * t_ship
            cash += (f.gifts_and_drones(pop) + f.gifts_and_drones(f.pop))/2 * t_ship
            layed += f.laying_chick * (pop + f.pop)/2 * t_ship

            cash += f.earnings(pop) * f.effective_rcb* (t - t_ship)
            cash += (f.gifts_and_drones(pop) + f.gifts_and_drones(pop + growth * (t - t_ship)))/2 * (t - t_ship)
            layed += f.max_shipping * (t - t_ship)
            pop += growth * (t - t_ship)

        # habblocked
        elif t_hab<t and t_ship>=t_hab:
            pop = f.hab_size
            cash += f.earnings(pop + f.pop/2) * f.effective_rcb * t_hab
            cash += (f.gifts_and_drones(pop-1) + f.gifts_and_drones(f.pop))/2 * t_hab
            layed += f.laying_chick * (pop + f.pop)/2 * t_hab
            
            cash += f.earnings(pop) * (t - t_hab)
            cash += f.gifts_and_drones(pop) * (t - t_hab)
            layed += f.laying_chick * pop * (t - t_hab)

        # shipblocked, then habblocked
        elif t_hab<t and t_ship<t_hab:
            pop += growth * t_ship
            cash += f.earnings((pop + f.pop)/2) * f.effective_rcb * t_ship
            cash += (f.gifts_and_drones(pop) + f.gifts_and_drones(f.pop))/2 * t_ship
            layed += f.laying_chick * (pop + f.pop)/2 * t_ship

            cash += f.earnings(pop) * f.effective_rcb * (t_hab - t_ship)
            cash += (f.gifts_and_drones(pop) + f.gifts_and_drones(f.hab_size-1))/2 * (t_hab - t_ship)
            layed += f.max_shipping * (t_hab - t_ship)

            cash += f.earnings(pop) * (t - t_hab)
            pop = f.hab_size
            cash += f.gifts_and_drones(pop) * (t - t_hab)
            layed += f.max_shipping * (t - t_hab)   

    # update farm state
    if write:
        state.time_elapsed += t
        state.eggs_layed[virtue_egg_index[f.egg]] += layed
        f.cash += cash
        f.pop = pop

    if printout:
        index(state)
        print(f"Population: {format(pop0)} -> {format(pop)}")
        print(f"Cash: {format(f.cash-cash)} -> {format(f.cash)}")
        print()
    return layed


def time_cash_active(state, cash, printout=True): # leaves state unchanged!
    if isinstance(cash, str): cash = egg_read(cash)

    f = state.farm
    growth = f.ihr + f.manual_hatchery_rate
    cash_to_go = cash - f.cash
    pop = f.pop

    if cash <= f.cash or (pop == 0 and growth == 0):
        return 0

    if pop == f.hab_size:
        if printout: print(f"Takes {format_time(cash_to_go / f.earnings_active())}")
        return cash_to_go / f.earnings_active()
    else:
        t_hab = (f.hab_size - pop)/growth
        t_ship = (f.max_shipping - f.laying_chick*pop)/(f.laying_chick*growth)
        if t_ship < 0: t_ship = 0
        if t_hab>=t_ship:
            cash_ship = (f.earnings(pop + growth*t_ship/2) * f.effective_rcb + (f.gifts_and_drones(pop) + f.gifts_and_drones(min(pop+growth*t_ship,f.hab_size-1)))/2) * t_ship
            cash_hab = cash_ship + (f.earnings(growth*t_ship) + f.gifts_and_drones(0.5*(pop+f.hab_size)))*(t_hab-t_ship)
        else: 
            cash_hab = (f.earnings(pop + growth*t_hab/2) * f.effective_rcb + (f.gifts_and_drones(pop) + f.gifts_and_drones(f.hab_size-1))/2)  * t_hab
            cash_ship = cash_hab + 1

        # farm grows unrestricted (this works)
        if cash_hab>=cash_to_go and cash_ship>=cash_to_go:
            t = quad_formula(
                a=f.earnings(1)*f.effective_rcb*growth + (f.gifts_and_drones(f.hab_size-1) - f.gifts_and_drones(0))/f.hab_size*growth,
                b=f.earnings(f.pop)*f.effective_rcb + f.gifts_and_drones(f.pop) + f.gifts_and_drones(0) + (f.gifts_and_drones(f.hab_size-1) - f.gifts_and_drones(0))/f.hab_size*f.pop,
                c=-2*cash_to_go)

            if printout:
                print(f"Takes {format_time(t)}")  
            return max(t, 1)
        
        # shipblocked (a litle small sometimes dues to 0.6 part)
        elif cash_hab>=cash_to_go and cash_ship<cash_to_go:
            cash_to_go -= cash_ship
            pop += growth * t_ship
            t = quad_formula(
                a=(f.gifts_and_drones(f.hab_size-1) - f.gifts_and_drones(pop))/(f.hab_size-pop)*growth,
                b=2*f.earnings(pop)*f.effective_rcb + f.gifts_and_drones(pop) + f.gifts_and_drones(pop) + (f.gifts_and_drones(f.hab_size-1) - f.gifts_and_drones(pop))/(f.hab_size-pop)*pop,
                c=-2*cash_to_go)
            if printout: print(f"Takes {format_time(t*1.2+t_ship)}")
            return t*1.2 + t_ship #factor to compensate

        # habblocked
        elif cash_hab<cash_to_go and cash_ship>=cash_hab:
            cash_to_go -= cash_hab
            pop = f.hab_size
            if printout: print(f"Takes {format_time(cash_to_go / (f.earnings(pop)+f.gifts_and_drones(pop)) + t_hab)}")
            
            return cash_to_go / (f.earnings(pop)+f.gifts_and_drones(pop)) + t_hab

        # shipblocked, then habblocked (a litle small sometimes dues to ^0.6 part of farm value)
        elif cash_hab>=cash_ship and cash_ship<cash_to_go:
            cash_to_go -= cash_ship
            pop += growth * t_ship
            cash_to_go -= (f.earnings(pop) * f.effective_rcb + (f.gifts_and_drones((pop+f.hab_size)/2))) * (t_hab - t_ship)
            pop = f.hab_size
            if printout: print(f"Takes {format_time(cash_to_go / (f.earnings(pop)+f.gifts_and_drones(pop))*1.2 + t_hab)}")

            return cash_to_go / (f.earnings(pop)+f.gifts_and_drones(pop))*1.2 + t_hab
        raise ValueError(f"Nothing works :o")


def time_layed_active(state, lay): # leaves state unchanged!
    if isinstance(lay, str): lay = egg_read(lay)

    f = state.farm
    growth = f.ihr + f.manual_hatchery_rate
    lay_to_go = lay
    pop = f.pop

    if lay_to_go <= 0 or (pop == 0 and growth == 0):
        return 0

    if growth == 0 or pop == f.hab_size or f.max_shipping <= f.laying_chick*pop:
        return lay_to_go / min(f.max_shipping, f.laying_chick*pop)
    else:
        t_hab = (f.hab_size - pop)/growth
        t_ship = (f.max_shipping - f.laying_chick*pop)/(f.laying_chick*growth)
        if t_ship < 0: t_ship = 0
        lay_hab = f.laying_chick *growth/2 * t_hab
        lay_ship = f.laying_chick *growth/2 * t_ship

        # farm grows unrestricted
        if lay_hab>=lay_to_go and lay_ship>=lay_to_go: 
            return quad_formula(a=f.laying_chick*growth/2, b=f.laying_chick*pop,  c=-lay_to_go)
        
        # shipblocked
        elif lay_hab>=lay_ship and lay_ship<lay_to_go:
            lay_to_go -= lay_ship
            return lay_to_go / f.max_shipping + t_ship

        # habblocked
        elif lay_hab<lay_to_go and lay_ship>=lay_hab:
            lay_to_go -= lay_hab
            return lay_to_go / (f.laying_chick*f.hab_size) + t_hab
        raise ValueError(f"Nothing works :o")