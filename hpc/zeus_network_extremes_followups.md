# Network extreme-``S_born`` follow-ups

Both campaigns select the ten highest and ten lowest validated stored
``S_born`` cases independently within each of the four graph families. Exact
ties are broken by source-case path. They use one PBS job array per campaign
and can be resumed by resubmitting with the same `RUN_ROOT`.

## Five new N=12 graph realizations

Each of the 80 selected Hamiltonian parameter configurations is simulated on
five newly sampled graphs. Graph-family parameters are unchanged; each new
realization has a deterministic, recorded seed distinct from the source seed.
Every realization writes its own `COMPLETE.json` checkpoint.

```bash
bash hpc/submit_zeus_network_extremes_resampled_N12.sh
```

This submits one 20-element array. Each task owns four source configurations,
or 20 simulations after the five graph realizations.

## N=13,14,15 continuation

Each of the same 80 source configurations is simulated at N=13,14,15. Random
graphs do not possess a canonical size-scaling map: at every target N the graph
is regenerated from the saved family parameters and saved seed. Metadata states
explicitly that it is not a subgraph or extension of the original N=12 graph.

```bash
bash hpc/submit_zeus_network_extremes_largerN.sh
```

This submits one 10-element array. Each task owns eight source configurations,
or 24 simulations across the three target sizes. The fine-grained checkpoints
ensure that a walltime limit does not discard completed configurations or
smaller-N results.
N is the outer loop; each individual case writes `COMPLETE.json`, and the task
also writes `N13_COMPLETE.json`, `N14_COMPLETE.json`, and `N15_COMPLETE.json`
after finishing both assigned cases at that size.

The N=15 random-network calculations may be expensive because circular-shift
symmetry is unavailable. The larger-N array therefore requests 256 GB and a
120-hour walltime; completion is not guaranteed, but all smaller-N checkpoints
remain valid and resumable.
