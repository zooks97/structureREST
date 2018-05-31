from pymatgen import Structure
from pymatgen.analysis.structure_matcher import (StructureMatcher,
AbstractComparator, ElementComparator, FrameworkComparator, OccupancyComparator,
OrderDisorderElementComparator, SpeciesComparator, SpinComparator)
def pymatgen_comparisons(structures: [dict], anonymous: bool=False,
                         comparator: str='OccupancyComparator',
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
    comparisons = []
    for i, struct_1 in enumerate(structures):
        for j, struct_2 in enumerate(structures[i:]):
            if i != j + i:
                structure_matcher = StructureMatcher(comparator=comparator,
                                                     **kwargs)
                if anonymous:
                    comparison = structure_matcher.fit_anonymous(struct_1, struct_2)
                else:
                    comparison = structure_matcher.fit(struct_1, struct_2)
                comparisons.append(bool(comparison))
    return comparisons

import numpy as np
from pymatgen import Structure
from matminer.featurizers.site import CrystalSiteFingerprint
from matminer.featurizers.structure import SiteStatsFingerprint
def matminer_comparisons(structures: [Structure], preset: str='cn',
                         crystal_site_args: dict={},
                         site_stats_args: dict={},
                         tolerance: float=0.02) -> [float]:
    structures = [Structure.from_dict(structure)
                  for structure in structures]
    csf = CrystalSiteFingerprint.from_preset(preset, **crystal_site_args)
    ssf = SiteStatsFingerprint(csf, **site_stats_args)
    v = [np.array(ssf.featurize(structure)) for structure in structures]
    comparisons = []
    for i, v_1 in enumerate(v):
        for j, v_2 in enumerate(v[i:]):
            if i != j + i:
                distance = np.linalg.norm(v_1 - v_2)
                comparison = np.isclose(distance, 0, tolerance)
                comparisons.append(bool(comparison))
    return comparisons