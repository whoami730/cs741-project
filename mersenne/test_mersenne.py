import random
from time import time
from mersenne import *
import os

def urandbits(n):
    return int.from_bytes(os.urandom(n//8),'big')


def test():
    rand_seed = urandbits(32)
    r = MT19937(rand_seed)
    outputs = [r.extract_number() for i in range(3)]
    b = Breaker()
    recovered_seed = b.get_seed(outputs)
    assert rand_seed==recovered_seed
    print("works like a charm")

def test_64():
    rand_seed = urandbits(64)
    r = MT19937(rand_seed,bit_64=True)
    outputs = [r.extract_number() for i in range(3)]
    b = Breaker(bit_64=True)
    recovered_seed = b.get_seed(outputs)
    assert rand_seed==recovered_seed
    print("works like a charm")

def twist(mt_orig):
    """
    return the twisted state of MT
    """
    mt = [i for i in mt_orig]
    um = 0x80000000
    lm = 0x7fffffff
    a = 0x9908B0DF
    n = 624
    m = 397
    for i in range(n):
        x = (mt[i]&um) + (mt[(i+1)%n]&lm)
        xA = x>>1
        if x&1:
            xA=xA^a
        mt[i] = mt[(i+m)%n]^xA
    return mt

def tamper(num):
    """
    tampering an output through an MT state
    """
    u,s,t,b,c,d,l,w,n,m = 11,7,15,0x9D2C5680,0xEFC60000,0xFFFFFFFF,18,32,624,397
    y = num
    y = y^((y>>u)&d)
    y = y^((y<<s)&b)
    y = y^((y<<t)&c)
    y = y^(y>>l)
    return y

def check_untwist():
    """
    checking the untwist function to reverse back the
    MT twist operation
    """
    rand_seed = urandbits(32)
    r = MT19937()
    r.seed_mt(rand_seed)
    untwisted_orig = [i for i in r.MT]
    outputs = [r.extract_number() for i in range(624)]
    b = Breaker()
    untampered = list(map(b.ut,outputs))
    assert list(map(tamper,untampered))==outputs
    assert twist(untwisted_orig)==untampered
    untwisted = b.untwist(untampered)
    assert twist(untwisted)==untampered
    #assert untwisted == untwisted_orig 
    #wont work we only know a single from the first element
    assert untwisted_orig[1:]==untwisted[1:]
    print("all good and dandy")

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