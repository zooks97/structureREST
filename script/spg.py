import spglib
import pymatgen
import pymatgen.io.cif  
def _get_cell(structure: pymatgen.core.Structure) -> tuple:
    '''
    Generate cell tuple for spglib in the form
        ([[3x3 lattice]], [[Nx3 positions]], [N atomic numbers])
    '''
    lattice = structure.lattice.matrix
    positions = structure.frac_coords
    numbers = [site.specie.Z for site in structure.sites]
    return (lattice, positions, numbers)

def _get_wyckoffs(cell: tuple, symprec: float=1e-3,
                 angle_tolerance: float=3.) -> [str]:
    '''
    Get Wyckoff occupancies from an spglib cell tuple
    
    Args:
        cell (tuple): ([[3x3 lattice]], [[Nx3 positions]], [N atomic numbers])
        symprec (float): cartesian distance tolerance for symmetries
        angle_tolerance (float): angle tolerance in degrees
        
    Returns:
        list: list of Wyckoff occupancy strings (one per site)
    '''
    # space_group = spglib.get_spacegroup(cell, symprec=symprec)
    symmetry = spglib.get_symmetry(cell, symprec=symprec)
    hall_number = spglib.get_hall_number_from_symmetry(symmetry['rotations'],
                                                       symmetry['translations'],
                                                       symprec=symprec)
    symmetry_dataset = spglib.get_symmetry_dataset(cell, symprec=symprec,
                                                   angle_tolerance=angle_tolerance,
                                                   hall_number=hall_number)
    return symmetry_dataset['wyckoffs']

def _get_structure(cell: tuple) -> pymatgen.core.Structure:
    '''
    Generate pymatgen.core.Structure object from an spglib cell tuple
    
    Args:
        cell (tuple): ([[3x3 lattice]], [[Nx3 positions]], [N atomic numbers])
    
    Returns:
        pymatgen.core.Structure: pymatgen Structure object
    '''
    return pymatgen.Structure(cell[0], cell[2], cell[1])

def _wyckoff_fingerprint(cell: tuple, symprec: float=1e-3,
                         angle_tolerance: float=3.) -> str:
    '''
    Generate Wyckoff fingerprint from a pymatgen.core.Structure in the form of
        [space group number]_[Wyckoff_number_for_each_site]
        e.g. 164_d_d_d

    Args:
        cell (tuple): ([[3x3 lattice]], [[Nx3 positions]], [N atomic numbers])
        symprec (float): cartesian distance tolerance for symmetries
        angle_tolerance (float): angle tolerance in degrees
    Returns:
        str: Wyckoff fingerprint
    '''
    wyckoffs = _get_wyckoffs(cell=cell, symprec=symprec,
                            angle_tolerance=angle_tolerance)
    space_group = spglib.get_spacegroup(cell, symprec=symprec)
    space_group = space_group.split('(')[-1].split(')')[0]
    return '_'.join([space_group] + wyckoffs)

def wyckoff_fingerprints(structure: dict) -> (str, dict):
    structure = pymatgen.Structure.from_dict(structure)
    cell = structure.get_cell()
    ps_cell = spglib.standardize_cell(cell, to_primitive=True,
                                      no_idealize=False, symprec=1e-3)
    ps_structure = _get_structure(ps_cell)
    fingerprint = _wyckoff_fingerprint(ps_cell) 
    return fingerprint, ps_structure