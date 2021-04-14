from z3 import *
import random

from Crypto.Util.number import *
from fpylll import IntegerMatrix, LLL
from time import time
from sympy import QQ, Matrix
from sympy.polys.matrices import DomainMatrix
import sys
sys.setrecursionlimit(100000)

set_param('parallel.enable', True)
set_param('parallel.threads.max', 32)
set_param('sat.local_search_threads', 4)
set_param('sat.threads', 4)

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
    def __init__(self, seed, a, b, n, truncation, **kwargs):
        super().__init__(seed, a, b, n, truncation)
        self.n_bitlen = n.bit_length()
        self.known_a: bool = kwargs.get('known_a', True)
        self.known_b: bool = kwargs.get('known_b', True)
        self.known_n: bool = kwargs.get('known_n', True)
        
    def break_sat(self, outputs):
        """
        Thought this wont suck
        well this sucks too XD
        """
        seed0 = BitVec('seed0', self.n_bitlen)
        seed = ZeroExt(self.n_bitlen,seed0)
        s = Solver()

        if (self.known_a):
            a = BitVecVal(self.a, self.n_bitlen)
        else:
            a = BitVec('a', self.n_bitlen)
            
        if (self.known_b):
            b = BitVecVal(self.b, self.n_bitlen)
        else:
            b = BitVec('b', self.n_bitlen)

        if (self.known_n):
            n = BitVecVal(self.n, self.n_bitlen)
        else:
            n = BitVec('n', self.n_bitlen)

        s.add(ULT(seed0,n),ULT(a,n),ULT(b,n),UGE(seed0,0),UGE(a,0),UGE(b,0))
        for v in outputs:
            seed = simplify(URem(ZeroExt(self.n_bitlen,a)*seed+ZeroExt(self.n_bitlen,b), ZeroExt(self.n_bitlen,n)))
            s.add(v == LShR(seed,self.truncation))

        start_time, last_time = time(), time()
        terms = [seed0,a,b,n]
        if not self.known_a:
            terms.append(a)
        if not self.known_b:
            terms.append(b)
        if not self.known_n:
            terms.append(n)

        guess = []

        for m in all_smt(s,terms):
            SAT_guessed_seed = m[seed0]
            A = m.eval(a)
            B = m.eval(b)
            N = m.eval(n)
            print(f"{SAT_guessed_seed = } {A = } {B = } {N = }")
            guess.append((SAT_guessed_seed,A,B,N))
        print("Total time taken(SAT) :",time()-start_time)
        return guess

    def shorten(self,u):
        for i in range(u.nrows):
            u[i,0] %= self.n
            if 2*u[i,0] >=self.n:
                u[i,0]-=self.n

    def break_lattice(self, outputs):
        k = len(outputs)
        start_time = time()
        L = IntegerMatrix(k, k)
        v = IntegerMatrix(k, 1)
        U = IntegerMatrix.identity(k)
        for i in range(k):
            L[i, 0] = self.a**i
            L[i, i] = -1
            v[i, 0] = (((1 - (self.a ** i)) // (self.a - 1))*self.b) % self.n
            
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
    num_out = 16
    truncation = 0
    
    print(f"{seed_original = } {a = } {b = } {p = }")

    brkr = Breaker(seed_original, a, b, p, truncation,known_a=False,known_b=False,known_n=True)
    l = []
    for i in range(num_out):
        l.append(brkr.next())
    
    brkr.break_lattice(l)
    brkr.break_sat(l)