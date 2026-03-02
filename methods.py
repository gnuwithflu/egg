import math
import re
import numpy as np
import cmath
import warnings

def quad_formula(a,b,c): #return only positive solution
    d = (b**2) - (4*a*c)
    if d < 0:
        raise ValueError(f"No real root")
    root1 = (-b + np.sqrt(d)) / (2 * a)
    root2 = (-b - np.sqrt(d)) / (2 * a)
    if root1 < 0: return float(root2)
    return float(root1)
    

def format(n):
    # converts number to egg format 
    try:    
        l = ['','K','M','B','T','q','Q','s','S','o','N','d','U','D','Td','qd','Qd','sd','Sd','od','Nd','V','uV','dV','tV','qV','QV','sV','SV','oV','NV']
        if n==0: return 0

        k = math.trunc(math.log(n,10)/3)
        m = n/pow(10,3*k)

        if m>=100: return f"{round(m)}{l[k]}"
        elif m>=10: return f"{round(m,1)}{l[k]}"
        else: return f"{round(m,2)}{l[k]}"  
    except:
        raise ValueError(f"Invalid number for conversion: {n}")
        return np.inf


def egg_read(s):
    # converts egg format to number
    l = ['','K','M','B','T','q','Q','s','S','o','N','d','U','D','Td','qd','Qd','sd','Sd','od','Nd','V','uV','dV','tV','qV','QV','sV','SV','oV','NV']
    pattern = r'([0-9]*\.?[0-9]+)([a-zA-Z]*)'
    match = re.match(pattern, s)

    if not match:
        raise ValueError(f"Invalid egg string: {s}")

    number = float(match.group(1))
    unit = match.group(2)

    if unit not in l:
        raise ValueError(f"Invalid suffix in egg string: {unit}")

    k = l.index(unit)
    return number * (10**(3*k))


def format_time(time):
    # time in seconds to human readable
    if time<60:
        return f"{round(time,3)}s"
    elif time<3600:
        return f"{round(time/60,3)}min"
    elif time<3600*24:
        return f"{round(time/3600,3)}h"
    elif time<3600*24*365:
        return f"{round(time/(3600*24),3)}d"
    elif time<3600*24*356*10000:
        return f"{round(time/(3600*24*365),3)}y"
    else:
        return f"{format(time/(3600*24*365))}y"


def read_time(s):
    # human readable time to seconds
    pattern = r'(-?[0-9]*\.?[0-9]+)([a-zA-Z]*)'
    match = re.match(pattern, s)

    if not match:
        raise ValueError(f"Invalid time input: {s}")

    number = float(match.group(1))
    unit = match.group(2)
    
    if unit=="s" or unit=="sec" or unit=="":
        return number
    if unit=="min" or unit=="m":
        return number*60
    if unit=="h":
        return number*3600
    if unit=="d":
        return number*3600*24
    if unit=="y":
        return number*3600*24*365
    raise ValueError(f"Invalid time input: {s}")    