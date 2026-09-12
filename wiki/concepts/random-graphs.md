# Random Graph Detectors

The `unitary-collapse` project uses several random graph topologies for the detector pixels to test whether Born-like geometry is a product of specific structural symmetry or a more general property of "complex" networks.

## Supported Topologies
These are implemented in `core/detector_graphs.py`:

### 1. Erdős–Rényi (ER)
- **Construction**: Every pair of nodes is connected with probability $p$.
- **Characteristic**: Homogeneous randomness; no inherent clustering or hierarchy.

### 2. Watts–Strogatz (WS)
- **Construction**: Starts with a regular ring lattice (each node connected to $k$ neighbors), then rewires edges with probability $p$.
- **Characteristic**: "Small-world" property—high clustering like a lattice, but low average path length like a random graph.

### 3. Barabási–Albert (BA)
- **Construction**: Growth model where new nodes attach to existing nodes with a probability proportional to their current degree.
- **Characteristic**: "Scale-free" property—the degree distribution follows a power law, creating high-degree "hubs."

### 4. Random Regular (Expander)
- **Construction**: Every node has exactly the same degree $d$.
- **Characteristic**: High algebraic connectivity (large Laplacian spectral gap), making them excellent expander graphs.

## Scientific Role
By comparing these families, the project tests whether:
- **Spectral Gap**: The expansion property (Random Regular) is a requirement for Born behavior.
- **Hierarchy**: The existence of hubs (BA) introduces non-Born artifacts.
- **Locality**: The transition from lattice to random (WS) shifts the root distribution.

See also: [[hamiltonian-families]], [[spectral-statistics]].
