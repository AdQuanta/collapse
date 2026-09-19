# Probing the Planck Scale with Quantum Computation

> Source: https://arxiv.org/abs/2604.06322 (PDF supplied locally by the user)
> Collected: 2026-09-15
> Published: 2026-04-07

## Page 1

Probing the Planck scale with quantum computation

arXiv:2604.06322v1 [quant-ph] 7 Apr 2026

Boaz Katz1∗ , Shlomi Kotler2∗
1 Department of Particle Physics and Astrophysics, Weizmann Institute of Science, Rehovot 76100, Israel.

2 Racah Institute of Physics, The Hebrew University of Jerusalem, Jerusalem 91904, Israel.
∗ Corresponding author. Email: boaz.katz@weizmann.ac.il; shlomi.kotler@mail.huji.ac.il

General relativity and quantum mechanics are incompatible at the Planck
scale.‌ This contention can be examined if a quantum computer is set to operate at
a rate that exceeds the classical limit of one operation per Planck volume-time, or
equivalently 2491 m−3 s−1 . Here we quantify the relation between the logical qubit
count and the extent to which classicality is challenged. We argue that 500 logical
qubits are sufficient to reject theories confined to a laboratory. We account for
the operational cost of computation and communication at all scales up to and
including the observable universe, ultimately constrained by a 1600-logical-qubit
computer. Remarkably, current plans for commercial quantum computers are
projected to surpass this limit, thereby putting the quantum-gravity standoff to
the test.
Our current understanding of the universe at large distances, embodied by the theory of general relativity, is at odds with that of the sub-atomic sizes governed by quantum mechanics. On astrophysical
scales, quantum corrections to gravity are negligible, while on microscopic scales, gravity is too
weak to be observed. The Planck scale is a point of contention where both should be significant and
in contradiction. Addressing this problem requires devising experiments that probe the constituents
√︁
of the universe at distances of 𝑙 𝑃 ≡ ℏ𝐺/𝑐3 ≈ 1.6 × 10−35 m, at times of 𝑡 𝑃 ≡ 𝑙 𝑝 /𝑐 ≈ 5.4 × 10−44 s,
or at energies of 𝐸 𝑃 ≡ ℏ/𝑡 𝑃 ≈ 1.2 × 1028 eV, where 𝑐 is the speed of light, ℏ is the reduced Planck
constant and 𝐺 is the gravitational constant.

## Page 2

The large energies involved preclude the direct approach of using particle accelerators, as
illustrated by the fact that even the most energetic accelerator to date, the Large Hadron Collider,
reaches ∼ 1013 eV, which is 15 orders of magnitude smaller than the Planck energy (1). A promising
indirect approach to explore the boundary between quantum mechanics and gravity is to search
for anomalies in sensitive measurements. These include astronomical observations (2), massive
quantum systems (3, 4), and laser interferometers (5, 6).
Quantum computation allows for new tests of the fundamental laws of nature due to its extraordinary property of achieving an exponential number of operations (7–10). In particular, the ability
to reach very high computational rate densities that exceed one operation per Planck volume per
Planck time may allow a direct test of classical theories at this scale (8). Here we quantify the
relation between computational capability and the resulting constraints on classical theories. We
show that theories that are confined to a typical laboratory volume and experiment time can be ruled
out by a quantum computer with approximately 500 logical qubits. We consider more extensive
theories that account for computation and communication costs at ever-growing scale and should
therefore be contended against larger and larger quantum computers. The most inclusive theory,
describing a fully connected universe that is only limited by causality, corresponds to approximately
1600 logical qubits. As a result, we argue that Planck physics will soon be probed by quantum
computers aiming at breaking RSA-2048 encryption by implementing Shor’s algorithm for integer
number factoring.
A simplified model of a computer consists of a grid of computing elements, at a distance 𝑙 from
one another, that perform a single operation every time step 𝜏, as shown in Fig. 1. For example,
in a contemporary processor, the computing elements are transistors, separated by 𝑙 ∼ 50 nm and
operating at a clock cycle of 𝜏 ∼ 10−10 s. Inverting this perspective, given a computer with hidden
internal elements, a constraint on 𝑙 can be derived based on its performance. Put simply, if 𝑁ops is
the number of operations performed in a single cycle, then 𝑙 must obey 𝑙 ≤ (𝑉3 /𝑁ops ) 1/3 , where 𝑉3
is the volume of the computer.
A more general case involves a black-box computer that has demonstrated 𝑁ops operations
within a time span 𝑇. In this case, since 𝜏 is unknown, a strict upper limit on 𝑙 can be derived from
the fact that information cannot propagate faster than the speed of light, limiting the cycle time to

## Page 3

τ
l
l

time

Figure 1: Computational Rate Density (CRD). A simplified model of a computational process.
Computing elements are spaced at a distance 𝑙 from one another, performing an operation (represented by dots) every clock cycle 𝜏. The resulting number of operations per unit volume per
unit time (CRD) is C = 1/(𝑙 3 𝜏); see Eq. 2. The spatial coordinates are represented here by a
two-dimensional grid for simplicity.
𝜏 ≥ 𝑙/𝑐. Therefore the length scale must satisfy:


𝑉3 𝑐𝑇
𝑙≤
𝑁ops

 1/4
.

(1)

This bound depends on the intrinsic Computational Rate Density (CRD) of the computer,
C≡

𝑁ops
1
= 3 ,
𝑉3𝑇
𝑙 𝜏

(2)

i.e., the number of operations per unit volume per unit time. Equation 1 can be restated as C ≤ 𝑐/𝑙 4 .
The upper limits obtained by the current capabilities of classical computers using Eq. 1 do not
add new constraints on known physics. For example, a modern GPU die, with volume ∼ 744 mm3
capable of 3352 trillion operations per second (11), translates to a conservative upper limit of
𝑙 ≲ 0.5 mm. In fact, current technologies are ultimately limited by the atomic scale and will not be
able to probe lengths smaller than ∼ 1 Å.
Quantum computers dramatically increase the CRD. Specifically, a quantum computer with 𝑛
logical qubits is expected to perform
𝑁ops ≥ 2𝑛

(3)

equivalent classical operations. The resulting length scale probed by quantum computers is shown
in Fig. 2 versus the logarithm of the Number of Equivalent classical Operations (NEO). This figure

## Page 4

lly

3
m)

3s

1m
10−30

fu

co

100

co
nn
ec
te
d

nn

ec
te
d

10

−50

10

−60

AGS (1960)
LHC (2026)

un
ive
rs

e

1010

1020

lab

rse

10

−40

radioactivity (1900)

1030

Planck scale

1040

RSA-2048
200

400

600

800

1000

1200

1400

1600

1800

Equivalent energy scale (eV)

lly

ive
un
ble
rva
se
ar
ob
ye

10

−20

fu

(10

10

−10

lab

Probed length scale (m)

100

1050

2000

log2 (Number of equivalent classical operations)

Figure 2: Length scale probed by a quantum computer. The probed length scale is shown versus
the Number of Equivalent classical Operations (NEO) demonstrated by a verified calculation of a
quantum algorithm. The dotted line corresponds to a small experiment of size 1 m3 running for
1 s while the lower solid line corresponds to a large laboratory building of size 1000 m3 running
for a full year (Eq. 1). The upper solid line extends the resources of the lab to include all possible
calculations within its past light cone throughout the history of the universe since the Big Bang
(Eq. 7). The dashed line corresponds to a fully connected lab where each computational event
integrates direct inputs from all previous calculations in its causal past (Eq. 8 and Fig. 4B). The
dash-dotted line represents this fully connected computation when extended to the entire observable
universe (Eq. 9 and Fig. 3). The range of the estimated number of logical qubits required to break a
modern RSA code using Shor’s algorithm is marked on the x-axis (12, 13). The y-axis on the righthand side shows the corresponding energy scales. Marked years 1900, 1960 and 2026 correspond
to the highest particle energies probed at those eras with radioactivity, the Alternating Gradient
Synchrotron (14), and the Large Hadron Collider (1), respectively.

## Page 5

encapsulates the main results of this paper. As can be seen, the trend line of a large lab (1000 m3 ),
operating for a full year, will reach the Planck scale with 𝑛 = 525 logical qubits. Such a computer
will reach the Planck computational rate density of
C𝑃 ≡

1
𝑙 𝑃3 𝑡 𝑃

≈ 1.37 × 2490 ops m−3 s−1 .

(4)

Given that quantum computers are planned to accommodate a much larger number of logical qubits,
their computational rate density is expected to far exceed C𝑃 , requiring any underlying classical
elements to be much smaller than the Planck scale.
We next discuss important extensions of this bound with fewer restrictions on computational
power. Computers often increase their capacity by accessing additional processors using a shared
communication network. Moreover, a computation may incorporate tabulated results from previous
calculations. Therefore, the possible NEO of a lab may be much larger than that used in Eq. 1.
Estimating its magnitude requires knowledge of the details of the network and the data storage
capability of its processors.
Regardless of the intricacies of computing systems, all are ultimately limited by causality.
The latter can be used to set upper bounds on computation capacity. For an external resource to
contribute, it must be in the past light cone of the final output. The portion of the light cone that
needs to be accounted for should include all preceding calculations that were tabulated, requiring
knowledge of their history.
The most inclusive choice for the history of a computation is to extend its origin all the way to
the Big Bang. In this case, the shape of the light cone is set by the expansion history of the universe,
shown in Fig. 3 (orange wire-frame). At a time 𝑡 in the past, the universe was smaller compared
to today by the cosmic scale factor 𝑎(𝑡). Naturally, not all of the universe at that time could have
contributed to a calculation today. Only those events from which light had enough time to reach us
should be accounted for. The distance 𝑑 (𝑡1 , 𝑡2 ) light travels from time 𝑡1 to time 𝑡 2 , as measured
today between the emitting and receiving galaxies (co-moving distance), is given by,
∫ 𝑡2
𝑐𝑑𝑡
𝑑 (𝑡 1 , 𝑡2 ) =
.
𝑡1 𝑎(𝑡)

(5)

The 3-dimensional region at 𝑡 1 from which calculations can affect an operation at 𝑡2 is therefore
a sphere of radius 𝑎(𝑡 1 )𝑑 (𝑡 1 , 𝑡2 ), as measured at 𝑡 1 . Integrating all of these spheres since the Big

## Page 6

Today

Big Bang

Earth

Computational
event

Figure 3: Causal history of a computation on Earth today since the Big Bang. The expansion
history of the universe is shown by a black wireframe whose diameter is proportional to the cosmological scale factor 𝑎(𝑡). Any computational event within the past light cone (orange wireframe)
of an experiment today may have contributed to its result and is therefore accounted for in the
spacetime volume calculated in Eq. 7, corresponding to the upper solid line in Fig. 2. In a fully
connected universe, every intermediate computational event can directly receive information from
all other events within its past light cone (purple wireframe), adding to the operation count in Eq. 9,
corresponding to the dash-dotted line in Fig. 2.
Bang results in the total spacetime volume that can affect a calculation at 𝑡2 ,
∫
4𝜋 𝑡2
𝑉4 (𝑡2 ) =
𝑑𝑡 1 𝑎 3 (𝑡1 )𝑑 3 (𝑡 1 , 𝑡2 ).
3 0

(6)

The number of operations available to an experiment today cannot exceed that of a universe densely
packed at the upper CRD limit of 𝑐/𝑙 4 ,

4
𝑐𝑉4 (𝑇𝑈 )
𝑐/𝐻0
𝑁ops =
= 𝑘 4𝑈
,
𝑙
𝑙4

(7)

where 𝑇𝑈 ≈ 14 Gyr is the age of the universe, 𝐻0 ≈ 70 km s−1 Mpc−1 is the Hubble constant, and
𝑘 4𝑈 ≈ 0.13 is a dimensionless factor set by the cosmological parameters (15). Shown by the upper
solid line in Fig. 2, this limit intersects the Planck scale at a threshold of log2 (𝑁ops ) ≈ 806 logical
qubits. Note that the implied number of operations available in the entire universe may seem larger

## Page 7

than the estimate in Ref. (16). Those differ, however, since the latter enumerates quantum rather
than classical operations.
Communications between computing elements increase the number of operations and should
also be accounted for. In the case of nearest-neighbor connectivity shown in Fig. 4A, where each
event is influenced by a small number of predecessors, the increased computational overhead will
have negligible impact. For example, in the laboratory scenario, eight inputs per operation will
modify the required number of logical qubits needed to reach the Planck scale from 525 to 528.
By contrast, networks that exhibit much higher linkage may impact the overall operation count
significantly. Examples include distributed systems (17) and biological neural networks.
Different choices of network connectivity may result in significantly different operation counts.
For a natural example of a relativistic connectivity, see Supplementary Text. All possible choices,
however, can be bounded by the fully connected mesh, where all causally connected events are
included. In this case each computational event integrates inputs from all events in its past light
cone. In a typical laboratory, the computation time, 𝑇, is much longer than the lab light-crossing
time. Therefore, each computational event will include inputs from almost all previous events,
since only a small fraction occur within the preceding light-crossing time. Neglecting this minor
correction, every pair of events is connected and should be counted once. The resulting number of
operations is therefore

2
1 𝑉3 𝑐𝑇
𝑁ops =
.
2 𝑙4

(8)

Full connectivity is illustrated in Fig. 4B. The length scale probed by the fully connected lab is
shown by the dashed line of Fig. 2. It intersects the Planck scale at 1050 qubits.
We are now in a position to account for the largest possible extension for computation capacity—the fully connected universe. It involves full-connectivity extended to the entire universe since
the Big Bang. This calculation can be broken down as follows. At each time 𝑡, all computational
events that could influence today are encapsulated within a sphere of radius 𝑎(𝑡)𝑑 (𝑡, 𝑇𝑈 ), shown by
a dark circle in Fig. 3. Each one of these events, in turn, can be affected by all events within its own
past light cone. The corresponding spacetime volume 𝑉4 (𝑡) is depicted by the purple wireframe in
Fig. 3. The total number of operations is obtained by integrating the product of these two factors

## Page 8

A

τ

l

time

B

Figure 4: Computational connectivity. Possible communications (illustrated by lines) between
computational events (illustrated by dots). The laboratory computational process in Fig. 1 is represented here with one spatial dimension. Two limiting cases of connectivity are drawn. (A) Nearestneighbor connectivity. Each computational event integrates the output of its adjacent events from
the previous clock cycle. (B) Fully connected laboratory. Each computational event incorporates all
prior events that are in its past light cone. For the typical scenario depicted here, the computation
extends over a time that is much longer than the lab light-crossing time. Therefore, effectively all
preceding computational events from all elements contribute; see Eq. 8.
over the history of the universe:
4𝜋𝑐2
𝑁ops =
3𝑙 8

∫ TU

3

3

𝑑𝑡 𝑎 (𝑡) 𝑑 (𝑡, 𝑇𝑈 )𝑉4 (𝑡) = 𝑘 8𝑈
0



𝑐/𝐻0
𝑙

8
,

(9)

where 𝑘 8𝑈 ≈ 8.6 × 10−4 is a second dimensionless factor set by the cosmological parameters (15).
The resulting limit is shown in Fig. 2 by the dashed-doted line.
Even for this most extensive model, the Planck scale will be probed for machines with only
1609 logical qubits, within the requirements to break RSA-2048 encryption (12, 13). To appreciate
the magnitude of this ultimate NEO limit, it is worth revisiting its underlying physical constituents,
depicted in Fig. 3. The universe is tightly packed with computing elements, at a Planck distance from
one another, performing calculations every Planck time. Moreover, as the universe expands, new

## Page 9

elements are constantly being added, filling the newly created gaps. Accounting for the operational
cost of communication, the result of a calculation today includes direct inputs from all events in its
past light cone since the Big Bang. Finally, each of these individual past events carries it own past
light cone, also furnished with computational events that are densely packed at the Planck scale.
The bounds above demonstrate that a quantum computer that successfully factorizes numbers
with 𝑛 = 2048 binary digits will all but rule out models in which the universe has classical rules
at the Planck scale, such as those discussed in Refs. (8, 18, 19). A reservation to this conclusion is
that the underlying classical evolution may have performed substantially fewer than 2𝑛 operations.
In fact, there are classical algorithms that can factor numbers much more efficiently (20), and
those could be further improved in the future. The existence of such algorithms, however, is
not the determining factor for our purposes, unlike quantum computational advantage. Here, any
contending classical explanation of the computation would not only have to account for number
factoring, but also mimic the steps of the specific quantum algorithm implementation. Indeed, the
process of developing quantum computers entails rigorous tests of their memory elements, quantum
gates, and algorithmic submodules. We believe that the combined evidence provided by a solution
to a computationally hard problem that can be verified, together with access to sub-components
and interim results, would tilt the scale in favor of quantum mechanics.
To date, there have been experimental demonstrations that involved up to a few dozen logical
qubits (21–24) and there are detailed plans to extend these numbers to the thousands in order to
break RSA-2048 (13, 25–28). An exciting alternative that may allow reaching high CRD sooner
is to use Noisy Intermediate-Scale Quantum devices (29) that run algorithms such as boson sampling (30). This was demonstrated, for example, with random circuits (31) and Gaussian boson
sampling (32). While experiments with noisy systems have shown faster progress, they involve a
nontrivial reduction of computational complexity. Quantifying the NEO of such experiments is a
worthwhile endeavor that is beyond the scope of this paper.
Does quantum mechanics have boundaries? If so, what experimental axes lead there? Newtonian
mechanics breaks down at high speeds. Classical physics fails at subatomic scales. There are
no known analogous limits to quantum mechanics. At the Planck length, quantum mechanics
clashes with another successful theory—general relativity. At this small scale, at least one of
these theories must fail. Unfortunately, direct experiments show little hope of testing this regime

## Page 10

in the foreseeable future. As a result, indirect approaches are currently being pursued. Quantum
computation is an emerging technology that may soon push the boundary of experimental physics
along a completely new axis—Computational Rate Density (CRD). Quantum mechanics has a
unique potency to condense an exponential number of equivalent classical operations (NEO) into
the volume and time span of a laboratory experiment. Remarkably, future quantum computers
that are currently under industrial development are expected to far exceed the Planck CRD of
≈ 1.37 × 2490 operations m−3 s−1 , eventually surpassing the computational capacity of the fully
connected universe. If successful, this will vindicate quantum mechanics and challenge our current
fundamental theory of gravity. If, however, quantum computation efforts persistently fail, with no
apparent technical reasons, this may be the first sign of the limits of quantum mechanics. In either
case, it appears that this extensive human endeavor, which is largely driven by its technological
potential, may soon probe into some of the deepest mysteries of nature.

## Page 11

References and Notes
1. L. Evans, P. Bryant, LHC Machine. Journal of Instrumentation 3 (08), S08001 (2008), doi:10.
1088/1748-0221/3/08/S08001, https://doi.org/10.1088/1748-0221/3/08/S08001.
2. R. Alves Batista, et al., White paper and roadmap for quantum gravity phenomenology in
the multi-messenger era. Classical and Quantum Gravity 42 (3), 032001 (2025), doi:10.1088/
1361-6382/ad605a, https://doi.org/10.1088/1361-6382/ad605a.
3. S. Bose, et al., Massive quantum systems as interfaces of quantum mechanics and gravity. Rev.
Mod. Phys. 97, 015003 (2025), doi:10.1103/RevModPhys.97.015003, https://link.aps.
org/doi/10.1103/RevModPhys.97.015003.
4. D. Carney, P. C. E. Stamp, J. M. Taylor, Tabletop experiments for quantum gravity: a user’s manual. Classical and Quantum Gravity 36 (3), 034001 (2019), doi:10.1088/1361-6382/aaf9ca,
https://doi.org/10.1088/1361-6382/aaf9ca.
5. A. Chou, et al., The Holometer: an instrument to probe Planckian quantum geometry. Classical
and Quantum Gravity 34 (6), 065005 (2017), doi:10.1088/1361-6382/aa5e5c, https://doi.
org/10.1088/1361-6382/aa5e5c.
6. The LIGO Scientific Collaboration, et al., Advanced LIGO. Classical and Quantum Gravity
32 (7), 074001 (2015), doi:10.1088/0264-9381/32/7/074001, https://doi.org/10.1088/
0264-9381/32/7/074001.
7. D. Deutsch, The Fabric of Reality (Allen Lane / Penguin Press, New York) (1997).
8. G. ’t Hooft, The Cellular Automaton Interpretation of Quantum Mechanics (Springer International Publishing, Cham), vol. 185 of Fundamental Theories of Physics, chap. 5.8 (2016),
doi:10.1007/978-3-319-41285-6, Open Access.
9. T. Palmer, Rational quantum mechanics: Testing quantum theory with quantum computers.
Proceedings of the National Academy of Sciences 123 (12), e2523350123 (2026), doi:10.1073/
pnas.2523350123, https://www.pnas.org/doi/abs/10.1073/pnas.2523350123.

## Page 12

10. S. Aaronson, Limits on Efficient Computation in the Physical World, Ph.D. thesis, University
of California, Berkeley (2004), https://arxiv.org/pdf/quant-ph/0412143.pdf.
11. NVIDIA, GeForce Graphics Cards Compare, https://www.nvidia.com/en-eu/geforce/
graphics-cards/compare/ (accessed 30 March 2026).
12. M. A. Nielsen, I. L. Chuang, Quantum Computation and Quantum Information: 10th Anniversary Edition (Cambridge University Press, Cambridge) (2010),
doi:10.1017/CBO9780511976667,

https://www.cambridge.org/core/product/

01E10196D0A682A6AEFFEA52D53BE9AE.
13. C. Chevignard, P.-A. Fouque, A. Schrottenloher, Reducing the Number of Qubits in Quantum
Factoring, in Advances in Cryptology – CRYPTO 2025, Y. Tauman Kalai, S. F. Kamara, Eds.
(Springer Nature Switzerland, Cham) (2025), pp. 384–415.
14. R. A. Beth, C. Lasky, The Brookhaven Alternating Gradient Synchrotron. Science
128 (3336), 1393–1401 (1958), doi:10.1126/science.128.3336.1393, https://doi.org/10.
1126/science.128.3336.1393.
15. Materials and methods are available as supplementary material.
16. S. Lloyd, Computational Capacity of the Universe. Physical Review Letters 88 (23),
237901 (2002), doi:10.1103/PhysRevLett.88.237901, https://link.aps.org/doi/10.
1103/PhysRevLett.88.237901.
17. L. Lamport, Time, clocks, and the ordering of events in a distributed system. Commun.
ACM 21 (7), 558–565 (1978), doi:10.1145/359545.359563, https://doi.org/10.1145/
359545.359563.
18. K. Zuse, Calculating space (Rechnender Raum), in A Computable Universe: Understanding
and Exploring Nature as Computation, H. Zenil, R. Penrose, Eds. (World Scientific), pp.
729–786 (2012), doi:10.1142/8306.
19. E. Fredkin, Discrete theoretical processes (DTP), in A Computable Universe: Understanding
and Exploring Nature as Computation, H. Zenil, R. Penrose, Eds. (World Scientific), pp.
365–380 (2012), doi:10.1142/8306.

## Page 13

20. A. K. Lenstra, H. W. Lenstra, M. S. Manasse, J. M. Pollard, The number field sieve, in
Proceedings of the Twenty-Second Annual ACM Symposium on Theory of Computing, STOC
’90 (Association for Computing Machinery, New York, NY, USA) (1990), pp. 564–572, doi:
10.1145/100216.100295, https://doi.org/10.1145/100216.100295.
21. D. Bluvstein, et al., Logical quantum processor based on reconfigurable atom arrays. Nature
626 (7997), 58–65 (2024), doi:10.1038/s41586-023-06927-3, https://doi.org/10.1038/
s41586-023-06927-3.
22. B. Hetényi, J. R. Wootton, Creating Entangled Logical Qubits in the Heavy-Hex Lattice with
Topological Codes. PRX Quantum 5 (4), 040334 (2024), doi:10.1103/PRXQuantum.5.040334,
https://link.aps.org/doi/10.1103/PRXQuantum.5.040334.
23. A. Paetznick, et al., Demonstration of logical qubits and repeated error correction with betterthan-physical error rates (2024), https://arxiv.org/pdf/2404.02280v3.pdf.
24. R. Acharya, et al., Quantum error correction below the surface code threshold. Nature
638 (8052), 920–926 (2025), doi:10.1038/s41586-024-08449-y, https://doi.org/10.
1038/s41586-024-08449-y.
25. C. Gidney, How to factor 2048 bit RSA integers with less than a million noisy qubits (2025),
https://arxiv.org/pdf/2505.15917.pdf.
26. H. Zhou, et al., Resource Analysis of Low-Overhead Transversal Architectures for Reconfigurable Atom Arrays, in Proceedings of the 52nd Annual International Symposium on
Computer Architecture, ISCA ’25 (Association for Computing Machinery, New York, NY,
USA) (2025), pp. 1432–1448, doi:10.1145/3695053.3731039, https://doi.org/10.1145/
3695053.3731039.
27. T. J. Yoder, et al., Tour de gross: A modular quantum computer based on bivariate bicycle
codes (2025), https://arxiv.org/pdf/2506.03094.pdf.
28. M. Cain, et al., Shor’s algorithm is possible with as few as 10,000 reconfigurable atomic qubits
(2026), https://arxiv.org/pdf/2603.28627.pdf.

## Page 14

29. J. Preskill, Quantum Computing in the NISQ era and beyond. Quantum 2, 79 (2018), doi:
10.22331/q-2018-08-06-79, https://doi.org/10.22331/q-2018-08-06-79.
30. S. Aaronson, A. Arkhipov, The computational complexity of linear optics, in Proceedings of
the Forty-Third Annual ACM Symposium on Theory of Computing, STOC ’11 (Association
for Computing Machinery, New York, NY, USA) (2011), pp. 333–342, doi:10.1145/1993636.
1993682, https://doi.org/10.1145/1993636.1993682.
31. F. Arute, et al., Quantum supremacy using a programmable superconducting processor. Nature 574 (7779), 505–510 (2019), doi:10.1038/s41586-019-1666-5, https://doi.org/10.
1038/s41586-019-1666-5.
32. H.-L. Liu, et al., Robust quantum computational advantage with programmable 3050-photon
Gaussian boson sampling (2025), https://arxiv.org/pdf/2508.09092v3.pdf.
33. Planck Collaboration, et al., Planck 2018 results. VI. Cosmological parameters. Astronomy &
Astrophysics 641, A6 (2020), doi:10.1051/0004-6361/201833910.
34. A. G. Riess, et al., A Comprehensive Measurement of the Local Value of the Hubble Constant
with 1 km s-1 Mpc-1 Uncertainty from the Hubble Space Telescope and the SH0ES Team.
The Astrophysical Journal Letters 934 (1), L7 (2022), doi:10.3847/2041-8213/ac5c5b, https:
//doi.org/10.3847/2041-8213/ac5c5b.

Supplementary materials
Materials and Methods
Supplementary Text
References (33-34)

## Page 15

Supplementary Materials for
Probing the Planck scale with quantum computation
Boaz Katz∗
Shlomi Kotler∗
∗ Corresponding author. Email: boaz.katz@weizmann.ac.il; shlomi.kotler@mail.huji.ac.il

This PDF file includes:
Materials and Methods
Supplementary Text

## Page 16

Materials and Methods
Detailed calculation of the cosmological pre-factors
We adopt a flat Lambda-CDM (cold dark matter) cosmological model for the expanding universe (33). For simplicity, we round the model parameters to one significant digit within their experimental uncertainty. This results in the following parameters: unitless density parameters Ω 𝑀 = 0.3
for matter, ΩΛ = 0.7 for dark energy and a Hubble constant value of 𝐻0 = 70 km s−1 Mpc−1 (33,34).
We neglect the contribution of radiation density (Ωrad ∼ 10−4 ). The scale factor 𝑎(𝑡) is given by,


Ω𝑀
𝑎(𝑡) =
ΩΛ

 1/3

sinh2/3 (𝑡/𝑡Λ ),

(S1)

√
where 𝑡Λ = 2/(3𝐻0 ΩΛ ). The age of the universe for these parameters is 𝑇𝑈 = 13.5 Gyr.
The resulting numerical constants appearing in Eq. 7 and Eq. 9 of the main text are,
𝑘 4𝑈 =
and,
𝑘 8𝑈 =

4𝜋𝐻08

∫ 𝑇𝑈

3𝑐6

0

𝐻04
𝑐3

𝑉4 (𝑇𝑈 ) = 0.13,

𝑑𝑡𝑉4 (𝑡)𝑎 3 (𝑡)𝑑 3 (𝑡, 𝑇𝑈 ) = 8.6 × 10−4 ,

(S2)

(S3)

respectively, where we used Eq. 5 and Eq. 6 of the main text.

Supplementary Text
Example of relativistic connectivity
A simple model of connectivity that is manifestly relativistic involves a distributed system of moving
computing elements (17) that perform calculations with proper time durations 𝜏 and broadcast their
results at the end of each calculation. Signals are transmitted to all directions at the speed of
light with no loss of information. Each element, in turn, integrates the signals it received to an
extent that depends on the connectivity. In this model, the data from a signal that was received
by an element may be used in many following calculations and each such usage is counted as an
additional operation.
The computational spacetime events are associated with the locations and times of broadcasts.
These events are equally spaced along the worldlines of the computing elements with equal proper

## Page 17

time spacing 𝜏. The output of a computational event 𝐴1 by element 𝐴 will be considered as an input
for an event 𝐵1 by element 𝐵 if the broadcast from 𝐴1 was received by 𝐵 prior to 𝐵1 and integrated
in the calculation that lead to 𝐵1 . Full connectivity is achieved if elements use in each calculation
all previous signals they received. This implies that each computational event uses as direct inputs
the results of all previous events in its past light cone as described in the main text.
A simple choice for a limited connectivity within this model is to include in a computational
event only signals that were received by the computing element during the time interval 𝜏 that
preceded the event. This significantly reduces the memory requirements of the model. We next
estimate the resulting number of operations of a computer for this choice for the two cases of
resource accessibility considered in the main text: first, where communication is limited to the lab,
and second, where it is unlimited and the lab can access all previous calculations in the observable
universe.
For communications that are limited to the lab, the duration of the entire calculation is typically
much larger than the light-crossing time of the computer. In this case, every computing element
will receive one broadcast per time step from all the other 𝑉3 /𝑙 3 elements. The resulting number of
operations is therefore,


𝑉3
𝑁ops = 3
𝑙

2

𝑇
.
𝜏

(S4)

In the Planck limit of 𝑙 = 𝑙 𝑃 and 𝜏 = 𝑙/𝑐 = 𝑡 𝑃 , this corresponds to 882 logical qubits. Even for this
limited connectivity, the resulting threshold is much higher compared to the laboratory bound of
525 that was obtained in the main text by ignoring the impact of communication.
We next estimate the number of operations obtained within this model if the communication
spans the observable universe. As in the main text, we assume that the universe is filled with
co-moving computing elements that are spaced by 𝑙, with new elements constantly being added as
the universe expands. The rate density of computational events is thus C = 1/(𝑙 3 𝜏) everywhere.
The number of accumulated signals that arrive at a given element up to time 𝑡 is given by C𝑉4 (𝑡).
The rate at which the signals arrive is thus C𝑉¤4 , where 𝑉¤4 = 𝑑𝑉4 (𝑡)/𝑑𝑡, so that each calculation
integrates C𝑉¤4 𝜏 inputs. The total amount of communication operations that can influence an output
today is therefore,
4𝜋C
𝑁ops =
3

∫ 𝑇𝑈

C𝑉¤4 𝜏 𝑎(𝑡) 3 𝑑 3 (𝑡, 𝑇𝑈 )𝑑𝑡.

0

S3

(S5)

## Page 18

An explicit expression for 𝑉¤4 can be obtained using equations Eq. 5 and Eq. 6 of the main text,
∫ 𝑡2
𝑎(𝑡1 )
¤
𝑉4 (𝑡2 ) = 4𝜋
𝑐𝑑𝑡1 .
(S6)
𝑎 2 (𝑡 1 )𝑑 2 (𝑡 1 , 𝑡2 )
𝑎(𝑡2 )
0
The resulting arrival rate of signals at 𝑡 2 , C𝑉¤4 (𝑡2 ), takes the form of a sum of contributions from
different distances, 𝑎(𝑡1 )𝑑 (𝑡 1 , 𝑡2 ), and their corresponding emission times, 𝑡1 . The broadcast rate
from each of these spherical shells is C · 4𝜋𝑎 2 (𝑡1 )𝑑 2 (𝑡 1 , 𝑡2 )𝑐𝑑𝑡 1 and is red-shifted by 𝑎(𝑡1 )/𝑎(𝑡2 ).
Setting 𝜏 at the causal limit, 𝜏 = 𝑙/𝑐, the resulting total number of operations using equations
Eq. S5 and Eq. S6 can be expressed as,

𝑁ops = 𝑘 7𝑈
where,
𝑘 7𝑈 =

4𝜋𝐻07

∫ 𝑇𝑈

3𝑐6

0

𝑐/𝐻0
𝑙

7
,

(S7)

𝑎 3 (𝑡)𝑑 3 (𝑡, 𝑇𝑈 )𝑉¤4 (𝑡)𝑑𝑡,

(S8)

is a third dimensionless parameter that depends on the cosmological parameters and is approximately equal to 𝑘 7𝑈 = 6.2 × 10−3 for the choice of values described in (15).
