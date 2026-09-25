# Ring with h0z = hz and g_x/sqrt(N) coupling: exact-sector numerics (running record)

> Source: Orchestrator computations in the go/no-go session, 2026-09-24; scripts dicke.py, gscale.py, fine.py, ksec.py, scan.py, chi2.py, dedup.py (scratchpad gonogo/h0zhz/). Logs pasted verbatim below.
> Collected: 2026-09-24
> Published: 2026-09-24

## Model (user-specified, SPEC positive convention, Pauli matrices, qubit first, periodic ring)

H = h0z s0^z + hz sum_i s_i^z + J sum_i s_i^z s_{i+1}^z + (gx/sqrt(N)) s0^x sum_i s_i^x,   h0z = hz = h = 1.

Zero: h0x, h0y, hx, hy, Jxx, Jyy, gy, gz. Conserved: parity Z0 prod Z_i (so z is an exact fixed point of the axis map, roots come in pairs lambda, -lambda), detector translation, reflection. Outcome-0 forward pencil (U10 + lambda U11) D = 0, z output basis, single times T (no pooling), unit root weights. tau = gx T. S_Born-type weak ratio R(theta) = h0/(h0+h1) with outcome 1 = antipode.

Methods: J = 0 by exact collective-spin (Dicke) sectors with multiplicities, up to N = 400 (sectors of total weight < 1e-7 dropped); J != 0 by exact detector-momentum sectors (ksec.py), cross-checked against dense bornkit roots: max sorted theta difference 9.285627822208653e-14 (N = 5) and 6.583622536027178e-12 (N = 8) at T = 23, J = 0.37, g = 0.1.

## J = 0 (non-interacting detector control), Dicke sectors
```
{'h': 1.0, 'gx': 0.1} N 10 T2:med0.110/q90 0.33/S0.08/cov12/sth0.000/Et2 0.00783/az2 0.84 T5:med0.155/q90 0.50/S0.15/cov22/sth0.000/Et2 0.018/az2 0.64 T10:med0.290/q90 1.43/S-0.11/cov24/sth0.041/Et2 0.575/az2 0.87 T20:med0.519/q90 2.99/S0.04/cov26/sth0.283/Et2 24.7/az2 0.56 T50:med0.398/q90 0.70/S0.17/cov28/sth0.000/Et2 0.0537/az2 0.53 T100:med0.647/q90 2.14/S0.02/cov28/sth0.234/Et2 3.42/az2 0.18 T300:med0.233/q90 1.60/S-0.18/cov24/sth0.156/Et2 3.05/az2 0.03
{'h': 1.0, 'gx': 0.1} N 40 T2:med0.110/q90 0.28/S0.36/cov46/sth0.000/Et2 0.00784/az2 0.90 T5:med0.157/q90 0.40/S-0.25/cov84/sth0.000/Et2 0.0185/az2 0.86 T10:med0.292/q90 1.02/S-0.60/cov94/sth0.043/Et2 2.16/az2 0.89 T20:med0.479/q90 2.49/S-0.14/cov88/sth0.175/Et2 2.32/az2 0.49 T50:med0.309/q90 1.55/S-0.30/cov84/sth0.091/Et2 0.56/az2 0.43 T100:med0.419/q90 0.79/S0.17/cov82/sth0.003/Et2 0.0806/az2 0.38 T300:med0.259/q90 0.92/S0.28/cov84/sth0.002/Et2 0.109/az2 0.43
{'h': 1.0, 'gx': 0.1} N 160 T2:med0.110/q90 0.28/S0.50/cov70/sth0.000/Et2 0.00784/az2 0.92 T5:med0.160/q90 0.44/S0.16/cov100/sth0.000/Et2 0.0193/az2 0.90 T10:med0.301/q90 1.15/S0.10/cov100/sth0.053/Et2 2.91/az2 0.90 T20:med0.540/q90 2.21/S0.07/cov100/sth0.183/Et2 6.03/az2 0.47 T50:med0.407/q90 1.28/S-0.11/cov100/sth0.071/Et2 0.518/az2 0.29 T100:med0.359/q90 1.40/S0.20/cov100/sth0.067/Et2 0.239/az2 0.33 T300:med0.379/q90 1.09/S0.02/cov100/sth0.013/Et2 0.149/az2 0.03
{'h': 1.0, 'gx': 0.1} N 400 T2:med0.122/q90 0.28/S0.50/cov70/sth0.000/Et2 0.00789/az2 0.94 T5:med0.195/q90 0.48/S0.23/cov100/sth0.000/Et2 0.0244/az2 0.77 T10:med0.379/q90 1.24/S0.60/cov100/sth0.057/Et2 3.51/az2 0.77 T20:med0.718/q90 2.23/S0.15/cov100/sth0.285/Et2 8.68/az2 0.41 T50:med0.437/q90 1.35/S0.33/cov100/sth0.073/Et2 2.8/az2 0.26 T100:med0.409/q90 1.30/S0.27/cov100/sth0.061/Et2 3.47/az2 0.23 T300:med0.454/q90 1.11/S0.15/cov100/sth0.053/Et2 0.907/az2 0.08
{'h': 1.0, 'gx': 0.1, 'gy': 0.05, 'gz': 0.06} N 10 T2:med0.096/q90 0.29/S0.08/cov12/sth0.000/Et2 0.00585/az2 0.80 T5:med0.136/q90 0.43/S0.15/cov22/sth0.000/Et2 0.0138/az2 0.61 T10:med0.254/q90 0.80/S0.23/cov28/sth0.000/Et2 0.0576/az2 0.37 T20:med0.189/q90 0.44/S0.19/cov28/sth0.000/Et2 0.0228/az2 0.14 T50:med0.124/q90 0.42/S0.13/cov24/sth0.000/Et2 0.0241/az2 0.21 T100:med0.245/q90 0.41/S0.18/cov26/sth0.000/Et2 0.0172/az2 0.21 T300:med0.191/q90 0.28/S0.16/cov24/sth0.000/Et2 0.0133/az2 0.12
{'h': 1.0, 'gx': 0.1, 'gy': 0.05, 'gz': 0.06} N 40 T2:med0.096/q90 0.24/S0.43/cov52/sth0.000/Et2 0.00585/az2 0.89 T5:med0.138/q90 0.35/S0.27/cov84/sth0.000/Et2 0.0146/az2 0.84 T10:med0.269/q90 0.71/S0.34/cov68/sth0.000/Et2 0.0696/az2 0.51 T20:med0.188/q90 0.51/S0.33/cov78/sth0.003/Et2 0.0304/az2 0.19 T50:med0.160/q90 0.44/S0.11/cov72/sth0.020/Et2 0.0562/az2 0.27 T100:med0.175/q90 0.47/S0.25/cov66/sth0.006/Et2 0.0388/az2 0.12 T300:med0.253/q90 0.54/S0.14/cov58/sth0.003/Et2 0.176/az2 0.27
{'h': 1.0, 'gx': 0.1, 'gy': 0.05, 'gz': 0.06} N 160 T2:med0.096/q90 0.24/S0.50/cov68/sth0.000/Et2 0.00594/az2 0.92 T5:med0.163/q90 0.47/S0.42/cov100/sth0.001/Et2 0.0237/az2 0.75 T10:med0.323/q90 1.00/S0.00/cov100/sth0.004/Et2 0.0947/az2 0.60 T20:med0.213/q90 0.50/S0.06/cov100/sth0.002/Et2 0.0397/az2 0.07 T50:med0.164/q90 0.59/S0.01/cov96/sth0.003/Et2 0.0861/az2 0.13 T100:med0.188/q90 0.61/S-0.10/cov98/sth0.007/Et2 0.124/az2 0.11 T300:med0.167/q90 0.43/S-0.17/cov84/sth0.020/Et2 0.153/az2 0.26
{'h': 1.0, 'gx': 0.1, 'gy': 0.05, 'gz': 0.06} N 400 T2:med0.112/q90 0.27/S0.45/cov78/sth0.000/Et2 0.00728/az2 0.79 T5:med0.186/q90 0.70/S0.37/cov100/sth0.003/Et2 0.0502/az2 0.51 T10:med0.419/q90 1.45/S0.30/cov100/sth0.065/Et2 0.224/az2 0.40 T20:med0.292/q90 0.74/S0.47/cov100/sth0.009/Et2 0.0768/az2 0.06 T50:med0.208/q90 0.86/S0.12/cov100/sth0.017/Et2 0.108/az2 0.10 T100:med0.247/q90 0.76/S0.04/cov100/sth0.025/Et2 0.123/az2 0.08 T300:med0.230/q90 0.64/S-0.08/cov94/sth0.025/Et2 0.133/az2 0.18
```

### g -> 0 at fixed tau, N = 160 (6-bin ratio)
```
(g-scaling table: see gscale output in session; rerun pending)

### 18-bin ratio vs N, g, tau (fine.py)
```
N80_g0.0125_tau0.5 E=0.246 R_north= [1.0, 1.0, 1.0, 1.0, 1.0, 0.999, 0.995, 0.933, 0.901]
N80_g0.0125_tau1 E=0.156 R_north= [0.996, 0.993, 0.979, 0.975, 0.641, 0.685, 0.699, 0.906, 0.695]
N80_g0.0125_tau2 E=0.269 R_north= [1.0, 1.0, 0.799, 0.703, 1.0, 0.78, 1.0, 1.0, 0.147]
N80_g0.0125_tau5 E=0.445 R_north= [0.98, 1.0, 1.0, 1.0, 1.0, 0.0, 0.134, 0.743, 0.0]
N80_g0.025_tau0.5 E=0.188 R_north= [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.992, 0.905, 0.523]
N80_g0.025_tau1 E=0.089 R_north= [0.993, 1.0, 0.981, 0.96, 0.854, 0.991, 0.65, 0.557, 0.575]
N80_g0.025_tau2 E=0.324 R_north= [1.0, 0.856, 0.841, 1.0, 0.595, 1.0, 1.0, 1.0, 0.001]
N80_g0.025_tau5 E=0.231 R_north= [0.978, 1.0, 1.0, 1.0, 0.645, 0.977, 0.988, 1.0, 0.348]
N80_g0.05_tau0.5 E=0.208 R_north= [1.0, 1.0, 1.0, 1.0, 1.0, 0.999, 0.992, 0.973, 0.619]
N80_g0.05_tau1 E=0.179 R_north= [0.991, 0.993, 0.99, 0.922, 0.697, 0.856, 0.896, 0.791, 0.218]
N80_g0.05_tau2 E=0.154 R_north= [1.0, 0.847, 0.91, 0.665, 1.0, 0.99, 0.77, 0.532, 0.355]
N80_g0.05_tau5 E=0.284 R_north= [0.968, 1.0, 1.0, 0.628, 0.918, 1.0, 0.944, 0.999, 0.986]
N80_g0.1_tau0.5 E=0.204 R_north= [1.0, 1.0, 1.0, 1.0, 1.0, 0.998, 0.987, 0.931, 0.704]
N80_g0.1_tau1 E=0.212 R_north= [0.99, 0.989, 0.955, 0.967, 0.927, 0.94, 0.301, 0.92, 0.545]
N80_g0.1_tau2 E=0.216 R_north= [0.941, 0.819, 0.851, 1.0, 0.702, 1.0, 0.437, 0.552, 0.191]
N80_g0.1_tau5 E=0.303 R_north= [0.94, 1.0, 0.919, 0.989, 0.98, 0.447, 1.0, 1.0, 1.0]
N160_g0.0125_tau0.5 E=0.237 R_north= [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.999, 0.985, 0.803]
N160_g0.0125_tau1 E=0.187 R_north= [0.996, 0.994, 0.981, 0.932, 0.932, 0.882, 0.851, 0.365, 0.221]
N160_g0.0125_tau2 E=0.212 R_north= [1.0, 0.916, 0.796, 0.859, 1.0, 1.0, 0.81, 0.776, 0.139]
N160_g0.0125_tau5 E=0.369 R_north= [1.0, 1.0, 1.0, 1.0, 0.989, 1.0, 1.0, 0.023, 0.002]
N160_g0.025_tau0.5 E=0.234 R_north= [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.997, 0.978, 0.796]
N160_g0.025_tau1 E=0.078 R_north= [0.994, 0.993, 0.969, 0.995, 0.897, 0.908, 0.742, 0.728, 0.459]
N160_g0.025_tau2 E=0.160 R_north= [1.0, 0.804, 0.877, 1.0, 0.884, 1.0, 0.872, 0.672, 0.281]
N160_g0.025_tau5 E=0.281 R_north= [1.0, 1.0, 1.0, 0.994, 1.0, 0.715, 0.398, 0.999, 1.0]
N160_g0.05_tau0.5 E=0.216 R_north= [1.0, 1.0, 1.0, 1.0, 1.0, 0.999, 0.994, 0.944, 0.749]
N160_g0.05_tau1 E=0.063 R_north= [0.993, 0.988, 0.985, 0.962, 0.939, 0.839, 0.751, 0.658, 0.651]
N160_g0.05_tau2 E=0.201 R_north= [1.0, 0.77, 0.933, 0.911, 0.911, 0.724, 0.697, 0.726, 0.997]
N160_g0.05_tau5 E=0.147 R_north= [1.0, 1.0, 0.997, 0.996, 0.613, 0.743, 0.999, 0.594, 0.533]
N160_g0.1_tau0.5 E=0.197 R_north= [1.0, 1.0, 1.0, 1.0, 1.0, 0.998, 0.984, 0.945, 0.594]
N160_g0.1_tau1 E=0.064 R_north= [0.987, 0.984, 0.976, 0.96, 0.919, 0.892, 0.805, 0.659, 0.517]
N160_g0.1_tau2 E=0.135 R_north= [0.954, 0.882, 0.873, 0.834, 0.73, 0.642, 0.931, 0.491, 0.469]
N160_g0.1_tau5 E=0.174 R_north= [1.0, 1.0, 0.995, 0.851, 0.841, 0.579, 1.0, 0.842, 0.414]
N320_g0.0125_tau0.5 E=0.246 R_north= [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.997, 0.988, 0.847]
N320_g0.0125_tau1 E=0.122 R_north= [0.997, 0.991, 0.901, 0.969, 0.728, 0.926, 0.818, 0.844, 0.575]
N320_g0.0125_tau2 E=0.266 R_north= [0.986, 0.928, 0.938, 0.916, 0.893, 0.21, 0.374, 0.797, 0.54]
N320_g0.0125_tau5 E=0.160 R_north= [1.0, 1.0, 0.952, 0.883, 0.887, 0.963, 0.871, 0.603, 0.854]
N320_g0.025_tau0.5 E=0.231 R_north= [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.998, 0.973, 0.787]
N320_g0.025_tau1 E=0.122 R_north= [0.995, 0.99, 0.955, 0.967, 0.858, 0.871, 0.865, 0.764, 0.74]
N320_g0.025_tau2 E=0.217 R_north= [0.942, 0.972, 0.898, 0.957, 0.644, 0.412, 0.488, 0.761, 0.786]
N320_g0.025_tau5 E=0.190 R_north= [1.0, 0.998, 0.933, 0.934, 0.764, 0.966, 0.988, 0.93, 0.673]
N320_g0.05_tau0.5 E=0.219 R_north= [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.995, 0.965, 0.734]
N320_g0.05_tau1 E=0.057 R_north= [0.993, 0.987, 0.975, 0.953, 0.911, 0.865, 0.811, 0.663, 0.542]
N320_g0.05_tau2 E=0.173 R_north= [0.915, 1.0, 0.897, 0.796, 0.768, 0.812, 0.501, 0.445, 0.833]
N320_g0.05_tau5 E=0.170 R_north= [1.0, 0.966, 0.977, 0.895, 0.954, 1.0, 0.987, 0.516, 0.344]
N320_g0.1_tau0.5 E=0.210 R_north= [1.0, 1.0, 1.0, 1.0, 1.0, 0.999, 0.989, 0.939, 0.722]
N320_g0.1_tau1 E=0.072 R_north= [0.987, 0.98, 0.977, 0.96, 0.924, 0.86, 0.774, 0.735, 0.465]
N320_g0.1_tau2 E=0.082 R_north= [0.89, 0.92, 0.894, 0.774, 0.791, 0.677, 0.626, 0.563, 0.517]
N320_g0.1_tau5 E=0.078 R_north= [0.998, 0.953, 0.964, 0.921, 0.995, 0.855, 0.706, 0.611, 0.671]
```

## J != 0, momentum sectors, g = 0.1 (scan.py; E = 18-bin sin-weighted RMS ratio error on occupied bins, floorE = same-count i.i.d. exact-Born value, cal = E tan^2(theta/2) which Born sets to 1, az = |<e^{2i phi}>|)
```
J= 0.37 g=0.1 N= 8 floorE=0.071 (0s) | t0.5:med0.12 s0.00 E0.065 cov8 az0.76 cal0.0084 | t1:med0.23 s0.00 E0.277 cov14 az0.84 cal0.043 | t2:med0.34 s0.13 E0.231 cov18 az0.47 cal2.1 | t5:med0.26 s0.06 E0.288 cov14 az0.03 cal0.69 | t10:med0.26 s0.05 E0.244 cov18 az0.10 cal0.24 | t30:med0.29 s0.05 E0.296 cov16 az0.10 cal0.19 | t100:med0.35 s0.05 E0.126 cov18 az0.14 cal2.2
J= 0.37 g=0.1 N=10 floorE=0.034 (1s) | t0.5:med0.13 s0.00 E0.065 cov8 az0.88 cal0.0084 | t1:med0.20 s0.00 E0.242 cov16 az0.90 cal0.044 | t2:med0.33 s0.15 E0.167 cov18 az0.50 cal1.4 | t5:med0.32 s0.04 E0.246 cov18 az0.12 cal0.47 | t10:med0.31 s0.02 E0.160 cov18 az0.06 cal0.12 | t30:med0.30 s0.03 E0.167 cov18 az0.04 cal0.17 | t100:med0.32 s0.03 E0.207 cov18 az0.04 cal0.46
J= 0.37 g=0.1 N=12 floorE=0.018 (28s) | t0.5:med0.12 s0.00 E0.101 cov10 az0.90 cal0.0084 | t1:med0.22 s0.00 E0.195 cov18 az0.92 cal0.046 | t2:med0.35 s0.13 E0.123 cov18 az0.51 cal4.2 | t5:med0.32 s0.06 E0.106 cov18 az0.13 cal0.97 | t10:med0.33 s0.05 E0.049 cov18 az0.05 cal0.41 | t30:med0.32 s0.06 E0.079 cov18 az0.04 cal1.1 | t100:med0.33 s0.04 E0.093 cov18 az0.02 cal0.49
J= 2.50 g=0.1 N= 8 floorE=0.071 (0s) | t0.5:med0.11 s0.00 E0.036 cov6 az0.71 cal0.0077 | t1:med0.20 s0.00 E0.242 cov14 az0.69 cal0.041 | t2:med0.33 s0.12 E0.217 cov18 az0.61 cal2.4 | t5:med0.25 s0.09 E0.313 cov18 az0.05 cal0.66 | t10:med0.23 s0.04 E0.195 cov18 az0.10 cal0.26 | t30:med0.23 s0.05 E0.349 cov16 az0.09 cal0.19 | t100:med0.27 s0.08 E0.208 cov18 az0.08 cal58
J= 2.50 g=0.1 N=10 floorE=0.034 (1s) | t0.5:med0.12 s0.00 E0.036 cov6 az0.83 cal0.0077 | t1:med0.22 s0.00 E0.287 cov16 az0.83 cal0.042 | t2:med0.32 s0.14 E0.191 cov18 az0.63 cal2 | t5:med0.27 s0.04 E0.201 cov18 az0.12 cal0.62 | t10:med0.29 s0.01 E0.251 cov18 az0.04 cal0.11 | t30:med0.23 s0.02 E0.136 cov18 az0.03 cal0.14 | t100:med0.28 s0.04 E0.114 cov18 az0.07 cal4.9
J= 2.50 g=0.1 N=12 floorE=0.018 (28s) | t0.5:med0.12 s0.00 E0.065 cov8 az0.84 cal0.0077 | t1:med0.22 s0.00 E0.274 cov18 az0.85 cal0.044 | t2:med0.35 s0.14 E0.105 cov18 az0.67 cal6 | t5:med0.27 s0.05 E0.081 cov18 az0.13 cal1.8 | t10:med0.29 s0.06 E0.075 cov18 az0.06 cal0.99 | t30:med0.27 s0.05 E0.080 cov18 az0.04 cal1.1 | t100:med0.29 s0.04 E0.106 cov18 az0.03 cal0.61
```

## Binomial chi-square of the north-half ratio (9 bins), raw and with exactly degenerate roots (parity pairs, k <-> -k sectors) counted once
```
J=0.37 g=0.1 N=10 tau=10.0: chi2_north=47.0 / dof 9  R=[1.    1.    1.    1.    0.941 1.    0.938 0.727 0.75 ]  counts=[258 296 202 114  68  16  32  22  16]
J=0.37 g=0.1 N=10 tau=30.0: chi2_north=42.5 / dof 9  R=[1.    1.    0.976 1.    1.    0.867 0.692 1.    0.5  ]  counts=[272 342 170  88  50  30  26  26  20]
J=0.37 g=0.1 N=10 tau=100.0: chi2_north=34.6 / dof 9  R=[1.    0.993 0.963 1.    0.933 0.909 0.778 0.917 0.167]  counts=[256 306 214  90  60  44  18  24  12]
J=0.37 g=0.1 N=12 tau=10.0: chi2_north=46.7 / dof 9  R=[1.    0.995 0.978 0.957 0.852 0.904 0.727 0.619 0.521]  counts=[ 948 1232  724  422  270  146  132  126   96]
J=0.37 g=0.1 N=12 tau=30.0: chi2_north=60.3 / dof 9  R=[0.993 0.994 0.959 0.971 0.891 0.782 0.603 0.776 0.585]  counts=[ 900 1324  734  412  220  156  146   98  106]
J=0.37 g=0.1 N=12 tau=100.0: chi2_north=71.0 / dof 9  R=[1.    0.989 0.99  0.961 0.911 0.807 0.855 0.792 0.531]  counts=[ 910 1270  780  408  248  166  110  106   98]
Born north bins [0.998 0.983 0.953 0.91  0.854 0.787 0.711 0.629 0.544]
th_J0.37_g0.1_N10_tau10.0.npy    n=  1024 unique=   288 ratio=3.56 chi2=  47.0 chi2_unique=  12.2/9  E_unique=0.148
th_J0.37_g0.1_N10_tau100.0.npy   n=  1024 unique=   287 ratio=3.57 chi2=  34.6 chi2_unique=   8.5/9  E_unique=0.168
th_J0.37_g0.1_N10_tau30.0.npy    n=  1024 unique=   287 ratio=3.57 chi2=  42.5 chi2_unique=  13.0/9  E_unique=0.174
th_J0.37_g0.1_N12_tau10.0.npy    n=  4096 unique=  1196 ratio=3.42 chi2=  46.7 chi2_unique=  15.1/9  E_unique=0.053
th_J0.37_g0.1_N12_tau100.0.npy   n=  4096 unique=  1183 ratio=3.46 chi2=  71.0 chi2_unique=  19.2/9  E_unique=0.090
th_J0.37_g0.1_N12_tau30.0.npy    n=  4096 unique=  1189 ratio=3.44 chi2=  60.3 chi2_unique=  26.2/9  E_unique=0.061
```

## g-variation at J = 0.37 (chi2.py, then dedup.py over all saved theta sets)
```
J=0.37 g=0.05 N=10 tau=10.0: chi2_north=33.4 / dof 9  R=[1.    1.    1.    1.    1.    0.857 1.    0.8   0.333]  counts=[376 338 168  52  36  28  10  10   6]
J=0.37 g=0.05 N=10 tau=30.0: chi2_north=42.3 / dof 9  R=[1.    1.    1.    1.    0.882 1.    1.    0.6   1.   ]  counts=[400 352 116  60  34  14  28  10  10]
J=0.37 g=0.05 N=10 tau=100.0: chi2_north=20.1 / dof 9  R=[0.995 0.994 0.961 1.    0.895 0.9   0.667 0.667 1.   ]  counts=[364 348 154  76  38  20  12   6   6]
J=0.37 g=0.05 N=12 tau=10.0: chi2_north=74.2 / dof 9  R=[1.    0.994 0.974 0.971 0.738 0.902 0.891 0.75  0.595]  counts=[1388 1336  610  272  160   82   92   72   84]
J=0.37 g=0.05 N=12 tau=30.0: chi2_north=43.0 / dof 9  R=[0.996 0.997 0.97  0.884 0.9   0.848 0.761 0.705 0.357]  counts=[1514 1310  526  276  140   66   92   88   84]
J=0.37 g=0.05 N=12 tau=100.0: chi2_north=69.7 / dof 9  R=[0.999 0.997 0.983 0.969 0.861 0.918 0.818 0.76  0.759]  counts=[1420 1378  600  260  144   98   88   50   58]
Born north bins [0.998 0.983 0.953 0.91  0.854 0.787 0.711 0.629 0.544]
J=0.37 g=0.2 N=10 tau=10.0: chi2_north=74.0 / dof 9  R=[1.    1.    0.992 0.985 1.    0.875 0.828 0.818 1.   ]  counts=[164 222 244 134  98  32  58  44  28]
J=0.37 g=0.2 N=10 tau=30.0: chi2_north=50.2 / dof 9  R=[1.    0.984 1.    0.967 0.974 0.974 0.81  0.773 0.333]  counts=[168 254 222 122  78  76  42  44  18]
J=0.37 g=0.2 N=10 tau=100.0: chi2_north=32.5 / dof 9  R=[1.    1.    0.982 0.978 0.829 0.81  0.889 0.667 0.333]  counts=[158 244 222 180  82  42  36  18  42]
J=0.37 g=0.2 N=12 tau=10.0: chi2_north=67.6 / dof 9  R=[1.    0.996 0.983 0.963 0.87  0.85  0.714 0.723 0.652]  counts=[582 948 848 538 368 294 210 130 178]
J=0.37 g=0.2 N=12 tau=30.0: chi2_north=56.6 / dof 9  R=[0.996 0.991 0.991 0.946 0.897 0.806 0.772 0.655 0.625]  counts=[538 910 870 590 390 268 202 168 160]
J=0.37 g=0.2 N=12 tau=100.0: chi2_north=82.4 / dof 9  R=[1.    0.996 0.973 0.966 0.891 0.924 0.775 0.702 0.615]  counts=[534 930 882 582 384 238 222 168 156]
Born north bins [0.998 0.983 0.953 0.91  0.854 0.787 0.711 0.629 0.544]
th_J0.37_g0.05_N10_tau10.0.npy   n=  1024 unique=   296 ratio=3.46 chi2=  33.4 chi2_unique=   9.3/9  E_unique=0.140
th_J0.37_g0.05_N10_tau100.0.npy  n=  1024 unique=   291 ratio=3.52 chi2=  20.1 chi2_unique=   8.4/9  E_unique=0.196
th_J0.37_g0.05_N10_tau30.0.npy   n=  1024 unique=   295 ratio=3.47 chi2=  42.3 chi2_unique=  12.8/9  E_unique=0.240
th_J0.37_g0.05_N12_tau10.0.npy   n=  4096 unique=  1694 ratio=2.42 chi2=  74.2 chi2_unique=  32.9/9  E_unique=0.118
th_J0.37_g0.05_N12_tau100.0.npy  n=  4096 unique=  1558 ratio=2.63 chi2=  69.7 chi2_unique=  23.5/9  E_unique=0.124
th_J0.37_g0.05_N12_tau30.0.npy   n=  4096 unique=  1611 ratio=2.54 chi2=  43.0 chi2_unique=  19.6/9  E_unique=0.091
th_J0.37_g0.1_N10_tau10.0.npy    n=  1024 unique=   288 ratio=3.56 chi2=  47.0 chi2_unique=  12.2/9  E_unique=0.148
th_J0.37_g0.1_N10_tau100.0.npy   n=  1024 unique=   287 ratio=3.57 chi2=  34.6 chi2_unique=   8.5/9  E_unique=0.168
th_J0.37_g0.1_N10_tau30.0.npy    n=  1024 unique=   287 ratio=3.57 chi2=  42.5 chi2_unique=  13.0/9  E_unique=0.174
th_J0.37_g0.1_N12_tau10.0.npy    n=  4096 unique=  1196 ratio=3.42 chi2=  46.7 chi2_unique=  15.1/9  E_unique=0.053
th_J0.37_g0.1_N12_tau100.0.npy   n=  4096 unique=  1183 ratio=3.46 chi2=  71.0 chi2_unique=  19.2/9  E_unique=0.090
th_J0.37_g0.1_N12_tau30.0.npy    n=  4096 unique=  1189 ratio=3.44 chi2=  60.3 chi2_unique=  26.2/9  E_unique=0.061
th_J0.37_g0.2_N10_tau10.0.npy    n=  1024 unique=   288 ratio=3.56 chi2=  74.0 chi2_unique=  19.3/9  E_unique=0.215
th_J0.37_g0.2_N10_tau100.0.npy   n=  1024 unique=   287 ratio=3.57 chi2=  32.5 chi2_unique=   7.6/9  E_unique=0.119
th_J0.37_g0.2_N10_tau30.0.npy    n=  1024 unique=   287 ratio=3.57 chi2=  50.2 chi2_unique=  12.6/9  E_unique=0.115
th_J0.37_g0.2_N12_tau10.0.npy    n=  4096 unique=  1157 ratio=3.54 chi2=  67.6 chi2_unique=  18.0/9  E_unique=0.062
th_J0.37_g0.2_N12_tau100.0.npy   n=  4096 unique=  1156 ratio=3.54 chi2=  82.4 chi2_unique=  24.2/9  E_unique=0.075
th_J0.37_g0.2_N12_tau30.0.npy    n=  4096 unique=  1156 ratio=3.54 chi2=  56.6 chi2_unique=  17.0/9  E_unique=0.052
```

## Repository sector worker (scripts/ring_h0z_eq_hz_sector_roots.py, commits abab90e / 97565bf / 769d569)
Validated against the independent momentum-sector solver at N = 8, T = 23: max |diff| = 2.654654274181212e-12; focused test tests/test_ring_h0z_eq_hz_sector_roots.py 1 passed (N = 5, dense outcome-0 pencil).

### Scores (analyze_sectors.py; unique = each sector once, parity copies once; chi2u = north-half binomial chi-square of unique roots)
```
N=14 sectors= 8 tau= 10.0 T=    100 n= 16384 uniq=  5625 med=0.339 south=0.049 cov=18 E=0.066 chi2u=121.1/9 cal=0.6 R_N=[0.996, 0.993, 0.985, 0.964, 0.952, 0.874, 0.769, 0.684, 0.484]
N=14 sectors= 8 tau= 30.0 T=    300 n= 16384 uniq=  5546 med=0.332 south=0.046 cov=18 E=0.055 chi2u=101.5/9 cal=0.382 R_N=[0.999, 0.998, 0.983, 0.962, 0.93, 0.879, 0.728, 0.676, 0.586]
N=14 sectors= 8 tau=100.0 T=   1000 n= 16384 uniq=  5585 med=0.332 south=0.037 cov=18 E=0.079 chi2u=155.3/9 cal=0.22 R_N=[1.0, 0.999, 0.991, 0.981, 0.945, 0.899, 0.832, 0.647, 0.497]
N=10 sectors= 6 tau=  1.0 T=    100 n=  1024 uniq=   292 med=0.195 south=0.002 cov=16 E=0.220 chi2u=10.0/8 cal=0.0417 R_N=[1.0, 1.0, 1.0, 1.0, 1.0, 1.0, None, 1.0, 0.75]
N=10 sectors= 6 tau=  3.0 T=    300 n=  1024 uniq=   303 med=0.343 south=0.100 cov=18 E=0.046 chi2u=103.3/9 cal=7.07 R_N=[0.958, 0.938, 0.941, 0.925, 0.879, 0.885, 0.75, 0.588, 0.56]
N=10 sectors= 6 tau= 10.0 T=   1000 n=  1024 uniq=   293 med=0.272 south=0.012 cov=18 E=0.251 chi2u=13.3/9 cal=0.11 R_N=[1.0, 1.0, 1.0, 1.0, 0.895, 0.875, 0.8, 1.0, 1.0]
N=10 sectors= 6 tau= 30.0 T=   3000 n=  1024 uniq=   308 med=0.201 south=0.023 cov=18 E=0.162 chi2u=10.3/9 cal=0.13 R_N=[1.0, 1.0, 1.0, 0.931, 1.0, 0.9, 1.0, 0.8, 0.4]
N=12 sectors= 7 tau=  1.0 T=    100 n=  4096 uniq=  1165 med=0.224 south=0.001 cov=18 E=0.274 chi2u=46.3/9 cal=0.0433 R_N=[1.0, 1.0, 1.0, 1.0, 1.0, 0.97, 0.926, 1.0, 1.0]
N=12 sectors= 7 tau=  3.0 T=    300 n=  4096 uniq=  1423 med=0.376 south=0.100 cov=18 E=0.045 chi2u=98.2/9 cal=8.95 R_N=[0.97, 0.952, 0.914, 0.907, 0.844, 0.779, 0.761, 0.714, 0.508]
N=12 sectors= 7 tau= 10.0 T=   1000 n=  4096 uniq=  1511 med=0.282 south=0.056 cov=18 E=0.055 chi2u=13.1/9 cal=0.92 R_N=[0.997, 0.984, 0.969, 0.956, 0.915, 0.848, 0.649, 0.566, 0.492]
N=12 sectors= 7 tau= 30.0 T=   3000 n=  4096 uniq=  1580 med=0.230 south=0.049 cov=18 E=0.073 chi2u=7.6/9 cal=0.997 R_N=[0.997, 0.981, 0.974, 0.906, 0.903, 0.771, 0.688, 0.659, 0.707]
Born north [0.998 0.983 0.953 0.91  0.854 0.787 0.711 0.629 0.544]
```
sec_N14: h = 1, J = 0.37, g = 0.1, taus 10, 30, 100. new_N*: user parameters h0z = hz = 0.1, J = 1, gx = 0.01, taus 1, 3, 10, 30.

### Zeus submission (2026-09-24)
zeus_new_q refused (queue-wide cap). Submitted to zeus_all_q, 8 cpus, 80gb, walltime 24:00:00, source commit 769d5698adb6035e7061ee4048744be5d491e66f in /home/matanhaller/research/collapse_src_ring_h0zhz_769d569:
- 4701701[].zeus-master: N = 16, kp 0..8, run_root work/zeus_ring_h0zhz_h0.1_J1_g0.01_N16_20260924_v3
- 4701702[].zeus-master: N = 18, kp 0..9, run_root work/zeus_ring_h0zhz_h0.1_J1_g0.01_N18_20260924_v3

### User parameters at N = 14 (local, analyze_sectors.py)
```
N=14 sectors= 8 tau=  1.0 T=    100 n= 16384 uniq=  4643 med=0.212 south=0.003 cov=18 E=0.183 chi2u=158.4/9 cal=0.0447 R_N=[1.0, 1.0, 1.0, 1.0, 0.993, 0.959, 1.0, 0.796, 0.76]
N=14 sectors= 8 tau=  3.0 T=    300 n= 16384 uniq=  6988 med=0.375 south=0.109 cov=18 E=0.030 chi2u=54.6/9 cal=13.2 R_N=[0.984, 0.965, 0.93, 0.869, 0.825, 0.748, 0.708, 0.586, 0.556]
N=14 sectors= 8 tau= 10.0 T=   1000 n= 16384 uniq=  7631 med=0.280 south=0.043 cov=18 E=0.070 chi2u=117.6/9 cal=0.874 R_N=[0.996, 0.988, 0.985, 0.953, 0.918, 0.845, 0.859, 0.668, 0.54]
N=14 sectors= 8 tau= 30.0 T=   3000 n= 16384 uniq=  7829 med=0.252 south=0.042 cov=18 E=0.045 chi2u=104.7/9 cal=0.642 R_N=[0.997, 0.992, 0.984, 0.964, 0.927, 0.83, 0.69, 0.62, 0.603]
Born north [0.998 0.983 0.953 0.91  0.854 0.787 0.711 0.629 0.544]
```

### N = 14 perturbation cloud about (hz = 0.1, h0z = 0.1, J = 1, gx = 0.01), taus 10, 30 (cloud.sh; h0p3 = h0z 0.103, h0m3 = 0.097, h0p10 = 0.11, h0m10 = 0.09, Jp20 = J 1.2, Jm20 = J 0.8, gp30 = gx 0.013, gm30 = gx 0.007)
```
== cloud/Jm20
N=14 sectors= 8 tau= 10.0 T=   1000 n= 16384 uniq=  7660 med=0.281 south=0.043 cov=18 E=0.070 chi2u=123.0/9 cal=0.881 R_N=[0.996, 0.988, 0.985, 0.953, 0.918, 0.845, 0.859, 0.659, 0.541]
N=14 sectors= 8 tau= 30.0 T=   3000 n= 16384 uniq=  7787 med=0.253 south=0.041 cov=18 E=0.051 chi2u=106.1/9 cal=0.65 R_N=[0.997, 0.992, 0.984, 0.963, 0.923, 0.837, 0.679, 0.634, 0.625]
== cloud/Jp20
N=14 sectors= 8 tau= 10.0 T=   1000 n= 16384 uniq=  7682 med=0.280 south=0.044 cov=18 E=0.073 chi2u=122.7/9 cal=0.871 R_N=[0.996, 0.988, 0.985, 0.953, 0.921, 0.841, 0.869, 0.656, 0.519]
N=14 sectors= 8 tau= 30.0 T=   3000 n= 16384 uniq=  7813 med=0.252 south=0.042 cov=18 E=0.050 chi2u=104.9/9 cal=0.637 R_N=[0.997, 0.992, 0.983, 0.96, 0.933, 0.835, 0.659, 0.636, 0.605]
== cloud/gm30
N=14 sectors= 8 tau= 10.0 T=   1429 n= 16384 uniq=  8472 med=0.202 south=0.030 cov=18 E=0.080 chi2u=109.3/9 cal=1.5 R_N=[0.998, 0.989, 0.979, 0.958, 0.904, 0.845, 0.744, 0.776, 0.638]
N=14 sectors= 8 tau= 30.0 T=   4286 n= 16384 uniq=  8126 med=0.223 south=0.035 cov=18 E=0.072 chi2u=114.6/9 cal=0.616 R_N=[0.997, 0.993, 0.983, 0.967, 0.924, 0.84, 0.769, 0.664, 0.41]
== cloud/gp30
N=14 sectors= 8 tau= 10.0 T=    769 n= 16384 uniq=  7828 med=0.267 south=0.048 cov=18 E=0.060 chi2u=105.5/9 cal=1.37 R_N=[0.997, 0.987, 0.976, 0.95, 0.893, 0.877, 0.821, 0.628, 0.516]
N=14 sectors= 8 tau= 30.0 T=   2308 n= 16384 uniq=  6832 med=0.289 south=0.050 cov=18 E=0.039 chi2u=82.8/9 cal=0.661 R_N=[0.997, 0.99, 0.987, 0.953, 0.915, 0.85, 0.686, 0.649, 0.564]
== cloud/h0m10
N=14 sectors= 8 tau= 10.0 T=   1000 n= 16384 uniq=  5136 med=0.154 south=0.000 cov=10 E=0.101 chi2u=53.3/5 cal=0.00972 R_N=[1.0, 1.0, 1.0, 1.0, 1.0, None, None, None, None]
N=14 sectors= 8 tau= 30.0 T=   3000 n= 16384 uniq=  4749 med=0.125 south=0.000 cov=10 E=0.101 chi2u=43.8/5 cal=0.00853 R_N=[1.0, 1.0, 1.0, 1.0, 1.0, None, None, None, None]
== cloud/h0m3
N=14 sectors= 8 tau= 10.0 T=   1000 n= 16384 uniq=  6571 med=0.207 south=0.002 cov=18 E=0.231 chi2u=137.1/9 cal=0.0276 R_N=[1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.941, 0.263]
N=14 sectors= 8 tau= 30.0 T=   3000 n= 16384 uniq=  6918 med=0.184 south=0.001 cov=18 E=0.224 chi2u=130.8/9 cal=0.0241 R_N=[1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.4]
== cloud/h0p10
N=14 sectors= 8 tau= 10.0 T=   1000 n= 16384 uniq=  5840 med=0.104 south=0.000 cov=8 E=0.065 chi2u=39.4/4 cal=0.00701 R_N=[1.0, 1.0, 1.0, 1.0, None, None, None, None, None]
N=14 sectors= 8 tau= 30.0 T=   3000 n= 16384 uniq=  4943 med=0.117 south=0.000 cov=10 E=0.101 chi2u=38.1/5 cal=0.00742 R_N=[1.0, 1.0, 1.0, 1.0, 1.0, None, None, None, None]
== cloud/h0p3
N=14 sectors= 8 tau= 10.0 T=   1000 n= 16384 uniq=  6634 med=0.191 south=0.000 cov=18 E=0.217 chi2u=128.7/9 cal=0.024 R_N=[1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.6]
N=14 sectors= 8 tau= 30.0 T=   3000 n= 16384 uniq=  7106 med=0.174 south=0.000 cov=18 E=0.219 chi2u=118.5/9 cal=0.0222 R_N=[1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.909, 0.8]

[exited with code 0]
```

### Zeus N = 16 (job 4701701[], collected to work/zeus_ring_h0zhz_h0.1_J1_g0.01_N16_collected_20260924_203739; all 9 sector markers valid, SHA-256 match)
```
N=16 sectors= 9 tau=  1.0 T=    100 n= 65536 uniq= 36505 med=0.200 south=0.006 cov=18 E=0.093 chi2u=716.1/9 cal=0.128 R_N=[1.0, 0.999, 0.995, 0.981, 0.953, 0.935, 0.83, 0.704, 0.593]
N=16 sectors= 9 tau=  3.0 T=    300 n= 65536 uniq= 36547 med=0.314 south=0.059 cov=18 E=0.020 chi2u=231.8/9 cal=1.07 R_N=[0.995, 0.986, 0.973, 0.942, 0.881, 0.806, 0.73, 0.634, 0.563]
N=16 sectors= 9 tau= 10.0 T=   1000 n= 65536 uniq= 36515 med=0.332 south=0.041 cov=18 E=0.065 chi2u=908.1/9 cal=0.388 R_N=[0.999, 0.995, 0.982, 0.972, 0.936, 0.882, 0.793, 0.683, 0.567]
N=16 sectors= 9 tau= 30.0 T=   3000 n= 65536 uniq= 36504 med=0.327 south=0.040 cov=18 E=0.064 chi2u=918.8/9 cal=0.332 R_N=[0.999, 0.995, 0.986, 0.967, 0.942, 0.876, 0.793, 0.689, 0.551]
Born north [0.998 0.983 0.953 0.91  0.854 0.787 0.711 0.629 0.544]
```
Ratio error at tau = 3 by N (user parameters): N=10 0.046, N=12 0.045, N=14 0.030, N=16 0.020 (rows above and earlier in this record).
