#!/usr/local/miniconda3/envs/structure/bin/python
# -*- coding: utf-8 -*-
from pymatgen import Structure
from pymatgen.analysis.structure_matcher import (StructureMatcher,
                                                 AbstractComparator,
                                                 ElementComparator,
                                                 FrameworkComparator,
                                                 OccupancyComparator,
                                                 OrderDisorderElementComparator,
                                                 SpeciesComparator, SpinComparator)
from matminer.featurizers.site import CrystalSiteFingerprint
from matminer.featurizers.structure import SiteStatsFingerprint
import numpy as np


def matminer_comparisons(structures, preset='cn', crystal_site_args={},
                         site_stats_args={}, distance_tol=0.01):
    '''
    Distance based on crystal sites implmented by matminer

    Args:
        structures ([dict]): dictionary-encoded pymatgen Structure objects
        preset (str): ['cn', 'ops'] CrystalSiteFingerprint preset
        crystal_site_args (dict): **kwargs passed to CrysatlSiteFingerprint
        site_stats_args (dict): **kwargs passed to SiteStatsFingerprint
        distance_tol (float): distance below which comparison will return True

    Returns:
        [bool]: comparisons between each pair of structures; goes like
            [1-2, 1-3, ..., 1-n, 2-3, 2-4, ..., 2-n, ...]
    '''
    structures = [Structure.from_dict(structure)
                  for structure in structures]
    csf = CrystalSiteFingerprint.from_preset(preset, **crystal_site_args)
    ssf = SiteStatsFingerprint(csf, **site_stats_args)
    v = [ssf.featurize(structure) for structure in structures]
    comparisons = []
    for i, v_1 in enumerate(v):
        for j, v_2 in enumerate(v[i:]):
            if i != j + i:
                distance = np.linalg.norm(np.array(v_1) - np.array(v_2))
                if distance <= distance_tol:
                    distance = 0.
                comparisons.append(not bool(distance))
    return comparisons


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
    structures = [Structure.from_dict(structure)
                  for structure in structures]
    comparisons = []
    for i, struct_1 in enumerate(structures):
        for j, struct_2 in enumerate(structures[i:]):
            if i != j + i:
                structure_matcher = StructureMatcher(comparator=comparator,
                                                     **kwargs)
                if anonymous:
                    comparison = structure_matcher.fit_anonymous(
                        struct_1, struct_2)
                else:
                    comparison = structure_matcher.fit(struct_1, struct_2)
                comparisons.append(bool(comparison))
    return comparisons
