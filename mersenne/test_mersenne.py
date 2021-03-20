import random
from time import time
from twister import MT19937, Breaker
import os

def urandbits(n):
    return int.from_bytes(os.urandom(n//8),'big')


def test():
    rand_seed = urandbits(32)
    r = MT19937(rand_seed)
    outputs = [r.extract_number() for i in range(3)]
    b = Breaker()
    print(b.get_seed(outputs),rand_seed)

def test_64():
    rand_seed = urandbits(64)
    r = MT19937(rand_seed,bit_64=True)
    outputs = [r.extract_number() for i in range(3)]
    b = Breaker(bit_64=True)
    print(b.get_seed(outputs),rand_seed)


seed = urandbits(32)
r = MT19937(seed)
outputs = [r.extract_number() for i in range(624)]
b = Breaker()
#r.init_by_array([0x44434241,0x45])
#random.seed(0x4544434241)
#print(r.get_state()==random.getstate())
#r.init_by_array([0x44434241])
#init_state = r.MT.copy()
#r.init_32bit_seed(0x44434241)
#random.seed(0x44434241)
#print(r.get_state()==random.getstate())
#outputs = [r.extract_number() for i in range(3000)]
#untampered = list(map(b.ut,outputs))

#r2 = random.Random()
#r2.setstate(r.get_state())
#initial = r.get_state()
#assert r.get_state() == r2.getstate()
#o1 = [r.extract_number() for i in range(1000)]
#o2 = [r2.getrandbits(32) for i in range(1000)]
#common = list(set(o1)&set(o2))
#test()
#test_64()
#outputs = [random.getrandbits(32) for i in range(3)]
#b = Breaker()
#print(b.get_seed(outputs))