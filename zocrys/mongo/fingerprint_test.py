#!/usr/local/miniconda3/envs/structure/bin/python
# -*- coding: utf-8 -*-
import requests
import pymongo
import logging
import sys
sys.path.insert(0, '../rest')
import fingerprints
from pymatgen import Structure

DB = 'structureREST'
INPUT_COLLECTION = 'icsd'
OUTPUT_COLLECTION = 'fingerprint_test'
N = 1000
MAX_SITES = 50

client = pymongo.MongoClient('mongodb://localhost:27017/')
db = client[DB]

input_collection = db[INPUT_COLLECTION]
output_collection = db[OUTPUT_COLLECTION]

for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                    level=logging.DEBUG,
                    filename='fingerprint_test.log')

logging.info('Starting to fingerprint')
materials = input_collection.find()
structures = []
documents = []
while len(documents) < N:
    material, structure, document = [None] * 3
    try:
        material = materials.next()
    except Exception as e:
        logging.critical('Could not get next material: {}'.format(e))
        raise Exception(e)
    structure = Structure.from_dict(material['structure'])
    if structure.is_ordered:
        if (len(structure.sites) < MAX_SITES):
            try:
                structures.append(material['structure'])
                document = {'source_id': material['_id'],
                            'soruce_collection': INPUT_COLLECTION,
                            'matminer_fingerprint': None,
                            'stidy_fingerprint': None}
                documents.append(document)
                if not (len(documents) % (N / 10)):
                    logging.info(
                        '{} documents collected'.format(len(documents)))
            except Exception as e:
                logging.error('source_id: {} {}'.format(material['_id'], e))
        else:
            logging.error('Too large, {} atoms {}'.format(
                len(structure.sites), material['_id']))
    else:
        logging.error('Unordered {}'.format(material['_id']))

logging.info('Calcluating matminer fingerprints')
matminer_fingerprints = fingerprints.matminer_fingerprints(structures)

# logging.info('Calculating STRUCTURE TIDY fingerprints')
# stidy_fingerprints = fingerprints.stidy_fingerprints(structures)

logging.info('Adding fingerprints to documents')
for d, document in enumerate(documents):
    documents[d]['matminer_fingerprint'] = matminer_fingerprints[d]
    documents[d]['stidy_fingerprint'] = stidy_fingerprints[d]

logging.info('Inserting {} documents into {}'.format(
    len(documents), OUTPUT_COLLECTION))
result = output_collection.insert_many(documents)
logging.info('Inserted {} documents'.format(len(result.inserted_ids)))

logging.info('Finished')
