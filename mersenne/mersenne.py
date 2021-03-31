import random
from time import time
from collections import Counter
from z3 import *

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




class MT19937:
    def __init__(self, c_seed=0, bit_64=False):
        # MT19937
        """
        bit_64 initializes MT19937-64 bit
        """
        if bit_64:
            (self.w, self.n, self.m, self.r) = (64, 312, 156, 31)
            self.a = 0xB5026F5AA96619E9
            (self.u, self.d) = (29, 0x5555555555555555)
            (self.s, self.b) = (17, 0x71D67FFFEDA60000)
            (self.t, self.c) = (37, 0xFFF7EEE000000000)
            self.l = 43
            self.f = 6364136223846793005
        else:
            (self.w, self.n, self.m, self.r) = (32, 624, 397, 31)
            self.a = 0x9908B0DF
            (self.u, self.d) = (11, 0xFFFFFFFF)
            (self.s, self.b) = (7, 0x9D2C5680)
            (self.t, self.c) = (15, 0xEFC60000)
            self.l = 18
            self.f = 1812433253
        self.MT = [0 for i in range(self.n)]
        self.index = self.n + 1
        self.lower_mask = (1 << self.r) - 1  # 0x7FFFFFFF
        self.upper_mask = (1 << self.r)  # 0x80000000
        self.seed_mt(c_seed)

    def seed_mt(self, num):
        """initialize the generator from a seed"""
        self.MT[0] = num
        self.index = self.n
        for i in range(1, self.n):
            temp = self.f * (self.MT[i - 1] ^
                             (self.MT[i - 1] >> (self.w - 2))) + i
            self.MT[i] = temp & ((1 << self.w) - 1)

    def twist(self):
        """ Generate the next n values from the series x_i"""
        for i in range(0, self.n):
            x = (self.MT[i] & self.upper_mask) + \
                (self.MT[(i + 1) % self.n] & self.lower_mask)
            xA = x >> 1
            if (x % 2) != 0:
                xA = xA ^ self.a
            self.MT[i] = self.MT[(i + self.m) % self.n] ^ xA
        self.index = 0

    def extract_number(self):
        if self.index >= self.n:
            self.twist()
        y = self.MT[self.index]
        y = y ^ ((y >> self.u) & self.d)
        y = y ^ ((y << self.s) & self.b)
        y = y ^ ((y << self.t) & self.c)
        y = y ^ (y >> self.l)
        self.index += 1
        return y & ((1 << self.w) - 1)

    def get_state(self):
        return (3, tuple(self.MT + [self.index]), None)


class MTpython(MT19937):
    def __init__(self,seed):
        MT19937.__init__(self,0)
        self.init_32bit_seed(seed)

    def init_by_array(self, init_key):
        self.seed_mt(19650218)
        i, j = 1, 0
        for k in range(max(self.n, len(init_key))):
            self.MT[i] = (self.MT[i] ^ (
                (self.MT[i - 1] ^ (self.MT[i - 1] >> 30)) * 1664525)) + init_key[j] + j
            self.MT[i] &= 0xffffffff
            i += 1
            j += 1
            if i >= self.n:
                self.MT[0] = self.MT[self.n - 1]
                i = 1
            if j >= len(init_key):
                j = 0
        for k in range(self.n - 1):
            self.MT[i] = (self.MT[i] ^ (
                (self.MT[i - 1] ^ (self.MT[i - 1] >> 30)) * 1566083941)) - i
            self.MT[i] &= 0xffffffff
            i += 1
            if i >= self.n:
                self.MT[0] = self.MT[self.n - 1]
                i = 1
        self.MT[0] = 0x80000000

    def init_32bit_seed(self, seed_32):
        """
        Just an oversimplification of `init_by_array` for single element array
        of upto 32 bit number
        """
        self.seed_mt(19650218)
        i = 1
        for k in range(self.n):
            self.MT[i] = (self.MT[i] ^ (
                (self.MT[i - 1] ^ (self.MT[i - 1] >> 30)) * 1664525)) + seed_32
            self.MT[i] &= 0xffffffff
            i += 1
            if i >= self.n:
                self.MT[0] = self.MT[self.n - 1]
                i = 1
        for k in range(self.n - 1):
            self.MT[i] = (self.MT[i] ^ (
                (self.MT[i - 1] ^ (self.MT[i - 1] >> 30)) * 1566083941)) - i
            self.MT[i] &= 0xffffffff
            i += 1
            if i >= self.n:
                self.MT[0] = self.MT[self.n - 1]
                i = 1
        self.MT[0] = 0x80000000

class Breaker():
    def __init__(self, bit_64=False):
        if bit_64:
            (self.w, self.n, self.m, self.r) = (64, 312, 156, 31)
            self.a = 0xB5026F5AA96619E9
            (self.u, self.d) = (29, 0x5555555555555555)
            (self.s, self.b) = (17, 0x71D67FFFEDA60000)
            (self.t, self.c) = (37, 0xFFF7EEE000000000)
            self.l = 43
            self.f = 6364136223846793005
            self.num_bits = 64
        else:
            (self.w, self.n, self.m, self.r) = (32, 624, 397, 31)
            self.a = 0x9908B0DF
            (self.u, self.d) = (11, 0xFFFFFFFF)
            (self.s, self.b) = (7, 0x9D2C5680)
            (self.t, self.c) = (15, 0xEFC60000)
            self.l = 18
            self.f = 1812433253
            self.num_bits = 32
        self.MT = [0 for i in range(self.n)]
        self.index = self.n + 1
        self.lower_mask = (1 << self.r) - 1
        self.upper_mask = (1 << self.r)

    def ut(self, num):
        """
        untamper
        """
        def get_bit(number, position):
            if position < 0 or position > self.num_bits - 1:
                return 0
            return (number >> (self.num_bits - 1 - position)) & 1

        def set_bit_to_one(number, position):
            return number | (1 << (self.num_bits - 1 - position))

        def undo_right_shift_xor_and(result, shift_len, andd=-1):
            original = 0
            for i in range(self.num_bits):
                if get_bit(result, i) ^ \
                   (get_bit(original, i - shift_len) &
                        get_bit(andd, i)):
                    original = set_bit_to_one(original, i)
            return original

        def undo_left_shift_xor_and(result, shift_len, andd):
            original = 0
            for i in range(self.num_bits):
                if get_bit(result, self.num_bits - 1 - i) ^ \
                   (get_bit(original, self.num_bits - 1 - (i - shift_len)) &
                        get_bit(andd, self.num_bits - 1 - i)):
                    original = set_bit_to_one(original, self.num_bits - 1 - i)
            return original
        num = undo_right_shift_xor_and(num, self.l)
        num = undo_left_shift_xor_and(num, self.t, self.c)
        num = undo_left_shift_xor_and(num, self.s, self.b)
        num = undo_right_shift_xor_and(num, self.u, self.d)
        return num

    def untamper_slow(self, num):
        S = Solver()
        y = BitVec('y', self.num_bits)
        y = y ^ (LShR(y, self.u) & self.d)
        y = y ^ ((y << self.s) & self.b)
        y = y ^ ((y << self.t) & self.c)
        y = y ^ (LShR(y, self.l))
        S.add(num == y)
        if S.check() == sat:
            m = S.model()
            return m[m.decls()[0]].as_long()

    def clone_state(self, outputs):
        assert len(outputs) == 624, "To clone full state, 624 outputs needed"
        return list(map(self.ut, outputs))

    def get_seed_mt(self, outputs):
        STATE = [BitVec(f'MT[{i}]', self.num_bits) for i in range(self.n + 1)]
        SEED = BitVec('seed', self.num_bits)
        STATE[0] = SEED
        for i in range(1, self.n):
            temp = self.f * \
                (STATE[i - 1] ^ (LShR(STATE[i - 1], (self.w - 2)))) + i
            STATE[i] = temp & ((1 << self.w) - 1)
        for i in range(0, self.n):
            x = (STATE[i] & self.upper_mask) + \
                (STATE[(i + 1) % self.n] & self.lower_mask)
            xA = LShR(x, 1)
            xA = If(x & 1 == 0, xA, xA ^ self.a)
            STATE[i] = STATE[(i + self.m) % self.n] ^ xA
            STATE[i] = simplify(STATE[i])
        t_start = time()
        S = Solver()
        for index,value in outputs:
            #S.add([i == j for i, j in zip(STATE, map(self.ut, outputs))])
            S.add(STATE[index]==self.ut(value))
        if S.check() == sat:
            m = S.model()
            print("time take", time() - t_start)
            return m[m.decls()[0]].as_long()
        else:
            print(time()-t_start)
        
    def untwist(self, outputs):
        """
        Reversing the twist operation of MT 19937
        Recovers the state before twist 
        (all bits of STATE[1:624] and MSB of STATE[0])
        since we have information about only 32*623+1 bit (19937)
        rest bits are dont care
        """
        MT = [BitVec(f'MT[{i}]', 32) for i in range(self.n)]
        for i in range(self.n):
            x = (MT[i] & self.upper_mask) + \
                (MT[(i + 1) % self.n] & self.lower_mask)
            xA = LShR(x, 1)
            xA = If(x & 1 == 1, xA ^ self.a, xA)
            MT[i] = MT[(i + self.m) % self.n] ^ xA
        s = Solver()
        for i in range(len(outputs)):
            s.add(outputs[i] == MT[i])
        if s.check() == sat:
            model = s.model()
            untwisted = {str(i): model[i].as_long() for i in model.decls()}
            untwisted = [untwisted[f'MT[{i}]'] for i in range(624)]
            return untwisted
        print('uh oh')

class BreakerPy(Breaker):
    def __init__(self):
        Breaker.__init__(self)
    def clone_state_index(self, outputs, index, num_tries=1000):
        untampered = list(map(self.ut, outputs))
        MT = [BitVec(f'MT[{i}]', 32) for i in range(self.n)]
        for i in range(index, self.n):
            MT[i] = BitVecVal(untampered[i - index], 32)
        for i in range(0, self.n):
            x = (MT[i] & self.upper_mask) + \
                (MT[(i + 1) % self.n] & self.lower_mask)
            xA = LShR(x, 1)
            xA = If(Extract(0, 0, x) == 0, xA, xA ^ self.a)
            MT[i] = MT[(i + self.m) % self.n] ^ xA
            MT[i] = simplify(MT[i])
        constraints = []
        S = Solver()
        t_start = time()
        #models = [Counter() for _ in range(624)]
        models = []
        S.add([MT[i % self.n] == v for i,
               v in enumerate(untampered[self.n - index:])])
        count = 0
        while S.check() == sat and count < num_tries:
            m = S.model()
            #block = [ decl()!=m[decl] for decl in m ]
            # S.add(Or(block))
            result = {str(i): m[i].as_long() for i in m}
            # for i in range(self.n):
            #    if i<index:
            #        models[i][result[f'MT[{i}]']]+=1
            #    else:
            #        models[i][untampered[i]]+=1
            count += 1
            result = [result[f'MT[{i}]'] for i in range(
                index)] + untampered[:self.n - index]
            return result
            print(result[:index])
            models.append(result)
        print("time take", time() - t_start)
        return models

    def discover_index(self, first, outputs):
        for i in range(624):
            r = MT19937(0)
            mt = self.clone_state_index(outputs, i, 1)
            r.MT = mt
            r.MT[0] = first
            r.index = i
            our = [r.extract_number() for _ in range(len(outputs))]
            if our == outputs:
                print(i)
                # return mt,i
    def get_state_before_twist(self, outputs):
        MT_init = MT19937(19650218).MT
        MT = [BitVec(f'MT[{i}]', 32) for i in range(self.n + 1)]
        # for i in range(self.n):
        #    MT[i] = BitVecVal(MT_init[i],32)
        #SEED = BitVec('seed',32)
        # i=1
        # for k in range(self.n):
        #    MT[i] = (MT[i] ^ ((MT[i-1] ^ LShR(MT[i-1],30)) * 1664525)) + SEED
        #    i+=1
        #    if i>=self.n:
        #        MT[0] = MT[self.n-1]
        #        i=1
        #i = 2
        # for k in range(self.n-1):
        #    MT[i] = (MT[i] ^ ((MT[i-1] ^ LShR(MT[i-1],30)) * 1566083941)) - i
        #    i+=1
        #    if i>=self.n:
        #        MT[0] = MT[self.n-1]
        #        i=1
        S = Solver()
        S.add(MT[0] == 0x80000000)
        #MT[0] = BitVecVal(0x80000000,32)
        for i in range(0, self.n):
            x = (MT[i] & self.upper_mask) + \
                (MT[(i + 1) % self.n] & self.lower_mask)
            xA = LShR(x, 1)
            xA = If(Extract(0, 0, x) == 0, xA, xA ^ self.a)
            MT[i] = MT[(i + self.m) % self.n] ^ xA
        t_start = time()
        models = []
        S.add([i == j for i, j in zip(MT, map(self.ut, outputs))])
        while S.check() == sat:  # and len(models)<1000:
            print(len(models))
            m = S.model()
            block = [decl() != m[decl] for decl in m]
            S.add(Or(block))

            result = {str(i): m[i].as_long() for i in m}
            models.append([result[f'MT[{i}]'] for i in range(624)])
            # models.append(m)
            #models.append([ m[MT[i]] for i in range(624) ])
        print("time take", time() - t_start)
        return models

    def get_seed_python(self, outputs):
        MT_init = MT19937(19650218).MT
        MT = [BitVec(f'MT[{i}]', 32) for i in range(self.n + 1)]
        for i in range(self.n):
            MT[i] = BitVecVal(MT_init[i], 32)
        SEED = BitVec('seed', 32)
        i = 1
        for k in range(self.n):
            MT[i] = (MT[i] ^ ((MT[i - 1] ^ LShR(MT[i - 1], 30)) * 1664525)) + SEED
            i += 1
            if i >= self.n:
                MT[0] = MT[self.n - 1]
                i = 1
        for k in range(self.n - 1):
            MT[i] = (MT[i] ^ ((MT[i - 1] ^ LShR(MT[i - 1], 30)) * 1566083941)) - i
            i += 1
            if i >= self.n:
                MT[0] = MT[self.n - 1]
                i = 1
        MT[0] = BitVecVal(0x80000000, 32)
        for i in range(0, self.n):
            x = (MT[i] & self.upper_mask) + \
                (MT[(i + 1) % self.n] & self.lower_mask)
            xA = LShR(x, 1)
            xA = If(Extract(0, 0, x) == 0, xA, xA ^ self.a)
            MT[i] = MT[(i + self.m) % self.n] ^ xA
        t_start = time()
        S = Solver()
        S.add([i == j for i, j in zip(MT, map(self.ut, outputs))])
        if S.check() == sat:
            m = S.model()
            print("time take", time() - t_start)
            return m[m.decls()[0]].as_long()