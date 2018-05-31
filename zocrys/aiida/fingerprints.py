from pymatgen import Structure
from matminer.featurizers.site import CrystalSiteFingerprint
from matminer.featurizers.structure import SiteStatsFingerprint


def matminer_fingerprints(structures: [Structure], preset: str='cn',
                          crystal_site_args: dict={},
                          site_stats_args: dict={}) -> [float]:
    structures = [Structure.from_dict(structure)
                  for structure in structures]
    csf = CrystalSiteFingerprint.from_preset(preset, **crystal_site_args)
    ssf = SiteStatsFingerprint(csf, **site_stats_args)
    v = [ssf.featurize(structure) for structure in structures]
    return v


import spglib
from pymatgen import Structure
from string import ascii_uppercase


def _get_cell(structure: Structure) -> tuple:
    '''
    Generate cell tuple for spglib in the form
        ([[3x3 lattice]], [[Nx3 positions]], [N atomic numbers])
    '''
    lattice = structure.lattice.matrix
    positions = structure.frac_coords
    numbers = [site.specie.Z for site in structure.sites]
    return (lattice, positions, numbers)


def _get_structure(cell: tuple) -> Structure:
    '''
    Generate pymatgen.core.Structure object from an spglib cell tuple

    Args:
        cell (tuple): ([[3x3 lattice]], [[Nx3 positions]], [N atomic numbers])

    Returns:
        pymatgen.core.Structure: pymatgen Structure object
    '''
    return Structure(cell[0], cell[2], cell[1])


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
    symmetry = spglib.get_symmetry(cell, symprec=symprec)
    hall_number = spglib.get_hall_number_from_symmetry(symmetry['rotations'],
                                                       symmetry['translations'],
                                                       symprec=symprec)
    symmetry_dataset = spglib.get_symmetry_dataset(cell, symprec=symprec,
                                                   angle_tolerance=angle_tolerance,
                                                   hall_number=hall_number)
    return symmetry_dataset['wyckoffs']


def _get_wyckoff_fingerprint(structure: Structure, symprec: float=1e-3,
                             angle_tolerance: float=3.) -> str:
    cell = spglib.standardize_cell(_get_cell(structure), to_primitive=True,
                                   no_idealize=False, symprec=symprec)

    species = [site.specie for site in structure.sites]
    species_map = {specie: ascii_uppercase[s]
                   for s, specie in enumerate(sorted(species))}
    print(species_map)
    mapped_species = [species_map[specie] for specie in species]

    wyckoffs = _get_wyckoffs(cell, symprec=symprec,
                             angle_tolerance=angle_tolerance)

    wyckoff_tuples = [(mapped_specie, wyckoff) for mapped_specie, wyckoff
                      in zip(mapped_species, wyckoffs)]

    wyckoff_set = {}
    for wyckoff in set(wyckoffs):
        wyckoff_set[wyckoff] = []
        for wyckoff_tuple in set(wyckoff_tuples):
            if wyckoff_tuple[1] == wyckoff:
                info = (wyckoff_tuples.count(wyckoff_tuple), wyckoff_tuple[0])
                wyckoff_set[wyckoff].append(info)
    return wyckoff_set


def spglib_fingerprints(structures: [dict], symprec=1e-3,
                        angle_tolerance=3.) -> [str]:
    fingerprints = []
    for structure in structures:
        structure = Structure.from_dict(structure)

    return fingerprints
