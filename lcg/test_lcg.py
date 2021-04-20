from lcg import Breaker
from random import randint
from Crypto.Util.number import *

def test_known_trunc_prime(num_out=8, truncation=24):
    p = getPrime(32)
    a = randint(0,p-1)
    b = randint(0, p - 1)
    seed_original = randint(0, p - 1)
    
    print(f"{seed_original = } {a = } {b = } {p = }")

    brkr = Breaker(seed_original, a, b, p, truncation,known_a=True,known_b=True,known_n=True)
    l = []
    for i in range(num_out):
        l.append(brkr.next())
    
    brkr.break_lattice(l)
    brkr.break_sat(l)

def test_known_trunc_2(num_out=8, truncation=16):
    p = 2**32
    a = randint(0,p-1)
    b = randint(0, p - 1)
    seed_original = randint(0, p - 1)
    
    print(f"{seed_original = } {a = } {b = } {p = }")

    brkr = Breaker(seed_original, a, b, p, truncation,known_a=True,known_b=True,known_n=True)
    l = []
    for i in range(num_out):
        l.append(brkr.next())
    
    brkr.break_lattice(l)
    brkr.break_sat(l)

def test_unknown_a_b_trunc_2(num_out=16, truncation=16):
    p = 2**32
    a = randint(0,p-1)
    b = randint(0, p - 1)
    seed_original = randint(0, p - 1)
    
    print(f"{seed_original = } {a = } {b = } {p = }")

    brkr = Breaker(seed_original, a, b, p, truncation,known_a=False,known_b=False,known_n=True)
    l = []
    for i in range(num_out):
        l.append(brkr.next())
    
    brkr.break_sat(l)
