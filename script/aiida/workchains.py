from spglib import get_symmetry, get_hall_number_from_symmetry, get_symmetry_dataset, standardize_cell
from pymatgen import Structure
from aiida.orm.data.base import Str, Float
from aiida.orm import DataFactory
from aiida.work.workchain import WorkChain
StructureData = DataFactory('structure')


class FingerprintWorkChain(WorkChain):

    @classmethod
    def define(cls, spec):
        super(FingerprintWorkChain, cls).define(spec)
        spec.input('structure', valid_type=StructureData)
        spec.input('symprec', valid_type=Float)
        spec.input('angle_tolerance', valid_type=Float)
        spec.outline(
            cls.get_pymatgen_structure,
            cls.get_cell,
            cls.get_primitive_standard_cell,
            cls.get_symmetry_dataset,
            cls.get_primitive_standard_structure,
            cls.get_fingerprint
        )
        spec.output('result', valid_type=Str)

    def get_pymatgen_structure(self):
        self.ctx.structure = StructureData.get_pymatgen(self.inputs.structure)

    def get_cell(self):
        lattice = self.ctx.structure.lattice.matrix
        positions = self.ctx.structure.frac_coords
        numbers = [site.specie.Z for site in self.ctx.structure]
        self.ctx.cell = (lattice, positions, numbers)

    def get_primitive_standard_cell(self):
        self.ctx.ps_cell = standardize_cell(
            self.ctx.cell, to_primitive=True, no_idealize=False, symprec=self.inputs.symprec)

    def get_symmetry_dataset(self):
        symmetry = get_symmetry(self.ctx.ps_cell,
                                symprec=self.inputs.symprec)
        hall_number = get_hall_number_from_symmetry(symmetry['rotations'],
                                                    symmetry['translations'],
                                                    symprec=self.inputs.symprec)
        self.ctx.symmetry_dataset = get_symmetry_dataset(self.ctx.ps_cell,
                                                         symprec=self.inputs.symprec,
                                                         angle_tolerance=self.inputs.angle_tolerance,
                                                         hall_number=hall_number)

    def get_primitive_standard_structure(self):
        self.ctx.ps_structure = Structure(
            self.ctx.ps_cell[0], self.ctx.ps_cell[2], self.ctx.ps_cell[1])

    def get_fingerprint(self):
        symbols = [site.specie.symbol for site in self.ctx.ps_structure]
        wyckoffs = self.ctx.symmetry_dataset['wyckoffs']
        space_group = self.ctx.symmetry_dataset['number']
        sites = [(symbol, wyckoff)
                 for symbol, wyckoff in zip(symbols, wyckoffs)]
        formatted_wyckoffs = []
        for wyckoff in sorted(set(wyckoffs)):
            formatted_wyckoff = []
            for symbol in sorted(set(symbols)):
                count = sites.count((symbol, wyckoff))
                if count:
                    formatted_wyckoff.append('%s%02d' % (
                        symbol, count))
            formatted_wyckoffs.append(''.join(formatted_wyckoff + [wyckoff]))
        fingerprint = '_'.join([str(space_group)] + formatted_wyckoffs)
        self.out('result', Str(fingerprint))
