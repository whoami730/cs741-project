
## Mersenne Twister (19937)
Mersenne Twister is by far the most widely used general-purpose PRNG, which derives its name from the fact that its period is the mersenne prime $2^{19937} -1$  

It is the default PRNG in Dyalog APL, Microsoft Excel, GAUSS, GLib, GNU Multiple Precision Arithmetic Library, GNU Octave, GNU Scientific Library, gretl, IDL, Julia,CMU Common Lisp, Embeddable Common Lisp, Steel Bank Common Lisp, Maple,MATLAB, Free Pascal, PHP, Python,R,Ruby,SageMath, Scilab, Stata, SPSS, SAS, Apache Commons,  standard C++ (since C++11), Mathematica. Add-on implementations are provided in many program libraries, including the Boost C++ Libraries, the CUDA Library, and the NAG Numerical Library.

### Algorithmic Details
The Mersenne Twister algorithm is based on a matrix linear recurrence over a finite binary field $F_2$. The algorithm is a twisted generalised feedback shift register (twisted GFSR, or TGFSR) of rational normal form, with state bit reflection and tempering. 

The internal state is defined by a sequence of $n=624$, 32-bit registers ($w$)  

$$x_{k+n} \to x_{k+m} \oplus (( x_k^{u} \| x_{k+1}^{l})A)$$
To compensate for reduced dimensionality of equidistribution, the state is cascaded with tampering transform (to improve the equidistribution) to produce the output

$$y \to x \oplus(( x >> u)\&d)$$
$$y \to y \oplus(( y << s)\&b)$$
$$y \to y \oplus(( y << t)\&c)$$
$$z \to y \oplus( y >> l)$$

The computed $z$ is returned by the algorithm
where the choice of constants is as follows
```
(w, n, m, r) = (32, 624, 397, 31)
a = 0x9908B0DF
(u, d) = (11, 0xFFFFFFFF)
(s, b) = (7, 0x9D2C5680)
(t, c) = (15, 0xEFC60000)
l = 18
f = 1812433253 
```

### Initialization
The state needed for a Mersenne Twister implementation is an array of $n$ values of $w$ bits each. To initialize the array, a w-bit seed value is used to supply $x_0$ through $x_{n − 1}$ by setting $x_0$ to the seed value and thereafter setting

$$x_i = f \times (x_{i−1} \oplus (x_{i−1} >> (w−2))) + i$$

for i from 1 to n−1. The first value the algorithm then generates is based on $x_n$

![](merstw.gif)

While implementing, we need to consider only three things
1. State initialization i.e. seeding
2. The `twist` operation to produce next 624 state registers by "twisting" the current state of 624 registers
3. The `tamper` operation to tamper a state register to the produced 32-bit output

## Background
There exist various conference talks for mersenne twister seed and state recovery for the aid of pentesters at various security conferences e.g
- [untwister](https://github.com/bishopfox/untwister) presented at B-Sides Las Vegas 2014, which recovers upto 32 bit seeds by a parallalized bruteforce using a pool of workers or state recovery using 624 consecutive outputs (will be discussed soon).  
- [PRNG Cracker](https://dspace.cvut.cz/bitstream/handle/10467/69409/F8-BP-2017-Molnar-Richard-thesis.pdf?sequence=-1&isAllowed=y) which in addition to parallalized seed bruteforcing, creates a rainbow table of outputs for lookup in seed database.
- [PHP mt_rand predictor](https://www.ambionics.io/blog/php-mt-rand-prediction) achieves seed recover using two outputs which are 227 apart of each other exploiting the improper implementation of mersenne twister in PHP in particular. This works only for PHP as it doesnt use the standard MT algorithm.

### State recovery from 624 consecutive outputs
The mersenne twister keeps a state of 624 registers `MT` and an index `i` to track the position in the state. Once `i` reaches the end of state array, the `twist` operation is called to twist the state to next 624 numbers in the sequence and `i` is set to 0. The output $y_i$ is generated using the `tamper` function on the state `MT[i]`. This tamper function is completely reversible, hence given $y_i$ we can recover `MT[i]`. Once we recover any 624 state registers, we can set $i=0$ from there and predict any future outputs.

#### Untamper
Each of the step of instructions in `tamper` is reversible since it is simple xor of a register and right or left shifted select bits of it. Merely tracking which bits were xored with which bits of the input register to get the next value, we can undo the operation. Since in xoring with right shifting, the MSB of y would be MSB of x, and in xoring with left shifting, the LSB of y will be LSB of x.
```
y = undo_right_shift_xor_and(z, l)
y = undo_left_shift_xor_and(y, t, c)
y = undo_left_shift_xor_and(y, s, b)
x = undo_right_shift_xor_and(y, u, d)
```

## Our work
We began with the implementation of standard MT19937 from algorithm described on [Wikipedia](https://en.wikipedia.org/wiki/Mersenne_Twister). This involved a lot of debugging and testing against various random number library implementations, reading the source code of the MT implementations in Python, Ruby, PHP. And figuring out how each of these vary from the standard implementation on wiki. 

### Modelling
We modelled the seed recovery algorithm as a SMT problem using the SMT solver [Z3Prover](https://github.com/Z3Prover/z3), as a sequential program written in theory of BitVectors(32) (since the algorithm is designed to work on 32bit architectures) and theory of BitVectors(64) for MT19937-64 . After (painfully) modelling the program, we begin a SAT solver search (all-SAT to give all satisfying models for possible seed values) which leads us to a given sequence of outputs (the generated random numbers). 

### Results
We were able to recover the seed of the mersenne twister for both MT19937 and MT19937-64 using any **3** consecutive outputs, in about ~200 seconds.  

The modelling of `untwist` can reverse the `twist` operation to go back 624 outputs, which cannot be done easily by any of usual methods thus enabling us to predict unseen outputs which were produced before the observed set of outputs.  

Our method is extremely memory and space efficient since SAT solvers work with negligible memory (<500 MB). And way faster and efficient considering the space time tradeoff involved.




## Challenges
While the wikipedia implementation is treated as the standard mersenne twister, we found that our implementation was producing different outputs from the implementations in programming languages even after initializing by the same seed. After dissecting a lot of source code, we figured out that the wiki implementation serves as the base of merssene twister implementation everywhere with a difference in the way it is seeded. All modern mersenne twister are seeded with a function `init_by_array` which takes an array of 32-bit seeds (or 32 bit hashes of seed objects). Later we found that this was proposed as an enhancement to equidistribution property to the base mersenne twister [MT2002](http://www.math.sci.hiroshima-u.ac.jp/m-mat/MT/MT2002/emt19937ar.html).  
This `init_by_array` is much more non-linear that the standard `seed_mt` operation and makes it much more difficult to recover the seed values from a few outputs. We tried following the same approach, and it turns out it was unable to deduce the seed even in a couple of hours. 

## References
- [The Mersenne Twister](http://www.quadibloc.com/crypto/co4814.htm)
- [Wikipedia](https://en.wikipedia.org/wiki/Mersenne_Twister)