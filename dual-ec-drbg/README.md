# Dual EC DRBG - Kleptographic Backdoor

Dual EC(Elliptic Curve) DRBG(Deterministic Random Bit Generator) was a pseudo-random number generator which was a one of its kind PRNG in that it relied on elliptic curves, while most earlier PRNGs relied on symmetric components like block ciphers or hash functions. As a result, it was quite slow than it's competitive RNGs. However, since it was based on elliptic curves, it was believed that this could be a provably PRNG; but it suffered from many flaws. Despite all its shortcomings, it was highly standardized by NSA and was one of the four PRNGs proposed by NIST as **approved RNGs**.

## Working

![](./decdrbg.png)

A particular curve $C$ and two points on the curve $P$ and $Q$ are chosen apriori and remain fixed throughout.

The RNG is initially seeded with a random seed $s_0$. Whenever the RNG is asked for an output, assuming that the current seed(state) is $s_i$; $r_i \leftarrow (s_i * P) |_{x}$ is computed where $M |_{x}$ denotes the $x$-coordinate of the point $M$.

The seed is then updated as $s_{i+1} \leftarrow (r_i * P) |_{x}$, $t_i$ is computed as $t_i \leftarrow (r_i * Q) |_{x}$ and then the output generated is $LSB_{bitlen - 16}(t_i)$ where $LSB_{k}$ denotes the Least Significant $k$ bits.

We work with the case where $C$ is the NIST $P-256$ curve, in which case $bitlen = 256$ and therefore, in a single round, $240$ bits are obtained.

## Backdoor

Note that the RNG only throws out the top $16$ bits, which is a very small amount compared to the total bit-length being $256$.

This also gives the Dual-EC a bias; and this bias can indeed be taken advantage of to recover the generated point($r_i * Q$) from the output bits. Note that the number of bits being discarded are just $16$ which can be bruteforced to find out which bits ensure that the point is on the curve. This yields a list of plausible generated points. This would be the end of the attack usually.

However, there's a subtle issue underlying the choice of $P$ and $Q$. If these were totally random points, calculating $r_i * Q$ doesn't help us in any manner in calculating $r_i * P$. However, if $P$ and $Q$ were deliberately chosen such that $Q = e*P$ or $P = d * Q$; one could actually obtain the list of possible next states from these generated points as $r_i * P = r_i * d * Q$. This way we could refine our list of plausible generated points or the corresponding states to finally yield the actual internal state, thereby totally breaking down the RNG.

In our Proof-of-Concept, we demonstrate that choosing $P$ and $Q$ of our own accord allows us to recover the internal state of the RNG in mere 32 bytes of output. This confirms the possibility of there being a backdoor in the RNG, and hence, allowing the attacker to gain access to many of the encrypted information where Dual-EC-DRBG was being employed.

The values of $P$ and $Q$ which were used in the actual implementation had been publicised by NSA/NIST to be the ones which allowed "fast computations", nobody knows where these values actually came from! Since the values were chosen by themselves, it is unknown whether they actually had utilized this backdoor but the existence of a backdoor in a popular PRNG is very troublesome to the cryptographic community in itself.