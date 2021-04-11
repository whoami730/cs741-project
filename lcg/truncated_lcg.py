import gmpy2
from z3 import *
import random

from Crypto.Util.number import *
from fpylll import *
from time import *

def all_smt(s, initial_terms):
    """
    Yield all satisfying models for solver s 
    for the given set of `initial_terms`
    """
    def block_term(s, m, t):
        s.add(t != m.eval(t))

    def fix_term(s, m, t):
        s.add(t == m.eval(t))

    def all_smt_rec(terms):
        if sat == s.check():
            m = s.model()
            yield m
            for i in range(len(terms)):
                s.push()
                block_term(s, m, terms[i])
                for j in range(i):
                    fix_term(s, m, terms[j])
                for m in all_smt_rec(terms[i:]):
                    yield m
                s.pop()
    for m in all_smt_rec(list(initial_terms)):
        yield m

class truncated_lcg:
    # assume that n < 2**32; and truncated_lcg outputs top 16 bits of the result
    def __init__(self, seed, a, b, n,truncation=16):
        self.state = seed
        self.a = a
        self.b = b
        self.n = n
        self.truncation = truncation

    def next(self):
        self.state = ((self.a * self.state) + self.b) % self.n
        # print(self.state)
        return (self.state >> self.truncation)
        
        
class Breaker(truncated_lcg):
    def __init__(self, seed, a, b, n,truncation=16):
        super().__init__(seed, a, b, n,truncation)
        self.bitlen = (a*n+b).bit_length()+1
        
    def break_sat(self, outputs):
        """
        Thought this wont suck
        well this sucks too XD
        """
        seed = BitVec('seed',self.bitlen)
        s = Solver()
        s.add(seed>=0)
        s.add(seed<self.n)
        for v in outputs:
            seed = simplify(URem(( (self.a * seed) + self.b), self.n))
            s.add(v == LShR(seed,self.truncation))

        start_time, last_time = time(), time()
        k = all_smt(s,[seed])
        for m in k:
        	time_taken = time()
        	print(m[m.decls()[0]],time_taken-last_time)
        	last_time = time_taken
        print("total time taken :",time()-start_time)

    def break_sat_slow(self, outputs):
        """
        slow af piece of shit
        gets slower with increasing lengths of outputs
        """
        LCG = [BitVec(f'LCG[{i}]',self.bitlen) for i in range(len(outputs) + 1)]
        s = Solver()
        for i in LCG:
        	s.add(i<self.n)
        	s.add(i>=0)
        for i in range(len(outputs)):
            s.add(LCG[i + 1] == (URem(( (self.a * LCG[i]) + self.b), self.n)))
            s.add(outputs[i] == LShR(LCG[i + 1],16))
        
        start_time, last_time = time(), time()
        k = all_smt(s,LCG)
        for m in k:
        	time_taken = time()
        	vals = {str(i):m[i].as_long() for i in m}
        	vals = [vals[f'LCG[{i}]'] for i in range(len(m)) ]
        	print(vals,time_taken-last_time)
        	last_time = time_taken
        print("total time taken :", time() - start_time)
        
    def find_poly(self, output, t=3):
        pass

    def break_lattice(self, outputs):
        o = len(outputs)
        L = IntegerMatrix(o,o+1) # lattice
        f,g = 1,1

        vec = outputs.copy()

        for i in range(o):
            L[i, 0] = self.a * f
            f = L[i, 0]
            g += f
            L[i, i + 1] = self.n
            vec[i] -= self.b * (g)
            vec[i] *= int(gmpy2.invert(2 ** self.truncation, self.n))
            # vec[i] %= self.n # not sure if this should be done or not 
        Lred = BKZ.reduction(L,BKZ.Param(5))

        t = tuple(vec)
        print(t,L,Lred)        
        z = CVP.closest_vector(Lred,t)
        print(z)


if __name__ == "__main__":
    
    p = getPrime(20)
    a = random.randint(0, p - 1)
    b = random.randint(0, p - 1)
    seed = random.randint(0, p - 1)
    num_out = 10
    
    brkr = Breaker(seed, a, b, p)
    l = []
    for i in range(num_out):
        l.append(brkr.next())

    print(a,b,p,seed)
    brkr.break_sat(l)
    brkr.break_sat_slow(l)
    # brkr.break_lattice(l)
    