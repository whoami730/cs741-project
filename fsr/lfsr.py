""" Some functions to implement Linear Feedback Shift Register. """

from functools import reduce


#NOTE: The use of 1 in feedback_polynomial is still unknown to me!
def lfsr_fib_16bit(n, seed, feedback_polynomial, steps):
    """ 16-bit Fibonnaci LFSR defined by given feedback polynomial """

    lfsr = seed                             # Initial seed of lfsr
    bit = 0                                 # Initial o/p of lfsr
    cycle = 0                               # The cycle length of LFSR, i.e. cycles completed till now
    size = len(feedback_polynomial)         # num of bits of feeback polynomial
    opt = ''

    while lfsr != seed and size != 0:
        # Compute the leftmost bit using the (tabs of) feeback polynomial
        bit = reduce(lambda x, y: x^y,[lfsr>>(size - 1 - i) for i in feedback_polynomial if i != 0],0) & 1
        opt += str(lfsr%2)
        lfsr = (bit << (n-1)) | (lfsr >> 1)

        cycle += 1
        steps -= 1
    
    # Seed for next cycle is current value of lfsr
    seed = lfsr
    print(f"Output: {opt}, cycle: {cycle}")
    return cycle

def bm_algo(S):
    """ Berlekamp - Massey algo: PYTHON IMPLEMENTATION
    i/p:    S:  `list` of 0s and 1s, ith index is ith bit in (MSB) S0, S1, ..., Sn (LSB). The n bit o/p of lfsr.
    o/p:   min degree of C, Feedback Polynomial, anything else that we want 
    """
    C = [1]     # Connection polynomial. The one that generates next o/p bit
    L = 0       # IDK
    m = -1      # somethingg
    B = [1]     # Previous value of C, before it was updated.
    n = 0       # counter. i.e. the iterator
    N = len(S)  # The length of i/p

    while(n < N):
        bit_calc = [i&j for i,j in zip(C[1:],S[n-1:n-L-1:-1])]
        d = S[n] ^ reduce(lambda x, y: x^y, bit_calc,0)
        if d & 1:
            c_temp = C.copy()
            lc = len(C)
            next_C = [0]*(n-m) + B
            C = [i^j for i,j in zip(C,next_C)] + next_C[lc:]
            if L <= n//2:
                L = n + 1 - L
                m = n
                B = c_temp.copy()
        n += 1
    return (L,C)

s = list(map(int, input("Enter the seqn in space seperated form, MSB to LSB form: ").strip().split(' ')))
print("L (minimal length), C (Feedback polynomial): ")
print(bm_algo(s))
