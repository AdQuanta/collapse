"""Run the corrected Ising h_z resonance-neighborhood atlas for N=11 through 18."""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from collapse.scaling_campaign import main_for_study


if __name__ == "__main__":
    main_for_study("hz_resonance", __doc__)
