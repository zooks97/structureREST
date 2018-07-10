# -*- coding: utf-8 -*-
# python 3.6
'''
    Functions for comparing sets of crystal structures with themselves
'''
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
    v = fingerprints.matminer_fingerprints(
        structures, preset=preset, crystal_site_args=crystal_site_args, site_stats_args=site_stats_args)
    distances = np.zeros((len(v), len(v)))
    for i in range(len(v)):
        for j in range(i, len(v)):
            distance = np.linalg.norm(np.array(v[i]) - np.array(v[j]))
            if distance <= distance_tol:
                distance = 0.
            distances[i, j] = (not bool(distance))
            distances[j, i] = distances[i, j]
    return distances.tolist()


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
    for i in range(len(structures)):
        for j in range(i, len(structures)):
            stars.append((structures[i], structures[j]))
    pool = mp.Pool()
    if anonymous:
        results = pool.starmap(structure_matcher.fit_anonymous, stars)
    else:
        results = pool.starmap(structure_matcher.fit, stars)
    results = [bool(results) for result in results]

    comparisons = np.zeros(len(structures), len(structures))
    counter = 0
    for i in range(len(structures)):
        for j in range(i+1, len(structures)):
            comparisons[i, j] = results[counter]
            counter += 1

    return comparisons.tolist()
