# TODO: how does ihr habs multiplied when internal hatchery sharing is not purchased?
# TODO: find exact laying rate formula. There is probably some rounding going on, but where? Does over 1 per mille FV
# TODO: enlightenment on artifacts

import numpy as np
import os

from farm import *
from methods import format
from farm.artifact import *
from simulation.simulator import simulation
from farm.prices import *
# from analyzer.analyzer import *




def main():
    set1 = Artifact_set(a1=Artifact(type="totem", level=4, rarity=3, stone1=Stone(type="lunar",level=3), stone2=Stone(type="lunar",level=3),stone3=Stone(type="lunar",level=3)),
            a2=Artifact(type="necklace", level=4, rarity=2, stone1=Stone(type="lunar",level=3), stone2=Stone(type="lunar",level=3)),
            a3=Artifact(type="ankh", level=3, rarity=1, stone1=Stone(type="lunar",level=3)),
            a4=Artifact(type="gusset", level=2, rarity=2, stone1=Stone(type="lunar",level=3), stone2=Stone(type="lunar",level=3)),    
    )
    set2 = Artifact_set(a1=Artifact(type="ankh", level=4, rarity=1),
            a2=Artifact(type="book", level=4, rarity=0),
            a3=Artifact(type="necklace", level=4, rarity=3, stone1=Stone(type="prophecy",level=4), stone2=Stone(type="prophecy",level=4), stone3=Stone(type="prophecy",level=4)),
            a4=Artifact(type="cube", level=4, rarity=3, stone1=Stone(type="prophecy",level=4),stone2=Stone(type="prophecy",level=4),stone3=Stone(type="prophecy",level=4)),    
    )



    #simulation(egg="curiosity", te=49, shifts=8, eggs_layed=[180e12,60.6e12,502.5e12,1.510e15,7.010e12], artifact_set=set1)
    simulation()
    

if __name__ == "__main__":
    main() 