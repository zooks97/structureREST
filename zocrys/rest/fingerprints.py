#!/usr/local/miniconda3/envs/structure/bin/python
# -*- coding: utf-8 -*-
from pymatgen import Structure
from matminer.featurizers.site import CrystalSiteFingerprint
from matminer.featurizers.structure import SiteStatsFingerprint
import stidy
import multiprocessing as mp
from os.path import isfile
from os import remove


def matminer_fingerprints(structures, preset='cn', crystal_site_args={}, site_stats_args={}):
    '''
    Fingerprint based on crystal sites implmented by matminer

    Args:
        structures ([dict]): dictionary-encoded pymatgen Structure objects
        preset (str): ['cn', 'ops'] CrystalSiteFingerprint preset
        crystal_site_args (dict): **kwargs passed to CrysatlSiteFingerprint
        site_stats_args (dict): **kwargs passed to SiteStatsFingerprint

    Returns:
        [[float]]: fingerprint vectors for each structure
    '''
    structures = [Structure.from_dict(structure)
                  for structure in structures]
    csf = CrystalSiteFingerprint.from_preset(preset, **crystal_site_args)
    ssf = SiteStatsFingerprint(csf, **site_stats_args)
    pool = mp.Pool()
    v = pool.map(ssf.featurize, structures)
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
    if isfile('check.def'):
        remove('check.def')
    return fingerprints
