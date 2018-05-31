from pymatgen import Structure
from pymatgen.analysis.structure_matcher import (StructureMatcher,
AbstractComparator, ElementComparator, FrameworkComparator, OccupancyComparator,
OrderDisorderElementComparator, SpeciesComparator, SpinComparator)
def pymatgen_distances(structures: [dict], comparator: str='OccupancyComparator',
                       **kwargs) -> [float]:
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
    distances = []
    for i, struct_1 in enumerate(structures):
        for j, struct_2 in enumerate(structures[i:]):
            if i != j + i:
                print(i, )
                structure_matcher = StructureMatcher(comparator=comparator,
                                                     **kwargs)
                distance = structure_matcher.get_rms_dist(struct_1, struct_2)
                if distance is not None:
                    distance = round(distance[0], 6) # FIXME: include tol
                distances.append(distance)
    return distances

import numpy as np
from pymatgen import Structure
from matminer.featurizers.site import CrystalSiteFingerprint
from matminer.featurizers.structure import SiteStatsFingerprint
def matminer_distances(structures: [Structure], preset: str='cn',
                       crystal_site_args: dict={},
                       site_stats_args: dict={}) -> [float]:
    structures = [Structure.from_dict(structure)
                  for structure in structures]
    csf = CrystalSiteFingerprint.from_preset(preset, **crystal_site_args)
    ssf = SiteStatsFingerprint(csf, **site_stats_args)
    v = [np.array(ssf.featurize(structure)) for structure in structures]
    distances = []
    for i, v_1 in enumerate(v):
        for j, v_2 in enumerate(v[i:]):
            if i != j + i:
                distance = np.linalg.norm(v_1 - v_2)
                distance = round(distance, 6) # FIXME: include tol
                distances.append(distance)
    return distances