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

