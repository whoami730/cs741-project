import gmpy2
from functools import *
from random import *
from Crypto.Util.number import *

def gcd(*args):
    return reduce(gmpy2.gcd,args)

class lcg:
    def __init__(self, seed, a, b, m):
        self.state = seed
        self.a = a
        self.b = b
        self.m = m

    def next(self):
        self.state = (self.state * self.a + self.b) % self.m
        return self.state

class Breaker(lcg):
    def __init__(self,seed):
        m = getPrime(32)       # some constants, can vary them
        a = randint(0,m-1)
        b = randint(0,m-1)
        super().__init__(seed,a,b,m)

    def break_lcg(self, ntimes):

        outputs = [self.next() for i in range(ntimes)]

        diffs = [(j-i) for i,j in zip(outputs,outputs[1:])]

        prods = [(b**2-a*c) for a,b,c in zip(diffs,diffs[1:],diffs[2:])]

        p = gcd(*prods)

        a = (diffs[1]*gmpy2.invert(diffs[0],p))%p

        b = (outputs[1]-a*outputs[0])%p

        assert all(j == (a*i + b)%p for i,j in zip(outputs,outputs[1:]))
        print(f"Recovered internal constants : p = {p} a = {a} b = {b}")
        return p,a,b

b = Breaker(100)
b.break_lcg(6)