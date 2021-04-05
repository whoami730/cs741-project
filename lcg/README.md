# Linear Congruential Generator

Linear Congruential Generator(LCG) is a method of generating a sequence of pseudo-randomized numbers calculated using modular arithmetic. This method has seen quite widespread usage since the theory behind this method is pretty easy to understand and is also easy to implement as well as fast and require minimal memory, especially on computer hardware.

However, LCG is not cryptographically secure. Moreover, they have been shown to be not so good even for [Monte-Carlo simulations](https://en.wikipedia.org/wiki/Marsaglia%27s_theorem) due to correlation between successive values. 

<!-- mention Truncated lcg -->

### Details
Linear Congruential Generator is defined by the following recurrence relation - $$X_{i+1} = (a*X_i + b) % m$$
where $X$ is the sequence of generated pseudo-random values; $m$ is the `modulus`, $a$ is the `multiplier`, $c$ is the `increment` and $X_0$ is the `seed` or the `start value`. 
 
Note that the above mentioned update applies not just to the generated values but also to the internal state; ie, whenever a call is made to the LCG, $X_{i+1}$ is yielded as well as the internal state is updated to $X_{i+1}$.

## Background
It has been shown that given sufficient number of outputs, one could recover the internal state even if the parameters of the generator - $a$,$c$ and $m$ are unknown. 

## Our Work
The existing method indeed allows us to recover the internal state given just a few outputs, and the probability of the attack succeeding increases with increase in the number of outputs chosen.

[Z3Prover](https://github.com/Z3Prover/z3) has also been used to recover the internal state, but it relies on the knowledge of the parameters, and works well only when $m$ is a power of $2$.




## References
- [Marsaglia's Theorem](https://en.wikipedia.org/wiki/Marsaglia%27s_theorem)