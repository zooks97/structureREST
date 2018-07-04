#!/usr/local/miniconda3/envs/structure/bin/python
# -*- coding: utf-8 -*-
import pymongo
import numpy as np
import sys

sys.path.insert(0, '../rest')
import fingerprints

from sklearn.cluster import DBSCAN
from sklearn import metrics
from sklearn.datasets.samples_generator import make_blobs
from sklearn.preprocessing import StandardScaler


DB = 'structureREST'
COLLECTION = 'matminer_fingerprint'

client = pymongo.MongoClient('mongodb://localhost:27017/')
db = client[DB]
collection = db[COLLECTION]

documents = collection.find()
documents = list(documents)
matminer_fingerprints = [document['fingerprint'] for document in documents]

dbscan = DBSCAN(min_samples=1, n_jobs=1).fit(matminer_fingerprints)
core_samples_mask = np.zeros_like(dbscan.labels_, dtype=bool)
core_samples_mask[dbscan.core_sample_indices_] = True
labels = dbscan.labels_

# Number of clusters in labels, ignoring noise if present.
n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)

print('Estimated number of clusters: %d' % n_clusters_)
# print("Homogeneity: %0.3f" % metrics.homogeneity_score(labels_true, labels))
# print("Completeness: %0.3f" % metrics.completeness_score(labels_true, labels))
# print("V-measure: %0.3f" % metrics.v_measure_score(labels_true, labels))
# print("Adjusted Rand Index: %0.3f"
#       % metrics.adjusted_rand_score(labels_true, labels))
# print("Adjusted Mutual Information: %0.3f"
#       % metrics.adjusted_mutual_info_score(labels_true, labels))
print("Silhouette Coefficient: %0.3f"
      % metrics.silhouette_score(matminer_fingerprints, labels))

clusters = {}
for i, label in enumerate(labels):
    if label not in clusters.keys():
        clusters[label] = []
    document = documents[i]
    material = db['mpds'].find_one({'_id': document['source_id']})
    clusters[label].append(document['stidy_fingerprint'])

print(clusters)
