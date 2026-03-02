import re
import os, sys
import random
import shutil

from farm.farm import *
from methods import *
from farm.prices import *



virtue_egg_index = {
    "curiosity": 0,
    "kindness": 1,
    "resilience": 2,
    "humility": 3,
    "integrity": 4
}

treshholds = [0, 50e6, 1e9, 10e9, 70e9, 500e9, 2e12, 7e12, 20e12, 60e12, 150e12, 500e12, 1.5e15, 4e15, 10e15, 25e15, 50e15, 100e15]


class State:
    def __init__(self, farm, time_elapsed, eggs_layed, shifts):
        self.farm = farm
        self.time_elapsed = time_elapsed
        self.eggs_layed = eggs_layed
        self.shifts = shifts

        self.shifts_start = shifts
        self.te_claimed = [0,0,0,0,0]
        for i in range(5):
            self.te_claimed[i] = te_numbers(self.eggs_layed[i])

def te_treshholds(n):
    # returns how many eggs layed are needed for n TE
    if n<17:
        return treshholds[n]
    return 1e17 + (n-17)*1e16*(n/2 - 4)

def te_numbers(eggs_layed):
    # number of te obtained when having a certain number of eggs layed
    i = 0
    while i<18:
        if te_treshholds(i)>eggs_layed:
            return i - 1
        i += 1
    return math.floor(quad_formula(a=0.5, b=-12.5, c=68-(eggs_layed-1e17)/1e16))

def te_growth(state):
    # return how many TE are pending (yah, this is poorly named)
    total = 0
    for i in range(5):
        total += te_numbers(state.eggs_layed[i])-state.te_claimed[i]
    return total
    
def research_available(state, cr_index):
    # is it allowed to upgrade a certain common research?
    if state.farm.cr[cr_index] == max_cr[cr_index]:
        return False
    research_count = sum(state.farm.cr)
    if cr_bounds[cr_names[cr_index][0]-1] > research_count:
        return False
    return True

def print_event(state, compact=True):
    # print out the events active right now
    l = []
    for e in state.farm.event_effects:
        if state.farm.event_effects[e] != 1:
            l.append(e)
    if len(l)==0:
        return ""
    if len(l)>1:
        if compact: return f"multiple events"
        else: 
            s = ""
            for e in l: s += f"{state.farm.event_effects[e]}x{e}, "
            s = s.removesuffix(", ")
            return s
    return f"{state.farm.event_effects[l[0]]}x{l[0]}"

def cr_priority(state, cr_index, time=0):
    # weights the cr by how much it is worth buying
    f = state.farm
    earnings0 = f.earnings(1)
    shipping0 = f.max_shipping
    hab0 = f.hab_size
    veh0 = f.max_vehicle_number
    effect = 0

    f.cr[cr_index] += 1
    effect += ((f.earnings(1)/earnings0)-1)*500
    # After trying a lot of different weight distributions, I found that those two arent useful at all
    #effect += (f.max_shipping/shipping0-1)*min(f.laying_chick*f.pop/f.max_shipping,1)*300
    #effect += (f.hab_size/hab0-1)*0
    if time>0.9: effect += (f.max_vehicle_number/veh0-1)*10000
    effect += 7
    f.cr[cr_index] -= 1
    return effect


def set_egg():
    os.system('clear')
    print("-----------------------------------------")
    print("| GnuWithFlu's Path of Virtue simulator |")
    print("-----------------------------------------")
    print()
    print("\033[34mWhich egg do you start on?\033[0m curiosity, kindness, resilience, humility or integrity?")

    while True:
        s = input()
        if s in {"curiosity", "kindness", "resilience", "humility", "integrity"}: return s
        sys.stdout.write("\033[1A\r\033[K")

def set_te():
    os.system('clear')
    print("-----------------------------------------")
    print("| GnuWithFlu's Path of Virtue simulator |")
    print("-----------------------------------------")
    print()
    print("\033[34mHow many TE do you have?\033[0m")
    while True:
        s = input()
        sys.stdout.write("\033[1A\r\033[K")
        try:
            if int(s)<0:
                continue
            return int(s)
        except ValueError:
            continue

def set_eggs_layed():
    os.system('clear')
    print("-----------------------------------------")
    print("| GnuWithFlu's Path of Virtue simulator |")
    print("-----------------------------------------")
    print()
    print("\033[34mHow many eggs have you already layed on each farm?\033[0m")
    print("Please enter 5 numbers separated by spaces for CKRHI, e.g. \"14M 27B 13.2T 150M 0\"")
    while True:
        s = input()
        sys.stdout.write("\033[1A\r\033[K")

        try:
            parts = s.split()
            if len(parts)!=5: continue
            return [egg_read(parts[0]), egg_read(parts[1]), egg_read(parts[2]), egg_read(parts[3]), egg_read(parts[4])]
        except ValueError:
            continue

def help(state, s=""):
    print(f"\033[34mYou can enter the following commands:\033[0m")
    print(f"\033[32mhelp\033[0m: Show this list of commands")
    print(f"\033[32mstats\033[0m: Show some more stats")
    print(f"\033[32mvirtue\033[0m: Show eggs shipped and TE claimed")
    print(f"\033[32mcr/hab/veh/silo\033[0m: Show respective status")
    print(f"\033[32mrun <number>\033[0m: Increases your population as if you ran chickens")
    print(f"\033[32mwait <duration>\033[0m: Wait with closed the game")
    print(f"\033[32mwaitonline <duration>\033[0m: Wait online, doing nothing")
    print(f"\033[32mwaitactive <duration>\033[0m: Wait online, running chickens, catching drones and gifts")
    print(f"\033[32mtimeaway <cash>\033[0m: How long does it take to obtain that cash when away?")
    print(f"\033[32mtimeactive <cash>\033[0m: How long does it take to obtain that cash when activ?")
    print(f"\033[32mbuy <number>\033[0m: Buy cr, hab, veh or silo")
    print(f"\033[32mbuyall\033[0m: Buy everything you can afford")
    print(f"\033[32m<egg> <duration>\033[0m: Simulates you are on that farm")    
    print(f"\033[32mshift <egg>\033[0m: Shift to another egg")
    print(f"\033[32mevent <event>\033[0m: Start event. Every false input resets events")    
    print(f"\033[32mprestige\033[0m: Leave the simulation")

    print()

def index(state, s=""):
    # index aka header which shows most of the important information
    from simulation.wait import time_layed
    egg = virtue_egg_index[state.farm.egg]
    egg_name = "\033[34m" + state.farm.egg.capitalize() + " egg farm\033[31m"
    layed = "Layed: \033[32m" + str(format(state.eggs_layed[egg])) + "/" +str(format(te_treshholds(te_numbers(state.eggs_layed[egg])+1)))
    te = "Total TE: \033[32m" + str(int(float(format(state.farm.te)))) + "+" + str(te_growth(state))
    te_egg = "Truth Eggs: \033[32m" + str(int(state.te_claimed[egg])) + "+" + str(te_numbers(state.eggs_layed[egg])-state.te_claimed[egg])
    time_te = "Next TE: \033[32m" + str(format_time(time_layed(state, te_treshholds(te_numbers(state.eggs_layed[egg])+1) - state.eggs_layed[egg])))
    pop = "Pop: \033[32m" + str(format(int(state.farm.pop))) + "/" + str(format(int(state.farm.hab_size)))
    cash = "Cash: \033[32m" + str(format(state.farm.cash))
    laying = "Laying: \033[32m" + str(format(state.farm.laying_chick*int(state.farm.pop)*60)) + "/min"
    shipping = "Shipping: \033[32m" + str(format(state.farm.max_shipping*60)) + "/min"
    active = "Active: \033[32m" + str(format(state.farm.earnings_active())) + "/s"
    os.system('clear')
    print("-----------------------------------------")
    print("| GnuWithFlu's Path of Virtue simulator |")
    print("-----------------------------------------")
    print()
    print(f"{egg_name:<20} {print_event(state, compact=False):>22}\033[0m") 
    print(f"{"Time: \033[32m"}{format_time(state.time_elapsed):<15}\033[0m{layed:<20}\033[0m")
    print(f"{te_egg:<25}\033[0m {te}\033[0m")
    print(f"{time_te:<24}\033[0m  Shifts: \033[32m{int(float(format(state.shifts)))}\033[0m")
    print(f"{pop:<25}\033[0m {cash:<20}\033[0m")
    print(f"{laying:<26}\033[0m{shipping:<20}\033[0m")
    print(f"{active:<25}\033[0m Offline: \033[32m{format(state.farm.earnings_away())}/s\033[0m")
    print()

def status(state, s=""):
    # Some additional information
    print(f"\033[34m----- Status -----\033[0m")
    print(f"Farm Value: \033[32m{format(state.farm.farm_value())}\033[0m")
    print(f"Egg Value: \033[32m{format(state.farm.egg_value)}\033[0m")
    print(f"IHR: \033[32m{format(state.farm.ihr*60)}/min\033[0m")
    print(f"Elite Drone (max RCB): \033[32m{format(state.farm.elite_drone_value)}\033[0m")
    print(f"Events active: \033[32m{print_event(state, compact=False)}\033[0m")

    print()

def virtue(state, s=""):
    # prints virtue stats
    print(f"\033[34m----- Virtue Stats -----\033[0m")
    print(f"Egg         Layed     Goal      TE")
    print(f"Curiosity:  \033[32m{format(state.eggs_layed[0]):<9} {format(te_treshholds(te_numbers(state.eggs_layed[0])+1)):<9} {state.te_claimed[0]}+{te_numbers(state.eggs_layed[0])-state.te_claimed[0]}\033[0m")
    print(f"Kindness:   \033[32m{format(state.eggs_layed[1]):<9} {format(te_treshholds(te_numbers(state.eggs_layed[1])+1)):<9} {state.te_claimed[1]}+{te_numbers(state.eggs_layed[1])-state.te_claimed[1]}\033[0m")
    print(f"Resilience: \033[32m{format(state.eggs_layed[2]):<9} {format(te_treshholds(te_numbers(state.eggs_layed[2])+1)):<9} {state.te_claimed[2]}+{te_numbers(state.eggs_layed[2])-state.te_claimed[2]}\033[0m")
    print(f"Humility:   \033[32m{format(state.eggs_layed[3]):<9} {format(te_treshholds(te_numbers(state.eggs_layed[3])+1)):<9} {state.te_claimed[3]}+{te_numbers(state.eggs_layed[3])-state.te_claimed[3]}\033[0m")
    print(f"Integrity:  \033[32m{format(state.eggs_layed[4]):<9} {format(te_treshholds(te_numbers(state.eggs_layed[4])+1)):<9} {state.te_claimed[4]}+{te_numbers(state.eggs_layed[4])-state.te_claimed[4]}\033[0m")
    print()


def run_chickens(state, s, printout=True):
    # increases chicken number, does not take any time
    if isinstance(s, str): number=egg_read(s)
    else: number = s
    population = state.farm.pop
    if number + population <= state.farm.hab_size:
        state.farm.pop += number
    else: state.farm.pop = state.farm.hab_size
    if printout:
        index(state)
        print(f"population increased from \033[32m{format(population)}\033[0m to \033[32m{format(state.farm.pop)}\033[0m")
        print()

def shift(state, new_egg, printout=True):
    # change egg
    if new_egg not in virtue_egg_index or new_egg==state.farm.egg:
        print("Invalid egg")
        return
    state.farm.egg = new_egg
    state.farm.cash = 0
    state.farm.pop = 0
    state.shifts += 1
    if printout:
        index(state)
        print(f"Shifted to {new_egg} egg farm")
        print()
    
def prestige(state, s):
    # prestige and finish an ascension
    te_updated = 0
    for i in range(5):
        te_updated += te_numbers(state.eggs_layed[i])

    os.system('clear')
    print(f"\033[35m----- Ascension completed! -----\033[0m")
    print(f"Spend \033[32m{format_time(state.time_elapsed)}\033[0m on this run")
    print(f"Eggs of Truth: \033[32m{state.farm.te} -> {te_updated}\033[0m")
    print(f"Shifts: \033[32m{state.shifts_start} -> {state.shifts}\033[0m")
    if state.time_elapsed > 0: print(f"That's \033[32m{format((te_updated-state.farm.te)/(state.time_elapsed/3600/24))}\033[0m te/day")
    if state.shifts-state.shifts_start>0:   
        print(f"Or \033[32m{format((te_updated-state.farm.te)/(state.shifts-state.shifts_start))}\033[0m te/shift")
        if state.time_elapsed > 0: print(f"Or \033[32m{format((te_updated-state.farm.te)/(state.shifts-state.shifts_start)/(state.time_elapsed/3600/24))}\033[0m te/shift/day")

    print()
    virtue(state)
    for i in range(5):
        state.te_claimed[i] = te_numbers(state.eggs_layed[i])

    print("Press enter to continue to the next ascension")
    input()

    state.time_elapsed = 0

    f2 = Farm(egg=set_egg(), 
            er=state.farm.er, 
            colleggtibles=state.farm.colleggtibles, 
            vehicles=[1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], 
            te=te_updated, 
            silos=1, 
            habs=[1,0,0,0],
            artifact_set=state.farm.artf,
            video_doubler=state.farm.video_doubler)
        
    state.farm = f2
    index(state)
    return

def silo_status(state, s=""):
    print(f"\033[34m----- Silos -----\033[0m")
    print(f"You own \033[32m{state.farm.silos}\033[0m silos")
    print(f"Max away time: \033[32m{state.farm.max_away_time/60}h\033[0m")

    if state.farm.silos == 10:
        print(f"Silos are maxed")
        print()

        return
    print(f"Upgrade cost: \033[32m{format(silo_price[state.farm.silos])}\033[0m")
    print()

def hab_status(state, s=""):
    print(f"\033[34m----- Habitats -----\033[0m")
    print(f"Habs: \033[32m{state.farm.habs[0]} {state.farm.habs[1]} {state.farm.habs[2]} {state.farm.habs[3]}\033[0m")
    print(f"Hab size: \033[32m{format(state.farm.hab_size)}\033[0m")

    for i in range (4):
        if state.farm.habs[i] == 19:
            print(f"Hab \033[32m{i}\033[0m is maxed")
        else: 
            same_habs = 0
            for j in range(4):
                if state.farm.habs[j] == state.farm.habs[i]+1: same_habs+=1
            print(f"Upgrade cost {i}: \033[32m{format(hab_prices[state.farm.habs[i]][same_habs] * (1-0.05*state.farm.er[5]) * state.farm.coll_effect("flame") * state.farm.event("hab"))}\033[0m")
    print()

def vehicle_status(state, s=""):
    print(f"\033[34m----- Vehicles -----\033[0m")
    print(f"Vehicles:", end='')
    for i in range(state.farm.max_vehicle_number):
        print(f" \033[32m{int(state.farm.vehicles[i])}\033[0m", end='')
    print()
    print(f"Shipping capacity: \033[32m{format(state.farm.max_shipping*60)}/min\033[0m")

    for i in range(state.farm.max_vehicle_number):
        if state.farm.vehicles[i] == 23:
            print(f"Vehicle {i} is maxed")

        elif state.farm.vehicles[i] == state.farm.max_vehicle_level:
            print(f"Vehicle {i} can't be upgraded, buy more cr!")
        elif state.farm.vehicles[i] > 12 and state.farm.vehicles[i] < 18 + state.farm.cr[50] :
            print(f"Upgrade cost {i}: \033[32m{format(vehicle_prices[12][state.farm.vehicles[i]-12] * (1-0.05*state.farm.er[6]) * state.farm.coll_effect("lithium") * state.farm.event("veh"))}\033[0m")
        else: 
            same_vehicles = 0
            for j in range(state.farm.max_vehicle_number):
                if state.farm.vehicles[j] == state.farm.vehicles[i]+1: same_vehicles+=1
            print(f"Upgrade cost {i}: \033[32m{format(vehicle_prices[int(state.farm.vehicles[i])][same_vehicles] * (1-0.05*state.farm.er[6]) * state.farm.coll_effect("lithium") * state.farm.event("veh"))}\033[0m")
    print()

def cr_status(state, s=""):
    print(f"\033[34m----- Research -----\033[0m")
    for i in range(len(state.farm.cr)):
        if research_available(state=state, cr_index=i):
            print(f"{i} \033[31m{cr_names[i][1]}\033[0m ({cr_names[i][2]}) Level \033[32m{int(state.farm.cr[i])}/{max_cr[i]}\033[0m costs \033[32m{format(cr_prices[i][int(state.farm.cr[i])] * state.farm.artf.cr_cost * (1-0.05*state.farm.er[7]) * state.farm.coll_effect("waterballoon") * state.farm.event("cr"))}\033[0m" )
    research_count = sum(state.farm.cr)
    for i in range(len(cr_bounds)-1):
        if cr_bounds[i] > research_count:
            print(f"Next tier unlocked in \033[32m{int(cr_bounds[i] - research_count)}\033[0m researches")
            print()
            return
    print()
    
def ship_status(state, s=""):
    print(f"\033[34m----- Ships -----\033[0m")
    for i in range(len(ship_prices)):
        print(f"\033[31m{ship_prices[i][0]}\033[0m: every \033[32m{format_time(ship_prices[i][1]/state.farm.earnings_away())}\033[0m")

def artifact_action(state, s=""):
    # both showing and setting artifacts, depending on the arguments
    rarity_map = {"C": 0, "R": 1, "E": 2, "L": 3}
    if s != "":
        if state.farm.egg != "humility":
            print("You can only set artifacts on humility!")
            return
        parts = s.split()
        if len(parts) < 2:
            print("Usage: art <slot 1-4> T<tier><rarity><type> [T<tier><stonetype> ...]")
            print("  e.g. art 1 T4Ltotem T3lunar T3lunar T3lunar")
            return

        if parts[0] not in ("1", "2", "3", "4"):
            print("Slot must be 1-4")
            return
        slot = int(parts[0]) - 1

        art_match = re.fullmatch(r'T([1-4])([CREL])([a-z]+)', parts[1])
        if not art_match:
            print("Invalid artifact format. Use T<tier><rarity><type>, e.g. T4Ltotem")
            return
        tier = int(art_match.group(1))
        rarity = rarity_map[art_match.group(2)]
        art_type = art_match.group(3)

        stones = [Stone(), Stone(), Stone()]
        for i, stone_str in enumerate(parts[2:5]):
            stone_match = re.fullmatch(r'T([2-4])([a-z]+)', stone_str)
            if not stone_match:
                print(f"Invalid stone format: {stone_str}. Use T<tier><stonetype>, e.g. T3lunar")
                return
            try:
                stones[i] = Stone(type=stone_match.group(2), level=int(stone_match.group(1)))
            except KeyError:
                print(f"Unknown stone: {stone_str}")
                return

        try:
            new_art = Artifact(type=art_type, level=tier, rarity=rarity,
                               stone1=stones[0], stone2=stones[1], stone3=stones[2])
        except (KeyError, ValueError) as e:
            print(f"Error: {e}")
            return

        arts = list(state.farm.artf.a)
        arts[slot] = new_art
        try:
            state.farm.artf = Artifact_set(arts[0], arts[1], arts[2], arts[3])
        except Exception as e:
            print(f"Error: {e}")
            return

    art_set = state.farm.artf.a
    print(f"\033[34m----- Artifacts -----\033[0m")
    for i in range(4):
        print(f"#{i+1}: \033[32m{art_set[i].name:<12}\033[0m", end='')
        for j in range(3):
            if art_set[i].stones[j].type != "":
                print(f" | {art_set[i].stones[j].name}", end='')
        print()



def buy(state, s="", printout=True):
    # distribute the buy keyword depending on the egg
    f = state.farm
    if f.egg == "resilience":
        return buy_silo(state, printout)
    elif s=="":
        if printout: print("No item selected")
        return False
    elif f.egg == "integrity":
        return buy_hab(state, int(s), printout)
    elif f.egg == "kindness":
        return buy_vehicle(state, int(s), printout)
    elif f.egg == "curiosity":
        return buy_cr(state, int(s), printout)
    elif f.egg == "humility":
        return True
    return False

def buy_all(state, s=""):
    # distribute the buyall keyword depending on the egg
    f = state.farm
    if f.egg == "resilience":
        buy_silo_all(state)
    elif f.egg == "integrity":
        buy_hab_all(state)
    elif f.egg == "kindness":
        buy_vehicle_all(state)
    elif f.egg == "curiosity":
        buy_cr_all(state)
    return False

def buy_silo(state, printout=True):
    f = state.farm
    if f.egg != "resilience":
        print(f"You cant buy silos from {f.egg} egg farm!")
        return False
    if f.silos >= 10:
        print(f"Already maxed silos!")
        return False
    if f.cash < silo_price[f.silos]:
        print(f"Not enough cash!")
        return False

    f.cash -= silo_price[f.silos]
    f.silos += 1
    if printout:
        index(state)
        print(f"Now you own {f.silos} silos!")
        print()
    return True

def buy_silo_all(state):
    f = state.farm
    counter=0
    while f.silos<10 and f.cash>silo_price[f.silos]:
        if buy_silo(state):
            counter+=1
        else:
            break
    index(state)
    print(f"Bought {counter} silos!")
    print()
    return

def buy_hab(state, hab, printout=True):
    f = state.farm
    if hab<0 or hab>3:
        print(f"Invalid hab: {hab}")
        return False
    if f.egg != "integrity":
        print(f"You cant buy habs from {f.egg} egg farm!")
        return False
        
    if f.habs[hab] == 19:
        print(f"Hab {hab} is maxed")
        return False

    same_habs = 0
    for j in range(4):
        if f.habs[j] == f.habs[hab]+1: same_habs+=1
    upgrade_cost = hab_prices[f.habs[hab]][same_habs] * (1-0.05*f.er[5]) * f.coll_effect("flame") * f.event("hab")
 
    if f.cash<upgrade_cost:
        index(state)
        print(f"Not enough cash!")
        return False
    
    f.cash -= upgrade_cost
    f.habs[hab] += 1
    if printout:
        index(state)
        print(f"Upgraded hab {hab} from {f.habs[hab]-1} to {f.habs[hab]}!")
        print()
    return True

def buy_hab_all(state):
    f = state.farm
    counter=0
    while True:
        counter+=1
        min_price = 1e34
        min_index = -1

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

        if min_index==-1 or f.cash<min_price: 
            if(counter==1):
                print("No hab bought :(")
            else:
                index(state)
                print(f"Bought {counter-1} habs!")
            print()
            break
        if not buy_hab(state, min_index, printout=False): break

def buy_vehicle(state, vehicle, printout=True):
    f = state.farm
    if vehicle<0 or vehicle>=f.max_vehicle_number:
        print(f"Invalid vehicle: {vehicle}")
        return False
    if f.egg != "kindness":
        print(f"You cant buy vehicles from {f.egg} egg farm!")
        return False

    if f.vehicles[vehicle] == f.max_vehicle_level:
        print(f"Vehicle {vehicle} is maxed")
        return False

    if f.vehicles[vehicle]>12:
        upgrade_cost = vehicle_prices[12][f.vehicles[vehicle]-12] * (1-0.05*f.er[6]) * f.coll_effect("lithium") * f.event("veh")
    else:
        same_vehicles = 0
        for j in range(f.max_vehicle_number):
            if f.vehicles[j] == f.vehicles[vehicle]+1: same_vehicles+=1
        upgrade_cost = vehicle_prices[int(f.vehicles[vehicle])][same_vehicles] * (1-0.05*f.er[6]) * f.coll_effect("lithium") * f.event("veh")

    if f.cash<upgrade_cost:
        print(f"Not enough cash!")
        return False
    
    f.cash -= upgrade_cost
    f.vehicles[vehicle] += 1
    if printout:
        index(state)
        print(f"Upgraded vehicle {vehicle} from {int(f.vehicles[vehicle]-1)} to {int(f.vehicles[vehicle])}!")
        print()
    return True

def buy_vehicle_all(state):
    f = state.farm
    counter=0
    while True:
        counter+=1
        min_price = 1e28
        min_index = -1

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

        if min_index==-1 or f.cash<min_price: 
            if(counter==1):
                print("No vehicle bought :(")
            else:
                index(state)
                print(f"Bought {counter-1} vehicles!")
            print()
            break
        if not buy_vehicle(state, min_index, printout=False):
            break

def buy_cr(state, cr_index, printout=True):
    f = state.farm
    if f.egg != "curiosity":
        print(f"You cant buy research from {f.egg} egg farm!")
        return False
    if not research_available(state=state, cr_index=cr_index):
        print(f"Research not available")
        return False
    upgrade_cost = cr_prices[cr_index][int(f.cr[cr_index])] * f.artf.cr_cost * (1-0.05*f.er[7]) * f.coll_effect("waterballoon") * f.event("cr")

    if f.cash<upgrade_cost:
        print(f"Not enough cash!")
        return False
    
    f.cash -= upgrade_cost
    f.cr[cr_index] += 1
    if printout:
        index(state)
        print(f"Researched {cr_names[cr_index][1]} to level {int(f.cr[cr_index])}/{max_cr[cr_index]}!")
        print()
    return True

def buy_cr_all(state):
    f = state.farm
    counter=0
    while True:
        counter+=1
        min_price = 1e55
        min_index = -1
        for i in range(len(f.cr)):
            if research_available(state=state, cr_index=i):
                upgrade_cost = cr_prices[i][int(f.cr[i])] * f.artf.cr_cost * (1-0.05*f.er[7]) * f.coll_effect("waterballoon") * f.event("cr")
                if upgrade_cost < min_price:
                    min_price = upgrade_cost
                    min_index = i

        if min_index==-1 or f.cash<min_price: 
            if(counter==1):
                print("No research bought :(")
            else:
                index(state)
                print(f"Bought {counter-1} researches!")
            print()
            break
        if not buy_cr(state, min_index, printout=False): break

def event(state, s):
    # set an event, or set it back to default
    f=state.farm
    pattern = r'([a-z]+)([0-9+].?[0-9]*)'
    match = re.match(pattern, s)
    if not match:
        print("No events active")
        f.reset_events()
        index(state)
        return
    e = match.group(1)
    x = match.group(2)    
    if e in f.event_effects:
        f.set_event(e,x)
        index(state)
        print(f"Activated {e} x {x} event")
    else:
        f.reset_events()
        index(state)
        print("No events active")