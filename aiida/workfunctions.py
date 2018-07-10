# -*- coding: utf-8 -*-

import re
import numpy as np
from sys import path
from os import path, remove
from string import ascii_uppercase
from distutils.spawn import find_executable
from tempfile import NamedTemporaryFile
from subprocess import Popen, PIPE, STDOUT
from pymatgen import Structure, Lattice
from pymatgen.io.cif import CifWriter
from aiida.orm import DataFactory
from aiida.work.workfunctions import workfunction
from aiida.work import ExitCode

# path.insert(0, 'GLOSIM2')
# from libmatch.soap import get_soap
# from libmatch.utils import ase2qp, get_spkit, get_spkitMax

StructureData = DataFactory('structure')
CifData = DataFactory('cif')

import requests
from cStringIO import StringIO


@workfunction
def soap_rest_workfunction(aiida_structure, address, spkitMax, do_anonimization=True,
                           do_scaling=True, scale_per='site',  nocenters=None,
                           centerweight=1.0, gaussian_width=0.5, cutoff=3.5,
                           cutoff_transition_width=0.5, nmax=8, lmax=6,
                           is_fast_average=False):
    def anonymize(structure):
        n_atoms = structure.n
        structure.set_atomic_numbers([1] * n_atoms)
        structure.set_chemical_symbols(['H'] * n_atoms)
        return structure

    def scale(structure, per='site'):
        if per == 'site':
            n_atoms = structure.n
        elif per == 'cell':
            n_atoms = 1  # scaling volume to 1/cell is the same as having 1 atom
        else:
            return ExitCode(400, '{} is not a valid `per` for scaling'.format(per))
        new_cell = structure.get_cell() / np.cbrt(structure.cell_volume() / n_atoms)
        structure.set_cell(new_cell)
        new_pos = structure.get_positions() / \
            np.linalg.norm(structure.get_cell(), axis=1) * \
            np.linalg.norm(new_cell, axis=1)
        structure.set_positions(new_pos)
        return structure

    ############################################################################

    ase_atoms = aiida_structure.get_ase()
    if do_anonimization:
        ase_atoms = anonymize(ase_atoms)
    if do_scaling:
        ase_atoms = scale(ase_atoms, per=scale_per)

    fake_file = StringIO()
    ase_atoms.write(filename=fake_file, format='json')
    ase_json = fake_file.getvalue()
    fake_file.close()

    payload = {'atoms': ase_json, 'spkitMax': spkitMax,
               'nocenters': nocenters, 'gaussian_width': gaussian_width,
               'cutoff': cutoff, 'cutoff_transition_width': cutoff_transition_width,
               'nmax': nmax, 'lmax': lmax, 'is_fast_average': is_fast_average}

    soap_request = requests.get(
        '{}/v1/soap'.format(address), params=payload)
    soap = soap_request.json()

    return soap


@workfunction
def soap_workfunction(aiida_structure, spkit_max, do_anonimization=True,
                      do_scaling=True, scale_per='site', **soapargs):
    def anonymize(structure):
        n_atoms = structure.n
        structure.set_atomic_numbers([1] * n_atoms)
        structure.set_chemical_symbols(['H'] * n_atoms)
        return structure

    def scale(structure, per='site'):
        if per == 'site':
            n_atoms = structure.n
        elif per == 'cell':
            n_atoms = 1  # scaling volume to 1/cell is the same as having 1 atom
        else:
            return ExitCode(400, '{} is not a valid `per` for scaling'.format(per))
        new_cell = structure.get_cell() / np.cbrt(structure.cell_volume() / n_atoms)
        structure.set_cell(new_cell)
        new_pos = structure.get_positions() / \
            np.linalg.norm(structure.get_cell(), axis=1) * \
            np.linalg.norm(new_cell, axis=1)
        structure.set_positions(new_pos)
        return structure

    ############################################################################

    ase_atoms = aiida_structure.get_ase()
    quippy_atoms = ase2qp(ase_atoms)
    if do_anonimization:
        quippy_atoms = anonymize(quippy_atoms)
    if do_scaling:
        quippy_atoms = scale(quippy_atoms, per=scale_per)
    soap = get_soap(quippy_atoms, spkit=get_spkit(
        quippy_atoms), spkitMax=spkit_max, **soapargs)
    return soap


@workfunctions
def stidy_workfunction(structure, ang=5, d1=0.55, d2=0.55, d3=0.55):
    def stidy(structure, ang, d1, d2, d3):
        PLATON = find_executable('platon')
        if not PLATON:
            PLATON = '../bin/platon'

        with NamedTemporaryFile(suffix='.cif') as temp_file:
            # write temporary cif file
            CifWriter(structure).write_file(temp_file.name)
            temp_file.flush()
            # run ADDSYM_SHX to make PLATON recognize symmetries
            addsym_shx_process = Popen(['platon', '-o', temp_file.name],
                                       stdout=PIPE,
                                       stderr=STDOUT,
                                       stdin=PIPE)
            try:
                addsym_shx_process.communicate(
                    input=b'ADDSYM_SHX {} {} {} {}'.format(ang, d1, d2, d3))
            except TimeoutExpired as t:
                return ExitCode(408, 'ADDSYM_SHX timed out: {}'.format(t))
            except Exception as e:
                return ExitCode(500, 'ADDSYM_SHX crashed: {}'.format(e))
            # call STIDY on the ADDSYM_SHX output
            temp_file_dirname, temp_file_basename = path.split(
                temp_file.name)
            temp_file_basename_extless, _ = path.splitext(
                temp_file_basename)
            temp_file_basename_spf = temp_file_basename_extless + '_pl.spf'
            temp_file_spf = path.join(
                temp_file_dirname, temp_file_basename_spf)

            if not os.path.isfile(temp_file_spf):
                return ExitCode(500, 'ADDSYM_SHX failed to write *_pl.spf file')

            stidy_process = Popen(['platon', '-o', temp_file_spf],
                                  stdout=PIPE,
                                  stderr=STDOUT,
                                  stdin=PIPE)
            try:
                stidy_data = stidy_process.communicate(input=b'STIDY')
            except TimeoutExpired as t:
                return ExitCode(408, 'STIDY timed out: {}'.format(t))
            except Exception as e:
                return Exitcode(500, 'STIDY crashed: {}'.format(e))
        stidy_output = stidy_data[0].decode('utf-8')

        # clean up files
        if path.isfile('check.def'):
            remove('check.def')

        return stidy_output

    def get_space_group(stidy_output):
        regexp = re.compile(r'\s*Number in IT :\s*(\d+)')
        match = regexp.search(stidy_output)
        space_group = int(match.group(1))
        return space_group

    def get_wyckoffs(sites):
        wyckoffs = []
        for site in sites:
            wyckoffs.append(site[1].split('(')[-1].split(')')[0])
        return wyckoffs

    def get_sites(stidy_output):
        regexp = re.compile(
            r'\s+([a-zA-Z]{1,2})(\d)+\s+([\w\(\)]{4,5})\s+([\d\/\.]+)\s+([\d\/\.]+)\s+([\d\/\.]+)\s+(\w+)\s+(\d+)')
        match_blocks = []
        for block in stidy_output.split('Wyckoff'):
            matches = []
            matches = regexp.findall(block)
            for m, match in enumerate(matches):
                match = list(match)
                for i in range(3, 6):
                    if '/' in match[i]:
                        j = [float(k) for k in match[i].split('/')]
                        num = j[0] / j[1]
                        match[i] = num
                    else:
                        match[i] = float(match[i])
                match[0] = ''.join(match[0:2])
                del match[1]
                match[6] = int(match[6])
                matches[m] = tuple(match)
            if matches:
                match_blocks.append(matches)
        sites = match_blocks[0]
        return sites

    def get_fingerprint(space_group, wyckoffs, sites):
        ascii_iter = iter(ascii_uppercase)
        symbols = [site[5] for site in sites]
        symbol_map = {}
        for symbol in symbols:
            if symbol not in symbol_map.keys():
                symbol_map[symbol] = next(ascii_iter)
        sites = [(symbol, wyckoff)
                 for symbol, wyckoff in zip(symbols, wyckoffs)]
        formatted_wyckoffs = []
        for wyckoff in sorted(set(wyckoffs)):
            formatted_wyckoff = []
            for symbol in sorted(set(symbols)):
                count = sites.count((symbol, wyckoff))
                if count:
                    formatted_wyckoff.append(
                        '{:02d}{}'.format(count, symbol_map[symbol]))
            formatted_wyckoffs.append(''.join(formatted_wyckoff + [wyckoff]))
        fingerprint = '_'.join([str(space_group)] + formatted_wyckoffs)
        return fingerprint

    ############################################################################

    if isinstance(structure, StructureData):
        structure = structure.get_pymatgen()
    elif isinstance(structure, Atoms):
        structure = AseAtomsAdaptor.get_structure(structure)
    # elif isinstance(structure, CifData):
        # structure = CifParser(CifData.get_attr(
        #     'source')).get_structures(primitive=False)[0]

    stidy_output = stidy(structure, ang, d1, d2, d3)
    space_group = get_space_group(stidy_output)
    sites = get_sites(stidy_output)
    wyckoffs = get_wyckoffs(sites)
    fingerprint = get_fingerprint(space_group, wyckoffs, sites)
    return space_group, wyckoffs, sites, fingerprint
