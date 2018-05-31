from pymatgen.io.cif import CifParser
import pymongo
import logging

DB = 'structureREST'
COLLECTION = 'cod'
N = 10000

client = pymongo.MongoClient('mongodb://localhost:27017/')
db = client[DB]

group = Group.get_from_string('%s_cif_raw' % COLLECTION)

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                    level=logging.DEBUG,
                    filename='%s.log' % COLLECTION)
logging.info('Creating collection %s', COLLECTION)

collection = db[COLLECTION]
documents = []
for cif in group.nodes:
    path, structures, source, structure, document = [None] * 5
    path = cif.get_file_abs_path()
    try:
        structures = CifParser(path).get_structures(primitive=False)
    except Exception as exception:
        logging.error('%s', str(exception))
    else:
        source = cif.get_attr('source')
        for structure in structures:
            document = {
                'source': source,
                'structure': structure.as_dict()
            }
            documents.append(document)
            if not (len(documents) % (N / 10)):
                logging.info('%d documents collected', len(documents))
            if len(documents) == N:
                logging.info('Inserting %d documents into %s',
                              len(documents), COLLECTION)
                try:
                    result = collection.insert_many(documents)
                except Exception as exception:
                    logging.critical('%s', str(exception))
                    raise Exception(exception)
                else:
                    logging.info('Successfuly inserted %d documents into %s',
                                 len(result.inserted_ids), COLLECTION)
                    documents = []

if documents:
    logging.info('Inserting %d documents into %s', len(documents), COLLECTION)
    try:
        result = collection.insert_many(documents)
    except Exception as exception:
        logging.critical('%s', str(exception))
        raise Exception(exception)
    else:
        logging.info('Successfuly inserted %d documents into %s',
                        len(result.inserted_ids), COLLECTION)
        documents = []
logging.info('Complete')