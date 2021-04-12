import gmpy2
from z3 import *
import random

from Crypto.Util.number import *
from fpylll import *
from time import *
import sympy
import sympy.polys.matrices as matrices

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
    def __init__(self, seed, a, b, n,truncation):
        self.state = seed
        self.a = a
        self.b = b
        self.n = n
        self.truncation = truncation

    def next(self):
        self.state = ((self.a * self.state) + self.b) % self.n
        print(self.state)
        return (self.state >> self.truncation)
        
        
class Breaker(truncated_lcg):
    def __init__(self, seed, a, b, n,truncation):
        super().__init__(seed, a, b, n,truncation)
        self.bitlen = (a*n+b).bit_length()+2
        
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
        SAT_seeds = []
        for m in all_smt(s,[seed]):
            SAT_guessed_seed = m[m.decls()[0]]
            print(f"{SAT_guessed_seed = }")
            SAT_seeds.append(SAT_guessed_seed)
        print("Total time taken(SAT) :",time()-start_time)
        return SAT_seeds

    def break_sat_slow(self, outputs):
        """
        slow af piece of shit
        gets slower with increasing lengths of outputs
        DON'T USE!
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
        for m in all_smt(s,LCG):
        	vals = {str(i):m[i].as_long() for i in m}
        	vals = [vals[f'LCG[{i}]'] for i in range(len(m)) ]
        	print(vals)
        print("total time taken :", time() - start_time)

    def shorten(self,u):
        for i in range(u.nrows):
            t = u[i, 0]
            t %= self.n
            if (2 * t >= self.n):
                t -= self.n
            u[i, 0] = t

    def break_lattice(self, outputs):
        o = len(outputs)
        start_time = time()
        L = IntegerMatrix(o + 1, o + 1)
        v = IntegerMatrix(o + 1, 1)
        U = IntegerMatrix.identity(o+1)
        f = 1
        L[0, 0] = self.n
        for i in range(1, o+1):
            f *= self.a
            L[i, 0] = f
            L[i, i] = -1
            v[i, 0] = (outputs[i-1] << self.truncation) - ((((self.a ** i) - 1) // (self.a - 1))*self.b)
            
        _ = LLL.reduction(L, U)

        u = (U * v)
        self.shorten(u)

        A = matrices.DomainMatrix.from_Matrix(sympy.Matrix(o + 1, o + 1, lambda i, j: L[i, j])).convert_to(sympy.QQ)
        b = matrices.DomainMatrix.from_Matrix(sympy.Matrix(o + 1, 1, lambda i, j: u[i, 0])).convert_to(sympy.QQ)
        M = (A.inv()*b).to_Matrix()
        lattice_guessed_seed = M[0,0]%self.n
        print(f"{lattice_guessed_seed = }")
        print(f"Total time taken(LLL) : {time()-start_time}")
        return lattice_guessed_seed


if __name__ == "__main__":
    
    p = 2**48
    a = 184115153590892
    b = 23402086254269

    seed_original = 237765462071002
    num_out = 16
    truncation = 24
    
    print(f"{a = } {b = } {seed_original = }")

    brkr = Breaker(seed_original, a, b, p, truncation)
    l = []
    for i in range(num_out):
        l.append(brkr.next())
    
    brkr.break_lattice(l)
    brkr.break_sat_slow(l)
    # print(M)