# Project -  Analysis, state and seed recovery of RNGs
## Description
Study of (novel) methods for seed and state recovery using reduced number of outputs for general purpose random number generators like MT19937, MT19937-64, LCGs, LSFRs, NLSFRs using SMT/SAT solvers.

## Relevance
A lot of applications use RNGs for various tasks (sometimes unintentionally by developers in cryptographic code instead of some CSPRNG) which might leave it vulnerable to prediction of exact outputs using some initial outputs and thus compromising the security assumption of the application.  

Ability to deduce the initial state/seed of the RNG from reduced set of outputs (than theoretically required to predict) could further weaken the predictability considerations of some RNGs.  
Use of SAT/SMT solvers in this area is less explored and many existing state recovery attacks could further be performed more efficiently by such methods.

## Plan of execution
- Study and implementation of standard algorithms for various mentioned RNGs.
- Implementation and understanding of various RNGs used in the standard libraries of various programming languages

## References
- [mersenne twister](https://en.wikipedia.org/wiki/Mersenne_Twister)
- [random number generators](https://en.wikipedia.org/wiki/List_of_random_number_generators)
- [SAT-SMT by example](https://sat-smt.codes/SAT_SMT_by_example.pdf)

## Side mini project (upto availability of time)
- Automated linear-cryptanalysis for SPN

# Team members
1. Himanshu Sheoran 170050105
2. Lakshya Kumar 170050033
3. Sahil Jain 180050089
4. Yash Ajitbhai Parmar 170050004
