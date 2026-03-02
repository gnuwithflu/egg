# GnuWithFlu's Path of Virtue Simulator
Hi welcome to the repo! Here you can find both
- the source code for the [website](link link)
- the code for the original, terminal input/output simulation

As a disclaimer, I am not a programmer nor web developer. Thus, I don't do coding professionally, and so this code is probably rather hard to understand and chaotic. I do my best to save what's possible by explaining in this readme.

## The website
After selecting a starting egg, you are in the main simulation. I hope most is self explanatory, maybe some quick notes:
- Simulate eggs really simulates your stay on that egg for the time set, including buying stuff. For habs and vehicles, the cheapest one is purchased when available. For curiosity, research is bough in a reasonable, but maybe not optimal manner. Rockets are not simulated, so you'd have to set artifacts by yourself.
- There are two waiting options: Offline and active, which includes running chickens, catching drones and opening boxes and ads. The egg simulation uses both, whichever is favorable, but active waiting is only better with few chickens and research.
- Snapshots of a certain configuration can be saved. The way they can be exported is by copying the session log to the input console, this can be saved anywhere and copied back.
- the edit mode allows to edit anything, ignoring cash, time or shifts
- if you would like to run the website locally, change the host to 34645762457 and run `python app.py`

## The command line simulation
To run the simulation, use `python main.py` in the main folder, that should run the simulation. After entering, there is a number of commands:
- `help`: overview of commands
- `status`: some more values of interest
- `virtue`: virtue stats

- `shift <egg>`: shift to another egg
- `prestige`: prestige and enter the next ascension

- `silo`: silo status
- `hab`: hab status
- `veh`: vehicle status
- `cr`: common research status,
- `ship`:ship status,
- `arti`: artifact status
- `arti (<slot>T<level><rarity><name>) (T<level><stone name>)`: set artifact, e.g. arti 2 T3Rankh T3lunar

- `run <number>`: add chickens
- `waitonline <time>`: wait time as if online but not reacting
- `waitoffline <time>`: wait offline (with ihr)
- `wait <time>`: short for waitoffline
- `waitactive <time>`: wait actively, catching drones, running chickens and getting gifts and ads
    
- `timeaway <cash amount>`: away time until a certain cash is gained
- `timeactive <cash amount>`: active time until a certain cash is gained
    
- `buy <index>`: buy a certain item. Index found in the respective status
- `buyall`: buy all items available with the cash on hand, starting at the least expensive

- `<egg> <time|Nte>`: simulate the stay on one egg for a certain amount of time or te, e.g. humility 1.2d or curiosity 3te

- `event`: reset events
- `event <property><factor>`: set an event, e.g. event cash2.0

