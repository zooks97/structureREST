import pymatgen
from pymatgen.symmetry.analyzer import SpacegroupAnalyzer
def _wyckoff_fingerprint(structure: pymatgen.core.Structure,
                         symprec: float=1e-3, angle_tolerance: float=3.) -> str:
    '''
    Generate Wyckoff fingerprint from a pymatgen.core.Structure in the form of
        [space group number]_[Wyckoff_number_for_each_site]
        e.g. 164_d_d_d

    Args:
        structure (pymatgen.core.Structure): Structure object
    Returns:
        str: Wyckoff fingerprint string
    '''
    sg_analyzer = SpacegroupAnalyzer(structure, symprec=symprec,
                                     angle_tolerance=angle_tolerance)
    ps_structure = sg_analyzer.get_primitive_standard_structure()
    ps_sg_analyzer = SpacegroupAnalyzer(ps_structure, symprec=symprec,
                                        angle_tolerance=angle_tolerance)
    fingerprint = '_'.join([str(ps_sg_analyzer.get_space_group_number())] + 
                            ps_sg_analyzer.get_symmetry_dataset()['wyckoffs'])
    return fingerprint

def wyckoff_fingerprint(structure: dict) -> (str, dict):
    structure = pymatgen.Structure.from_dict(structure)
    sg_analyzer = SpacegroupAnalyzer(structure, symprec=1e-3,
                                    angle_tolerance=3.)
    ps_structure = sg_analyzer.get_primitive_standard_structure()
    return _wyckoff_fingerprint(structure), ps_structure