"""
core — Quantum Disentanglement & Wrapped-Cauchy Analysis
=========================================================

Public API re-exports.  Users can import directly from the package::

    from core import DisentanglementAnalyzer, CentralSpinHamiltonianNumpy
    from core import wrapped_cauchy_pdf, compute_wrapped_sums
"""

# Analysis
from core.analysis import (
    DisentanglementAnalyzer,
    RelativeEvolutionSpectrum,
    diagonalize_relative_evolution,
    diagonalize_relative_evolution_from_unitary,
    relative_evolution_matrix,
)
from core.relative_evolution_pencil import (
    LinearPencilRegularityAudit,
    ProjectiveDuplicateDiagnostics,
    ProjectiveRootAudit,
    RelativeEvolutionPencilSpectrum,
    audit_linear_pencil_regularity,
    compare_direct_and_generalized,
    diagnose_projective_duplicates,
    generalized_relative_evolution_spectrum,
    matched_projective_angle_error,
    projective_chordal_distance,
)

# Visualization
from core.visualization import (
    DisentanglementVisualizer,
    LevelSpacingPlotter,
    WrappedCauchyPlotter,
)

# Hamiltonians (NumPy — always available)
from core.hamiltonians import (
    HamiltonianGenerator,
    CentralSpinHamiltonianNumpy,
    DimerizedPixelHamiltonianNumpy,
    MixedFieldIsingHamiltonianNumpy,
    SinglePixelHamiltonianNumpy,
    TwoPixelHamiltonianNumpy,
)

# Hamiltonians (QuSpin — optional)
try:
    from core.hamiltonians import (
        CentralSpinHamiltonianQuSpin,
        DimerizedPixelHamiltonianQuSpin,
        MixedFieldIsingHamiltonianQuSpin,
        SinglePixelHamiltonianQuSpin,
        TwoPixelHamiltonianQuSpin,
    )
except ImportError:
    pass

# Quantum utilities
from core.quantum_utils import (
    generate_random_unitary,
    generate_time_evolution_operator,
    time_evolution_from_eigenbasis,
    sample_from_born_distribution,
    get_eigvals_from_z_and_theta,
    generate_special_unitary_from_eigvals,
)

# Wrapped Cauchy
from core.wrapped_cauchy import wrapped_cauchy_pdf, compute_wrapped_sums

# Folded wrapped-distribution fit diagnostics
from core.distribution_fit import (
    FoldedDistributionFit,
    fit_folded_circular_models,
    folded_wrapped_cauchy_bin_probabilities,
    folded_wrapped_gaussian_bin_probabilities,
)

# Born-rule diagnostics
from core.born import (
    BornDiagnostics,
    BornRatioResult,
    PhaseUniformityResult,
    TailEstimate,
    born_ratio_from_radii,
    born_ratio_from_theta,
    born_ratio_from_z,
    diagnostics_from_analyzer,
    diagnostics_from_radii,
    hill_tail_exponent,
    phase_angles_from_eigenvalues,
    phase_uniformity_from_eigenvalues,
    reciprocity_error_from_radii,
    theta_pair_from_eigenvalues,
    theta_from_z,
    theta_pair_from_radii,
)

# Level spacing diagnostics
from core.level_spacing import (
    compute_level_spacings,
    compute_level_spacing_ratios,
    compute_unfolded_spacings,
    mean_level_spacing_ratio,
    unfold_spectrum,
    wigner_surmise,
    wigner_spacing_distribution,
    poisson_surmise,
    poisson_spacing_distribution,
    MEAN_R_POISSON,
    MEAN_R_GOE,
    MEAN_R_GUE,
    MEAN_R_GSE,
)

# Disorder
from core.disorder import (
    DisorderStrategy,
    UniformDisorder,
    GaussianDisorder,
    LorentzianDisorder,
    create_disorder_strategy,
)

# Pauli
from core.pauli import (
    build_pauli_x,
    build_pauli_z,
    build_pauli_operators,
)

# Projective root conventions
from core.projective_roots import (
    QubitFirstBlocks,
    append_uncoupled_spectator,
    antipodal_homogeneous_coordinates,
    bloch_vectors_from_homogeneous,
    direct_sum_detector_contexts,
    forward_pole_root_spectrum,
    matched_bloch_distance,
    production_root_spectrum,
    split_qubit_first_blocks,
)

# Full-sphere Gleason/Born diagnostics
from core.gleason_diagnostics import (
    EqualAreaLabeledHistogram,
    FullSphereBornDiagnostics,
    antipodal_equal_area_field,
    born_density_ratio_cross_residual,
    composition_consistency_error,
    diagnose_asymmetry_function,
    diagnose_labeled_bloch_histogram,
)

# Common Hamiltonian-classification workflow
from core.hamiltonian_classification import (
    ClassificationPointResult,
    SinglePixelClassificationPoint,
    build_single_pixel_hamiltonian,
    classify_single_pixel_point,
)

# Spherical harmonics (SciPy-backed, optional)
try:
    from core.spherical_harmonics import (
        SphericalHarmonicExpansion,
        SphericalHarmonicProjector,
        evaluate_spherical_harmonic,
        project_onto_spherical_harmonics,
    )

    _SPHERICAL_HARMONICS_AVAILABLE = True
except ImportError:
    _SPHERICAL_HARMONICS_AVAILABLE = False

__all__ = [
    # Analysis
    "DisentanglementAnalyzer",
    "LinearPencilRegularityAudit",
    "ProjectiveDuplicateDiagnostics",
    "ProjectiveRootAudit",
    "RelativeEvolutionPencilSpectrum",
    "audit_linear_pencil_regularity",
    "compare_direct_and_generalized",
    "diagnose_projective_duplicates",
    "generalized_relative_evolution_spectrum",
    "matched_projective_angle_error",
    "projective_chordal_distance",
    # Visualization
    "DisentanglementVisualizer",
    "LevelSpacingPlotter",
    "WrappedCauchyPlotter",
    # Hamiltonians
    "HamiltonianGenerator",
    "CentralSpinHamiltonianNumpy",
    "DimerizedPixelHamiltonianNumpy",
    "MixedFieldIsingHamiltonianNumpy",
    "SinglePixelHamiltonianNumpy",
    "TwoPixelHamiltonianNumpy",
    # Quantum utilities
    "generate_random_unitary",
    "generate_time_evolution_operator",
    "time_evolution_from_eigenbasis",
    "sample_from_born_distribution",
    "get_eigvals_from_z_and_theta",
    "generate_special_unitary_from_eigvals",
    # Wrapped Cauchy
    "wrapped_cauchy_pdf",
    "compute_wrapped_sums",
    "FoldedDistributionFit",
    "fit_folded_circular_models",
    "folded_wrapped_cauchy_bin_probabilities",
    "folded_wrapped_gaussian_bin_probabilities",
    # Born-rule diagnostics
    "BornDiagnostics",
    "BornRatioResult",
    "PhaseUniformityResult",
    "RelativeEvolutionSpectrum",
    "TailEstimate",
    "born_ratio_from_radii",
    "born_ratio_from_theta",
    "born_ratio_from_z",
    "diagonalize_relative_evolution",
    "diagonalize_relative_evolution_from_unitary",
    "diagnostics_from_analyzer",
    "diagnostics_from_radii",
    "hill_tail_exponent",
    "phase_angles_from_eigenvalues",
    "phase_uniformity_from_eigenvalues",
    "relative_evolution_matrix",
    "reciprocity_error_from_radii",
    "theta_pair_from_eigenvalues",
    "theta_from_z",
    "theta_pair_from_radii",
    # Disorder
    "DisorderStrategy",
    "UniformDisorder",
    "GaussianDisorder",
    "LorentzianDisorder",
    "create_disorder_strategy",
    # Pauli
    "build_pauli_x",
    "build_pauli_z",
    "build_pauli_operators",
    # Projective root conventions
    "QubitFirstBlocks",
    "append_uncoupled_spectator",
    "antipodal_homogeneous_coordinates",
    "bloch_vectors_from_homogeneous",
    "direct_sum_detector_contexts",
    "forward_pole_root_spectrum",
    "matched_bloch_distance",
    "production_root_spectrum",
    "split_qubit_first_blocks",
    # Full-sphere Gleason/Born diagnostics
    "EqualAreaLabeledHistogram",
    "FullSphereBornDiagnostics",
    "antipodal_equal_area_field",
    "born_density_ratio_cross_residual",
    "composition_consistency_error",
    "diagnose_asymmetry_function",
    "diagnose_labeled_bloch_histogram",
    # Common Hamiltonian-classification workflow
    "ClassificationPointResult",
    "SinglePixelClassificationPoint",
    "build_single_pixel_hamiltonian",
    "classify_single_pixel_point",
    # Level spacing diagnostics
    "compute_level_spacings",
    "compute_level_spacing_ratios",
    "compute_unfolded_spacings",
    "mean_level_spacing_ratio",
    "unfold_spectrum",
    "wigner_surmise",
    "wigner_spacing_distribution",
    "poisson_surmise",
    "poisson_spacing_distribution",
    "MEAN_R_POISSON",
    "MEAN_R_GOE",
    "MEAN_R_GUE",
    "MEAN_R_GSE",
    "LevelSpacingPlotter",
]

if _SPHERICAL_HARMONICS_AVAILABLE:
    __all__ += [
        "SphericalHarmonicExpansion",
        "SphericalHarmonicProjector",
        "evaluate_spherical_harmonic",
        "project_onto_spherical_harmonics",
    ]
