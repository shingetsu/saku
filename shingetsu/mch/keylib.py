

import threading
import os


keycache = {}
_lock = threading.Lock()

class DatkeyNotFound(Exception):
    pass

def calc(filekey):
    if '_' in filekey:
        type, key = filekey.split('_', 1)
    else:
        return False

    try:
        n = int(key, 16) % 9999999999
    except (TypeError, ValueError):
        return False

    datkey = str(n).rjust(10, '0')  # 10 digits
    with _lock:
        keycache[filekey] = datkey
        keycache[datkey] = filekey
    return True

def get_datkey(filekey):
    if filekey in keycache:
        return keycache[filekey]

    if not calc(filekey):
        raise DatkeyNotFound

    return keycache[filekey]

def get_filekey(datkey):
    if datkey in keycache:
        return keycache[datkey]
    raise DatkeyNotFound

def load(cache_dir):
    for k in os.listdir(cache_dir):
        calc(k)

def clear():
    with _lock:
        keycache.clear()
