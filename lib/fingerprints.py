# -*- coding: utf-8 -*-
# python 3.6
'''
    Functions for calculating structure fingerprints for sets of crystal structures
'''
from pymatgen import Structure
# from matminer.featurizers.site import CrystalNNFingerprint
from matminer.featurizers.site import CrystalNNFingerprint
from matminer.featurizers.structure import SiteStatsFingerprint
import multiprocessing as mp
from os.path import isfile
from os import remove
import functools
import logging
# from . import stidy
import stidy
logger = logging.getLogger(__name__)


def matminer_wrapper(structure, preset, crystal_site_args, site_stats_args):
    csf = CrystalNNFingerprint.from_preset(preset, **crystal_site_args)
    ssf = SiteStatsFingerprint(csf, **site_stats_args)
    try:
        return ssf.featurize(structure)
    except Exception as e:
        print('Exception caught!')
        logger.error(e)


def matminer_fingerprints(structures, preset='cn', crystal_site_args={}, site_stats_args={}):
    '''
    Fingerprint based on crystal sites implmented by matminer
    Args:
        structures ([dict]): dictionary-encoded pymatgen Structure objects
        preset (str): ['cn', 'ops'] CrystalNNFingerprint preset
        crystal_site_args (dict): **kwargs passed to CrystalNNFingerprint
        site_stats_args (dict): **kwargs passed to SiteStatsFingerprint
    Returns:
        [[float]]: fingerprint vectors for each structure
    '''
    structures = [Structure.from_dict(structure)
                  for structure in structures]
    pool = mp.Pool()
    stars = [(structure, preset, crystal_site_args, site_stats_args)
             for structure in structures]
    v = pool.starmap(matminer_wrapper, stars)
    pool.close()
    pool.join()
    return v


def stidy_fingerprints(structures, symprec=0.01, angle_tolerance=5.):
    '''
    Combination of Pymatgen for tolerances and STRUCTURE TIDY for standardization
        and primitivization to construct a wyckoff fingerprint with the format:
            [ICT space group number]_[[2-digit count][Species letter]][Wyckoff letter]_"
    Args:
        structures ([dict]): dictionary-encoded pymatgen Structure objects
        symprec (float): distance symmetry tolerance passed to pymatgen and then to spglib in Angstrom
        angle_tolerance (float): angle symmetry tolerance passed to pymatgen and then to spglib in Degreees
    Returns:
        [str]: wyckoff fingerprints
    '''
    structures = [Structure.from_dict(structure) for structure in structures]
    pool = mp.Pool()
    stidy_outputs = pool.map(stidy.stidy, structures)
    pool.close()
    pool.join()

    fingerprints = [s.wyckoff_fingerprint for s in stidy_outputs]
    fingerprints = [f[0] if f else None for f in fingerprints]
    # for i, f in enumerate(fingerprints):
    #     if not f:
    #         print(stidy_outputs[i].output)
    if isfile('check.def'):
        remove('check.def')
    # return fingerprints
    return fingerprints
