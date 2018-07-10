import sys
sys.path.insert(0, '/home/app/glosim2')
from ase import Atoms
import numpy as np
from libmatch.soap import get_Soaps
from libmatch.utils import ase2qp

# Read structures and convert to ase Atoms
# raw_structures =
# ase_atoms =

quippy_atoms = [ase2qp(ase_atoms_instance) for ase_atoms_instance in ase_atoms]

# atoms: [quippy.Atoms]
# nocenters: None or [Atomic numbers to ignore]
# chem_channels: bool (whether or not to include chemical combinations)
# centerweight: float (weight of gaussian on central atom)
# gaussian_width: float (sigma of gaussian)
# cutoff: float (integration cutoff distance)
# cutoff_transition_width: float (width of sigmoid used to smooth integration cutoff)
# nmax: int (number of radial basis functions)
# lmax: int (number of spherical harmonics)
# spkitMax: dict {atomic numbers: max. number of occurrences in a structure in the set atoms}
# nprocess: int (number of subprocesses spawned)
# chemicalProjection: ???
# dispbar: bool ???
# is_fast_average: None or bool (use fast averaging to calculate average soap; no average calculated if None)
soaps = get_Soaps(atoms=quippy_atoms,
                  nocenters=None, chem_channels=False,
                  centerweight=1.0, gaussian_width=0.5,
                  cutoff=2.0, cutoff_transition_width=0.5,
                  nmax=16, lmax=14,
                  spkitMax=None, nprocess=8,
                  chemicalProjection=None, dispbar=False,
                  is_fast_average=False)

# soaps should be a list of `OrderedDict`s keyed by the species symbols + an integer (e.g. keys = ["H0", "H1", "O0"])
