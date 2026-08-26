# Zeus HPC workflows

This directory contains PBS jobs and submission wrappers. Production jobs must
be submitted from Zeus; local checks and manifest generation do not submit
anything.

For the Hamiltonian-classification research program, use:

- `zeus_hamiltonian_classification_array.pbs`;
- `submit_zeus_hamiltonian_classification.sh`;
- `hamiltonian_classification_campaign.md`.

The campaign uses the same single-point Python implementation as local tests,
stores every point independently, and can be resumed safely.

The controlled central-field follow-up for the top stored-`S_born` cases in
the four random-network families is documented in
`zeus_network_top_hz0_variants_N12.md`. Its submission wrapper is
`submit_zeus_network_top_hz0_variants_N12.sh`.
