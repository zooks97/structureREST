# -*- coding: utf-8 -*-
# python 3.6
import flask
import flask_restful
from flask_restful.reqparse import Argument, RequestParser
from requests import get
from sys import path
import json
path.insert(0, '../../lib/')
import comparisons
import distances
import fingerprints
import atoms_utils

app = flask.Flask(__name__)
api = flask_restful.Api(app)
VERSION = 1

### Argumernts ###
ARGUMENTS = {
    # generic
    'structures': Argument('structures', type=str, required=True,
                           help='Pymatgen structure objects'),
    # pymatgen
    'ltol': Argument('ltol', type=float, store_missing=False,
                     help='Fractional length tolerance'),
    'stol': Argument('stol', type=float, store_missing=False,
                     help='Site tolerance'),
    'angle_tol': Argument('angle_tol', type=float, store_missing=False,
                          help='Angle tolerance in degrees'),
    'primitive_cell': Argument('primitive_cell', type=bool, store_missing=False,
                               help='Whether to reduce structures to primitive cells prior to matching'),
    'attempt_supercell': Argument('attempt_supercell', type=bool, store_missing=False,
                                  help='If set to True and number of sites in cells differ after a primitive cell reduction (divisible by an integer) attempts to generate a supercell transformation of the smaller cell which is equivalent to the larger structure'),
    'allow_subset': Argument('allow_subset', type=bool, store_missing=False,
                             help='Allow one structure to match to the subset of another structure'),
    'comparator': Argument('comparator',
                           choices=['AbstractComparator', 'ElementComparator',
                                    'FrameworkComparator',
                                    'OccupancyComparator',
                                    'OrderDisorderElemementComparator',
                                    'SpeciesComparator', 'SpinComparator'],
                           store_missing=False,
                           help='Name of a comparator object'),
    'supercell_size': Argument('supercell_size', type=str, store_missing=False,
                               help='Method to use for determining the size of a supercell if applicable'),
    'ignored_species': Argument('ignored_species', type=list, store_missing=False,
                                help='A list of ions to be ignored in matching'),
    'anonymous': Argument('anonymous', type=bool, store_missing=False,
                          help='Allow distinct species in one species to map to another'),

    # matminer
    'preset': Argument('preset', type=str,
                       choices=['cn', 'ops'],
                       store_missing=False,
                       help='Use preset parameters to get the fingerprint args'),
    'crystal_site_args': Argument('crystal_site_args', type=dict, store_missing=False,
                                  help='Arguments passed to CrystalNNFingerprint'),
    'site_stats_args': Argument('site_stats_args', type=dict, store_missing=False,
                                help='Arguments passed to SiteStatsFingerprint'),
    'distance_tol': Argument('distance_tol', type=float, store_missing=False,
                             help='Distance tolerance for comparison to return True or distance to be rounded to 0'),

    # spglib
    'symprec': Argument('symprec', type=float,
                        store_missing=False,
                        help='Cartesian symmetry tolerance (please use Å!)'),
    'angle_tolerance': Argument('angle_tolerance', type=float,
                                store_missing=False,
                                help='Angle tolerance in degrees')

}


### Distances ###
class Pymatgen_Distances(flask_restful.Resource):
    def get(self):
        parser = RequestParser()
        argument_names = ['structures', 'ltol', 'stol', 'angle_tol',
                          'primitive_cell', 'attempt_supercell',
                          'allow_subset', 'comparator', 'supercell_size',
                          'ignored_species']
        for argument_name in argument_names:
            parser.add_argument(ARGUMENTS[argument_name])
        args = parser.parse_args(strict=True)
        args['structures'] = flask.json.loads(args['structures'])
        calculated_distances = distances.pymatgen_distances(**args)

        return flask.jsonify(calculated_distances)


api.add_resource(Pymatgen_Distances,
                 '/v{:d}/distances/pymatgen/'.format(VERSION))


class Matminer_Distances(flask_restful.Resource):
    def get(self):
        parser = flask_restful.reqparse.RequestParser()
        argument_names = ['structures', 'preset', 'crystal_site_args',
                          'site_stats_args', 'distance_tol']
        for argument_name in argument_names:
            parser.add_argument(ARGUMENTS[argument_name])
        args = parser.parse_args(strict=True)
        args['structures'] = flask.json.loads(args['structures'])
        calculated_distances = distances.matminer_distances(**args)

        return flask.jsonify(calculated_distances)


api.add_resource(Matminer_Distances,
                 '/v{:d}/distances/matminer/'.format(VERSION))


### Comparisons ###
class Pymatgen_Comparisons(flask_restful.Resource):
    def get(self):
        parser = RequestParser()
        argument_names = ['structures', 'ltol', 'stol', 'angle_tol',
                          'primitive_cell', 'attempt_supercell',
                          'allow_subset', 'comparator', 'supercell_size',
                          'ignored_species', 'anonymous']
        for argument_name in argument_names:
            parser.add_argument(ARGUMENTS[argument_name])
        args = parser.parse_args(strict=True)
        args['structures'] = flask.json.loads(args['structures'])
        calculated_comparisons = comparisons.pymatgen_comparisons(**args)

        return flask.jsonify(calculated_comparisons)


api.add_resource(Pymatgen_Comparisons,
                 '/v{:d}/comparisons/pymatgen/'.format(VERSION))


class Matminer_Comparisons(flask_restful.Resource):
    def get(self):
        parser = flask_restful.reqparse.RequestParser()
        argument_names = ['structures', 'preset', 'crystal_site_args',
                          'site_stats_args', 'distance_tol']
        for argument_name in argument_names:
            parser.add_argument(ARGUMENTS[argument_name])
        args = parser.parse_args(strict=True)
        args['structures'] = flask.json.loads(args['structures'])
        calculated_comparisons = comparisons.matminer_comparisons(**args)

        return flask.jsonify(calculated_comparisons)


api.add_resource(Matminer_Comparisons,
                 '/v{:d}/comparisons/matminer/'.format(VERSION))


### Fingerprints ###
class Matminer_Fingerprints(flask_restful.Resource):
    def get(self):
        parser = flask_restful.reqparse.RequestParser()
        argument_names = ['structures', 'preset', 'crystal_site_args',
                          'site_stats_args']
        for argument_name in argument_names:
            parser.add_argument(ARGUMENTS[argument_name])
        args = parser.parse_args(strict=True)
        args['structures'] = flask.json.loads(args['structures'])
        calculated_fingerprints = fingerprints.matminer_fingerprints(**args)

        return flask.jsonify(calculated_fingerprints)


api.add_resource(Matminer_Fingerprints,
                 '/v{:d}/fingerprints/matminer/'.format(VERSION))


class Stidy_Fingerprints(flask_restful.Resource):
    def get(self):
        parser = flask_restful.reqparse.RequestParser()
        argument_names = ['structures', 'symprec', 'angle_tolerance']
        for argument_name in argument_names:
            parser.add_argument(ARGUMENTS[argument_name])
        args = parser.parse_args(strict=True)
        args['structures'] = flask.json.loads(args['structures'])
        calculated_fingerprints = fingerprints.stidy_fingerprints(**args)

        return flask.jsonify(calculated_fingerprints)


api.add_resource(Stidy_Fingerprints,
                 '/v{:d}/fingerprints/stidy/'.format(VERSION))


@app.route('/v{:d}/fingerprints/soap/'.format(VERSION), methods=['GET'])
def Soap_Fingerprint():
    args = dict(flask.request.args)
    args['structure'] = json.loads(args['structure'])
    args['atoms'] = atoms_utils.from_structure_dict(args.pop('structure'))
    args['atoms'] = atoms_utils.dumps(args['atoms'])
    soap_request = get('http://127.0.0.1:8080/v1/get_soap/',
                       params=args)
    return flask.jsonify(soap_request.json())


@app.route('/v{:d}/fingerprints/soaps/'.format(VERSION), methods=['GET'])
def Soap_Fingerprints():
    args = dict(flask.request.args)
    args['structures'] = [json.loads(d) for d in args['structures']]
    args['atoms'] = [atoms_utils.from_structure_dict(s) for s in args.pop('structures')]
    args['atoms'] = [atoms_utils.dumps(a) for a in args['atoms']]
    soap_request = get('http://127.0.0.1:8080/v1/get_Soaps/',
                       params=args)
    return flask.jsonify(soap_request.json())


if __name__ == '__main__':
    app.run(debug=True)
