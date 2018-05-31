from aiida.orm.data.base import Str, Float
from aiida.work.launch import run
from aiida.orm import DataFactory
from pymatgen.io.cif import CifParser
from pymatgen import Structure
import workchains

StructureData = DataFactory('structure')

test_structure = CifParser(
    '../../data/AgBr_mp-866291_conventional_standard.cif').get_structures(primitive=False)[0]
test_structure = StructureData(pymatgen=test_structure)

inputs = {
    'structure': test_structure,
    'symprec': Float(1e-3),
    'angle_tolerance': Float(3),
}

results = run(workchains.FingerprintWorkChain, **inputs)
print(results)
