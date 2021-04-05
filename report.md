# Project -  Analysis, state and seed recovery of RNGs
## Abstract
Study of (novel) methods for seed and state recovery using reduced number of outputs for general purpose random number generators like MT19937, MT19937-64, LCGs Truncated LCGs, LSFRs, using SMT/SAT solvers.

## Introduction
Given a PRNG algorithm $A$, which is initialised using an initial value aka `seed` and $x_1, x_2, ..., x_k$ be the generated outputs from the random number generator, we wish to determine the starting `seed` or the state $S$ required to predict the future outputs of the generator.

We were able to recover `seed` of standard mersenne twister (MT19937), which is the most used PRNG across all software systems, using only **3** outputs using SMT solvers in under 5 minutes, whereas all previous work is on state recovery using 624 consecutive outputs.

We also employed SMT solvers to recover the state of other well known PRNGs like LCG, LSFRs and combiner generators using a set of LSFRs.

We aim to understand the predictability of PRNGs and further analysed the design of some cryptographically secure PRNGs and case study of the notorious DUAL_EC_DRBG CSPRNG for presence of a kleptographic backdoor to give NSA ability to predict all outputs.

Problem Statement + Summary

## Background
Previous work done in this topic

## Our Work
Exactly what we did (setup up something, installed something, ran code from github etc. whatever small things we did for the project)

# Personal Section
## Challenges / Difficulties


## Limitations / Assumptions


## Compatibility issues
Could not run a particular version of software or a software didn't worked in a particular os

## Understanding existing papers
sir ka example -> this particular paper was very cryptic and there were a lot of notions and after enormous discussion it took us 1 week to understand 

## Reading manual


## Critique / Comparison
Critique an idea or paper or an attack senario
Comparison with others work or idea

## Extensions


# Team members
1. Himanshu Sheoran 170050105
2. Lakshya Kumar 170050033
3. Sahil Jain 180050089
4. Yash Ajitbhai Parmar 170050004
