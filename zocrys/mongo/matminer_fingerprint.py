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
OUTPUT_COLLECTION = 'matminer_fingerprint'
N = 1000

client = pymongo.MongoClient('mongodb://localhost:27017/')
db = client[DB]

input_collection = db[INPUT_COLLECTION]
output_collection = db[OUTPUT_COLLECTION]

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                    level=logging.DEBUG,
                    filename='matminer_fingerprint_test.log')

logging.info('Starting to fingerprint')
materials = input_collection.find()
documents = []
while len(documents) < N:
    if not (len(documents) % (N / 10)):
        logging.info('{} documents collected'.format(len(documents)))
    material, structure, document = [None] * 3
    try:
        material = materials.next()
    except Exception as e:
        logging.critical('Could not get next material: {}'.format(e))
        raise Exception(e)
    structure = Structure.from_dict(material['structure'])
    if structure.is_ordered:
        try:
            document = {'source_id': material['_id'],
                        'fingerprint': fingerprints.matminer_fingerprints([material['structure']])[0]}
            documents.append(document)
        except Exception as e:
            logging.error('source_id: {} {}'.format(material['_id'], e))
    else:
        logging.error('Unordered {}'.format(material['_id']))
print(len(documents))

logging.info('Inserting {} documents into {}'.format(
    len(documents), OUTPUT_COLLECTION))
result = output_collection.insert_many(documents)
logging.info('Inserted {} documents'.format(len(result.inserted_ids)))

logging.info('Finished')
