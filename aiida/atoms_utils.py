from ase import Atoms
import json

def as_dict(atoms):
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
    atoms_dict = as_dict(atoms)
    return json.dumps(atoms_dict)

def loads(atoms):
    atoms_dict = json.loads(atoms)
    return from_dict(atoms_dict)
