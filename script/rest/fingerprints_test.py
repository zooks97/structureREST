from pymatgen import Structure, Element
from pymatgen.io.cif import CifParser
from string import ascii_uppercase
import spglib
import fingerprints

base = '/Users/zooks/Dropbox/EPFL/structure/structureREST'
cifs = ['{}/data/YCu7O12_mvc-1832_conventional_standard.cif',
        '{}/data/Ca3Ge3(MoO6)2_mvc-4467_conventional_standard.cif']
cifs = [c.format(base) for c in cifs]

structures = [CifParser(cif).get_structures()[0] for cif in cifs]

print(fingerprints._get_wyckoff_fingerprint(structures[0]))
