""" Some functions to implement Linear Feedback Shift Register. """

from functools import reduce
from z3 import *
import tqdm

class LFSR:
    """ Normal LFSR impl with pythonic inputs. Everything is in `GF(2)`
    n-bit LFSR defined by given feedback polynomial
    seed = MSB to LSB list of bits
    feedback_polynomial = MSB to LSB list of bits
    """

    def __init__(self, seed, poly):
        assert len(seed) == len(poly), "Error: Seed and taps poly  should be of same length"
        self._seed = seed.copy()      # MSB to LSB  
        self._comb_poly = poly[::-1]  # LSB to MSB
    
    def next_bit(self):
        """ Generate next output bit """
        tapped = [self._seed[i] for i,j in enumerate(self._comb_poly) if j == 1]
        xored = reduce(lambda x,y: x^y, tapped)
        opt = self._seed.pop(0)
        self._seed.append(xored)
        return opt
    
    def get_lfsr(self, steps):
        """ Get next `steps` number of output bits """
        opt = [self.next_bit() for _ in range(steps)]
        return opt

class Berlekamp_Massey:
    """ Berlekamp - Massey algo: PYTHON IMPLEMENTATION
    i/p:    S:  `list` of 0s and 1s, Sn, Sn-1, Sn-2, ... S1, S0.
    o/p:   min degree of C, Feedback Polynomial, anything else that we want 
    """

    def __init__(self, S):
        self.S = S
        C = [1]     # Connection polynomial. The one that generates next o/p bit. 1, C1, C2, ..., CL.
        L = 0       # Minimal size of LFSR at o/p
        m = -1      # num iterations since L and B were updated.
        B = [1]     # Previous value of C, before it was updated.
        n = 0       # counter. i.e. the iterator
        N = len(S)  # The length of i/p

        while(n < N):
            bit_calc = [i&j for i,j in zip(C,S[n-L:n+1][::-1])]
            d = reduce(lambda x, y: x^y, bit_calc,0)
            if d:
                c_temp = C.copy()
                lc = len(C)
                next_C = [0]*(n-m) + B + [0]*(lc - len(B) - n + m)
                C = [i^j for i,j in zip(C,next_C)] + next_C[lc:]
                # print(n, d, m,L, B, next_C, C)

                if L <= n>>1:
                    L = n + 1 - L
                    m = n
                    B = c_temp.copy()
            n += 1
        self._L = L
        self._C = C[::-1]
        self._seed = S[:L]
        assert len(self._seed) + 1 == len(self._C)

    def get_seed(self):
        return self._seed

    def get_taps(self):
        return self._C[1:]

    def get_degree(self):
        return self._L

class UnLFSR_Z3:
    """ Similar to berlekamp in the sense that it finds the seed and the comb poly using z3 solver. """

    def __init__(self, opt):
        """ opt is list of 0s and 1s. 1st bit 1st """
        self._opt = opt.copy()
        self._seed = [BitVec(f'k_{i}',1) for i in range(len(opt)//2)]
        self._poly = [BitVec(f'c_{i}',1) for i in range(len(opt)//2)]

    def solve(self):
        s = Solver()
        lfsr = LFSR(self._seed, self._poly)
        for i in range(len(self._opt)):
            s.add(lfsr.next_bit() == self._opt[i])
        if s.check() == sat:
            model = s.model()
            print(len(model))
            sd = ''.join(str(model[i]) for i in self._seed)
            taps = ''.join(str(model[i]) for i in self._poly)
            return sd,taps
        else:
            print("ERROR: unsolvable... unpossible!!")

class Geffe:
    """ Jeff Generator's Solver in z3. We need to know  the combination polynomial beforehand """

    def __init__(self, c1, c2, c3):
        self._l1 = [BitVec(f'l1_{i}',1) for i in range(len(c1))]
        self._l2 = [BitVec(f'l2_{i}',1) for i in range(len(c2))]
        self._l3 = [BitVec(f'l3_{i}',1) for i in range(len(c3))]
        self._c1, self._c2, self._c3 = c1, c2, c3
        self._lfsrs = [LFSR(self._l1,c1), LFSR(self._l2, c2), LFSR(self._l3, c3)]
    
    def next_bit(self):
        bits = [lfsr.next_bit() for lfsr in self._lfsrs]
        return (bits[0] & bits[1]) | ((~bits[0]) & bits[2])

    def solve(self, opt):
        """ opt is a list of output bits gen by jeff gen """
        s = Solver()
        for b in opt:
            s.add(self.next_bit() == b)
        if s.check() == sat:
            model = s.model()
            one = ''.join(str(model[k]) for k in self.l1)
            two = ''.join(str(model[k]) for k in self.l2)
            thr = ''.join(str(model[k]) for k in self.l3)
            return (one,two,thr)
        else:
            return None
    
    def solve_bruteforce(self, lo, hi, l , corr):
        max_v, max_k = 0, 0
        for k in tqdm(range(lo, hi)):
            # lfsr = 
            opt = []

# opt = [int(i) for i in input("Enter the seqn, MSB to LSB: ").strip()]
# ans = UnLFSR_Z3(opt).solve()
# print(ans[0])
# print(ans[1])
# c1 = [int(i) for i in '0000000000000100111']
# c2 = [int(i) for i in '000000000000000000000100111']
# c3 = [int(i) for i in '00000000000000000101011']

# print(Geffe(c1,c2,c3).solve(opt))

# # Jeff's gen in python
# l1 = lambda key: LFSR( list(map(int,"{:019b}".format(key))) ,[19,18,17,14])
# l2 = lambda key: LFSR( list(map(int,"{:027b}".format(key))) ,[27,26,25,22])
# l3 = lambda key: LFSR( list(map(int,"{:023b}".format(key))) ,[23,22,20,18])
# def bruteforce(lo,hi,l,corr):
#     max_v, max_k = 0,0
#     for key in tqdm(range(lo,hi)):
#         lfsr = l(key)
#         output = [lfsr.bit() for _ in range(256)]
#         correlation = sum([i==j for i,j in zip(output,stream)])
#         if correlation>=corr:
#             max_k = key
#             max_v = correlation
#             print(max_k,max_v)

# # Jeff's generator in Z3
# class LFSR:
#     def __init__(self, key, taps):
#         d = max(taps)
#         assert len(key) == d, "Error: key of wrong size."
#         self._s = key
#         self._t = [d - t for t in taps]
#     def _sum(self, L):
#         s = 0
#         for x in L:
#             s = s ^ x
#         return s
#     def _get_next_bit(self):
#         b = self._s[0]
#         self._s = self._s[1:] + [self._sum(self._s[p] for p in self._t)]
#         return b
#     def bit(self):
#         return self._get_next_bit()

# class Jeff:
#     def __init__(self, key):
#         assert len(key) <= 19 + 23 + 27 # shard up 69+ bit key for 3 separate lfsrs
#         self.LFSR = [
#             LFSR(key[:19], [19, 18, 17, 14]),
#             LFSR(key[19:46], [27, 26, 25, 22]),
#             LFSR(key[46:], [23, 22, 20, 18]),
#         ]
#     def bit(self):
#         b = [lfsr.bit() for lfsr in self.LFSR]
#         return (b[0] & b[1]) | ((~b[0]) & b[2])
# output = [1, 0, 0, 1, 1, 0, 0, 1, 1, 1, 0, 1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 1, 0, 0, 1, 1, 0, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 0, 1, 1, 1, 0, 0, 1, 0, 1, 1, 1, 0, 0, 0, 1, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 0, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 1, 0, 0, 0, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 1, 0, 1, 1, 1, 1, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 1, 0, 1, 0, 0, 0, 1, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 1, 1, 0, 1, 0, 1, 1, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 1, 0, 0, 0, 1, 0, 1, 1, 0, 0, 1, 0, 1, 1, 1, 1, 1]
# encryption = {'iv': '310c55961f7e45891022668eea77f805', 'encrypted_flag': '2aa92761b36a4aad9a578d6cd7a62c52ba0709cb560c0ecff33a09e4af43bff0a1c865023bf28b387df91d6319f0e103d39dda88a88c14cfcec94c8ad02a6fb3152a4466c1a184f69184349e576d8950cac0a5b58bf30e67e5269883596a33a6'}
# def decrypt(key):
#     key = sha1(str(key).encode()).digest()[:16]
#     iv = bytes.fromhex(encryption['iv'])
#     return AES.new(key, AES.MODE_CBC, iv).decrypt(bytes.fromhex(encryption['encrypted_flag']))
# s = Solver()
# KEY = [BitVec(f"k_{i}", 1) for i in range(69)]
# J = Jeff(KEY)
# for b in output:
#     s.add(J.bit() == b)
# assert s.check() == sat
# print(unpad(decrypt(int(''.join(str(s.model()[k]) for k in KEY) , 2)), 16))