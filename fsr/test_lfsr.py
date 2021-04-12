import time, random
from lfsr import *

def test_n_bit_k_steps(n: int, k: int):
    # Generate seed and combination polynomial and generate some eandom bits
    rndm_seed = bin(random.getrandbits(n))[2:]
    seed = rndm_seed + '0'*(n-len(rndm_seed))
    rndm_poly = bin(random.getrandbits(n))[2:]
    feedback_poly = rndm_poly + '0'*(n - len(rndm_poly)) + '1'
    gen_opt = generate_lfsr(list(map(int,seed)), list(map(int,feedback_poly)), 2*k)

    # Test bm algo
    L, C, S = bm_algo(gen_opt[:k//2])

    bm_opt = generate_lfsr(S, C, 2*k)

    if bm_opt == gen_opt:
        print("No mismatch!!")
        print("Success!")
    else:
        mismatch = -1
        # print(bm_opt, gen_opt)
        for i, j in enumerate(zip(bm_opt, gen_opt)):
            if j[0] != j[1]:
                print(f"For {2*k} bits, 1st mismatch at index: {i}")
                print("Partial Success.")
                break
    return

test_n_bit_k_steps(1024,4096)