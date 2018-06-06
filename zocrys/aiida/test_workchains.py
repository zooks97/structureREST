#!/usr/local/miniconda3/envs/aiida-latest/bin/python
# -*- coding: utf-8 -*-

import unittest
import glob
import numpy as np
from aiida import is_dbenv_loaded, load_dbenv
if not is_dbenv_loaded():
    load_dbenv()
from aiida.orm.data.base import Str, Float
from aiida.work.launch import run
from aiida.orm import DataFactory
from pymatgen.io.cif import CifParser, CifWriter
from pymatgen import Structure

from zocrys.aiida.workchains import FingerprintWorkChain, FingerprintWorkChainPymatgen, FingerprintWorkChainStidy
StructureData = DataFactory('structure')


class TestFingerprintWorkChain(unittest.TestCase):

    def setUp(self):
        super(TestFingerprintWorkChain, self).setUp()

    def test_fingerprint_work_chain(self):
        fingerprints = []
        cifs = sorted(list(glob.glob('../../data/Li4Y3VO8*.cif')))
        for cif in cifs:
            print(cif)
            structure = CifParser(cif).get_structures(primitive=False)[0]
            print(structure)
            structure_data = StructureData(pymatgen=structure)
            # with open(cif.split('/')[-1].replace('.cif', '.xsf'), 'w') as f:
            #     f.write(structure_data._exportstring('xsf')[0])
            inputs = {
                'structure': structure_data,
                'symprec': Float(1e-3),
                'angle_tolerance': Float(3),
            }
            result = run(FingerprintWorkChainStidy, **inputs)
            structure = result['structure'].get_pymatgen()
            print(structure)
            fingerprint = result['fingerprint']
            print(fingerprint)
            print(''.join(['=']*80))
            # CifWriter(structure).write_file('%s' % cif.split('/')[-1])
            fingerprints.append(fingerprint)
        fingerprint_set = set(fingerprints)

        self.assertEqual(len(set(fingerprint_set)), 1)
