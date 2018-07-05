# -*- coding: utf-8 -*-
# python 3.6
from pymatgen import Structure
from pymatgen.analysis.structure_matcher import (StructureMatcher,
                                                 AbstractComparator,
                                                 ElementComparator,
                                                 FrameworkComparator,
                                                 OccupancyComparator,
                                                 OrderDisorderElementComparator,
                                                 SpeciesComparator, SpinComparator)
from matminer.featurizers.site import CrystalNNFingerprint
from matminer.featurizers.structure import SiteStatsFingerprint
import numpy as np
import fingerprints
import multiprocessing as mp


def matminer_comparisons(structures, preset='cn', crystal_site_args={},
                         site_stats_args={}, distance_tol=0.01):
    '''
    Distance based on crystal sites implmented by matminer

    Args:
        structures ([dict]): dictionary-encoded pymatgen Structure objects
        preset (str): ['cn', 'ops'] CrystalNNFingerprint preset
        crystal_site_args (dict): **kwargs passed to CrysatlSiteFingerprint
        site_stats_args (dict): **kwargs passed to SiteStatsFingerprint
        distance_tol (float): distance below which comparison will return True

    Returns:
        [bool]: comparisons between each pair of structures; goes like
            [1-2, 1-3, ..., 1-n, 2-3, 2-4, ..., 2-n, ...]
    '''
    # structures = [Structure.from_dict(structure)
    #               for structure in structures]
    v = fingerprints.matminer_fingerprints(
        structures, preset=preset, crystal_site_args=crystal_site_args, site_stats_args=site_stats_args)
    distances = []
    for i, v_1 in enumerate(v):
        for j, v_2 in enumerate(v[i:]):
            if i != j + i:
                distance = np.linalg.norm(np.array(v_1) - np.array(v_2))
                if distance <= distance_tol:
                    distance = 0.
                distances.append(not bool(distance))
    return distances


def pymatgen_comparisons(structures, comparator='OccupancyComparator', anonymous=False,
                         **kwargs):
    '''
    Distance based on pymatgen StructureMatcher rms distance

    Args:
        structures ([dict]): dictionary-encoded pymatgen Structure objects
        comparator (str): name of comparator object to use from ['StructureMatcher',
                                                 'AbstractComparator', 'ElementComparator',
                                                 'FrameworkComparator', 'OccupancyComparator',
                                                 'OrderDisorderElementComparator',
                                                 'SpeciesComparator', 'SpinComparator']
        anonymous (bool): whether or not to ignore species
        **kwargs: **kwargs to be passed to pymatgen's StructureMatcher object

    Returns:
        [bool]: comparisons between structures; goes like
            1-2, 1-3, ..., 1-n, 2-3, 2-4, ..., 2-n, ...]
    '''
    comparators = {'AbstractComparator': AbstractComparator,
                   'ElementComparator': ElementComparator,
                   'FrameworkComparator': FrameworkComparator,
                   'OccupancyComparator': OccupancyComparator,
                   'OrderDisorderElemementComparator':
                       OrderDisorderElementComparator,
                   'SpeciesComparator': SpeciesComparator,
                   'SpinComparator': SpinComparator,
                   None: None}
    comparator = comparators[comparator]()
    structure_matcher = StructureMatcher(comparator=comparator,
                                         **kwargs)
    structures = [Structure.from_dict(structure)
                  for structure in structures]
    stars = []
    comparisons = []
    for i, struct_1 in enumerate(structures):
        for j, struct_2 in enumerate(structures[i:]):
            if i != j + i:
                stars.append((struct_1, struct_2))
                # if anonymous:
                #     comparison = structure_matcher.fit_anonymous(
                #         struct_1, struct_2)
                # else:
                #     comparison = structure_matcher.fit(struct_1, struct_2)
                # comparisons.append(bool(comparison))
    pool = mp.Pool()
    if anonymous:
        comparisons = pool.starmap(structure_matcher.fit_anonymous, stars)
    else:
        comparisons = pool.starmap(structure_matcher.fit, stars)
    return [bool(comparison) for comparison in comparisons]
