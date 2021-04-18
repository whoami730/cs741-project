import time, random
from lfsr import *

def test_n_bit_k_steps(n: int, k: int):
    # Generate seed and combination polynomial and generate some eandom bits
    rndm_seed = bin(random.getrandbits(n))[2:]
    seed = rndm_seed + '0'*(n-len(rndm_seed))
    rndm_poly = bin(random.getrandbits(n))[2:]
    feedback_poly = rndm_poly + '0'*(n - len(rndm_poly))
    lfsr = LFSR(list(map(int,seed)), list(map(int,feedback_poly)))
    gen_opt = lfsr.get_lfsr(2*k)

    # Test bm algo
    start_time = time.time()
    bm = Berlekamp_Massey(gen_opt[:len(gen_opt)//2])
    print("Time taken to recover LFSR seed: ", time.time() - start_time)
    sd = bm.get_seed()
    taps = bm.get_taps()
    print(sd,seed)
    print(feedback_poly, taps)
    lfsr_new = LFSR(sd, taps)
    bm_opt = lfsr_new.get_lfsr(2*k)

    if bm_opt == gen_opt:
        print(f"No mismatch for {n} bit seed. Matched {2*k} (random) output bits")
        print("Success!")
    else:
        for i, j in enumerate(zip(bm_opt, gen_opt)):
            if j[0] != j[1]:
                print(f"For {2*k} bits, 1st mismatch at index: {i}")
                print("Partial Success.")
                break
    return

test_n_bit_k_steps(2048,4096)

# Test Geffes generator
def test_geffe_generator(num_opt_bits, size_taps):
    """ Given n output bits and taps of all the 3 LFSRs, find the actual seeds of LFSRs """
    c1 = bin(random.getrandbits(size_taps))[2:]
    c1 = c1 + '0'*(size_taps - len(c1))
    c2 = bin(random.getrandbits(size_taps))[2:]
    c2 = c2 + '0'*(size_taps - len(c2))
    c3 = bin(random.getrandbits(size_taps))[2:]
    c3 = c3 + '0'*(size_taps - len(c3))

    opt = bin(random.getrandbits(num_opt_bits))[2:]
    opt = opt + '0'*(num_opt_bits - len(opt))
    geffe = Geffe(list(map(int,c1)), list(map(int,c2)), list(map(int,c3)))
    start_time = time.time()
    geffe.solve(list(map(int, opt)))
    print("Time taken Geffe: " , time.time() - start_time)

test_geffe_generator(1024, 500)