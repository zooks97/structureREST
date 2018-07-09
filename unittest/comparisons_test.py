import unittest
import json
import numpy as np
import os
from subprocess import run
from pymatgen import Structure
import sys
sys.path.insert(0, '../lib')
import comparisons
from itertools import combinations


class TestMatminerComparisons(unittest.TestCase):

    def setUp(self):
        if not os.path.isfile('test_structures.json'):
            run(['python', 'get_test_structures.py'])
        with open('test_structures.json', 'r') as f:
            self.test_structures = json.load(f)

    def test_same(self):
        same = [['fcc', 'big_fcc'],
                ['bcc', 'big_bcc'],
                ['diamond', 'gaas', 'zincblende']]
        for structures in same:
            structure_dicts = [self.test_structures[s]['structure'] for s in structures]
            comparison = comparisons.matminer_comparisons(structure_dicts)
            self.assertTrue(np.array(comparison).all())

    def test_different(self):
        unique = ['diamond', 'rocksalt', 'cubic_perovskit', 'tetragonal_perovskite',
                  'trigonal_perovskite', 'orthorombic_perovskite', 'wurtzite', 'fcc',
                  'bcc', 'hcp', 'monoclinic', 'triclinic']
        for combo in combinations(unique, 2):
            comparison = comparisons.matminer_comparisons([self.test_structures[s]['structure'] for s in combo])
            self.assertFalse(np.array(comparison)[1,1])


# class TestPymatgenComparisons(unittest.TestCase):
# 
#     def test_same(self):
#         self.assertTrue()
# 
#     def test_different(self):
#         self.assertTrue()

