import pymongo
import sys
sys.path.insert(0, '../rest')
import fingerprints
from pymatgen import Structure
import multiprocessing as mp

DB = 'structureREST'
INPUT_COLLECTION = 'icsd'

N = 1000

client = pymongo.MongoClient('mongodb://localhost:27017/')
db = client[DB]
input_collection = db[INPUT_COLLECTION]

documents = []
structures = []
db_iter = input_collection.find()
while len(documents) < N:
    tmp = db_iter.next()
    structure = Structure.from_dict(tmp['structure'])
    if structure.is_ordered and (len(structure.sites) < 400):
        documents.append({'source_id': tmp['_id'],
                          'source_collection': 'icsd',
                          'matminer_fingerprint': None,
                          'stidy_fingerprint': None,
                          })
        structures.append(tmp['structure'])
