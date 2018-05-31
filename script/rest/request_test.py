import requests
import pymatgen
from pymatgen.io.cif import CifParser
import json
from tabulate import tabulate

base = '/Users/zooks/Dropbox/EPFL/structure/structureREST'
cifs = ['{}/data/Si_mp-149_conventional_standard.cif',
        '{}/data/GaAs_mp-2534_conventional_standard.cif',
        '{}/data/AgBr_mp-866291_conventional_standard.cif',
        '{}/data/C_mp-66_conventional_standard.cif',
        '{}/data/Ti_mp-6985_conventional_standard.cif']
# cifs = ['{}/data/YCu7O12_mvc-1832_conventional_standard.cif',
#         '{}/data/Ca3Ge3(MoO6)2_mvc-4467_conventional_standard.cif']
cifs = [c.format(base) for c in cifs]

structures = [CifParser(cif).get_structures()[0].as_dict() for cif in cifs]
structures = json.dumps(structures)

payload = {'structures': structures}

# working: /comparisons/[pymatgen, matminer], /distances/[pymatgen, matminer]
#          /fingerprints/[matminer]
r = requests.get('http://127.0.0.1:5000/v1/distances/matminer/',
                 params=payload)
print(r)
distances = json.loads(r.text)
print(distances)