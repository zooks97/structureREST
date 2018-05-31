import pymatgen
from pymatgen.symmetry.analyzer import SpacegroupAnalyzer
import re
import distutils.spawn
import pymatgen.io.cif
import tempfile
import subprocess
import os
import pathlib

class StidyParser(object):
    def __init__(self: object, stidy_output: str) -> None:
        self.output = stidy_output
        return
    
    @property
    def formula(self: object) -> str:
        '''str: Reduced chemical formula'''
        regexp = re.compile(r'Structure Tidy Results for\s*(\w*)')
        match = regexp.search(self.output)
        return match.group(1)

    @property
    def space_group(self: object) -> str:
        '''str: Space group descriptor e.g. "P 1"'''
        regexp = re.compile(r'Structure Tidy Results for\s*\w*\s*(.*)')
        match = regexp.search(self.output)
        return str(match.group(1).strip())

    @property
    def axes_change(self: object) -> (str):
        '''tuple: New axes in terms of originals e.g. ('a', 'b+c', 'b')'''
        regexp = re.compile(r'Axes changed to : (.*)')
        match = regexp.search(self.output)
        return tuple(match.group(1).strip().split(','))

    @property
    def pearson(self: object) -> str:
        '''str: Pearson code e.g. "aP"'''
        regexp = re.compile(r'Pearson code : (\w*)')
        match = regexp.search(self.output)
        return match.group(1)

    @property
    def cell(self: object) -> ((float)):
        '''tuple: abc and angles of the standardized cell'''
        regexp = re.compile(r'^Cell :.*$', re.MULTILINE)
        match = regexp.search(self.output).group(0)
        abc = tuple(map(float, match.split(':')[-1].strip().split()[:3]))
        angles = tuple(map(float, match.split(':')[-1].strip().split()[3:]))
        return (abc, angles)

    @property
    def itc_number(self: object) -> int:
        '''int: ???'''
        regexp = re.compile(r'\s*Number in IT :\s*(\d+)')
        match = regexp.search(self.output)
        return int(match.group(1))
    
    @property
    def setting(self: object) -> [(str)]:
        '''
        list: ???
              One entry per output structure
        '''
        regexp = re.compile(r'Setting\s*([-\w]*),([-\w]*),([-\w]*)')
        return regexp.findall(self.output)
    
    @property
    def origin(self: object) -> [(float)]:
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
    def gamma(self: object) -> [float]:
        '''
        list: Gamma values for standardization minimization
              One entry per output structure
        '''
        regexp = re.compile(r'Gamma\s*=\s*.*')
        matches = regexp.findall(self.output)
        return [float(match.split()[-1]) for match in matches]
   
    @property
    def sites(self: object) -> list:
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
        regexp = re.compile(r'\s+([a-zA-Z]{1,2})(\d)+\s+([\w\(\)]{4,5})\s+([\d\/\.]+)\s+([\d\/\.]+)\s+([\d\/\.]+)\s+(\w+)\s+(\d+)')
        match_blocks = []
        for block in self.output.split('Wyckoff'):
            matches = []
            matches = regexp.findall(block)
            for m, match in enumerate(matches):
                match = list(match)
                for i in range(3,6):
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
    def wyckoff(self: object) -> [(str)]:
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
    def summary_and_remarks(self: object) -> str:
        '''str: Unprocessed summary and remarks cut from output file'''
        regexp = re.compile(r'^Summary and Remarks.*-\n',
                            re.MULTILINE|re.DOTALL)
        return regexp.search(self.output).group(0)
    
    @property
    def structure(self: object) -> [pymatgen.core.Structure]:
        '''
        pymatgen.core.Structure: Structure object
        One entry per output structure
        '''
        structures = []
        cell = self.cell
        for sites in self.sites:
            species = [site[-2] for site in sites]
            fractional_coords = [tuple(site[2:5]) for site in sites]
            lattice = pymatgen.Lattice.from_lengths_and_angles(abc=cell[0],
                                                               ang=cell[1])
            structure = pymatgen.Structure(lattice=lattice,
                                           species=species,
                                           coords=fractional_coords)
            structures.append(structure)
        return structures
    
    @property
    def wyckoff_fingerprint(self: object) -> str:
        '''
        str: Wickoff fingerprint of the form
            [space group number]_[Wyckoff_number_for_each_site]
        '''
        fingerprint = []
        for sequence in self.wyckoff:
            fingerprint.append('_'.join([str(self.itc_number)] + sequence))
        return fingerprint

def _stidy(structure: pymatgen.core.Structure) -> StidyParser:
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
    Returns:
        pymatgen.core.Structure: STRUCTURE TIDY standardized structure in
            Pymatgen object form
        
    '''
    PLATON = distutils.spawn.find_executable('platon')
    if not PLATON: 
        PLATON = '../bin/platon'

    structure_cif = str(pymatgen.io.cif.CifWriter(structure))
    with tempfile.NamedTemporaryFile(suffix='.cif') as temp_file:
        # write temporary cif file
        temp_file.write(bytes(structure_cif, encoding='utf-8'))
        temp_file.flush()
        temp_file_path = pathlib.Path(temp_file.name)
        # run ADDSYM_SHX to make PLATON recognize symmetries
        addsym_shx_process = subprocess.Popen(['platon', '-o', temp_file.name],
                                              stdout=subprocess.PIPE,
                                              stderr=subprocess.STDOUT,
                                              stdin=subprocess.PIPE)
        addsym_shx_data = addsym_shx_process.communicate(input=b'ADDSYM_SHX')
        # call STIDY on the ADDSYM_SHX output
        temp_file_spf = str(temp_file_path.parent / (str(temp_file_path.stem) +
                            '_pl.spf'))
        stidy_process = subprocess.Popen(['platon', '-o', temp_file_spf],
                                          stdout=subprocess.PIPE,
                                          stderr=subprocess.STDOUT,
                                          stdin=subprocess.PIPE)
        stidy_data = stidy_process.communicate(input=b'STIDY')
    stidy_output = stidy_data[0].decode('utf-8')
    
    # clean up files
    if pathlib.Path('check.def').exists():
        os.remove('check.def')

    return StidyParser(stidy_output)

def wyckoff_fingerprint(structure: dict) -> (str, dict):
    structure = pymatgen.Structure.from_dict(structure)
    stidy_parser = _stidy(structure)
    fingerprint = stidy_parser.wyckoff_fingerprint
    ps_structure = stidy_parser.structure[0]
    return fingerprint, ps_structure
