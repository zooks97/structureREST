# -*- coding: utf-8 -*-

import numpy as np
from sys import path
path.insert(0,'/home/azadoks/git/glosim2/')
from libmatch.soap import get_Soaps, get_soap
from libmatch.utils import ase2qp, get_spkit, get_spkitMax
from spglib import standardize_cell
from ase import Atoms
from pymatgen import Structure
from pymatgen.io.ase import AseAtomsAdaptor
from multiprocessing import Pool

def structure2cell(structure, anonymize):
    '''
    Convert pymatgen structures to cell tuples for spglib
    with optional compositional anonymization
    Args:
        structure (pymatgen.core.Structure): pymatgen Structure object
        anonymize (bool): replace all species with hydrogen
    Returns:
        tuple: cell tuple (lattice, positions, numbers) for spglib
    '''
    lattice = structure.lattice.matrix
    positions = structure.frac_coords
    if anonymize:
        numbers = [1] * len(structure.sites)
    else:
        numbers = [site.specie.Z for site in structure.sites]
    return(lattice, positions, numbers)


def structure2quippy(structure, anonymize=False, scale=False,
                     standardize=False, primitivize=False, symprec=1e-3, from_dict=False):
    '''
    Convert pymatgen Structure to quippy Atoms
    Args:
        structure (pymatgen.core.Structure): pymatgen Structure object
        anonymize (bool): replace all species with hydrogen
        scale (bool): scale volume to 1 Å^3 / atom
        standardize (bool): use spglib to standardize the structure
        primitivize (bool): use spglib to standardize and primitivize the structure
        symprec (float): symmetry tolerance factor (see spglib documentation)
    Returns:
        quippy.atoms.Atoms: quippy Atoms object
    '''
    if from_dict:
        structure = Structure.from_dict(structure)
    cell = structure2cell(structure, anonymize) # (matrix, positions, numbers)
    if standardize or primitivize:
        cell = standardize_cell(cell, to_primitive=primitivize, symprec=symprec)
        if cell:
            cell = list(cell)
        else:
            try:
                return ase2qp(AseAtomsAdaptor.get_atoms(structure))  # spglib can't make a primitive
            except ValueError as e:  # TODO: warn the user here maybe
                return None  # Must be either really fucked up or disordered
    if scale:
        volume = np.dot(np.cross(cell[0][0], cell[0][1]), cell[0][2])  # cell[0] = matrix
        cell[0] = cell[0] / np.cbrt(volume / len(cell[2]))  # len(cell[2]) = n_atoms
    return ase2qp(Atoms(cell=cell[0], positions=cell[1], numbers=list(cell[2]), pbc=True))  


def average_distance(average_soap1, average_soap2):
    '''
    Calculate distance between to averaged SOAP vectors
    using the average distance kernel from De et al. (2016)
    Args:
        average_soap1 (numpy.ndarray): numpy array of average SOAP vector 1
        average_soap2 (numpy.ndarray): numpy array of average SOAP vector 2
    Returns:
        float: normalized distance between average_soap1 and average_soap2
    '''
    k11 = np.linalg.norm(average_soap1)
    k22 = np.linalg.norm(average_soap2)
    k12 = np.linalg.norm(average_soap1 - average_soap2)
    d12 = np.sqrt(2 - 2 * (k12 / np.sqrt(k11 * k12)))
    return d12
