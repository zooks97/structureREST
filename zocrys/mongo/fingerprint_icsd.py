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
N = 5000
MAX_SITES = 64

client = pymongo.MongoClient('mongodb://localhost:27017/')
db = client[DB]

input_collection = db[INPUT_COLLECTION]
matminer_collection = db['matminer']
stidy_collection = db['stidy']

for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                    level=logging.DEBUG,
                    filename='fingerprint_test.log')

logging.info('Starting to fingerprint')
structures = []
documents = []

for material in input_collection.find():
    structure, document = [None] * 2
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
            except Exception as e:
                logging.error('source_id: {} {}'.format(material['_id'], e))
        else:
            logging.error('Too large, {} atoms {}'.format(
                len(structure.sites), material['_id']))
    else:
        logging.error('Unordered {}'.format(material['_id']))
    if not (len(documents) % (N / 10)):
        logging.info('{} documents collected'.format(len(documents)))
    if len(documents) == N:
        logging.info('Calcluating matminer fingerprints')
        matminer_fingerprints = fingerprints.matminer_fingerprints(structures)
        logging.info('Adding fingerprints to documents')
        matminer_documents = documents.copy()
        for d, document in enumerate(matminer_documents):
             matminer_documents[d]['matminer_fingerprint'] = matminer_fingerprints[d]
        logging.info('Inserting {} documents into {}'.format(
            len(documents), 'matminer'))
        result = matminer_collection.insert_many(documents)
        logging.info('Inserted {} documents'.format(len(result.inserted_ids)))

        logging.info('Calculating STRUCTURE TIDY fingerprints')
        stidy_fingerprints = fingerprints.stidy_fingerprints(structures)
        logging.info('Adding fingerprints to documents')
        stidy_documents = documents.copy()
        for d, document in enumerate(stidy_documents):
             stidy_documents[d]['stidy_fingerprint'] = stidy_fingerprints[d]
        logging.info('Inserting {} documents into {}'.format(
            len(documents), 'stidy'))
        result = stidy_collection.insert_many(documents)
        logging.info('Inserted {} documents'.format(len(result.inserted_ids)))

        logging.info('Resetting documents and structures')
        documents = []
        structures = []

if documents:
    logging.info('Calcluating matminer fingerprints')
    matminer_fingerprints = fingerprints.matminer_fingerprints(structures)
    logging.info('Adding fingerprints to documents')
    matminer_documents = documents.copy()
    for d, document in enumerate(matminer_documents):
         matminer_documents[d]['matminer_fingerprint'] = matminer_fingerprints[d]
    logging.info('Inserting {} documents into {}'.format(
        len(documents), 'matminer'))
    result = matminer_collection.insert_many(documents)
    logging.info('Inserted {} documents'.format(len(result.inserted_ids)))

    logging.info('Calculating STRUCTURE TIDY fingerprints')
    stidy_fingerprints = fingerprints.stidy_fingerprints(structures)
    logging.info('Adding fingerprints to documents')
    stidy_documents = documents.copy()
    for d, document in enumerate(stidy_documents):
         stidy_documents[d]['stidy_fingerprint'] = stidy_fingerprints[d]
    logging.info('Inserting {} documents into {}'.format(
        len(documents), 'stidy'))
    result = stidy_collection.insert_many(documents)
    logging.info('Inserted {} documents'.format(len(result.inserted_ids)))

    logging.info('Resetting documents and structures')
    documents = []
    structures = []

logging.info('Finished')
