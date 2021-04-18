""" Some functions to implement Linear Feedback Shift Register. """

from functools import reduce
from z3 import *

class LFSR_python:
    """ Normal LFSR impl with pythonic inputs. Everything is in `GF(2)`"""

    #NOTE: The use of 1 in feedback_polynomial is for the first bit. the bit that we are going to output.
    def generate_lfsr(self, seed: list, feedback_polynomial: list, steps: int):
        """ n-bit LFSR defined by given feedback polynomial
        seed = MSB to LSB list of bits
        feedback_polynomial = MSB to LSB list of bits
        """

        # Check that n bit seed have n-degree feeback polynomial.
        if len(seed) != len(feedback_polynomial) - 1:
            raise Exception("Number of bits in the seed and the degree of feedback polynomial should be same")
        
        # Check if 1st and last bit in feedback poly is 1. It should be 1
        if not (feedback_polynomial[0] or feedback_polynomial[-1]):
            raise Exception("0th and nth degree of feedback polynomial should be 1!! for n-bit lfsr")
        
        lfsr = seed.copy()                      # Initial seed of lfsr
        bit = 0                                 # Initial o/p of lfsr
        n_bit = len(seed)                       # num of bits of feeback polynomial
        opt = []                                # 0th index is MSB... nth index is LSB

        while steps > 0:
            # Compute the leftmost bit using the (taps of) feeback polynomial
            conn_poly = [i&j for i,j in zip(lfsr[::-1],feedback_polynomial)]
            bit = reduce(lambda x,y: x^y, conn_poly,0)
            opt.append(lfsr.pop())
            lfsr.insert(0,bit)
            steps -= 1
        
        # Seed for next cycle is current value of lfsr
        # seed = lfsr
        # print(f"Output: {''.join(map(str,opt))}")
        return opt

    # i/p - o/p code for LFSR
    # print("\nLeftmost bit is MSB")
    # sd = [int(i) for i in input("Seed for LFSR: ").strip()]
    # fdb = [int(i) for i in input("Feedback Ploynomial: ").strip()]
    # st = int(input("Steps: ").strip())
    # generate_lfsr(sd,fdb,st)

    def bm_algo(self, S):
        """ Berlekamp - Massey algo: PYTHON IMPLEMENTATION
        i/p:    S:  `list` of 0s and 1s, Sn, Sn-1, Sn-2, ... S1, S0.
        o/p:   min degree of C, Feedback Polynomial, anything else that we want 
        """
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
        return (L,C[::-1],S[:L][::-1])

# s = [int(i) for i in input("Enter the seqn, MSB to LSB form: ").strip()]
# print("L (minimal length), C (Feedback polynomial MSB to LSB), Seed(MSB to LSB): ")
# l,c,ss = LFSR_python().bm_algo(s)
# print(l,''.join(map(str,c)),''.join(map(str,ss)))
# # Output 2*len(s) of random bits using the above feedback_poly and seed.
# print('\n2*len(i/p) LFSR bits using the above seen and feedback polynomial')
# generate_lfsr(ss,c,2*len(s))

# Z3 LFSR functoin
class LFSR_z3:
    """ LFSR for z3. i.e. All the input are of z3 datatypes. """
    def __init__(self, seed, comb_poly):
        assert len(seed) == len(comb_poly), "Error: Length of seed and combination polynomial should be same."
        # List of bitVecs, Sn... S0
        self._seed = seed.copy()
        # List of taps. C0, ..., Cn
        self._poly = comb_poly.copy()

    def _next_inp(self, lst_bitvec):
        return reduce(lambda x,y: x^y, lst_bitvec)
    
    def _get_next_bit(self):
        next_inp = self._next_inp([self._seed[i] for i in self._poly if i == 1])
        opt = self._seed.pop(0)
        self._seed.append(next_inp)
        return opt
    
    def next_bit(self):
        return self._get_next_bit()


class UnLFSR_Z3:
    """ Similar to berlekamp in the sense that it finds the seed and the comb poly using z3 solver. """

    def __init__(self, opt):
        """ opt is list of 0s and 1s. 1st bit 1st """
        self._opt = opt.copy()
        self._seed = [BitVec(f'k_{i}',1) for i in range(22)]
        self._poly = [BitVec(f'c_{i}',1) for i in range(22)]

    def solve(self):
        s = Solver()
        lfsr = LFSR_z3(self._seed, self._poly)
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

class Jeff_z3:
    """ Jeff Generator's Solver in z3. We need to know  the combination polynomial beforehand """
    def __init__(self, c1, c2, c3):
        self.l1 = [BitVec(f'l1_{i}',1) for i in range(len(c1))]
        self.l2 = [BitVec(f'l2_{i}',1) for i in range(len(c2))]
        self.l3 = [BitVec(f'l3_{i}',1) for i in range(len(c3))]
        self.lfsrs = [LFSR_z3(self.l1,c1), LFSR_z3(self.l2, c2), LFSR_z3(self.l3, c3)]
    
    def next_bit(self):
        bits = [lfsr.next_bit() for lfsr in self.lfsrs]
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
            return one,two,thr
        else:
            return None

opt = [int(i) for i in input("Enter the seqn, MSB to LSB: ").strip()]
# ans = UnLFSR_Z3(opt).solve()
# print(ans[0])
# print(ans[1])
n = 69
c1 = [int(i) for i in '0000000000000100111']
c2 = [int(i) for i in '000000000000000000000100111']
c3 = [int(i) for i in '00000000000000000101011']

print(Jeff_z3(c1,c2,c3).solve(opt))

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