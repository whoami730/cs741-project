# Linear Congruential Generator

Linear Congruential Generator(LCG) is a method of generating a sequence of pseudo-randomized numbers calculated using modular arithmetic. This method has seen quite widespread usage since the theory behind this method is pretty easy to understand and is also easy to implement as well as fast and require minimal memory, especially on computer hardware. However, having seen widespread usage does not imply security in any manner. In fact, it's recommended that LCGs not be used as random generators at all!

Donald Knuth suggested the usage of Truncated LCG, where only some bits of the internal state were outputted(say upper half bits). These turned out to have much better statistical properties than the original LCGs. However, these are not cryptographically secure either; and indeed there exist attacks which can find out the internal state given a few outputs!

## Algorithmic Details
A linear congruential generator maintains an internal state $s$, which is updated on every call to the generator as $s := (a*s + b) \% m$. The updated state is the generated pseudo-random number. Therefore, the generated numbers $X_i$ follow the recurrence relation $X_{i+1} = (a*X_i + b) \% m$, or, equivalently $X_i = (a^{i} * X_0 + b*(1 + a + \dots + a^{i-1})) \% m$.

For a truncated LCG which outputs certain most significant bits of the internal state, generated number $X$ can be written as $X = (s \gg trunc)$ where $\gg$ denotes logical right-shift and $trunc$ is the number of lower bits to be truncated.

## Background
It has been shown that given sufficient number of outputs, the parameters of a secret LCG can be recovered.
Lattice attacks have also been demonstrated on truncated LCGs to recover the seed.

## Our Work

[Z3Prover](https://github.com/Z3Prover/z3) has also been used to recover the internal state, but it relies on the knowledge of the parameters, and works well only when $m$ is a power of $2$.


## References
- [LCG](https://en.wikipedia.org/wiki/Linear_congruential_generator)
- [Truncated LCG](https://www.math.cmu.edu/~af1p/Texfiles/RECONTRUNC.pdf)