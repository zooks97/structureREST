from glob import glob
from ase.io import read
from sys import path
path.insert(0,'/home/azadoks/git/glosim2/')
from libmatch.soap import get_Soaps, get_soap
from libmatch.utils import ase2qp, get_spkit, get_spkitMax
import soap_utils
from pymatgen import Structure
from pymatgen.io.ase import AseAtomsAdaptor
from spglib import standardize_cell
from itertools import product, chain
import numpy as np
from multiprocessing import Pool
from fractions import gcd

def dict2structure(structure):
    return Structure.from_dict(structure)

def structure2cell(structure, anonymize):
    lattice = structure.lattice.matrix
    positions = structure.frac_coords
    if anonymize:
        numbers = [1] * len(structure.sites)
    else:
        numbers = [site.specie.Z for site in structure.sites]
    return(lattice, positions, numbers)

def cell2structure(cell):
    return Structure(cell[0], cell[2], cell[1])

def standardize_dict(args):
    return standardize_cell(**args)

def structure2atoms(structure):
    return AseAtomsAdaptor.get_atoms(structure)

def lcm(a, b):
    return a * b / gcd(a, b)

def zoap(structures, symprec=1e-3, **kwargs):
    structures = [Structure.from_dict(structure) for structure in structures]
    cells = [structure2cell(structure, True) for structure in structures]
    primitive_cells = [standardize_cell(cell, to_primitive=True, symprec=symprec) for cell in cells]
    primitive_structures = [cell2structure(cell) for cell in primitive_cells]
    atoms_objects = [AseAtomsAdaptor.get_atoms(structure) for structure in primitive_structures]
    qps = [ase2qp(atoms) for atoms in atoms_objects]
    # soaps = [get_soap(qp, get_spkit(qp), get_spkit(qp), **kwargs) for qp in qps]
    soaps = get_Soaps(qps, **kwargs)
    return soaps

def zoap_mp(structures, symprec=1e-3, to_primitive=True, anonymize=True,
            **kwargs):
    p = Pool()
    structures = p.map(dict2structure, structures)
    cell_stars = [(structure, anonymize) for structure in structures]
    cells = p.starmap(structure2cell, cell_stars)
    cell_args = [{'cell': cell, 'symprec': symprec, 'to_primitive': to_primitive} for cell in cells]
    primitive_cells = p.map(standardize_dict, cell_args)
    primitive_structures = p.map(cell2structure, primitive_cells)
    atoms_objects = p.map(structure2atoms, primitive_structures)
    qps = p.map(ase2qp, atoms_objects)
    soaps = get_Soaps(qps, **kwargs)
    p.close()
    p.join()
    return soaps

def average_distance(soap1, soap2):
    soap1 = np.array(soap1.values())
    soap2 = np.array(soap2.values())

    l = lcm(len(soap1), len(soap2))
    if len(soap1) != len(soap2):
        soap1 = list(chain.from_iterable([soap1] * (l / len(soap1))))
        soap2 = list(chain.from_iterable([soap2] * (l / len(soap2))))

    k11 = 1. / l**2 * np.sum([np.dot(*p) for p in list(product(soap1, soap1))])
    k22 = 1. / l**2 * np.sum([np.dot(*p) for p in list(product(soap2, soap2))])
    k12 = 1. / l**2 * np.sum([np.dot(*p) for p in list(product(soap1, soap2))])

    k = k12 / np.sqrt(k11 * k22)
    d = np.sqrt(2 - 2 * k)
    return d
