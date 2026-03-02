from farm.farm import *
import re
import os, sys
import traceback
from methods import *
from farm.prices import *
from simulation.commands import*
from simulation.egg_simulation import *
#TODO ER and Collectible setter

commands = {
    "help": help,
    "status": status,
    "virtue": virtue,

    "shift": shift,
    "prestige": prestige,

    "silo": silo_status,
    "hab": hab_status,
    "veh": vehicle_status,
    "cr": cr_status,
    "ship":ship_status,
    "arti": artifact_action,

    "run": run_chickens,
    "waitonline": wait_online,
    "waitoffline": wait_offline,
    "wait": wait_offline,
    "waitactive": wait_active,
    
    "timeaway": time_cash_away,
    "timeactive": time_cash_active,
    
    "buy": buy,
    "buyall": buy_all,

    "curiosity": curiosity,
    "kindness": kindness,
    "resilience": resilience,
    "humility": humility,
    "integrity": integrity,

    "event": event
}


def simulation(egg=None, te=None, eggs_layed=None, shifts=0, artifact_set=None):
    if eggs_layed is None: eggs_layed = [0,0,0,0,0]
    if artifact_set is None: artifact_set = Artifact_set()

    if egg is None:
        egg = set_egg()
    if te is None:
        te = set_te()
    if te>0 and eggs_layed == [0,0,0,0,0]:
        eggs_layed = set_eggs_layed()

    f = Farm(egg=egg, 
                er=[15,20,20,20,20,10,10,10,20,100,20,12,20,140,20,20,30,10,20,5,60,10], 
                colleggtibles=np.ones(11)*4, 
                vehicles=[1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], 
                te=te, 
                silos=1, 
                habs=[1,0,0,0],
                artifact_set=artifact_set,
                video_doubler=True)
    state = State(f, time_elapsed=0, eggs_layed=eggs_layed, shifts=shifts)



    index(state)

    while True:
        try:
            s = input()
            index(state)
            
            parts = s.split(None, 1)
            if len(parts)==1:
                parts.append("")
            if parts[0] not in commands:
                print(f"Unknown command: {parts[0]}")
                continue
            commands[parts[0]](state, parts[1])

                
        except Exception as e:
            traceback.print_exc()
            print(f"Invalid command: {s} (error: {e})")


if __name__ == '__main__':
    simulation()
