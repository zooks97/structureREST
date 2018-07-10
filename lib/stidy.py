# -*- coding: utf-8 -*-
# python 3.6
'''
    Functions and Object for interfacing with PLATON's STIDY routine
'''
from string import ascii_uppercase
from os import remove
from subprocess import Popen, PIPE, STDOUT
from distutils.spawn import find_executable
from tempfile import NamedTemporaryFile
from pymatgen import Structure, Lattice
from pymatgen.io.cif import CifWriter
import re
import os.path
import logging
logger = logging.getLogger(__name__)


class StidyParser(object):
    def __init__(self, stidy_output):
        self.output = stidy_output
        return

    @property
    def formula(self):
        '''str: Reduced chemical formula'''
        regexp = re.compile(r'Structure Tidy Results for\s*(\w*)')
        match = regexp.search(self.output)
        return match.group(1)

    @property
    def space_group(self):
        '''str: Space group descriptor e.g. "P 1"'''
        regexp = re.compile(r'Structure Tidy Results for\s*\w*\s*(.*)')
        match = regexp.search(self.output)
        return str(match.group(1).strip())

    @property
    def axes_change(self):
        '''tuple: New axes in terms of originals e.g. ('a', 'b+c', 'b')'''
        regexp = re.compile(r'Axes changed to : (.*)')
        match = regexp.search(self.output)
        return tuple(match.group(1).strip().split(','))

    @property
    def pearson(self):
        '''str: Pearson code e.g. "aP"'''
        regexp = re.compile(r'Pearson code : (\w*)')
        match = regexp.search(self.output)
        return match.group(1)

    @property
    def cell(self):
        '''tuple: abc and angles of the standardized cell'''
        regexp = re.compile(r'^Cell :.*$', re.MULTILINE)
        match = regexp.search(self.output).group(0)
        abc = tuple(map(float, match.split(':')[-1].strip().split()[:3]))
        angles = tuple(map(float, match.split(':')[-1].strip().split()[3:]))
        return (abc, angles)

    @property
    def itc_number(self):
        '''int: space group number from international tables of crystallography'''
        regexp = re.compile(r'\s*Number in IT :\s*(\d+)')
        match = regexp.search(self.output)
        return int(match.group(1))

    @property
    def setting(self):
        '''
        list: ???
              One entry per output structure
        '''
        regexp = re.compile(r'Setting\s*([-\w]*),([-\w]*),([-\w]*)')
        return regexp.findall(self.output)

    @property
    def origin(self):
        '''
        list: New origin in the old cell
        One entry per output structure
        '''
        regexp = re.compile(r'Origin\s*\(.*\)')
        matches = regexp.findall(self.output)
        for i, match in enumerate(matches):
            matches[i] = tuple(map(float, match.strip('() ').split()[2:]))
        return matches

    @property
    def gamma(self):
        '''
        list: Gamma values for standardization minimization
              One entry per output structure
        '''
        regexp = re.compile(r'Gamma\s*=\s*.*')
        matches = regexp.findall(self.output)
        return [float(match.split()[-1]) for match in matches]

    @property
    def sites(self):
        '''
        list: Site data including:
            str: numbered species e.g. 'Mo1'
            str: wyckoff site e.g. '2(d)'
            float: x
            float: y
            float: z
            str: species e.g. 'Mo'
            int: number
        One set of sites per output structure
        '''
        regexp = re.compile(
            r'\s+([a-zA-Z]{1,2})(\d)+\s+([\w\(\)]{4,5})\s+([\d\/\.]+)\s+([\d\/\.]+)\s+([\d\/\.]+)\s+(\w+)\s+(\d+)')
        match_blocks = []
        for block in self.output.split('Wyckoff'):
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
        return match_blocks

    @property
    def wyckoff(self):
        '''
        list: Wyckoff occupations
        One set of sites per output structure
        '''
        wyckoff = []
        for sites in self.sites:
            sequence = []
            for site in sites:
                sequence.append(site[1].split('(')[-1].split(')')[0])
            wyckoff.append(sequence)
        return wyckoff

    @property
    def summary_and_remarks(self):
        '''str: Unprocessed summary and remarks cut from output file'''
        regexp = re.compile(r'^Summary and Remarks.*-\n',
                            re.MULTILINE | re.DOTALL)
        return regexp.search(self.output).group(0)

    @property
    def structure(self):
        '''
        pymatgen.core.Structure: Structure object
        One entry per output structure
        '''
        structures = []
        cell = self.cell
        for sites in self.sites:
            species = [site[-2] for site in sites]
            fractional_coords = [tuple(site[2:5]) for site in sites]
            lattice = Lattice.from_lengths_and_angles(abc=cell[0],
                                                      ang=cell[1])
            structure = Structure(lattice=lattice,
                                  species=species,
                                  coords=fractional_coords)
            structures.append(structure)
        return structures

    @property
    def wyckoff_fingerprint(self):
        '''
        str: Wickoff fingerprint of the form
            [space group number]_[Wyckoff_number_for_each_site]
        '''
        fingerprints = []
        for sites, wyckoff in zip(self.sites, self.wyckoff):
            ascii_iter = iter(ascii_uppercase)
            symbols = [site[5] for site in sites]
            symbol_map = {}
            for symbol in symbols:
                if symbol not in symbol_map.keys():
                    symbol_map[symbol] = next(ascii_iter)
            sites = [(symbol, wyck)
                     for symbol, wyck in zip(symbols, wyckoff)]
            space_group_number = self.itc_number
            formatted_wycks = []
            for wyck in sorted(set(wyckoff)):
                formatted_wyck = []
                for symbol in sorted(set(symbols)):
                    count = sites.count((symbol, wyck))
                    if count:
                        formatted_wyck.append(
                            '{:02d}{}'.format(count, symbol_map[symbol]))
                formatted_wycks.append(''.join(formatted_wyck + [wyck]))
            fingerprints.append(
                '_'.join([str(space_group_number)] + formatted_wycks))
        return fingerprints


def stidy(structure, exact=True, ang=1., d1=0.25, d2=0.25, d3=0.25, timeout=15):
    '''
    Run STRUCTURE TIDY as implemented in the PLATON software package.
    PLATON must either be in the PATH or in ../bin.

    References:
        A. L. Spek (2009). Acta Cryst., D65, 148-155.
        E. Parthé and L. M. Gelato (1984). Acta Cryst., A40, 169-183.
        L. M. Gelato and E. Parthé (1987). J. Appl. Cryst. 20, 139-143.
        S-Z. Hu and E. Parthé (2004). Chinese J. Struct. Chem. 23, 1150-1160.

    Args:
        structure (pymatgen.core.Structure): Pymatgen Structure object for the
            (probably) untidy structure
        exact (bool): If False, allow up to 20% of atoms to be mis-fits
        ang (float): Angle criterium in search for metrical symmetry of the lattice in degrees
        d1 (float): Distance criterium for coinciding atoms for non-inversion symmetry elements in Angstrom 
        d2 (float): Distance criterium for coinciding atoms for inversion symmetry elements in Angstrom 
        d3 (float): Distance criterium for coinciding atoms for translation symmetry elements in Angstrom 
    Returns:
        pymatgen.core.Structure: STRUCTURE TIDY standardized structure in
            Pymatgen object form
    '''
    PLATON = find_executable('platon')
    if not PLATON:
        PLATON = '../bin/platon1'

    with NamedTemporaryFile(suffix='.cif') as temp_file:
        # write temporary cif file
        CifWriter(structure).write_file(temp_file.name)
        temp_file.flush()
        # run ADDSYM_SHX to make PLATON recognize symmetries
        addsym_shx_process = Popen(['platon', '-o', temp_file.name],
                                   stdout=PIPE,
                                   stderr=STDOUT,
                                   stdin=PIPE)
        if exact:
            try:
                addsym_shx_process.communicate(
                    input=b'ADDSYM_SHX EXACT', timeout=timeout)
            except Exception as e:
                logger.error(e)
        else:
            try:
                addsym_shx_process.communicate(
                    input=b'ADDSYM_SHX {} {} {} {}'.format(ang, d1, d2, d3), timeout=timeout)
            except Exception as e:
                logger.error(e)
        # call STIDY on the ADDSYM_SHX output
        temp_file_dirname, temp_file_basename = os.path.split(
            temp_file.name)
        temp_file_basename_extless, _ = os.path.splitext(
            temp_file_basename)
        temp_file_basename_spf = temp_file_basename_extless + '_pl.spf'
        temp_file_spf = os.path.join(
            temp_file_dirname, temp_file_basename_spf)

        stidy_process = Popen(['platon', '-o', temp_file_spf],
                              stdout=PIPE,
                              stderr=STDOUT,
                              stdin=PIPE)
        stidy_data = stidy_process.communicate(input=b'STIDY')
    stidy_output = stidy_data[0].decode('utf-8')

    # clean up files
    # if os.path.isfile('check.def'):
    #     remove('check.def')

    return StidyParser(stidy_output)
