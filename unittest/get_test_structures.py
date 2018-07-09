from pymatgen import MPRester
import json

material_ids = {
        'diamond': 'mp-66',  # C
        'gaas': 'mp-2534',  # GaAs
        'zincblende': 'mp-10695',  # ZnS

        'rocksalt': 'mp-22862',  # NaCl

        'cubic_perovskite': 'mp-2998',  # BaTiO3

        'tetragonal_perovskite': 'mp-5986',  # BaTiO3

        'trigonal_perovskite': 'mp-5020',  # BaTiO3

        'orthorhombic_perovskite': 'mp-5777',  # BaTiO3

        'wurtzite': 'mp-10281',  # ZnS

        'fcc': 'mp-23',  # Ni
        'big_fcc': 'mp-76',  # Sr

        'bcc': 'mp-13',  # Fe
        'big_bcc': 'mp-70',  # Rb

        'hcp': 'mp-153',  # Mg

        'trigonal': 'mp-782',  # Te2Pd

        'tetragonal': 'mp-742',  # Ti2Cu

        'monoclinic': 'mp-684',  # BaS2

        'triclinic': 'mp-9122',  # CaP3

        'orthorhombic': 'mp-872',  # BaSn
}

if __name__ == '__main__':
    print('Querying for structures')
    with MPRester('0WqdPfXxloze6T9N') as mpr:
        structures = {name: {'structure': mpr.get_structure_by_material_id(id).as_dict(),
                             'material_id': id}
                      for name, id in material_ids.items()}

    print('Writing structures to test_structures.json')
    with open('test_structures.json', 'w') as f:
        json.dump(structures, f)
