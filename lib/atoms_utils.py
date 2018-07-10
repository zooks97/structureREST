'''
    Utilities for ASE Atoms encoding and conversion
'''
from pymatgen import Structure
from pymatgen.io.ase import AseAtomsAdaptor
from ase import Atoms
import json


def as_dict(atoms):
    '''
    Convert an ASE Atoms object's core structural information to a dictionary
    Args:
        atoms (ase.Atoms): ASE Atoms object
    Returns:
        dict: dictionary with core ASE Atoms information
    '''
    atoms = atoms.copy()
    numbers = atoms.numbers.tolist()
    cell = atoms.cell.tolist()
    try:
        positions = atoms.positions.tolist()
        positions_type = 'absolute'
    except AttributeError:
        positions = atoms.scaled_positions.tolist()
        positions_type = 'scaled'

    atoms_dict = {'numbers': numbers,
                  'positions': positions,
                  'positions_type': positions_type,
                  'cell': cell}
    return atoms_dict


def from_dict(atoms_dict):
    '''
    Retrieve ASE Atoms object from an encoded dictionary
    Args:
        atoms_dict (dict): dictionary with core ASE Atoms information
    Returns
        ase.Atoms
    '''

    if atoms_dict['positions_type'] == 'absolute':
        atoms = Atoms(positions=atoms_dict['positions'],
                      numbers=atoms_dict['numbers'],
                      cell=atoms_dict['cell'])
    elif atoms_dict['positions_type'] == 'scaled':
        atoms = Atoms(scaled_positions=atoms_dict['positions'],
                      numbers=atoms_dict['numbers'],
                      cell=atoms_dict['cell'])
    else:
        raise ValueError('Unknown positions_type {}'.format(
            atoms_dict['positions_type']))
    return atoms


def dumps(atoms):
    '''
    Convert an ASE Atoms object to a dictionary then dump the dictionary
        to a json string
    Args:
        atoms (ase.Atoms)
    Returns:
        str: json-encoded ASE Atoms dictionary
    '''
    atoms_dict = as_dict(atoms)
    return json.dumps(atoms_dict)


def loads(atoms):
    '''
    Load a json-encoded ASE Atoms dictionary from the json string to an ASE
        Atoms object

    Args:
        atoms (str): json-encoded ASE Atoms dictionary

    Returns
        ase.Atoms
    '''
    atoms_dict = json.loads(atoms)
    return from_dict(atoms_dict)


def from_structure(structure):
    '''
    Wrapper for pymatgen.ase.io.AseAtomsAdaptor.get_atoms to convert
        pymatgen Structure objects to ASE Atoms objects
    Args:
        structure (pymatgen.core.Structure)
    Returns:
        ase.Atoms
    '''
    atoms = AseAtomsAdaptor.get_atoms(structure)
    return atoms


def from_structure_dict(structure_dict):
    '''
    Convert a dictionary-encoded pymatgen Structure object to an ASE Atoms
        object
    Args:
        structure_dict (dict)
    Returns
        ase.Atoms
    '''
    structure = Structure.from_dict(structure_dict)
    atoms = from_structure(structure)
    return atoms
