from ase import Atoms
import json


def atoms_dumps(atoms):
    numbers = atoms.numbers
    cell = atoms.cell
    try:
        positions = atoms.positions
        positions_type = 'absolute'
    except AttributeError:
        positions = atoms.scaled_positions
        positions_type = 'scaled'

    atoms_dict = {'numbers': numbers,
                  'positions': positions,
                  'positions_type': positions_type,
                  'cell': cell}
    atoms_string = json.dumps(atoms_dict)
    return atoms_string


def atoms_loads(atoms):
    atoms_dict = json.loads(atoms)
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
