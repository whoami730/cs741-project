""" Some functions to implement Linear Feedback Shift Register. """

from functools import reduce
import time

#NOTE: The use of 1 in feedback_polynomial is for the first bit. the bit that we are going to output.
def generate_lfsr(seed: list, feedback_polynomial: list, steps: int):
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
    print(f"Output: {''.join(map(str,opt))}")

# i/p - o/p code for LFSR
print("\nLeftmost bit is MSB")
sd = [int(i) for i in input("Seed for LFSR: ").strip()]
fdb = [int(i) for i in input("Feedback Ploynomial: ").strip()]
st = int(input("Steps: ").strip())
generate_lfsr(sd,fdb,st)

def bm_algo(S):
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

s = [int(i) for i in input("Enter the seqn, MSB to LSB form: ").strip()]
print("L (minimal length), C (Feedback polynomial MSB to LSB), Seed(MSB to LSB): ")
l,c,ss = bm_algo(s)
print(l,''.join(map(str,c)),''.join(map(str,ss)))
# Output 2*len(s) of random bits using the above feedback_poly and seed.
print('\n2*len(i/p) LFSR bits using the above seen and feedback polynomial')
generate_lfsr(ss,c,2*len(s))

# TODO: Encode the seed finding and BM algo into sat solver from Z3. Use BitVec.

def lfsr_z3(seed, feedback_polynomial, steps):
    """n-bit LFSR.
    seed: BitVec of n bits
    feedbackpoly = BitVec of n bits
    steps is steps
    """

def bm_algo_z3(S: list):
    """Berlekamp - Massey algo: in Z3-solver
    i/p:    S: `list` of 0s and 1s, Sn, Sn-1, Sn-2, ... S1, S0.
    o/p:    
    """
    t_start = time()
    n = len(list)
    S_bitvec = BitVec('s', n)
    seed = BitVec('seed', n)
    c = BitVec('comb_poly', n)
    # nxt_bev = 