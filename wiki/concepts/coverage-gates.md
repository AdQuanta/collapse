# Coverage Gates & Polar Acceptance

## The Concept of Coverage
In the `collapse` project, "coverage" refers to whether the set of projective roots provides enough support on the Bloch sphere to define a continuous-like distribution.

## The Finite-Bin Gate
Because we work with finite $N$, we cannot have a truly continuous density. Instead, we use a **bin-based coverage gate**:
- The polar interval $[0, \pi]$ is divided into $B$ uniform bins (typically $B=64$ or $B=100$).
- **Full Coverage**: A result "has coverage" if every bin contains at least one root.
- **Failure**: If any bin is empty, the global RMSE and maximum error are reported as `null` (undefined), as the distribution is not "full-sphere."

## Polar Acceptance Gate (Sept 11 Study)
For the constructive family study, the following strict gate was adopted:
1. **Full 64-bin coverage**.
2. **Bin-center R RMSE $\le 0.05$** against $\cos^2(\theta/2)$.
3. **Max Born moment residual $\le 0.05$** over the first eight relations.

## Why this is Necessary
Without coverage gates, a "Born-like" score could be artificially high if roots are clustered in a few favorable bins, even if huge gaps exist elsewhere. Coverage ensures that the Born-like behavior is a global property of the root distribution.

See also: [[born-like-points]], [[production-pipeline]].
