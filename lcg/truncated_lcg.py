from z3 import *
import random

from Crypto.Util.number import *
from fpylll import IntegerMatrix, LLL
from time import time
from sympy import QQ, Matrix
from sympy.polys.matrices import DomainMatrix
import sys
sys.setrecursionlimit(100000)

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
        # print(self.state)
        return (self.state >> self.truncation)
        
        
class Breaker(truncated_lcg):
    def __init__(self, seed, a, b, n,truncation):
        super().__init__(seed, a, b, n,truncation)
        if n&(n-1):
            self.binary_field = False
            self.bitlen = (a*n+b).bit_length()+1
        else:
            self.binary_field = True
            self.bitlen = n.bit_length()-1
        
    def break_sat(self, outputs):
        """
        Thought this wont suck
        well this sucks too XD
        """
        seed0 = BitVec('seed0',self.bitlen)
        seed = BitVec('seed',self.bitlen)
        s = Solver()
        if not self.binary_field:
            s.add(ULT(seed,self.n))
        s.add(UGE(seed,0))
        s.add(seed0==seed)
        for v in outputs:
            if self.binary_field:
                seed = simplify(self.a*seed+self.b)
            else:
                seed = simplify(URem(( (self.a * seed) + self.b), self.n))
            s.add(v == LShR(seed,self.truncation))

        start_time, last_time = time(), time()
        SAT_seeds = []
        for m in all_smt(s,[seed0]):
            SAT_guessed_seed = m[m.decls()[0]]
            print(f"{SAT_guessed_seed = }",time()-last_time)
            last_time=time()
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
            u[i,0] %= self.n
            if 2*u[i,0] >=self.n:
                u[i,0]-=self.n

    def break_lattice(self, outputs):
        k = len(outputs)
        start_time = time()
        L = IntegerMatrix(k + 1, k + 1)
        v = IntegerMatrix(k + 1, 1)
        U = IntegerMatrix.identity(k+1)
        L[0, 0] = self.n
        for i in range(1, k+1):
            L[i, 0] = self.a**i
            L[i, i] = -1
            v[i, 0] = (outputs[i-1] << self.truncation) - ((((self.a ** i) - 1) // (self.a - 1))*self.b)
            
        _ = LLL.reduction(L, U)

        u = (U * v)
        self.shorten(u)

        A = DomainMatrix.from_Matrix(Matrix(k + 1, k + 1, lambda i, j: L[i, j])).convert_to(QQ)
        b = DomainMatrix.from_Matrix(Matrix(k + 1, 1, lambda i, j: u[i, 0])).convert_to(QQ)
        M = (A.inv()*b).to_Matrix()
        lattice_guessed_seed = M[0,0]%self.n
        print(f"{lattice_guessed_seed = }")
        print(f"Total time taken(LLL) : {time()-start_time}")
        return lattice_guessed_seed


if __name__ == "__main__":
    
    p = 2**48
    a = random.randint(0,p-1)
    b = random.randint(0,p-1)
    seed_original = random.randint(0,p-1)
    num_out = 8
    truncation = 40
    
    print(f"{a = } {b = } {seed_original = }")

    brkr = Breaker(seed_original, a, b, p, truncation)
    l = []
    for i in range(num_out):
        l.append(brkr.next())
    
    brkr.break_lattice(l)
    brkr.break_sat(l)
    # print(M)


# def recover_truncated_lcg(p,a,b,h,knowns):
#     K = {0:b}
#     for n in range(1, 20):
#         K[n] = K[n-1] + b*a^(n)

#     # Y = y_i*2^40 - K
#     Y = [ ((knowns[i] << h) - K[i]) % p for i in range(len(knowns)) ]

#     L=Matrix(ZZ, 8, 8)
#     L[0,0] = p
#     for i in range(1,8):
#         L[i,0] = a^i
#         L[i,i] = -1 
#     B = L.LLL()
#     W1 = B * vector(Y)
#     W2 = vector([ round(RR(w) / p) * p - w for w in W1 ])    
#     Z = list(B.solve_right(W2))

#     # s_i = y_i*2^40 + z_i
#     s1 = (int(knowns[0]) << 40) | int(Z[0])    
#     return s1, Z  