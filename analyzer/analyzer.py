from farm.farm import Farm
from simulation.egg_simulation import *
import re
from simulation.commands import virtue_egg_index
from itertools import product
from scipy.optimize import minimize
egg = {
    "c": "curiosity",
    "i": "integrity",
    "k": "kindness",
    "r": "resilience",
    "h": "humility"
    }

egg_index = {
    "c": 0,
    "k": 1,
    "r": 2,
    "h": 3,
    "i": 4
    }

def simulate_asc(order, times, eggs_layed=None, printout=True):
    if eggs_layed is None: eggs_layed = [0,0,0,0,0]
    assert(bool(re.fullmatch(r"[cikrh]+", order)))
    te_owned = 0
    for i in range(5):
        te_owned += te_numbers(eggs_layed[i])
    f = Farm(egg=egg[order[0]], 
                te=te_owned, 
                #artifact_set=Artifact_set(),
                video_doubler=True)
                
    state = State(f, time_elapsed=0, eggs_layed=eggs_layed, shifts=0)
    for k in range(len(order)):
        simulate_egg(state, times[k], egg[order[k]], printout=False)
    with open("analyzer/analyzed.txt", "a") as fi:
        fi.write(f"{order} {times}\n")
        fi.write(f"{format_time(state.time_elapsed)}\n\n")
    if printout:
        print(f"{order} {times}")
        print(f"{format_time(state.time_elapsed)}")
        print()
    return state.time_elapsed



def create_dataset():
    max_hours=2.5
    steps=100
    a = int(steps/max_hours)
    with open("analyzer/dataset_cici.txt", "a") as fi:
        fi.write("[")
        for i in range(1,steps):
            fi.write("[")
            for j in range(1,steps):
                if j!=steps-1: fi.write(f"{round(simulate_asc("cici", [f"{i/a}h", f"{j/a}h", f"3te", f"2te"], [0,0,0,0,0], printout=False)/3600/24,3)}, ")
                else:fi.write(f"{round(simulate_asc("cici", [f"{i/a}h", f"{j/a}h", f"3te", f"2te"], [0,0,0,0,0], printout=False)/3600/24,3)}")
            fi.write("], \n")
        fi.write("]")





def test_times(order, te_goal, eggs_layed=[0,0,0,0,0]):
    assert(bool(re.fullmatch(r"[cikrh]+", order)))
    te_claimed = [0,0,0,0,0]
    for i in range(5):
        te_claimed[i] = te_numbers(eggs_layed[i])
    record_time = np.inf
    record_config = None

    n = 5 # must be larger 
    counter = 0
    for values in product(range(1, n), repeat=len(order)):
        print(f"{counter} / {(n-1)**len(order)}", end="\r")
        counter += 1

        times = []
        te_pending=0
        for i in range(len(values)):
            if order[i] in order[i+1:]:
                times.append(f"{1*values[i]}h")
            else:
                times.append(f"{values[i]+te_claimed[egg_index[order[i]]]}te")
                te_pending += values[i]
        
        if te_pending == te_goal:
            eggs_layed1 = [0,0,0,0,0]
            for k in range(5):
                eggs_layed1[k] += eggs_layed[k]
            t = simulate_asc(order, times, eggs_layed1, printout=False)
            if t < record_time:
                record_time = t
                record_config = times

    print(record_config)
    print(format_time(record_time))

def test_times2(order, times, eggs_layed=None, printout=True):
    assert(bool(re.fullmatch(r"[cikrh]+", order)))
    te_claimed = [0,0,0,0,0]
    for i in range(5):
        te_claimed[i] = te_numbers(eggs_layed[i])

        
    def func(params):
        eggs_layed1 = [0,0,0,0,0]
        for k in range(5):
          eggs_layed1[i] += eggs_layed[i]

        a,b,c = params
        c = a/60
        b = b/60
        a = int(a)
        return simulate_asc(order, [f"{c}h",f"{b}h",f"{a}te",f"{5-a}te"], eggs_layed1, printout=False)
    bounds = [(0, 5), (0, 60*24*3), (0, 60*24*3)]
    print(minimize(func, x0 = [2, 5*60,5*60], bounds=bounds, method="Powell", options={
        "maxiter": 1000,
        "xtol": 0.5,   # step size tolerance
        "ftol": 100,
    }).x)
